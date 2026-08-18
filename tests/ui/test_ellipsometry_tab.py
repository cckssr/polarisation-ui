"""Tests for EllipsometryTab (manual analyser-azimuth entry, live RAE fit, AOI series).

These tests call build() which constructs pyqtgraph widgets.  CI runs with
QT_QPA_PLATFORM=offscreen so no physical display is required.
"""

import dataclasses
import math

import pytest

from polarisation_ui.core.ellipsometry import (
    n_k_two_phase,
    psi_delta_three_phase,
    rho_from_psi_delta,
)
from polarisation_ui.core.models import Frame
from polarisation_ui.ui.widgets.tabs.ellipsometry_tab import EllipsometryTab

# Hand-picked (Psi, Delta) comfortably away from the Delta=0/180 deg edge,
# where modulation m = sqrt(alpha**2+beta**2) is mathematically exactly 1 (see
# module docs) -- too close to that edge, fitting 19 discrete samples in
# double precision can push a numerically recovered m fractionally over the
# valid m < 1 threshold. Used for tests that only need *some* consistent,
# well-posed (Psi, Delta), not a specific physical sample.
_PSI_SAFE = 25.0
_DELTA_SAFE = 100.0
# Tab default (see ellipsometry_tab.ui) -- n_k_two_phase() calls in these
# tests must match it to reproduce what the tab itself computes.
_N_AMBIENT_DEFAULT = 1.0003

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_frame(
    ts_ms: int = 1000,
    intensity: float = 0.5,
    sample_angle: float = 65.0,
    detector_angle: float = 130.0,
    pdtia_gain: int = 1,
    power_W: float | None = None,
    conv_factor_W_per_V: float | None = None,
) -> Frame:
    return Frame(
        ts_ms=ts_ms,
        sample_angle=sample_angle,
        detector_angle=detector_angle,
        intensity=intensity,
        pdtia_gain=pdtia_gain,
        power_W=power_W,
        conv_factor_W_per_V=conv_factor_W_per_V,
    )


def _feed_harmonic_points(
    tab: EllipsometryTab,
    *,
    psi_deg: float,
    delta_deg: float,
    polariser_deg: float,
    aoi_deg: float = 65.0,
    n_points: int = 19,
    conv_factor: float = 2e-6,
) -> None:
    """Feed n_points manual samples reproducing a known (Psi, Delta) at polariser_deg.

    Mirrors the derivation validated in tests/core/test_ellipsometry.py's
    _synthetic_intensity helper (the inverse of psi_delta_from_fit's formulas).
    Each point uses a fresh single-frame buffer so the 500 ms averaging window
    never mixes samples from different analyser azimuths.
    """
    tab._aoi_zero_sample = 0.0
    tab._aoi_zero_detector = 0.0
    tan_p = math.tan(math.radians(polariser_deg))
    tan_psi = math.tan(math.radians(psi_deg))
    alpha = (tan_psi**2 - tan_p**2) / (tan_psi**2 + tan_p**2)
    beta = (2 * tan_psi * tan_p * math.cos(math.radians(delta_deg))) / (tan_psi**2 + tan_p**2)
    offset = tab._ui.spinAnalyserOffset.value()
    step = 180.0 / n_points
    for i in range(n_points):
        a = i * step
        az = math.radians(a + offset)
        intensity = 1.0 + alpha * math.cos(2 * az) + beta * math.sin(2 * az)
        frame = _make_frame(
            ts_ms=100_000 + i * 1000,
            intensity=intensity,
            sample_angle=aoi_deg,
            detector_angle=2 * aoi_deg,
            power_W=intensity * conv_factor,
            conv_factor_W_per_V=conv_factor,
        )
        tab._buffer.clear()
        tab._buffer.append(frame)
        tab._latest_frame = frame
        tab._ui.spinAnalyserManual.setValue(a)
        tab._add_point()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tab(qtbot):
    t = EllipsometryTab()
    t.build()
    qtbot.addWidget(t)
    return t


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def test_build_creates_plots_and_inputs(tab):
    assert tab._ui.fitPlot is not None
    assert tab._ui.ellipsoCurvePlot is not None
    assert tab._ui.spinPolariser is not None
    assert tab._ui.spinAnalyserOffset is not None
    assert tab._ui.btnAddPoint is not None


def test_analyser_offset_defaults_to_polariser_plus_90(tab):
    tab._ui.spinPolariser.setValue(30.0)
    assert tab._ui.spinAnalyserOffset.value() == pytest.approx(120.0)


def test_manual_analyser_offset_edit_stops_auto_tracking(tab):
    tab._ui.spinAnalyserOffset.setValue(200.0)
    tab._ui.spinPolariser.setValue(10.0)
    # offset must stay at the user's value, not jump to 10+90=100
    assert tab._ui.spinAnalyserOffset.value() == pytest.approx(200.0)


