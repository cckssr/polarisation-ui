"""Detector: PD-TIA gain (manual and auto), calibration profile, PD-TIA id, dark tare, power.

Covers everything that decides how the intensity channel is read and converted to power. The
PM400 connection lives in ``PM400Controller``; this controller only reports which detector is
active. It never touches widgets; the window mirrors its signals.
"""

from __future__ import annotations

import math
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from polarisation_ui.core.power_calibration import (
    PROFILES_DIR,
    PowerCalibrationProfile,
    load_gain_power_limits,
    select_best_profile_for_device_id,
    select_gain_for_power,
)
from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.ui.controllers.connection_controller import ConnectionController
from polarisation_ui.ui.controllers.data_controller import DataController
from polarisation_ui.ui.controllers.status import LED_OK, LED_WARN, ROW_DETECTOR, StatusHub

DARK_TARE_SAMPLES = 20
GAIN_STAGES = (1, 2, 3, 4)


class DetectorController(QObject):
    """PD-TIA gain, calibration profile selection and dark-current tare."""

    row_state_changed = Signal(str, str, str)  # row, LED state, text (detector row only)
    gain_changed = Signal(int)  # the active gain stage 1-4 (the window checks the buttons)
    gain_cleared = Signal()  # no gain stage is active
    gain_auto_changed = Signal(bool)  # AUTO gain-select toggled from outside the buttons
    active_detector_changed = Signal(str)  # core.detector.DETECTOR_*
    profile_changed = Signal(str)  # stem of the selected calibration profile, "" for none
    pdtia_id_changed = Signal(str)  # PD-TIA device id restored from a session
    dark_tare_busy = Signal(bool)
    dark_offset_changed = Signal(float)  # dark-current offset in V (0.0 = reset)
    persist_requested = Signal()

    def __init__(
        self,
        config: AppConfig,
        data: DataController,
        status: StatusHub,
        connection: ConnectionController,
        profiles_dir: Path = PROFILES_DIR,
        parent: QObject | None = None,
    ) -> None:
        """Read the per-gain power windows from ``pdtia.gain_auto_switch_power_W``."""
        super().__init__(parent)
        self._cfg = config
        self._data = data
        self._status = status
        self._connection = connection
        self._profiles_dir = profiles_dir
        self._limits = load_gain_power_limits(config.data)

        self._calibration_profile: PowerCalibrationProfile | None = None
        self._profile_name = ""
        self._pdtia_id = ""
        # True once the profile was auto-selected for the current PD-TIA id; reset when the id
        # changes so a new id triggers the auto-selection again.
        self._pdtia_auto_cal_done = False
        # Gain stage to apply when the Arduino next connects (set by a session restore).
        self._pending_gain_restore = 0
        # AUTO gain-select: off by default each session; the last power is cached so toggling
        # AUTO on reacts immediately without waiting for a new frame.
        self._gain_auto_enabled = False
        self._last_power_W: float | None = None
        # Set by the KDC zero-find, which drives the gain deliberately.
        self.gain_auto_suspended = False

        data.active_detector_changed.connect(self.active_detector_changed)
        data.dark_tare_progress.connect(self._on_dark_tare_progress)
        data.dark_tare_done.connect(self._on_dark_tare_done)
        data.power_updated.connect(self.on_power)
        connection.ready.connect(self.on_link_ready)

    # ---- helpers -------------------------------------------------------------------------
    def _t(self, key: str, **fmt: object) -> str:
        return self._cfg.text(f"main_window.{key}", **fmt)

    def _m(self, key: str, **fmt: object) -> str:
        return self._cfg.message(f"detector.{key}", **fmt)

    @property
    def calibration_profile(self) -> PowerCalibrationProfile | None:
        """The loaded power-calibration profile, if any."""
        return self._calibration_profile

    @property
    def profile_name(self) -> str:
        """Stem of the selected profile ("" when none is selected)."""
        return self._profile_name

    @property
    def pdtia_id(self) -> str:
        """The selected PD-TIA device id."""
        return self._pdtia_id

    @property
    def gain_auto_enabled(self) -> bool:
        """True while AUTO gain-select is on."""
        return self._gain_auto_enabled

    @property
    def gain_auto_available(self) -> bool:
        """True when ``pdtia.gain_auto_switch_power_W`` defines power windows."""
        return bool(self._limits)

    @property
    def pdtia_ids(self) -> list[str]:
        """Device ids offered by ``pdtia.device_ids`` in config.json."""
        return [str(i) for i in self._cfg.get("pdtia.device_ids", [])]

    # ---- gain ----------------------------------------------------------------------------
    @Slot(int)
    def select_gain(self, stage: int) -> None:
        """Set the gain stage the user clicked; an explicit choice turns AUTO off."""
        if self._gain_auto_enabled:
            self._gain_auto_enabled = False
            self.gain_auto_changed.emit(False)
        if not self._data.set_pdtia_gain(stage):
            self.gain_cleared.emit()
            self._status.error(self._m("gain_failed", stage=stage))
            return
        self.gain_changed.emit(stage)
        self.persist_requested.emit()
        self._status.info(self._m("gain_set", stage=stage))

    def apply_gain(self, stage: int) -> bool:
        """Set the gain stage programmatically (no status message); True on success."""
        ok = self._data.set_pdtia_gain(stage)
        if ok:
            self.gain_changed.emit(stage)
        return ok

    @Slot(bool)
    def set_gain_auto(self, enabled: bool) -> None:
        """Turn AUTO gain-select on or off; turning it on applies the gain at once."""
        self._gain_auto_enabled = enabled
        self.gain_auto_changed.emit(enabled)
        if enabled:
            self.maybe_auto_switch_gain()

    def set_pending_gain(self, stage: int) -> None:
        """Gain stage to apply when the Arduino next connects (session restore)."""
        if 1 <= stage <= 4:
            self._pending_gain_restore = stage

    def maybe_auto_switch_gain(self, power_W: float | None = None) -> None:
        """Switch the gain to match ``power_W`` (or the last reading) per the config limits.

        A no-op while the KDC zero-find drives the gain, while no limits are configured, while no
        calibrated power is known, or while the PM400 is the active detector (the PD-TIA photodiode
        is then physically replaced).
        """
        if self.gain_auto_suspended or not self._limits or self._data.is_pm400_active:
            return
        if power_W is None:
            power_W = self._last_power_W
        if power_W is None or math.isnan(power_W):
            return
        current = self._data.pdtia_gain or None
        target = select_gain_for_power(power_W, self._limits, current)
        if target is None or target == current:
            return
        if self._data.set_pdtia_gain(target):
            self.gain_changed.emit(target)
            self.persist_requested.emit()
            self._status.info(self._m("gain_auto_set", stage=target))

    @Slot(float)
    def on_power(self, power_W: float) -> None:
        """Cache the latest calibrated power and let AUTO react to it."""
        self._last_power_W = power_W
        if not math.isnan(power_W) and not self._data.is_pm400_active and self._gain_auto_enabled:
            self.maybe_auto_switch_gain(power_W)

    @Slot()
    def on_link_ready(self) -> None:
        """After the Arduino connected: apply the gain, auto-select a profile, show the status."""
        pending, self._pending_gain_restore = self._pending_gain_restore, 0
        if 1 <= pending <= 4:
            stage = pending
        else:
            stage = self._data.device_manager.get_pdtia_gain() + 1  # firmware reports 0-based
            if not (1 <= stage <= 4):
                stage = 1  # always ensure a gain is active
        self.apply_gain(stage)

        if self._pdtia_id and not self._pdtia_auto_cal_done:
            self._auto_select_calibration_for_id(self._pdtia_id)
        self.update_calibration_status()

    # ---- calibration profile -------------------------------------------------------------
    def list_profiles(self) -> list[Path]:
        """Calibration profile files, newest layout as defined by ``PowerCalibrationProfile``."""
        return PowerCalibrationProfile.list_profiles(self._profiles_dir)

    @Slot(object)
    def select_profile(self, path: Path | None) -> None:
        """Load the profile at ``path`` (None clears it) and hand it to the data controller."""
        self._calibration_profile = None
        self._profile_name = path.stem if path is not None else ""
        if path is not None:
            try:
                self._calibration_profile = PowerCalibrationProfile.load(path)
                Debug.info(f"Loaded calibration profile: {path}")
            except Exception as exc:
                Debug.error(f"Failed to load calibration profile {path}: {exc}")
        self._data.update_calibration_profile(self._calibration_profile)
        self.update_calibration_status()
        self.profile_changed.emit(self._profile_name)
        self.persist_requested.emit()

    def select_profile_by_name(self, name: str) -> bool:
        """Select the listed profile called ``name``; False if there is none."""
        for path in self.list_profiles():
            if path.stem == name:
                self.select_profile(path)
                return True
        return False

    def update_calibration_status(self) -> None:
        """Show a calibration hint on the detector row when connected without a profile."""
        if not self._connection.is_connected:
            return
        if self._calibration_profile is None:
            self.row_state_changed.emit(
                ROW_DETECTOR, LED_WARN, self._t("status_select_calibration")
            )
        else:
            self.row_state_changed.emit(ROW_DETECTOR, LED_OK, self._t("status_adc"))

    # ---- PD-TIA device id ----------------------------------------------------------------
    def init_pdtia_id(self, device_id: str) -> None:
        """Take over the id the selector starts with (no auto-selection)."""
        self._pdtia_id = device_id

    @Slot(str)
    def set_pdtia_id(self, device_id: str) -> None:
        """The user picked another PD-TIA: re-run the profile auto-selection for it."""
        self._pdtia_id = device_id
        self._pdtia_auto_cal_done = False
        self.persist_requested.emit()
        if self._connection.is_connected and device_id:
            self._auto_select_calibration_for_id(device_id)

    def restore_pdtia_id(self, device_id: str) -> None:
        """Select a remembered id without triggering the auto-selection."""
        if device_id in self.pdtia_ids:
            self._pdtia_id = device_id
            self.pdtia_id_changed.emit(device_id)

    def _auto_select_calibration_for_id(self, device_id: str) -> None:
        """Select the newest profile whose filename contains ``device_id`` (once per id)."""
        if self._pdtia_auto_cal_done or not device_id:
            return
        best = select_best_profile_for_device_id(self.list_profiles(), device_id)
        if best is None:
            Debug.info(f"No calibration profile found for PDTIA ID: {device_id}")
            return
        self._pdtia_auto_cal_done = True
        self.select_profile(best)
        self._status.info(self._m("profile_auto_selected", name=best.stem))
        Debug.info(f"Auto-selected calibration profile: {best.stem}")

    # ---- dark tare -----------------------------------------------------------------------
    def start_dark_tare(self) -> None:
        """Average the dark current over ``DARK_TARE_SAMPLES`` readings (detector covered)."""
        self.dark_tare_busy.emit(True)
        self._status.info(self._m("dark_tare_progress", current=0, total=DARK_TARE_SAMPLES))
        self._data.start_dark_tare(n=DARK_TARE_SAMPLES)

    @Slot()
    def reset_dark_offset(self) -> None:
        """Clear the dark-current offset."""
        self._data.reset_dark_offset()

    @Slot(int, int)
    def _on_dark_tare_progress(self, current: int, total: int) -> None:
        self._status.info(self._m("dark_tare_progress", current=current, total=total))

    @Slot(float)
    def _on_dark_tare_done(self, offset_V: float) -> None:
        self.dark_tare_busy.emit(False)
        self.dark_offset_changed.emit(offset_V)
        if offset_V == 0.0:
            self._status.info(self._m("dark_offset_reset"))
        else:
            self._status.success(self._m("dark_offset_set", offset_mV=offset_V * 1000.0))
