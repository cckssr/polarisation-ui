"""Live PD-TIA power path of DataController: calibrated slope + per-gain zero offset."""

from unittest.mock import MagicMock

import pytest

from polarisation_ui.core.detector import point_power
from polarisation_ui.core.power_calibration import GainCalibration, PowerCalibrationProfile

_SLOPE = 1.2e-4  # W/V
_V0 = -5.6e-3  # zero-light voltage of gain 2


@pytest.fixture()
def controller(qapp, tmp_path, monkeypatch):
    import polarisation_ui.infrastructure.session_journal as sj_mod
    from polarisation_ui.ui.controllers.data_controller import DataController

    monkeypatch.setattr(sj_mod, "JOURNAL_BASE", tmp_path / "sessions")
    dm = MagicMock()
    dm.is_encoder_connected.return_value = True
    dm.read_angles.return_value = MagicMock(sample_angle=10.0, detector_angle=20.0)
    dm.get_firmware_version.return_value = "2.1.0"
    dm.get_desired_state.return_value.as_config_snapshot.return_value = {}

    ctrl = DataController(dm, use_mock_intensity=True)
    profile = PowerCalibrationProfile(name="T")
    profile.gains[2] = GainCalibration(
        gain_stage=2,
        points=[(p / _SLOPE + _V0, p) for p in (4e-7, 1e-6, 1e-5, 1e-4, 2.4e-4)],
    )
    ctrl.update_calibration_profile(profile)
    ctrl._current_pdtia_gain = 2
    yield ctrl
    ctrl.cleanup()


def _poll(ctrl, raw_V: float):
    ctrl._read_raw_adc = lambda _angle: raw_V  # type: ignore[method-assign]
    frames: list = []
    ctrl.frame_ready.connect(frames.append)
    ctrl._poll_sensors()
    return frames[-1]


def test_dark_reading_maps_to_zero_power_without_tare(controller):
    # Raw -5.6 mV is the zero-light reading: intensity is clipped to 0 V,
    # but the calibrated power must come from the unclipped voltage.
    frame = _poll(controller, _V0)
    assert frame.power_W == pytest.approx(0.0, abs=1e-12)


def test_power_matches_calibration_line(controller):
    frame = _poll(controller, 1.0)
    assert frame.conv_factor_W_per_V == pytest.approx(_SLOPE, rel=1e-6)
    assert frame.power_W == pytest.approx(_SLOPE * (1.0 - _V0), rel=1e-6)


def test_dark_tare_does_not_change_calibrated_power(controller):
    controller._dark_V = _V0  # user tared in the dark at this gain
    frame = _poll(controller, 1.0)
    assert frame.power_W == pytest.approx(_SLOPE * (1.0 - _V0), rel=1e-6)


@pytest.mark.parametrize("dark_V", [0.0, _V0, 0.003])
def test_point_power_from_tared_intensity_matches_live_power(controller, dark_V):
    """Tabs derive power from Frame.intensity (tared, clipped) — must agree with power_W."""
    controller._dark_V = dark_V
    frame = _poll(controller, 1.0)
    derived, conv = point_power(frame, frame.intensity)
    assert conv == pytest.approx(_SLOPE, rel=1e-6)
    assert derived == pytest.approx(frame.power_W, rel=1e-9)


def test_calibration_voltage_is_the_raw_untared_reading(controller):
    """Manual calibration points must live in the same (raw) domain the profile is applied to."""
    controller._dark_V = 0.003
    seen: list[float] = []
    controller.calibration_voltage_updated.connect(seen.append)
    shown: list[float] = []
    controller.intensity_updated.connect(shown.append)
    _poll(controller, _V0)
    assert seen[-1] == pytest.approx(_V0)  # raw, negative, not clipped
    assert shown[-1] == 0.0  # the tared display voltage is clipped at 0 V