# ---------------------------------------------------------------------------
# Power-calibration gate
# ---------------------------------------------------------------------------


def test_gates_disabled_without_measurement(tab):
    assert not tab._ui.gbManual.isEnabled()


def test_gates_stay_disabled_without_power_calibration(tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(1000, conv_factor_W_per_V=None))
    assert not tab._ui.gbManual.isEnabled()


def test_gates_enabled_once_measuring_and_calibrated(tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(1000, power_W=1e-6, conv_factor_W_per_V=2e-6))
    assert tab._ui.gbManual.isEnabled()


def test_uncalibrated_transition_emits_warning_once(tab):
    warnings: list[tuple[str, str]] = []
    tab.status_message.connect(lambda level, msg: warnings.append((level, msg)))
    tab.on_measurement_started()
    tab.on_frame(_make_frame(1000, power_W=1e-6, conv_factor_W_per_V=2e-6))
    tab.on_frame(_make_frame(1100, conv_factor_W_per_V=None))
    tab.on_frame(_make_frame(1200, conv_factor_W_per_V=None))  # no further warning
    assert len([w for w in warnings if w[0] == "warning"]) == 1


# ---------------------------------------------------------------------------
# AOI zero
# ---------------------------------------------------------------------------


def test_set_aoi_zero_without_frame_warns(tab):
    warnings: list[tuple[str, str]] = []
    tab.status_message.connect(lambda level, msg: warnings.append((level, msg)))
    tab._set_aoi_zero()
    assert warnings and warnings[0][0] == "warning"


def test_set_aoi_zero_captures_reference(tab):
    tab.on_frame(_make_frame(1000, sample_angle=12.0, detector_angle=24.0))
    tab._set_aoi_zero()
    assert tab._aoi_zero_sample == pytest.approx(12.0)
    assert tab._aoi_zero_detector == pytest.approx(24.0)


def test_live_aoi_label_after_zero(tab):
    tab.on_frame(_make_frame(1000, sample_angle=12.0, detector_angle=24.0))
    tab._set_aoi_zero()
    tab.on_frame(_make_frame(1100, sample_angle=77.0, detector_angle=154.0))
    assert "65.0" in tab._ui.lblLiveAoi.text()


def test_specular_error_near_zero_for_ideal_mirror_condition(tab):
    tab.on_frame(_make_frame(1000, sample_angle=0.0, detector_angle=0.0))
    tab._set_aoi_zero()
    tab.on_frame(_make_frame(1100, sample_angle=65.0, detector_angle=130.0))
    # detector at exactly 2*aoi -> specular error ~ 0
    assert "0.00" in tab._ui.lblSpecularError.text()


# ---------------------------------------------------------------------------
# Manual point collection + live RAE fit
# ---------------------------------------------------------------------------


def test_fit_invalid_with_fewer_than_three_points(tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(1000, power_W=1e-6, conv_factor_W_per_V=2e-6))
    tab._aoi_zero_sample = 0.0
    tab._buffer.clear()
    tab._buffer.append(_make_frame(2000, intensity=0.5, power_W=1e-6, conv_factor_W_per_V=2e-6))
    tab._ui.spinAnalyserManual.setValue(0.0)
    tab._add_point()
    assert tab._last_fit is None
    assert not tab._ui.btnAcceptPoint.isEnabled()


def test_manual_points_recover_known_psi_delta(tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(1000, power_W=1e-6, conv_factor_W_per_V=2e-6))
    aoi_val, polariser = 65.0, 45.0
    tab._ui.spinPolariser.setValue(polariser)

    _feed_harmonic_points(
        tab, psi_deg=_PSI_SAFE, delta_deg=_DELTA_SAFE, polariser_deg=polariser, aoi_deg=aoi_val
    )

    assert tab._last_fit is not None
    assert tab._last_fit.valid
    assert float(tab._ui.lblPsi.text().rstrip("°")) == pytest.approx(_PSI_SAFE, abs=0.1)
    assert float(tab._ui.lblDelta.text().rstrip("°")) == pytest.approx(_DELTA_SAFE, abs=0.1)
    assert tab._ui.btnAcceptPoint.isEnabled()

    expected_n, expected_k = n_k_two_phase(
        rho_from_psi_delta(_PSI_SAFE, _DELTA_SAFE), aoi_val, _N_AMBIENT_DEFAULT
    )
    n_pseudo, k_pseudo = tab._last_psi_delta[2], tab._last_psi_delta[3]
    assert n_pseudo == pytest.approx(expected_n, abs=1e-3)
    assert k_pseudo == pytest.approx(expected_k, abs=1e-3)


