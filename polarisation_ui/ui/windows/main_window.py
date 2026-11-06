"""Main window of the Goniometer Polarisation UI.

A thin shell around the Designer form ``main_window.ui``: toolbar, a left dock with the device
panels, a right dock with the readout / measurement / save panels, a bottom dock with the event
log and the experiment tabs in the central ``QTabWidget``. It builds the :class:`AppContext`
(controllers), maps controller signals to panel setters and panel signals to controller slots,
persists the window layout and opens the auxiliary windows. Device handling and business logic
live in ``polarisation_ui/ui/controllers/``, widget-specific mapping in
``polarisation_ui/ui/widgets/panels/``.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEvent, QSettings, Qt, QTimer, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QWidget

from polarisation_ui.core.detector import DETECTOR_PDTIA, DETECTOR_PM400
from polarisation_ui.core.models import AcquisitionSettings
from polarisation_ui.infrastructure.config import AppConfig, default_config
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.pyqt.ui_main_window import Ui_MainWindow
from polarisation_ui.ui.common.dialogs import show_error
from polarisation_ui.ui.common.session_prompts import SessionPrompts
from polarisation_ui.ui.common.statusbar import StatusBarManager
from polarisation_ui.ui.context import AppContext
from polarisation_ui.ui.controllers.detector_controller import DARK_TARE_SAMPLES
from polarisation_ui.ui.controllers.status import (
    ROW_ARDUINO,
    ROW_DETECTOR,
    ROW_DETECTOR_STAGE,
    ROW_SAMPLE,
)
from polarisation_ui.ui.i18n import apply_strings
from polarisation_ui.ui.widgets.tab_host import TabHost
from polarisation_ui.ui.widgets.vscroll import lock_vertical_scroll
from polarisation_ui.ui.windows.auxiliary_windows import AuxiliaryWindows

WINDOW_MODES = ("maximized", "fullscreen", "normal")
SETTINGS_ORGANISATION = "polarisation-ui"
SETTINGS_APPLICATION = "polarisation-ui"
DEFAULT_PROFILE = "expert"


def layout_settings() -> QSettings:
    """The user settings that hold the window layout (tests replace this function)."""
    return QSettings(SETTINGS_ORGANISATION, SETTINGS_APPLICATION)


class MainWindow(QMainWindow):
    """Main window: Designer form + controller wiring.

    ``simulate=True`` runs the whole bench on the mocks of ``SimulatedBench`` (no hardware).
    ``persist=False`` reads and writes no user files (session state, orphan journals, window
    layout) — for tests.
    """

    def __init__(
        self,
        config: AppConfig | None = None,
        simulate: bool = False,
        persist: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        """Build the form, the controllers and the tabs, then wire everything."""
        super().__init__(parent)
        self.config: AppConfig = config if config is not None else default_config()
        self._persist = persist
        self._was_maximized = False  # state to return to when leaving full screen
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        apply_strings(self, self.config.section("ui").get("main_window", {}))
        ui = self.ui
        for panel in (
            ui.arduinoPanel,
            ui.kdcPanel,
            ui.detectorPanel,
            ui.readoutPanel,
            ui.measurementPanel,
            ui.savePanel,
        ):
            panel.apply_config(self.config)
        ui.sampleStagePanel.apply_config(self.config, "sample")
        ui.detectorStagePanel.apply_config(self.config, "detector")

        self.ctx = AppContext.create(self.config, simulate=simulate, persist=persist, parent=self)
        self.prompts = SessionPrompts(self, self.ctx.session, self.config)
        self.aux = AuxiliaryWindows(self, self.ctx, self.config, self._reload_profiles)
        self.statusbar_manager = StatusBarManager(ui.statusBar)
        self.statusbar_manager.set_mirror(ui.eventLogPanel)  # status messages also go to the log
        self.tabs = TabHost(ui.tabWidget, self.config, self.ctx.data, self)
        self._status_rows = {
            ROW_ARDUINO: ui.arduinoPanel,
            ROW_SAMPLE: ui.sampleStagePanel,
            ROW_DETECTOR_STAGE: ui.detectorStagePanel,
            ROW_DETECTOR: ui.detectorPanel,
        }

        self._setup_docks()
        self._connect_status()
        self._connect_connection()
        self._connect_kdc()
        self._connect_pm400()
        self._connect_detector()
        self._connect_measurement()
        self._connect_session()
        self._connect_actions()
        self._setup_initial_widget_state()
        self.tabs.build()
        self._connect_tabs()
        self._publish_initial_state()
        if persist:
            self._restore_layout()
            # Defer until the event loop runs so the window is shown before any modal dialog
            # appears — otherwise the port combo ends up in a broken state on macOS.
            QTimer.singleShot(0, self.prompts.run_startup_checks)
        Debug.info("MainWindow initialized with Qt Designer UI")

    def _m(self, key: str, **fmt: object) -> str:
        return self.config.message(key, **fmt)

    # ==================== Docks, layout persistence, full screen ====================

    def _setup_docks(self) -> None:
        """Side docks never scroll horizontally; each has a toggle action wired both ways."""
        ui = self.ui
        for dock, scroll, action in (
            (ui.dockControls, ui.scrollControls, ui.actionToggleControls),
            (ui.dockMeasurement, ui.scrollMeasurement, ui.actionToggleMeasurement),
            (ui.dockEventLog, None, ui.actionToggleEventLog),
        ):
            if scroll is not None:
                dock.setMinimumWidth(lock_vertical_scroll(scroll) + 2)
            action.toggled.connect(dock.setVisible)
            dock.visibilityChanged.connect(action.setChecked)
        self.resizeDocks(
            [ui.dockControls, ui.dockMeasurement],
            [max(370, ui.dockControls.minimumWidth()), max(300, ui.dockMeasurement.minimumWidth())],
            Qt.Orientation.Horizontal,
        )
        self.resizeDocks([ui.dockEventLog], [120], Qt.Orientation.Vertical)

    def _layout_key(self, name: str) -> str:
        """Each profile keeps its own layout; the default profile uses the plain keys."""
        profile = self.config.profile
        return f"window/{name}" if profile == DEFAULT_PROFILE else f"window/{profile}/{name}"

    def _restore_layout(self) -> None:
        settings = layout_settings()
        geometry = settings.value(self._layout_key("geometry"))
        state = settings.value(self._layout_key("state"))
        if geometry is not None:
            self.restoreGeometry(geometry)
        if state is not None:
            self.restoreState(state)
        ui = self.ui  # a dock hidden by the restored state may not have announced it
        for dock, action in (
            (ui.dockControls, ui.actionToggleControls),
            (ui.dockMeasurement, ui.actionToggleMeasurement),
            (ui.dockEventLog, ui.actionToggleEventLog),
        ):
            action.setChecked(not dock.isHidden())

    def _save_layout(self) -> None:
        settings = layout_settings()
        settings.setValue(self._layout_key("geometry"), self.saveGeometry())
        settings.setValue(self._layout_key("state"), self.saveState())

    def show_initial(self, mode: str) -> None:
        """Show the window in ``mode`` (``maximized``, ``fullscreen`` or ``normal``).

        The saved layout may remember another window state, so the mode always wins; ``normal``
        keeps the saved geometry.
        """
        if mode not in WINDOW_MODES:
            Debug.warning(f"unknown window mode {mode!r}, using {WINDOW_MODES[0]!r}")
            mode = WINDOW_MODES[0]
        if mode == "fullscreen":
            self.showFullScreen()
        elif mode == "maximized":
            self.showMaximized()
        else:
            self.show()
        self.ui.actionFullScreen.setChecked(self.isFullScreen())

    @Slot(bool)
    def set_fullscreen(self, on: bool) -> None:
        """Enter or leave full screen (leaving returns to maximised or normal as before)."""
        if on == self.isFullScreen():
            return
        if on:
            self._was_maximized = self.isMaximized()
            self.showFullScreen()
        elif self._was_maximized:
            self.showMaximized()
        else:
            self.showNormal()
        self.ui.actionFullScreen.setChecked(self.isFullScreen())

    def changeEvent(self, event: QEvent) -> None:  # noqa: N802
        """Keep the full-screen action in sync when the OS changes the window state."""
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self.ui.actionFullScreen.setChecked(self.isFullScreen())

    # ==================== Wiring ====================

    def _connect_status(self) -> None:
        self.ctx.status.message.connect(self._show_status)
        self.ctx.connection.row_state_changed.connect(self._show_row)
        self.ctx.detector.row_state_changed.connect(self._show_row)

    def _connect_connection(self) -> None:
        conn, ui = self.ctx.connection, self.ui
        arduino = ui.arduinoPanel
        conn.ports_changed.connect(lambda ports: arduino.set_ports(ports, conn.ports_missing_text))
        conn.connected_changed.connect(self._on_arduino_connected_changed)
        conn.connecting_changed.connect(arduino.set_connecting)
        conn.ready.connect(self._apply_required_stream_sources)
        conn.zero_failed.connect(lambda title, text: show_error(self, title, text))
        conn.lost.connect(self.prompts.offer_partial_export)
        arduino.refresh_requested.connect(conn.refresh_ports)
        arduino.connect_requested.connect(conn.connect_port)
        arduino.disconnect_requested.connect(conn.disconnect_port)
        ui.sampleStagePanel.zero_requested.connect(conn.zero_sample)
        ui.detectorStagePanel.zero_requested.connect(conn.zero_detector)
        ui.detectorStagePanel.zero_180_requested.connect(conn.zero_detector_at_180)

        data = self.ctx.data
        data.angles_updated.connect(ui.readoutPanel.show_angles)
        data.intensity_updated.connect(ui.readoutPanel.show_voltage)
        data.power_updated.connect(ui.readoutPanel.show_power)

    def _connect_kdc(self) -> None:
        kdc, panel = self.ctx.kdc, self.ui.kdcPanel
        kdc.devices_changed.connect(panel.set_devices)
        kdc.state_changed.connect(panel.set_state)
        kdc.connected_changed.connect(panel.set_connected)
        kdc.controls_changed.connect(panel.set_controls)
        kdc.position_changed.connect(panel.set_position)
        kdc.offset_changed.connect(panel.set_offset)
        kdc.notice.connect(lambda title, text: QMessageBox.warning(self, title, text))
        panel.refresh_requested.connect(kdc.refresh_devices)
        panel.connect_requested.connect(kdc.connect_device)
        panel.disconnect_requested.connect(kdc.disconnect_device)
        panel.home_requested.connect(kdc.home)
        panel.zero_requested.connect(kdc.start_zero_find)
        panel.offset_reset_requested.connect(kdc.reset_offset)

    def _connect_pm400(self) -> None:
        pm, panel = self.ctx.pm400, self.ui.detectorPanel
        pm.resources_changed.connect(
            lambda resources: panel.set_pm400_resources(resources, pm.preferred_resource)
        )
        pm.resource_selected.connect(panel.select_pm400_resource)
        pm.wavelength_changed.connect(panel.set_pm400_wavelength)
        pm.state_changed.connect(panel.set_pm400_state)
        pm.connected_changed.connect(panel.set_pm400_connected)
        pm.notice.connect(lambda title, text: QMessageBox.warning(self, title, text))
        panel.pm400_refresh_requested.connect(pm.refresh_resources)
        panel.pm400_resource_changed.connect(pm.set_resource)
        panel.pm400_connect_requested.connect(pm.connect_resource)
        panel.pm400_disconnect_requested.connect(pm.disconnect_device)
        panel.pm400_zero_requested.connect(pm.zero)
        panel.pm400_wavelength_changed.connect(pm.set_wavelength)

    def _connect_detector(self) -> None:
        det, panel, readout = self.ctx.detector, self.ui.detectorPanel, self.ui.readoutPanel
        det.gain_changed.connect(readout.set_gain)
        det.gain_cleared.connect(readout.clear_gain)
        det.gain_auto_changed.connect(readout.set_gain_auto)
        det.active_detector_changed.connect(self._set_active_detector)
        det.profile_changed.connect(self._on_profile_changed)
        det.pdtia_id_changed.connect(panel.select_pdtia_id)
        det.dark_tare_busy.connect(panel.set_dark_busy)
        det.dark_offset_changed.connect(panel.set_dark_offset)
        readout.gain_selected.connect(det.select_gain)
        readout.gain_auto_toggled.connect(det.set_gain_auto)
        if not det.gain_auto_available:
            readout.set_gain_auto_unavailable()
        panel.pdtia_id_selected.connect(det.set_pdtia_id)
        panel.profile_selected.connect(det.select_profile)
        panel.profile_reload_requested.connect(self._reload_profiles)
        panel.calibration_requested.connect(self.aux.open_power_calibration)
        panel.dark_tare_requested.connect(self._on_dark_tare_clicked)
        panel.dark_reset_requested.connect(det.reset_dark_offset)

    def _connect_measurement(self) -> None:
        meas, ui = self.ctx.measurement, self.ui
        meas.started.connect(self._on_measurement_started)
        meas.stopped.connect(self._on_measurement_stopped)
        meas.reset_performed.connect(lambda: ui.measurementPanel.set_reset_enabled(False))
        meas.group_changed.connect(self._on_group_changed)
        meas.team_changed.connect(ui.savePanel.set_team)
        meas.suffix_changed.connect(ui.savePanel.set_suffix)
        meas.team_changed.connect(self._update_filename_display)
        meas.suffix_changed.connect(self._update_filename_display)
        meas.prefix_locked_changed.connect(ui.savePanel.set_prefix_locked)
        meas.acq_settings_replaced.connect(self._sync_averaging_controls)
        ui.measurementPanel.start_requested.connect(meas.start)
        ui.measurementPanel.stop_requested.connect(meas.stop)
        ui.measurementPanel.reset_requested.connect(meas.reset)
        ui.savePanel.group_changed.connect(meas.set_group)
        ui.savePanel.team_changed.connect(meas.set_team)
        ui.savePanel.suffix_changed.connect(meas.set_suffix)
        ui.savePanel.save_requested.connect(self._save_data)
        for panel in (ui.sampleStagePanel, ui.detectorStagePanel, ui.detectorPanel):
            panel.averaging_changed.connect(self._on_averaging_changed)

    def _connect_session(self) -> None:
        session = self.ctx.session
        session.set_tab_points_provider(self.tabs.saved_points)
        session.tab_points_restored.connect(self.tabs.restore_points)

    def _connect_tabs(self) -> None:
        tabs, ctx = self.tabs, self.ctx
        tabs.status_message.connect(self._show_status)
        tabs.filename_hint_changed.connect(self._update_filename_display)
        tabs.points_changed.connect(self._on_tab_points_changed)
        tabs.points_changed.connect(lambda _count: ctx.session.schedule_save())
        tabs.active_tab_changed.connect(self._on_active_tab_changed)
        tabs.sources_changed.connect(self._apply_required_stream_sources)
        ctx.kdc.modules_changed.connect(tabs.refresh_visibility)
        ctx.pm400.modules_changed.connect(tabs.refresh_visibility)
        ctx.connection.link_state_changed.connect(tabs.notify_link_state)
        ctx.measurement.started.connect(tabs.on_measurement_started)
        ctx.measurement.stopped.connect(tabs.on_measurement_stopped)
        ctx.measurement.reset_performed.connect(tabs.reset_all)

    def _connect_actions(self) -> None:
        ui = self.ui
        ui.actionAcquisitionSettings.triggered.connect(self.aux.open_acq_settings)
        ui.actionEncoderDebug.triggered.connect(self.aux.open_encoder_debug)
        ui.actionLogWindow.triggered.connect(self.aux.open_log_window)
        ui.actionPowerCalibration.triggered.connect(self.aux.open_power_calibration)
        ui.actionAutoPowerCalibration.triggered.connect(self.aux.open_auto_power_calibration)
        ui.actionFullScreen.triggered.connect(self.set_fullscreen)
        ui.actionAutoSaveEnabled.toggled.connect(ui.savePanel.set_suffix_visible)

    # ==================== Initial state ====================

    def _setup_initial_widget_state(self) -> None:
        """Widgets start disconnected; the controllers then publish their own initial state."""
        ui, det = self.ui, self.ctx.detector
        for panel in (ui.sampleStagePanel, ui.detectorStagePanel, ui.detectorPanel):
            panel.setEnabled(False)
        ui.detectorPanel.set_pdtia_ids(det.pdtia_ids)
        det.init_pdtia_id(ui.detectorPanel.current_pdtia_id())
        self._set_active_detector(DETECTOR_PDTIA)
        self._sync_averaging_controls(self.ctx.measurement.acq_settings)

    def _publish_initial_state(self) -> None:
        ctx = self.ctx
        ctx.connection.publish_state()
        ctx.kdc.publish_state()
        ctx.pm400.publish_state()
        self._reload_profiles()
        # Apply the initial group state (the selector starts empty: experiment tabs locked)
        self._on_group_changed(ctx.measurement.group_letter)

    # ==================== Status ====================

    @Slot(str, str)
    def _show_status(self, level: str, text: str) -> None:
        bar = self.statusbar_manager
        show = {
            "success": bar.show_success,
            "warning": bar.show_warning,
            "error": bar.show_error,
        }.get(level, bar.show_info)
        show(text)

    @Slot(str, str, str)
    def _show_row(self, row: str, led: str, text: str) -> None:
        self._status_rows[row].set_state(led, text)

    # ==================== Arduino connection and streaming ====================

    @Slot(bool)
    def _on_arduino_connected_changed(self, connected: bool) -> None:
        ui = self.ui
        ui.arduinoPanel.set_connected(connected)
        for panel in (ui.sampleStagePanel, ui.detectorStagePanel, ui.detectorPanel):
            panel.setEnabled(connected)
        ui.measurementPanel.set_start_enabled(connected)
        if connected:
            ui.readoutPanel.reset_displays()

    @Slot()
    def _apply_required_stream_sources(self) -> None:
        """Keep ``CONF:SRC`` at the union of the visible tabs' required sources."""
        self.ctx.connection.set_stream_sources(self.tabs.required_sources())

    # ==================== Detector: gain, profile, dark tare ====================

    @Slot(str)
    def _set_active_detector(self, source: str) -> None:
        """Apply every UI consequence of ``source`` becoming the active detector.

        The PD-TIA configuration (device ID, calibration profile, averaging, dark tare) stays
        interactive either way — only the gain buttons, which are meaningless once the PM400 has
        replaced the photodiode, go inert. AUTO also stays off when the config defines no power
        windows.
        """
        pm400_active = source == DETECTOR_PM400
        auto_ok = self.ctx.detector.gain_auto_available and not pm400_active
        self.ui.readoutPanel.set_gain_enabled(manual=not pm400_active, auto=auto_ok)

    @Slot()
    def _reload_profiles(self) -> None:
        """Refill the profile selector from the profiles directory and re-select the profile."""
        panel, det = self.ui.detectorPanel, self.ctx.detector
        current = panel.ui.comboProfile.currentText() or det.profile_name
        panel.set_profiles(det.list_profiles(), current)
        det.select_profile(panel.current_profile())

    @Slot(str)
    def _on_profile_changed(self, name: str) -> None:
        self.ui.detectorPanel.select_profile_name(name)
        self._update_filename_display()

    @Slot()
    def _on_dark_tare_clicked(self) -> None:
        reply = QMessageBox.question(
            self,
            self._m("detector.dark_tare_title"),
            self._m("detector.dark_tare_text", count=DARK_TARE_SAMPLES),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.ctx.detector.start_dark_tare()

    # ==================== Acquisition settings ====================

    @Slot()
    def _on_averaging_changed(self) -> None:
        """Build the settings from the per-device controls (spike filter etc. stay unchanged)."""
        ui, current = self.ui, self.ctx.measurement.acq_settings
        samp_on, samp_count = ui.sampleStagePanel.averaging()
        det_on, det_count = ui.detectorStagePanel.averaging()
        pdtia_on, pdtia_count = ui.detectorPanel.averaging()
        self.ctx.measurement.set_acq_settings_inline(
            AcquisitionSettings(
                samp_average_on=samp_on,
                samp_averages=samp_count,
                det_average_on=det_on,
                det_averages=det_count,
                pdtia_average_on=pdtia_on,
                pdtia_averages=pdtia_count,
                sample_stage_inverted=current.sample_stage_inverted,
                spike_filter_enabled=current.spike_filter_enabled,
                spike_max_delta_deg=current.spike_max_delta_deg,
            )
        )

    @Slot(object)
    def _sync_averaging_controls(self, settings: AcquisitionSettings) -> None:
        """Push ``settings`` to the averaging controls without re-emitting their signals."""
        ui = self.ui
        ui.sampleStagePanel.set_averaging(settings.samp_average_on, settings.samp_averages)
        ui.detectorStagePanel.set_averaging(settings.det_average_on, settings.det_averages)
        ui.detectorPanel.set_averaging(settings.pdtia_average_on, settings.pdtia_averages)

    # ==================== Group / filename / save ====================

    @Slot(str)
    def _on_group_changed(self, letter: str) -> None:
        self.ui.savePanel.set_group(letter)
        self.tabs.set_group_selected(bool(letter))
        self._update_filename_display()

    @Slot()
    def _update_filename_display(self) -> None:
        """Refresh the expected save path shown for the active tab."""
        meas = self.ctx.measurement
        text = meas.filename_display(self.tabs.active_export()) if meas.group_selected else ""
        self.ui.savePanel.set_filename(text)

    @Slot()
    def _save_data(self) -> None:
        """Export the active tab's saved points to a user-chosen CSV file."""
        tab = self.tabs.active_export_tab()
        title = self._m("save.no_points_title")
        if tab is None or not tab.get_saved_points():
            show_error(self, title, self._m("save.no_points"))
            return
        export = tab.build_export()
        if not export.rows:
            show_error(self, title, self._m("save.no_points"))
            return
        default = self.ctx.measurement.default_save_path(export)
        path, _ = QFileDialog.getSaveFileName(
            self, self._m("save.dialog_title"), str(default), self._m("save.csv_filter")
        )
        if path:
            self.ctx.measurement.save_export(Path(path), export)

    # ==================== Measurement / tabs ====================

    @Slot()
    def _on_measurement_started(self) -> None:
        ui = self.ui
        ui.measurementPanel.set_running(True)
        ui.savePanel.set_save_enabled(False)
        # No zeroing and no tab switching during a run
        ui.sampleStagePanel.set_zeroing_enabled(False)
        ui.detectorStagePanel.set_zeroing_enabled(False)
        ui.tabWidget.tabBar().setEnabled(False)

    @Slot()
    def _on_measurement_stopped(self) -> None:
        ui = self.ui
        ui.measurementPanel.set_running(False)
        ui.sampleStagePanel.set_zeroing_enabled(True)
        ui.detectorStagePanel.set_zeroing_enabled(True)
        ui.tabWidget.tabBar().setEnabled(True)
        self._sync_save_button()

    @Slot(int)
    def _on_tab_points_changed(self, _count: int) -> None:
        if not self.ctx.measurement.is_measuring:
            self._sync_save_button()

    @Slot()
    def _on_active_tab_changed(self) -> None:
        if not self.ctx.measurement.is_measuring:
            self._sync_save_button()
        self._update_filename_display()

    def _sync_save_button(self) -> None:
        """Enable Save iff the active tab has saved points."""
        self.ui.savePanel.set_save_enabled(self.tabs.active_tab_has_points())

    # ==================== Window lifecycle ====================

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Save the layout, stop measurement and polling, close all devices."""
        Debug.info("Closing application...")
        if self._persist:
            self._save_layout()
        self.ctx.shutdown()
        event.accept()
