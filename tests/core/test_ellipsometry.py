"""Tests for core.ellipsometry — pure numpy, no Qt/hardware, synthetic round-trips only."""

import math

import numpy as np
import pytest

from polarisation_ui.core.ellipsometry import (
    fit_film,
    fit_rae,
    n_k_two_phase,
    psi_delta_from_fit,
    psi_delta_three_phase,
    rho_from_psi_delta,
)

# ---------------------------------------------------------------------------
# fit_rae / psi_delta_from_fit round-trip
# ---------------------------------------------------------------------------


def _synthetic_intensity(
    azimuth_deg, psi_deg: float, delta_deg: float, polariser_deg: float, i0: float = 1.0
):
    """Generate noiseless I(A) samples for a known (Psi, Delta) at a fixed polariser azimuth."""
    tan_p = math.tan(math.radians(polariser_deg))
    tan_psi = math.tan(math.radians(psi_deg))
    alpha = (tan_psi**2 - tan_p**2) / (tan_psi**2 + tan_p**2)
    beta = (2 * tan_psi * tan_p * math.cos(math.radians(delta_deg))) / (tan_psi**2 + tan_p**2)
    az = np.radians(np.asarray(azimuth_deg, dtype=float))
    return i0 * (1 + alpha * np.cos(2 * az) + beta * np.sin(2 * az))


class TestFitRaeRoundTrip:
    def test_recovers_known_psi_delta(self):
        psi_true, delta_true, p = 25.0, 70.0, 45.0
        az = np.linspace(0, 180, 37, endpoint=False)
        signal = _synthetic_intensity(az, psi_true, delta_true, p)

        fit = fit_rae(az, signal)
        assert fit.valid
        psi, delta = psi_delta_from_fit(fit, p)
        assert psi == pytest.approx(psi_true, abs=0.05)
        assert delta == pytest.approx(delta_true, abs=0.05)

    def test_recovers_with_noise(self):
        rng = np.random.default_rng(42)
        psi_true, delta_true, p = 30.0, 100.0, 45.0
        az = np.linspace(0, 180, 73, endpoint=False)
        signal = _synthetic_intensity(az, psi_true, delta_true, p) + rng.normal(0, 1e-4, az.size)

        fit = fit_rae(az, signal)
        assert fit.valid
        psi, delta = psi_delta_from_fit(fit, p)
        assert psi == pytest.approx(psi_true, abs=0.5)
        assert delta == pytest.approx(delta_true, abs=0.5)

    def test_requires_at_least_three_points(self):
        with pytest.raises(ValueError):
            fit_rae([0.0, 90.0], [1.0, 1.0])

    def test_invalid_when_modulation_exceeds_one(self):
        # A signal that isn't of the physical form 1 + alpha*cos + beta*sin
        # (over-modulated) must not be reported as a usable fit.
        az = np.linspace(0, 180, 37, endpoint=False)
        signal = 1.0 + 3.0 * np.cos(2 * np.radians(az))  # alpha=3 -> modulation >= 1
        fit = fit_rae(az, signal)
        assert not fit.valid

    def test_psi_delta_from_fit_rejects_invalid_fit(self):
        az = np.linspace(0, 180, 37, endpoint=False)
        signal = 1.0 + 3.0 * np.cos(2 * np.radians(az))
        fit = fit_rae(az, signal)
        with pytest.raises(ValueError):
            psi_delta_from_fit(fit, 45.0)

    def test_psi_delta_from_fit_rejects_degenerate_polariser_azimuth(self):
        az = np.linspace(0, 180, 37, endpoint=False)
        signal = _synthetic_intensity(az, 30.0, 90.0, 45.0)
        fit = fit_rae(az, signal)
        with pytest.raises(ValueError):
            psi_delta_from_fit(fit, 0.0)


# ---------------------------------------------------------------------------
# Two-phase inversion
# ---------------------------------------------------------------------------


