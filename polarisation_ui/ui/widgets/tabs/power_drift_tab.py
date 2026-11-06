"""Laser-Drift (power stability) experiment tab.

Tracks laser intensity and both encoder angles over time so students can
observe the thermal warm-up behaviour and confirm the setup is stable before
taking Malus-law data.  Intended for runs of up to 1 hour after switching on
the laser.
"""

from __future__ import annotations

from collections import deque

import numpy as np
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget

from polarisation_ui.core.models import Frame
from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.pyqt.ui_power_drift_tab import Ui_PowerDriftTab
from polarisation_ui.ui.i18n import apply_strings
from polarisation_ui.ui.widgets.plot_tab_base import ConnState, PlotTabBase
from polarisation_ui.ui.widgets.tab_title import TabTitle
from polarisation_ui.ui.widgets.vscroll import lock_vertical_scroll

_MAX_DURATION_S: int = 3600  # 1 hour cap
_MAX_POINTS: int = _MAX_DURATION_S * 10  # 36 000 samples at 10 Hz
_DASH = "—"  # placeholder for an unavailable value


class PowerDriftTab(PlotTabBase):
    """Laser-Drift experiment tab: intensity + angle stability over up to 1 hour."""

    tab_id = "power_drift"
    tab_title = TabTitle()  # type: ignore[assignment]  # config: ui.tabs.power_drift
    required_sources: set[str] = {"ENC:BOTH", "ADC"}
    required_modules: set[str] = set()

    def __init__(self, parent: QWidget | None = None, config: AppConfig | None = None) -> None:
        """Initialise empty ring buffers; build() constructs the widgets."""
        super().__init__(parent, config)
        # -1 = measurement active but first frame not yet seen (sentinel)
        # None = measurement not running
        # >=0 = reference timestamp in ms from first recorded frame
        self._t0_ms: int | None = None
        self._times_s: deque[float] = deque(maxlen=_MAX_POINTS)
        self._intensity: deque[float] = deque(maxlen=_MAX_POINTS)
        self._sample_angle: deque[float] = deque(maxlen=_MAX_POINTS)
        self._detector_angle: deque[float] = deque(maxlen=_MAX_POINTS)
        self._first_sample_angle: float | None = None
        self._first_detector_angle: float | None = None

    def build(self) -> None:
        """Construct the tab's widgets and wire up signal connections."""
        self._ui = Ui_PowerDriftTab()
        self._ui.setupUi(self)
        apply_strings(self, self.config.section("ui").get("power_drift_tab", {}))
        self._ui.intensityPlot.apply_config(self.config)
        self._ui.anglesPlot.apply_config(self.config)
        lock_vertical_scroll(self._ui.scrollSide)
        self._ui.buttonClear.clicked.connect(self._clear_data)

    # ── PlotTabBase lifecycle ─────────────────────────────────────────────────

    def on_frame(self, frame: Frame) -> None:
        """Append a new sample to the ring buffers and refresh the plots/labels."""
        if self._t0_ms is None:
            return  # not measuring

        if self._t0_ms == -1:
            # First frame: latch the reference timestamp
            self._t0_ms = frame.ts_ms

        elapsed_s = (frame.ts_ms - self._t0_ms) / 1000.0
        if elapsed_s > _MAX_DURATION_S:
            return  # past the 1-hour cap; stop recording

        self._times_s.append(elapsed_s)
        self._intensity.append(frame.intensity)
        self._sample_angle.append(frame.sample_angle)
        self._detector_angle.append(frame.detector_angle)

        if self._first_sample_angle is None:
            self._first_sample_angle = frame.sample_angle
            self._first_detector_angle = frame.detector_angle

        self._refresh()

    def on_reset(self) -> None:
        """Clear all buffered drift data."""
        self._clear_data()

    def on_connection_state(self, state: ConnState) -> None:
        """No-op — this tab has no connection-state-dependent UI."""

    def on_activated(self) -> None:
        """No-op — this tab has no activation-dependent UI."""

    def on_deactivated(self) -> None:
        """No-op — this tab has no deactivation-dependent UI."""

    def on_measurement_started(self) -> None:
        """Latch a fresh time reference (if none is running yet) and enable Clear."""
        if self._t0_ms is None:
            self._t0_ms = -1  # sentinel: first frame will latch t0
        self._ui.buttonClear.setEnabled(True)

    def on_measurement_stopped(self) -> None:
        """Keep the data visible after stopping so students can examine the curve."""
        self._ui.buttonClear.setEnabled(False)

    def inject_modules(self, modules: dict[str, object]) -> None:
        """No-op — this tab does not require any host modules."""

    # ── private helpers ──────────────────────────────────────────────────────

    @Slot()
    def _clear_data(self) -> None:
        # If a measurement is active (t0 already latched or sentinel), reset to
        # sentinel so recording resumes from the next frame with a fresh clock.
        # If no measurement is running, leave t0 as None.
        if self._t0_ms is not None:
            self._t0_ms = -1
        self._times_s.clear()
        self._intensity.clear()
        self._sample_angle.clear()
        self._detector_angle.clear()
        self._first_sample_angle = None
        self._first_detector_angle = None
        self._refresh()

    def _refresh(self) -> None:
        if not self._times_s:
            self._ui.intensityPlot.clear()
            self._ui.anglesPlot.clear()
            self._set_elapsed(0.0)
            self._update_intensity_stats([])
            self._update_angle_deltas(None, None)
            return

        t_min = [t / 60.0 for t in self._times_s]
        intensity = list(self._intensity)
        sample_a = list(self._sample_angle)
        detector_a = list(self._detector_angle)

        self._ui.intensityPlot.set_data(t_min, intensity)
        self._ui.anglesPlot.set_data(t_min, sample_a, detector_a)

        self._set_elapsed(self._times_s[-1])
        self._update_intensity_stats(intensity)
        self._update_angle_deltas(sample_a[-1], detector_a[-1])

    def _set_elapsed(self, elapsed_s: float) -> None:
        total = int(elapsed_s)
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        self._ui.valueElapsed.setText(f"{h:02d}:{m:02d}:{s:02d}")
        self._ui.progressBar.setValue(total)

    def _update_intensity_stats(self, intensity: list[float]) -> None:
        labels = (
            self._ui.valueIntensityCurrent,
            self._ui.valueIntensityMean,
            self._ui.valueIntensityMin,
            self._ui.valueIntensityMax,
        )
        if not intensity:
            for label in labels:
                label.setText(_DASH)
            return
        arr = np.array(intensity, dtype=float)
        values = (intensity[-1], float(arr.mean()), float(arr.min()), float(arr.max()))
        for label, val in zip(labels, values, strict=True):
            label.setText(self.config.text("power_drift_tab.stat_voltage", value=f"{val:.5f}"))

    def _update_angle_deltas(self, sample: float | None, detector: float | None) -> None:
        if sample is None or detector is None or self._first_sample_angle is None:
            self._ui.valueDeltaSample.setText(_DASH)
            self._ui.valueDeltaDetector.setText(_DASH)
            return
        ds = sample - self._first_sample_angle
        dd = detector - (self._first_detector_angle or 0.0)
        self._ui.valueDeltaSample.setText(
            self.config.text("power_drift_tab.delta_angle", value=f"{ds:+.3f}")
        )
        self._ui.valueDeltaDetector.setText(
            self.config.text("power_drift_tab.delta_angle", value=f"{dd:+.3f}")
        )
