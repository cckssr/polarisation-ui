"""Profiles: the student profile leaves out the debug and calibration windows and renames the
title; the window can be rebuilt with the other profile while the devices stay connected."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtCore import QSettings, QThread
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget

from polarisation_ui.infrastructure.config import load_config
from polarisation_ui.infrastructure.modules import ModuleRegistry
from polarisation_ui.ui.launcher import Launcher
from polarisation_ui.ui.profile import (
    _keep_rows_left_aligned,
    apply_profile,
    next_profile,
    profile_roots,
)
from polarisation_ui.ui.windows import main_window as main_window_module
from polarisation_ui.ui.windows.main_window import MainWindow

FAST_SIM = {
    "timers": {"acquisition_timer_interval": 20},
    "connection": {"max_retry_attempts": 2, "backoff_delays_ms": [30, 30]},
}
HIDDEN_ACTIONS = ("actionEncoderDebug", "actionPowerCalibration", "actionAutoPowerCalibration")
WIDE = (1920, 1000)
NARROW = (1366, 700)


@pytest.fixture
def student(qtbot) -> Iterator[MainWindow]:
    ModuleRegistry.clear()
    win = MainWindow(
        load_config(profile="student", overrides=FAST_SIM), simulate=True, persist=False
    )
    qtbot.addWidget(win)
    win.show()
    yield win
    win.close()
    ModuleRegistry.clear()


@pytest.fixture
def launcher(qtbot) -> Iterator[Launcher]:
    ModuleRegistry.clear()
    created = Launcher(profile="expert", window_mode="normal", simulate=True, persist=False,
                       overrides=FAST_SIM)  # fmt: skip
    yield created
    if created.window is not None:
        created.window.close()
    ModuleRegistry.clear()


def _connect_arduino(qtbot, win: MainWindow) -> None:
    with qtbot.waitSignal(win.ctx.data.frame_ready, timeout=5000):
        win.ui.arduinoPanel.ui.buttonConnect.click()
    assert win.ctx.connection.is_connected


class _Sleeper(QThread):
    """A worker that runs until it is told to stop."""

    def run(self) -> None:
        while not self.isInterruptionRequested():
            self.msleep(5)


# ---- what the student profile hides --------------------------------------------------------
def test_the_student_window_lacks_the_debug_and_calibration_actions(student) -> None:
    for name in HIDDEN_ACTIONS:
        assert not getattr(student.ui, name).isVisible(), name
    toolbar_actions = student.ui.toolBar.actions()
    for name in HIDDEN_ACTIONS:
        assert getattr(student.ui, name) in toolbar_actions  # hidden, not removed


def test_the_student_window_lacks_the_button_that_opens_the_calibration(student) -> None:
    assert not student.ui.detectorPanel.ui.buttonOpenCalibration.isVisible()


def test_the_student_window_keeps_everything_else(student) -> None:
    ui = student.ui
    for name in ("actionAcquisitionSettings", "actionLogWindow", "actionAutoSaveEnabled",
                 "actionToggleControls", "actionToggleMeasurement", "actionToggleEventLog",
                 "actionFullScreen", "actionSwitchProfile"):  # fmt: skip
        assert getattr(ui, name).isVisible(), name
    assert not ui.detectorPanel.ui.buttonReloadProfiles.isHidden()
    assert not ui.kdcPanel.isHidden() and not ui.detectorPanel.isHidden()
    assert {t.tab_id for t in student.tabs.tabs} == {
        "brewster",
        "malus",
        "ellipsometry",
        "power_drift",
    }


def test_the_expert_window_keeps_everything(window) -> None:
    for name in HIDDEN_ACTIONS:
        assert getattr(window.ui, name).isVisible(), name
    assert window.ui.detectorPanel.ui.buttonOpenCalibration.isVisible()


def test_the_student_title_names_the_profile(student) -> None:
    assert "Praktikum" in student.config.text("main_window.self@title")
    assert student.windowTitle() == student.config.text("main_window.self@title")


# ---- config consistency ---------------------------------------------------------------------
@pytest.mark.parametrize("profile", ["expert", "student"])
def test_every_hidden_widget_of_every_profile_exists(qtbot, profile) -> None:
    ModuleRegistry.clear()
    win = MainWindow(load_config(profile=profile, overrides=FAST_SIM), simulate=True, persist=False)
    qtbot.addWidget(win)
    try:
        assert apply_profile(win) == [], profile
    finally:
        win.close()
        ModuleRegistry.clear()


def test_every_profile_of_the_configuration_has_a_name_and_known_hidden_lists() -> None:
    config = load_config()
    assert config.profile_names == ["expert", "student"]
    for profile in config.profile_names:
        assert config.get(f"profiles.{profile}.name")
    assert load_config(profile="student").profile_name == "Praktikum"


def test_the_profile_roots_name_every_panel_and_tab(student) -> None:
    roots = profile_roots(student)
    assert {"main_window", "arduino_panel", "sample_stage_panel", "detector_stage_panel",
            "kdc_panel", "detector_panel", "readout_panel", "measurement_panel",
            "save_panel"} <= set(roots)  # fmt: skip
    for tab in student.tabs.tabs:
        assert roots[tab.tab_id] is tab


def test_a_misspelled_widget_name_is_reported(student) -> None:
    hidden = student.config.data["profiles"]["student"]["hidden_widgets"]
    hidden["detector_panel"].append("noSuchButton")
    hidden["no_root"] = ["x"]
    assert apply_profile(student) == ["detector_panel.noSuchButton", "no_root"]


# ---- layout ----------------------------------------------------------------------------------
def test_hiding_the_only_stretching_widget_of_a_row_keeps_the_rest_left_aligned(qtbot) -> None:
    root = QWidget()
    qtbot.addWidget(root)
    row = QHBoxLayout(root)
    left, button = QLabel("left"), QPushButton("button")
    stretching = QLabel("stretching")
    stretching.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    row.addWidget(left)
    row.addWidget(stretching, 1)
    row.addWidget(button)
    root.show()
    stretching.setVisible(False)
    _keep_rows_left_aligned(root, stretching)
    last = row.itemAt(row.count() - 1)
    assert last.spacerItem() is not None  # the trailing stretch
    assert row.stretch(row.count() - 1) == 1
    root.resize(600, 40)
    qtbot.wait(20)
    assert left.x() < button.x() < 200  # packed to the left, not spread over the width


def test_a_row_that_still_has_a_visible_stretching_widget_gets_no_extra_stretch(qtbot) -> None:
    root = QWidget()
    qtbot.addWidget(root)
    row = QHBoxLayout(root)
    first, second, other = QLabel("a"), QLabel("b"), QLabel("c")
    for widget in (first, second, other):
        row.addWidget(widget, 1)
    count = row.count()
    first.setVisible(False)
    _keep_rows_left_aligned(root, first)
    assert row.count() == count


def test_the_profile_layout_keys_differ(window, student) -> None:
    assert window._layout_key("geometry") == "window/geometry"
    assert student._layout_key("geometry") == "window/student/geometry"
    assert window._layout_key("state") != student._layout_key("state")
    window._save_layout()
    student._save_layout()
    settings: QSettings = main_window_module.layout_settings()
    assert {
        "window/geometry",
        "window/state",
        "window/student/geometry",
        "window/student/state",
    } <= set(settings.allKeys())


# ---- small screens ---------------------------------------------------------------------------
def test_the_student_window_fits_the_wide_screen(qtbot, student) -> None:
    assert student.minimumSizeHint().width() <= WIDE[0]
    student.resize(*WIDE)
    qtbot.wait(50)
    assert student.width() == WIDE[0]


def test_the_student_window_fits_the_narrow_screen_with_the_right_dock_collapsed(
    qtbot, student
) -> None:
    student.ui.actionToggleMeasurement.setChecked(False)
    qtbot.wait(50)
    assert student.minimumSizeHint().width() <= NARROW[0]
    student.resize(*NARROW)
    qtbot.wait(50)
    assert student.width() == NARROW[0]
    assert not student.ui.scrollControls.horizontalScrollBar().isVisible()


# ---- hidden tabs -----------------------------------------------------------------------------
def _window_with_hidden_tabs(qtbot, tab_ids: list[str]) -> MainWindow:
    config = load_config(profile="student", overrides=FAST_SIM)
    config.data["profiles"]["student"]["hidden_tabs"] = tab_ids
    ModuleRegistry.clear()
    win = MainWindow(config, simulate=True, persist=False)
    qtbot.addWidget(win)
    win.show()
    return win


def test_widgets_of_a_hidden_tab_are_not_reported_as_an_unknown_root(qtbot) -> None:
    config = load_config(profile="student", overrides=FAST_SIM)
    config.data["profiles"]["student"]["hidden_tabs"] = ["malus"]
    config.data["profiles"]["student"]["hidden_widgets"]["malus"] = ["buttonAddPoint"]
    ModuleRegistry.clear()
    win = MainWindow(config, simulate=True, persist=False)
    qtbot.addWidget(win)
    try:
        assert apply_profile(win) == []
    finally:
        win.close()
        ModuleRegistry.clear()


def test_a_hidden_tab_is_never_instantiated(qtbot) -> None:
    win = _window_with_hidden_tabs(qtbot, ["malus"])
    try:
        assert "malus" not in {t.tab_id for t in win.tabs.tabs}
        assert win.ui.tabWidget.count() == len(win.tabs.tabs)
        assert "brewster" in {t.tab_id for t in win.tabs.tabs}
    finally:
        win.close()
        ModuleRegistry.clear()


def test_a_hidden_module_tab_stays_absent_when_its_module_appears(qtbot) -> None:
    win = _window_with_hidden_tabs(qtbot, ["waveplate"])
    try:
        win.ui.kdcPanel.ui.buttonConnect.click()
        assert win.ctx.kdc.is_connected
        assert "waveplate" not in {t.tab_id for t in win.tabs.tabs}
    finally:
        win.close()
        ModuleRegistry.clear()


def test_a_visible_module_tab_appears_when_its_module_does(student, qtbot) -> None:
    student.ui.kdcPanel.ui.buttonConnect.click()
    assert "waveplate" in {t.tab_id for t in student.tabs.tabs}


# ---- the switch action -----------------------------------------------------------------------
def test_next_profile_cycles_through_the_profiles() -> None:
    names = ["expert", "student"]
    assert next_profile("expert", names) == "student"
    assert next_profile("student", names) == "expert"
    assert next_profile("a", ["a", "b", "c"]) == "b"
    assert next_profile("c", ["a", "b", "c"]) == "a"


def test_next_profile_keeps_an_unknown_or_the_only_profile() -> None:
    assert next_profile("other", ["expert", "student"]) == "other"
    assert next_profile("expert", ["expert"]) == "expert"


def test_the_switch_action_names_the_other_profile(window, student) -> None:
    assert window.ui.actionSwitchProfile.text() == "Zu Praktikum wechseln"
    assert student.ui.actionSwitchProfile.text() == "Zu Experte wechseln"
    assert "Praktikum" in window.ui.actionSwitchProfile.toolTip()
    assert "Experte" in student.ui.actionSwitchProfile.toolTip()
    assert window.ui.actionSwitchProfile.isVisible()


def test_the_switch_action_is_hidden_when_there_is_only_one_profile(qtbot) -> None:
    config = load_config(overrides=FAST_SIM)
    del config.data["profiles"]["student"]
    win = MainWindow(config, simulate=True, persist=False)
    qtbot.addWidget(win)
    win.show()
    assert not win.ui.actionSwitchProfile.isVisible()
    win.close()


def test_triggering_the_switch_action_requests_the_other_profile(qtbot, window) -> None:
    with qtbot.waitSignal(window.profile_switch_requested) as blocker:
        window.ui.actionSwitchProfile.trigger()
    assert blocker.args == ["student"]


def test_the_switch_action_waits_while_a_measurement_runs(qtbot, connected) -> None:
    action = connected.ui.actionSwitchProfile
    connected.ui.measurementPanel.ui.buttonStart.click()
    assert connected.ctx.measurement.is_measuring
    assert not action.isEnabled()
    with qtbot.assertNotEmitted(connected.profile_switch_requested):
        connected.request_profile_switch()
    connected.ui.measurementPanel.ui.buttonStop.click()
    assert action.isEnabled()


def test_a_running_worker_blocks_the_switch_request(qtbot, window) -> None:
    worker = _Sleeper()
    window.tabs.tabs[0]._sweep_worker = worker  # what a running sweep looks like
    worker.start()
    try:
        assert window.is_busy()
        with qtbot.assertNotEmitted(window.profile_switch_requested):
            window.request_profile_switch()
        assert window.config.message("profile.switch_busy") in window.statusBar().currentMessage()
    finally:
        worker.requestInterruption()
        worker.wait(2000)
    assert not window.is_busy()


def test_the_window_is_idle_without_workers(window) -> None:
    assert not window.is_busy()


# ---- the launcher ----------------------------------------------------------------------------
def test_the_launcher_starts_with_the_profile_and_its_title(qtbot) -> None:
    ModuleRegistry.clear()
    created = Launcher(profile="student", window_mode="normal", simulate=True, persist=False,
                       overrides=FAST_SIM)  # fmt: skip
    win = created.start()
    qtbot.addWidget(win)
    try:
        assert created.window is win
        assert win.config.profile == "student"
        assert win.windowTitle().startswith(win.config.text("main_window.self@title"))
        assert "Praktikum" in win.windowTitle()
        assert win.windowTitle().endswith(str(win.config.get("version")))
        assert win.isVisible()
        assert not win.ui.actionEncoderDebug.isVisible()
    finally:
        win.close()
        ModuleRegistry.clear()


def test_the_launcher_uses_the_default_profile_without_one(qtbot) -> None:
    ModuleRegistry.clear()
    created = Launcher(window_mode="normal", simulate=True, persist=False, overrides=FAST_SIM)
    win = created.start()
    qtbot.addWidget(win)
    try:
        assert win.config.profile == load_config().get("application.profile")
    finally:
        win.close()
        ModuleRegistry.clear()


def test_switching_rebuilds_the_window_keeps_the_simulation_and_reconnects(qtbot, launcher) -> None:
    old = launcher.start()
    _connect_arduino(qtbot, old)
    old.ui.kdcPanel.ui.buttonConnect.click()
    assert old.ctx.kdc.is_connected
    old_bench = old.ctx.simulation
    assert old_bench is not None

    new = launcher.switch_to("student")
    qtbot.addWidget(new)

    assert new is not old and launcher.window is new
    assert new.config.profile == "student"
    assert not old.isVisible()
    assert new.isVisible()
    assert new.ctx.simulation is not None and new.ctx.simulation is not old_bench
    assert new.ctx.connection.is_connected
    assert new.ctx.kdc.is_connected
    assert not new.ctx.pm400.is_connected  # it was not connected before
    assert not new.ui.actionEncoderDebug.isVisible()
    assert new.ui.actionSwitchProfile.text() == "Zu Experte wechseln"


def test_switching_back_restores_the_expert_window(qtbot, launcher) -> None:
    launcher.start()
    launcher.switch_to("student")
    expert = launcher.switch_to("expert")
    qtbot.addWidget(expert)
    assert expert.config.profile == "expert"
    assert expert.ui.actionEncoderDebug.isVisible()
    assert expert.ui.detectorPanel.ui.buttonOpenCalibration.isVisible()


def test_switching_connects_nothing_that_was_not_connected(qtbot, launcher) -> None:
    launcher.start()
    new = launcher.switch_to("student")
    qtbot.addWidget(new)
    assert not new.ctx.connection.is_connected
    assert not new.ctx.kdc.is_connected


def test_switching_keeps_the_window_mode(qtbot) -> None:
    ModuleRegistry.clear()
    created = Launcher(profile="expert", window_mode="fullscreen", simulate=True, persist=False,
                       overrides=FAST_SIM)  # fmt: skip
    old = created.start()
    assert old.isFullScreen()
    new = created.switch_to("student")
    qtbot.addWidget(new)
    try:
        assert new.isFullScreen()
    finally:
        new.close()
        ModuleRegistry.clear()


def test_the_switch_request_of_the_window_swaps_it_through_the_event_loop(qtbot, launcher) -> None:
    old = launcher.start()
    old.ui.actionSwitchProfile.trigger()
    qtbot.waitUntil(lambda: launcher.window is not old, timeout=5000)
    qtbot.addWidget(launcher.window)
    assert launcher.window.config.profile == "student"


def test_no_switch_while_a_measurement_runs(qtbot, launcher) -> None:
    old = launcher.start()
    qtbot.addWidget(old)
    _connect_arduino(qtbot, old)
    old.ui.measurementPanel.ui.buttonStart.click()
    assert old.ctx.measurement.is_measuring
    assert launcher.switch_to("student") is old
    assert launcher.window is old and old.isVisible()
    assert old.ctx.measurement.is_measuring
    old.ui.measurementPanel.ui.buttonStop.click()


def test_no_switch_while_a_worker_runs(qtbot, launcher) -> None:
    old = launcher.start()
    qtbot.addWidget(old)
    worker = _Sleeper()
    old.tabs.tabs[0]._sweep_worker = worker
    worker.start()
    try:
        assert launcher.switch_to("student") is old
        assert old.isVisible()
    finally:
        worker.requestInterruption()
        worker.wait(2000)


def test_switching_to_the_current_profile_does_nothing(qtbot, launcher) -> None:
    old = launcher.start()
    qtbot.addWidget(old)
    assert launcher.switch_to("expert") is old
    assert launcher.window is old and old.isVisible()


def test_a_closed_launcher_window_is_a_noop_target(launcher) -> None:
    assert launcher.switch_to("student") is None  # nothing started yet


def test_the_quit_on_last_window_closed_flag_is_restored_after_a_switch(qtbot, launcher) -> None:
    from PySide6.QtWidgets import QApplication

    launcher.start()
    app = QApplication.instance()
    assert isinstance(app, QApplication)
    before = app.quitOnLastWindowClosed()
    new = launcher.switch_to("student")
    qtbot.addWidget(new)
    assert app.quitOnLastWindowClosed() == before