def test_add_point_empty_buffer_emits_warning(tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(1000, power_W=1e-6, conv_factor_W_per_V=2e-6))
    tab._buffer.clear()
    warnings: list[tuple[str, str]] = []
    tab.status_message.connect(lambda level, msg: warnings.append((level, msg)))
    tab._add_point()
    assert warnings and warnings[0][0] == "warning"


def test_clear_sweep_buffer_resets_fit_state(tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(1000, power_W=1e-6, conv_factor_W_per_V=2e-6))
    tab._ui.spinPolariser.setValue(45.0)
    _feed_harmonic_points(tab, psi_deg=_PSI_SAFE, delta_deg=_DELTA_SAFE, polariser_deg=45.0)
    assert tab._ui.fitPlot.get_points()

    tab._clear_sweep_buffer()
    assert tab._ui.fitPlot.get_points() == []
    assert tab._last_fit is None
    assert not tab._ui.btnAcceptPoint.isEnabled()


# ---------------------------------------------------------------------------
# Accept -> series
# ---------------------------------------------------------------------------


def test_accept_point_appends_to_series_and_clears_buffer(qtbot, tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(1000, power_W=1e-6, conv_factor_W_per_V=2e-6))
    tab._ui.spinPolariser.setValue(45.0)
    _feed_harmonic_points(tab, psi_deg=_PSI_SAFE, delta_deg=_DELTA_SAFE, polariser_deg=45.0)

    with qtbot.waitSignal(tab.points_changed, timeout=500) as blocker:
        tab._accept_point()

    assert blocker.args == [1]
    assert len(tab.get_saved_points()) == 1
    assert tab._ui.fitPlot.get_points() == []
    assert tab._series[0].aoi_deg == pytest.approx(65.0)
    expected_n, _ = n_k_two_phase(
        rho_from_psi_delta(_PSI_SAFE, _DELTA_SAFE), 65.0, _N_AMBIENT_DEFAULT
    )
    assert tab._series[0].n_pseudo == pytest.approx(expected_n, abs=1e-3)
    assert tab._ui.btnFitModel.isEnabled()


def test_accept_point_without_aoi_zero_is_rejected(tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(1000, power_W=1e-6, conv_factor_W_per_V=2e-6))
    tab._aoi_zero_sample = None  # AOI unknown
    tab._ui.spinPolariser.setValue(45.0)
    # _feed_harmonic_points forces aoi_zero_sample=0.0 -- bypass it here to keep aoi NaN
    tan_p = math.tan(math.radians(45.0))
    tan_psi = math.tan(math.radians(_PSI_SAFE))
    alpha = (tan_psi**2 - tan_p**2) / (tan_psi**2 + tan_p**2)
    beta = (2 * tan_psi * tan_p * math.cos(math.radians(_DELTA_SAFE))) / (tan_psi**2 + tan_p**2)
    offset = tab._ui.spinAnalyserOffset.value()
    for i in range(19):
        a = i * (180.0 / 19)
        az = math.radians(a + offset)
        intensity = 1.0 + alpha * math.cos(2 * az) + beta * math.sin(2 * az)
        frame = _make_frame(
            ts_ms=100_000 + i * 1000,
            intensity=intensity,
            power_W=intensity * 2e-6,
            conv_factor_W_per_V=2e-6,
        )
        tab._buffer.clear()
        tab._buffer.append(frame)
        tab._latest_frame = frame
        tab._ui.spinAnalyserManual.setValue(a)
        tab._add_point()

    assert not tab._ui.btnAcceptPoint.isEnabled()
    tab._accept_point()
    assert tab.get_saved_points() == []


# ---------------------------------------------------------------------------
# get_saved_points / build_export
# ---------------------------------------------------------------------------


def test_get_saved_points_initially_empty(tab):
    assert tab.get_saved_points() == []


def test_build_export_empty_tab(tab):
    exp = tab.build_export()
    assert exp.filename_hint == "ellipsometry"
    assert exp.rows == []
    assert "aoi_deg" in exp.columns
    assert "psi_deg" in exp.columns
    assert exp.metadata["delta_sign_ambiguous"] is True


def test_build_export_schema_with_series(qtbot, tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(1000, power_W=1e-6, conv_factor_W_per_V=2e-6))
    tab._ui.spinPolariser.setValue(45.0)
    _feed_harmonic_points(tab, psi_deg=_PSI_SAFE, delta_deg=_DELTA_SAFE, polariser_deg=45.0)
    tab._accept_point()

    exp = tab.build_export()
    assert exp.filename_hint == "ellipsometry"
    assert len(exp.rows) == 19  # one row per raw sample
    assert exp.filename_tokens == ["2phase"]
    assert exp.metadata["polariser_azimuth_deg"] == pytest.approx(45.0)