class TestTwoPhase:
    def test_n_k_two_phase_recovers_silicon(self):
        # Bare silicon at 632.8 nm, AOI 65 deg: forward-model via the 3-phase
        # function with thickness pinned to 0 (see its docstring: this reduces
        # exactly to the bare-substrate result, independent of the film's own
        # optical constants) then invert and check we recover (n_sub, k_sub).
        n_sub, k_sub, aoi = 3.88, 0.02, 65.0
        psi, delta = psi_delta_three_phase(
            aoi, 632.8, 0.0, n_film=1.46, k_film=0.0, n_sub=n_sub, k_sub=k_sub
        )
        rho = rho_from_psi_delta(float(psi), float(delta))
        n, k = n_k_two_phase(rho, aoi)
        assert n == pytest.approx(n_sub, abs=1e-6)
        assert k == pytest.approx(k_sub, abs=1e-6)

    def test_rejects_unreachable_rho(self):
        with pytest.raises(ValueError):
            n_k_two_phase(complex(-1.0, 0.0), 65.0)


# ---------------------------------------------------------------------------
# Three-phase forward model
# ---------------------------------------------------------------------------


class TestThreePhaseForward:
    def test_zero_thickness_matches_bare_substrate_regardless_of_film_index(self):
        aoi = np.array([45.0, 55.0, 65.0, 75.0])
        psi_a, delta_a = psi_delta_three_phase(
            aoi, 632.8, 0.0, n_film=1.46, k_film=0.0, n_sub=3.88, k_sub=0.02
        )
        psi_b, delta_b = psi_delta_three_phase(
            aoi, 632.8, 0.0, n_film=2.1, k_film=0.3, n_sub=3.88, k_sub=0.02
        )
        np.testing.assert_allclose(psi_a, psi_b, atol=1e-6)
        np.testing.assert_allclose(delta_a, delta_b, atol=1e-6)

    def test_vectorises_over_aoi(self):
        aoi = np.array([45.0, 55.0, 65.0, 75.0])
        psi, delta = psi_delta_three_phase(aoi, 632.8, 120.0, 1.46, 0.0, 3.88, 0.02)
        assert psi.shape == aoi.shape
        assert delta.shape == aoi.shape


# ---------------------------------------------------------------------------
# fit_film
# ---------------------------------------------------------------------------


class TestFitFilm:
    def test_recovers_known_thickness_and_index_from_multi_aoi_series(self):
        d_true, n_true = 120.0, 1.46
        aoi = [45.0, 55.0, 65.0, 75.0]
        psi, delta = psi_delta_three_phase(
            np.array(aoi), 632.8, d_true, n_true, 0.0, n_sub=3.88, k_sub=0.02
        )
        result = fit_film(
            aoi, psi.tolist(), delta.tolist(), wavelength_nm=632.8, n_sub=3.88, k_sub=0.02
        )
        assert result.thickness_nm == pytest.approx(d_true, abs=5.0)
        assert result.n_film == pytest.approx(n_true, abs=0.05)
        assert result.mse < 0.5

    def test_single_aoi_narrow_n_range_exposes_periodic_branches(self):
        # With the film index pinned to a narrow window around the true value,
        # a single AOI cannot distinguish d from d + period, so the coarse
        # search should surface more than one comparably-good local minimum.
        d_true, n_true, aoi_val = 120.0, 1.46, 65.0
        psi, delta = psi_delta_three_phase(
            aoi_val, 632.8, d_true, n_true, 0.0, n_sub=3.88, k_sub=0.02
        )
        result = fit_film(
            [aoi_val],
            [float(psi)],
            [float(delta)],
            wavelength_nm=632.8,
            n_sub=3.88,
            k_sub=0.02,
            n_range=(1.459, 1.461),
            d_range=(0.0, 1000.0),
            refine_rounds=1,
        )
        assert len(result.branches) >= 2
        # Which alias wins as `thickness_nm` is itself arbitrary among
        # near-degenerate aliases with only one AOI -- that ambiguity is
        # exactly what `branches` exposes. So check the true thickness is
        # recovered by *some* branch, not necessarily the reported "best" one.
        d_sorted = sorted(b[0] for b in result.branches)
        assert any(abs(d - d_true) < 10.0 for d in d_sorted)
        # Expected period from the standard thin-film interference formula.
        theta_rad = math.radians(aoi_val)
        period = 632.8 / (2 * math.sqrt(n_true**2 - math.sin(theta_rad) ** 2))
        gaps = np.diff(d_sorted)
        assert np.any(np.isclose(gaps, period, atol=15.0))

    def test_rejects_empty_series(self):
        with pytest.raises(ValueError):
            fit_film([], [], [], wavelength_nm=632.8, n_sub=3.88, k_sub=0.02)
