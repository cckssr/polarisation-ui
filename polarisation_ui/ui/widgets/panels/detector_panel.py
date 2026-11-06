"""Detector panel: PD-TIA photodiode (calibration, dark current) and PM400 power meter."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QGroupBox, QWidget

from polarisation_ui.infrastructure.config import AppConfig, default_config
from polarisation_ui.pyqt.ui_detector_panel import Ui_DetectorPanel
from polarisation_ui.ui.common.pm400_combo import populate_pm400_combo
from polarisation_ui.ui.common.status_led import set_led_state
from polarisation_ui.ui.i18n import apply_strings


class DetectorPanel(QGroupBox):
    """Two pages: the PD-TIA photodiode and the Thorlabs PM400 power meter."""

    pdtia_id_selected = Signal(str)
    profile_selected = Signal(object)  # Path of the chosen calibration profile, None for none
    profile_reload_requested = Signal()
    calibration_requested = Signal()
    dark_tare_requested = Signal()
    dark_reset_requested = Signal()
    averaging_changed = Signal(bool, int)  # PD-TIA moving average on, number of values
    pm400_refresh_requested = Signal()
    pm400_resource_changed = Signal(str)
    pm400_connect_requested = Signal(str)  # the selected VISA resource
    pm400_disconnect_requested = Signal()
    pm400_zero_requested = Signal()
    pm400_wavelength_changed = Signal(float)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the form; texts come from :meth:`apply_config`."""
        super().__init__(parent)
        self.ui = Ui_DetectorPanel()
        self.ui.setupUi(self)
        self._config: AppConfig = default_config()
        self._pm400_connected = False
        ui = self.ui
        ui.comboPdtiaId.currentIndexChanged.connect(
            lambda _index: self.pdtia_id_selected.emit(ui.comboPdtiaId.currentText())
        )
        ui.comboProfile.currentIndexChanged.connect(self._on_profile_index_changed)
        ui.buttonReloadProfiles.clicked.connect(self.profile_reload_requested)
        ui.buttonOpenCalibration.clicked.connect(self.calibration_requested)
        ui.buttonDarkTare.clicked.connect(self.dark_tare_requested)
        ui.buttonDarkReset.clicked.connect(self.dark_reset_requested)
        ui.checkPdtiaAverage.toggled.connect(ui.spinPdtiaAverages.setEnabled)
        ui.checkPdtiaAverage.toggled.connect(self._emit_averaging)
        ui.spinPdtiaAverages.valueChanged.connect(self._emit_averaging)
        ui.buttonPm400Refresh.clicked.connect(self.pm400_refresh_requested)
        ui.comboPm400Resource.currentTextChanged.connect(self.pm400_resource_changed)
        ui.buttonPm400Connect.clicked.connect(self._on_pm400_connect_clicked)
        ui.buttonPm400Zero.clicked.connect(self.pm400_zero_requested)
        ui.spinWavelength.valueChanged.connect(self.pm400_wavelength_changed)

    def apply_config(self, config: AppConfig) -> None:
        """Apply the ``ui.detector_panel`` strings."""
        self._config = config
        apply_strings(self, config.section("ui").get("detector_panel", {}))
        self.set_pm400_connected(self._pm400_connected)
        self.set_dark_offset(0.0)

    def _t(self, key: str, **fmt: object) -> str:
        return self._config.text(f"detector_panel.{key}", **fmt)

    # ---- PD-TIA: device id and calibration profile -----------------------------------------
    def set_pdtia_ids(self, ids: list[str]) -> None:
        """Fill the photodetector selector without emitting :attr:`pdtia_id_selected`."""
        combo = self.ui.comboPdtiaId
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(ids)
        combo.blockSignals(False)

    def current_pdtia_id(self) -> str:
        """The selected photodetector id ("" when none)."""
        return self.ui.comboPdtiaId.currentText()

    @Slot(str)
    def select_pdtia_id(self, device_id: str) -> None:
        """Select ``device_id`` (if listed) without emitting :attr:`pdtia_id_selected`."""
        combo = self.ui.comboPdtiaId
        index = combo.findText(device_id)
        if index >= 0 and index != combo.currentIndex():
            combo.blockSignals(True)
            combo.setCurrentIndex(index)
            combo.blockSignals(False)

    def set_profiles(self, profiles: list[Path], current: str = "") -> None:
        """Fill the profile selector (stem as text, path as data) and select ``current``.

        Emits nothing; call :meth:`current_profile` afterwards to load the selection.
        """
        combo = self.ui.comboProfile
        combo.blockSignals(True)
        combo.clear()
        for path in profiles:
            combo.addItem(path.stem, userData=path)
        combo.setCurrentIndex(combo.findText(current) if current else -1)
        combo.blockSignals(False)

    def current_profile(self) -> Path | None:
        """Path of the selected calibration profile, None when nothing is selected."""
        combo = self.ui.comboProfile
        index = combo.currentIndex()
        return combo.itemData(index) if index >= 0 else None

    @Slot(str)
    def select_profile_name(self, name: str) -> None:
        """Show the profile ``name`` ("" for none) as selected without emitting a signal."""
        combo = self.ui.comboProfile
        index = combo.findText(name) if name else -1
        if index != combo.currentIndex():
            combo.blockSignals(True)
            combo.setCurrentIndex(index)
            combo.blockSignals(False)

    @Slot(str, str)
    def set_state(self, led: str, text: str) -> None:
        """Show the detector status (``led`` is a controller LED state)."""
        set_led_state(self.ui.ledPdtiaStatus, self.ui.valuePdtiaStatus, text, led)

    @Slot(int)
    def _on_profile_index_changed(self, _index: int) -> None:
        self.profile_selected.emit(self.current_profile())

    # ---- PD-TIA: averaging and dark current ------------------------------------------------
    def set_averaging(self, on: bool, count: int) -> None:
        """Show the averaging settings without emitting :attr:`averaging_changed`."""
        for widget in (self.ui.checkPdtiaAverage, self.ui.spinPdtiaAverages):
            widget.blockSignals(True)
        self.ui.checkPdtiaAverage.setChecked(on)
        self.ui.spinPdtiaAverages.setValue(count)
        self.ui.spinPdtiaAverages.setEnabled(on)
        for widget in (self.ui.checkPdtiaAverage, self.ui.spinPdtiaAverages):
            widget.blockSignals(False)

    def averaging(self) -> tuple[bool, int]:
        """The PD-TIA averaging settings as shown: ``(on, count)``."""
        return self.ui.checkPdtiaAverage.isChecked(), self.ui.spinPdtiaAverages.value()

    @Slot()
    def _emit_averaging(self) -> None:
        self.averaging_changed.emit(*self.averaging())

    @Slot(bool)
    def set_dark_busy(self, busy: bool) -> None:
        """No second dark-current measurement or reset while one is running."""
        self.ui.buttonDarkTare.setEnabled(not busy)
        self.ui.buttonDarkReset.setEnabled(not busy)

    @Slot(float)
    def set_dark_offset(self, offset_V: float) -> None:
        """Show the subtracted dark-current offset (in volts), a dash when none."""
        if offset_V == 0.0:
            self.ui.valueDarkOffset.setText(self._t("dark_offset_none"))
        else:
            self.ui.valueDarkOffset.setText(
                self._t("dark_offset_value", offset_mV=offset_V * 1000.0)
            )

    # ---- PM400 ----------------------------------------------------------------------------
    @Slot(list)
    def set_pm400_resources(self, resources: list[str], preferred: str = "") -> None:
        """Fill the VISA resource list, preferring the current entry, then ``preferred``."""
        populate_pm400_combo(self.ui.comboPm400Resource, preferred, self._config, resources)

    @Slot(str)
    def select_pm400_resource(self, resource: str) -> None:
        """Select ``resource`` if it is listed."""
        index = self.ui.comboPm400Resource.findText(resource)
        if index >= 0:
            self.ui.comboPm400Resource.setCurrentIndex(index)

    def current_pm400_resource(self) -> str:
        """The selected VISA resource ("" when none is listed)."""
        return self.ui.comboPm400Resource.currentText()

    @Slot(float)
    def set_pm400_wavelength(self, nm: float) -> None:
        """Show the wavelength without emitting :attr:`pm400_wavelength_changed`."""
        spin = self.ui.spinWavelength
        if spin.value() != nm:
            spin.blockSignals(True)
            spin.setValue(nm)
            spin.blockSignals(False)

    @Slot(str, str)
    def set_pm400_state(self, led: str, text: str) -> None:
        """Show the PM400 status (``led`` is a controller LED state)."""
        set_led_state(self.ui.ledPm400Status, self.ui.valuePm400Status, text, led)

    @Slot(bool)
    def set_pm400_connected(self, connected: bool) -> None:
        """The connect button disconnects while connected; zeroing needs a connection."""
        self._pm400_connected = connected
        self.ui.buttonPm400Connect.setText(
            self._t("text_disconnect" if connected else "text_connect")
        )
        self.ui.buttonPm400Zero.setEnabled(connected)

    def _on_pm400_connect_clicked(self) -> None:
        if self._pm400_connected:
            self.pm400_disconnect_requested.emit()
        else:
            self.pm400_connect_requested.emit(self.current_pm400_resource())