def test_build_export_3phase_token(tab):
    tab._ui.cmbModel.setCurrentIndex(1)
    exp = tab.build_export()
    assert exp.filename_tokens == ["3phase"]
    assert exp.metadata["model"] == "3phase"


# ---------------------------------------------------------------------------
# restore_points round-trip
# ---------------------------------------------------------------------------


def test_restore_points_round_trip(qtbot, tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(1000, power_W=1e-6, conv_factor_W_per_V=2e-6))
    tab._ui.spinPolariser.setValue(45.0)
    _feed_harmonic_points(tab, psi_deg=_PSI_SAFE, delta_deg=_DELTA_SAFE, polariser_deg=45.0)
    tab._accept_point()
    saved = [dataclasses.asdict(p) for p in tab.get_saved_points()]

    tab2 = EllipsometryTab()
    tab2.build()
    qtbot.addWidget(tab2)
    with qtbot.waitSignal(tab2.points_changed, timeout=500):
        tab2.restore_points(saved)

    assert len(tab2.get_saved_points()) == 1
    restored = tab2.get_saved_points()[0]
    assert restored.aoi_deg == pytest.approx(65.0)
    assert len(restored.samples) == 19


def test_restore_points_ignores_malformed_entries(tab):
    tab.restore_points([{"not": "valid"}])
    assert tab.get_saved_points() == []


# ---------------------------------------------------------------------------
# Delete / clear
# ---------------------------------------------------------------------------


def _accept_one_point(tab, aoi_deg: float = 65.0) -> None:
    tab.on_measurement_started()
    tab.on_frame(_make_frame(1000, power_W=1e-6, conv_factor_W_per_V=2e-6))
    tab._ui.spinPolariser.setValue(45.0)
    _feed_harmonic_points(
        tab, psi_deg=_PSI_SAFE, delta_deg=_DELTA_SAFE, polariser_deg=45.0, aoi_deg=aoi_deg
    )
    tab._accept_point()


def test_delete_last_series_point(tab):
    _accept_one_point(tab)
    assert len(tab.get_saved_points()) == 1
    tab._delete_last_series_point()
    assert tab.get_saved_points() == []


def test_delete_last_on_empty_series_warns(tab):
    warnings: list[tuple[str, str]] = []
    tab.status_message.connect(lambda level, msg: warnings.append((level, msg)))
    tab._delete_last_series_point()
    assert warnings and warnings[0][0] == "warning"


def test_clear_series(tab):
    _accept_one_point(tab)
    tab._clear_series()
    assert tab.get_saved_points() == []
    assert not tab._ui.btnFitModel.isEnabled()


# ---------------------------------------------------------------------------
# on_reset
# ---------------------------------------------------------------------------


def test_reset_clears_series_and_buffers(qtbot, tab):
    _accept_one_point(tab)
    assert len(tab.get_saved_points()) == 1

    with qtbot.waitSignal(tab.points_changed, timeout=500):
        tab.on_reset()

    assert tab.get_saved_points() == []
    assert len(tab._buffer) == 0
    assert tab._ui.lblPsi.text() == "—"


# ---------------------------------------------------------------------------
# Optical model fit
# ---------------------------------------------------------------------------


def test_fit_model_two_phase_reports_mean_pseudo_index(tab):
    _accept_one_point(tab)
    expected_n, _ = n_k_two_phase(
        rho_from_psi_delta(_PSI_SAFE, _DELTA_SAFE), 65.0, _N_AMBIENT_DEFAULT
    )
    tab._ui.cmbModel.setCurrentIndex(0)
    tab._fit_model()
    reported_n = float(tab._ui.lblNFilm.text().split()[0])
    assert reported_n == pytest.approx(expected_n, abs=1e-3)
    assert tab._model_fit is None


def test_fit_model_three_phase_recovers_thickness(tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(1000, power_W=1e-6, conv_factor_W_per_V=2e-6))
    tab._ui.spinPolariser.setValue(45.0)
    for aoi_val in (45.0, 55.0, 65.0, 75.0):
        psi_true, delta_true = psi_delta_three_phase(aoi_val, 632.8, 120.0, 1.46, 0.0, 3.88, 0.02)
        _feed_harmonic_points(
            tab,
            psi_deg=float(psi_true),
            delta_deg=float(delta_true),
            polariser_deg=45.0,
            aoi_deg=aoi_val,
        )
        tab._accept_point()

    tab._ui.cmbModel.setCurrentIndex(1)
    tab._fit_model()
    assert tab._model_fit is not None
    assert tab._model_fit.thickness_nm == pytest.approx(120.0, abs=10.0)
    assert tab._model_fit.n_film == pytest.approx(1.46, abs=0.05)
    assert "nm" in tab._ui.lblThickness.text()


def test_fit_model_noop_without_series(tab):
    tab._fit_model()  # must not raise
    assert tab._model_fit is None
