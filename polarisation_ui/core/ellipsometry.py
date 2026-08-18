"""Rotating-analyser ellipsometry (RAE) physics — pure numpy, no Qt or I/O.

Bench geometry (PSA — Polariser, Sample, Analyser):

    source -> fixed polariser (azimuth P) -> sample (AOI theta) ->
    rotating analyser (KDC101, azimuth A) -> PD-TIA detector

The analyser intensity is a two-harmonic function of its azimuth::

    I(A) = I0 * [1 + alpha*cos(2A) + beta*sin(2A)]

which is *linear* in (I0, I0*alpha, I0*beta), so it is fit exactly with
``numpy.linalg.lstsq`` rather than a nonlinear solver — the same technique
used for the encoder-error harmonics in
``calibration_tool/calibration/analysis.py``.  From (alpha, beta) the
ellipsometric angles follow in closed form::

    tan(Psi)  = sqrt((1+alpha)/(1-alpha)) * |tan(P)|
    cos(Delta) = beta / sqrt(1-alpha**2)          -> Delta in [0, 180] deg

A rotating-analyser ellipsometer only measures cos(Delta), so **the sign of
Delta is fundamentally undetermined** by this bench (a compensator would be
needed to resolve it).  Every function below that returns or consumes a
measured Delta treats it as living in [0, 180] deg for this reason.

Two optical-model layers build on (Psi, Delta):

- ``n_k_two_phase`` — closed-form pseudo-dielectric-function inversion for a
  bare (ambient/substrate) sample.
- ``psi_delta_three_phase`` / ``fit_film`` — a full complex-Fresnel
  ambient/film/substrate model, fit by a vectorised coarse-to-fine numpy grid
  search (no scipy dependency — see project notes on why).  Film thickness is
  periodic in the model, so a single angle of incidence cannot pick a unique
  branch; ``fit_film`` reports the best branch *and* the alternative local
  minima found along the thickness axis so a multi-AOI series can be used to
  disambiguate them.
"""

from __future__ import annotations

import cmath
import math
from collections.abc import Sequence
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

__all__ = [
    "RaeFit",
    "FilmFit",
    "fit_rae",
    "psi_delta_from_fit",
    "rho_from_psi_delta",
    "n_k_two_phase",
    "psi_delta_three_phase",
    "fit_film",
]


@dataclass(frozen=True)
class RaeFit:
    """Result of fitting I(A) = I0*(1 + alpha*cos(2A) + beta*sin(2A))."""

    i0: float
    alpha: float
    beta: float
    residual_rms: float
    modulation: float  # sqrt(alpha**2 + beta**2); must be < 1 for a physical fit
    n_points: int
    valid: bool  # False if the fit is degenerate (i0 <= 0 or modulation >= 1)


@dataclass(frozen=True)
class FilmFit:
    """Result of fitting a 3-phase (ambient/film/substrate) model to a (theta, Psi, Delta) series.

    See fit_film() for how the search is performed.
    """

    thickness_nm: float
    n_film: float
    k_film: float
    mse: float
    # Alternative (thickness_nm, n_film, mse) local minima along the thickness
    # axis found during the coarse search — exposes the thickness-period
    # ambiguity inherent to a single-wavelength fit.
    branches: list[tuple[float, float, float]] = field(default_factory=list)


def fit_rae(azimuth_deg: Sequence[float], signal: Sequence[float]) -> RaeFit:
    """Fit analyser-azimuth samples to I(A) = I0*(1 + alpha*cos(2A) + beta*sin(2A)).

    Args:
        azimuth_deg: Analyser azimuth for each sample, degrees, relative to
            the plane of incidence (i.e. already offset-corrected).
        signal: Detector reading for each sample (power_W recommended — see
            module docs on why gain-normalised power is used, not raw volts).

    Returns:
        RaeFit. ``valid`` is False when the fit is degenerate (non-positive
        I0, or modulation >= 1, which cannot come from a real intensity
        signal and indicates noise/misalignment/insufficient points).

    Raises:
        ValueError: if fewer than 3 points are given (3 unknowns to fit).
    """
    az = np.radians(np.asarray(azimuth_deg, dtype=float))
    y = np.asarray(signal, dtype=float)
    n = az.size
    if n < 3:
        raise ValueError("fit_rae requires at least 3 points")
    design = np.column_stack([np.ones(n), np.cos(2 * az), np.sin(2 * az)])
    coeffs, *_ = np.linalg.lstsq(design, y, rcond=None)
    i0, i0_alpha, i0_beta = coeffs
    residuals = y - design @ coeffs
    residual_rms = float(np.sqrt(np.mean(residuals**2)))

    if not math.isfinite(i0) or i0 == 0.0:
        return RaeFit(
            i0=float(i0),
            alpha=float("nan"),
            beta=float("nan"),
            residual_rms=residual_rms,
            modulation=float("nan"),
            n_points=n,
            valid=False,
        )

    alpha = float(i0_alpha / i0)
    beta = float(i0_beta / i0)
    modulation = math.hypot(alpha, beta)
    valid = bool(i0 > 0 and modulation < 1.0 and abs(alpha) < 1.0)
    return RaeFit(
        i0=float(i0),
        alpha=alpha,
        beta=beta,
        residual_rms=residual_rms,
        modulation=modulation,
        n_points=n,
        valid=valid,
    )


def psi_delta_from_fit(fit: RaeFit, polariser_azimuth_deg: float) -> tuple[float, float]:
    """Convert an RaeFit + polariser azimuth to ellipsometric (Psi, Delta) in degrees.

    Args:
        fit: A valid RaeFit (see RaeFit.valid).
        polariser_azimuth_deg: Fixed polariser azimuth P relative to the
            plane of incidence. Must not be 0 or 90 deg (RAE is blind there).

    Returns:
        (psi_deg, delta_deg) with psi_deg in [0, 90) and delta_deg in [0, 180]
        (the sign of Delta is undetermined by RAE — see module docs).

    Raises:
        ValueError: if the fit is invalid or |alpha| is too close to 1 to
            invert (the associated Psi -> 90 deg limit is numerically unstable).
    """
    if not fit.valid:
        raise ValueError("cannot compute Psi/Delta from an invalid RaeFit")
    tan_p = math.tan(math.radians(polariser_azimuth_deg))
    if tan_p == 0.0 or not math.isfinite(tan_p):
        raise ValueError("polariser_azimuth_deg must not be 0 or 90 deg — RAE is blind there")
    denom_sq = 1.0 - fit.alpha**2
    if denom_sq <= 1e-12:
        raise ValueError("alpha too close to +/-1 — Psi/Delta inversion is numerically unstable")
    tan_psi = math.sqrt((1.0 + fit.alpha) / (1.0 - fit.alpha)) * abs(tan_p)
    psi_deg = math.degrees(math.atan(tan_psi))
    cos_delta = max(-1.0, min(1.0, fit.beta / math.sqrt(denom_sq)))
    delta_deg = math.degrees(math.acos(cos_delta))
    return psi_deg, delta_deg


def rho_from_psi_delta(psi_deg: float, delta_deg: float) -> complex:
    """Return the complex reflectance ratio rho = r_p/r_s = tan(Psi) * exp(i*Delta)."""
    psi = math.radians(psi_deg)
    delta = math.radians(delta_deg)
    return math.tan(psi) * cmath.exp(1j * delta)


def n_k_two_phase(rho: complex, aoi_deg: float, n_ambient: float = 1.0) -> tuple[float, float]:
    """Invert a bare (ambient/substrate) sample's pseudo-dielectric function to (n, k).

    Uses the standard two-phase closed form::

        <eps> = n_ambient**2 * sin(theta)**2 * [1 + tan(theta)**2 * ((1-rho)/(1+rho))**2]

    with the sign convention n~ = n - i*k (k >= 0 for an absorbing medium).
    This treats the sample as a bulk substrate with no overlying film —
    a film changes the apparent (n, k), which is why a genuine film needs
    the 3-phase model below.

    Args:
        rho: Complex reflectance ratio, e.g. from rho_from_psi_delta().
        aoi_deg: Angle of incidence, degrees.
        n_ambient: Ambient (incidence-medium) refractive index.

    Returns:
        (n, k) — the pseudo refractive index and extinction coefficient.

    Raises:
        ValueError: if rho == -1 (division by zero; a physically unreachable point).
    """
    if rho == -1:
        raise ValueError("rho == -1 is not physically reachable — cannot invert")
    theta = math.radians(aoi_deg)
    sin_t = math.sin(theta)
    tan_t = math.tan(theta)
    eps = (n_ambient**2) * (sin_t**2) * (1.0 + (tan_t**2) * (((1 - rho) / (1 + rho)) ** 2))
    nk = cmath.sqrt(eps)
    return nk.real, -nk.imag


def _complex_cos_theta(n_this: NDArray, sin_theta: NDArray) -> NDArray:
    """Complex cos(theta) in *n_this*, selecting the forward-decaying branch.

    Principal-branch sqrt(1 - sin_theta**2) is not guaranteed to represent a
    forward-decaying wave for an absorbing medium; flip sign where it does not
    (i.e. where Im(n_this * cos_theta) > 0, using the n~ = n - i*k convention
    where a decaying transmitted/reflected wave has Im(n~ * cos_theta) <= 0).
    """
    cos_theta = np.sqrt(1.0 - sin_theta**2)
    bad = (n_this * cos_theta).imag > 0
    return np.where(bad, -cos_theta, cos_theta)


def _fresnel_rs(n_i: NDArray, cos_i: NDArray, n_j: NDArray, cos_j: NDArray) -> NDArray:
    return (n_i * cos_i - n_j * cos_j) / (n_i * cos_i + n_j * cos_j)


def _fresnel_rp(n_i: NDArray, cos_i: NDArray, n_j: NDArray, cos_j: NDArray) -> NDArray:
    return (n_j * cos_i - n_i * cos_j) / (n_j * cos_i + n_i * cos_j)


def psi_delta_three_phase(
    aoi_deg: float | NDArray,
    wavelength_nm: float,
    thickness_nm: float | NDArray,
    n_film: float | NDArray,
    k_film: float | NDArray,
    n_sub: float,
    k_sub: float,
    n_ambient: float = 1.0,
) -> tuple[NDArray, NDArray]:
    """Forward 3-phase (ambient/film/substrate) model: (Psi, Delta) in degrees.

    Every scalar argument may instead be a numpy array; standard numpy
    broadcasting applies, which is what lets ``fit_film`` evaluate an entire
    (thickness, n_film) grid in one vectorised call, and what lets a caller
    pass an array of angles of incidence for a single (d, n_film, k_film) to
    plot a model curve across a whole AOI series.

    At thickness_nm == 0 this reduces exactly to the bare-substrate (n_sub,
    k_sub) result regardless of the film's own optical constants — a known
    identity of the Airy thin-film formula — which is why fitting a series
    with the film's thickness pinned at 0 is a valid way to sanity-check
    against ``n_k_two_phase``.

    Returns:
        (psi_deg, delta_deg) with delta_deg wrapped to [0, 360).
    """
    theta0 = np.radians(np.asarray(aoi_deg, dtype=float))
    n0 = complex(n_ambient, 0.0)
    n1 = np.asarray(n_film, dtype=float) - 1j * np.asarray(k_film, dtype=float)
    n2 = complex(n_sub, -k_sub)

    sin0 = np.sin(theta0)
    cos0 = np.cos(theta0)
    sin1 = n0 * sin0 / n1
    cos1 = _complex_cos_theta(n1, sin1)
    sin2 = n0 * sin0 / n2
    cos2 = _complex_cos_theta(n2, sin2)

    r_s01 = _fresnel_rs(n0, cos0, n1, cos1)
    r_p01 = _fresnel_rp(n0, cos0, n1, cos1)
    r_s12 = _fresnel_rs(n1, cos1, n2, cos2)
    r_p12 = _fresnel_rp(n1, cos1, n2, cos2)

    beta = 2.0 * np.pi * (np.asarray(thickness_nm, dtype=float) / wavelength_nm) * n1 * cos1
    exp_term = np.exp(-2j * beta)

    r_s = (r_s01 + r_s12 * exp_term) / (1.0 + r_s01 * r_s12 * exp_term)
    r_p = (r_p01 + r_p12 * exp_term) / (1.0 + r_p01 * r_p12 * exp_term)

    rho = r_p / r_s
    psi_deg = np.degrees(np.arctan(np.abs(rho)))
    delta_deg = np.degrees(np.angle(rho)) % 360.0
    return psi_deg, delta_deg


def _fold_delta_deg(delta_deg: NDArray) -> NDArray:
    """Fold a model Delta in [0, 360) to [0, 180] for comparison with a measured Delta.

    RAE only measures cos(Delta), so the measured value is inherently folded
    into [0, 180] (see module docs) — the model must be folded the same way
    before the two are compared.
    """
    return np.where(delta_deg > 180.0, 360.0 - delta_deg, delta_deg)


def _local_minima_branches(
    d_vals: NDArray, mse_along_d: NDArray, n_along_d: NDArray, max_branches: int = 6
) -> list[tuple[float, float, float]]:
    """Find local minima of *mse_along_d* over *d_vals*, sorted best-first."""
    branches: list[tuple[float, float, float]] = []
    n = len(mse_along_d)
    for i in range(1, n - 1):
        if mse_along_d[i] <= mse_along_d[i - 1] and mse_along_d[i] <= mse_along_d[i + 1]:
            if mse_along_d[i] < mse_along_d[i - 1] or mse_along_d[i] < mse_along_d[i + 1]:
                branches.append((float(d_vals[i]), float(n_along_d[i]), float(mse_along_d[i])))
    if n >= 2:
        if mse_along_d[0] <= mse_along_d[1]:
            branches.append((float(d_vals[0]), float(n_along_d[0]), float(mse_along_d[0])))
        if mse_along_d[-1] <= mse_along_d[-2]:
            branches.append((float(d_vals[-1]), float(n_along_d[-1]), float(mse_along_d[-1])))
    branches.sort(key=lambda b: b[2])
    return branches[:max_branches]


def fit_film(
    aoi_deg: Sequence[float],
    psi_deg: Sequence[float],
    delta_deg: Sequence[float],
    *,
    wavelength_nm: float,
    n_sub: float,
    k_sub: float,
    n_ambient: float = 1.0,
    d_range: tuple[float, float] = (0.0, 1000.0),
    n_range: tuple[float, float] = (1.2, 3.0),
    fit_k: bool = False,
    refine_rounds: int = 4,
) -> FilmFit:
    """Fit film thickness (+ optionally k) and index to a (theta, Psi, Delta) series.

    Runs a vectorised coarse-to-fine grid search rather than a nonlinear
    solver: no scipy dependency is required, a few hundred thousand model
    evaluations are milliseconds in numpy, and the coarse grid exposes *all*
    local minima along the thickness axis (see ``FilmFit.branches``) rather
    than silently reporting one possibly-wrong branch.

    Args:
        aoi_deg: Angle of incidence for each completed AOI measurement.
        psi_deg: Measured Psi for each AOI measurement.
        delta_deg: Measured Delta for each AOI measurement, in [0, 180]
            (see module docs on the RAE sign ambiguity).
        wavelength_nm: Illumination wavelength.
        n_sub: Known substrate refractive index at that wavelength.
        k_sub: Known substrate extinction coefficient at that wavelength.
        n_ambient: Ambient refractive index.
        d_range: Search bounds for film thickness, nm.
        n_range: Search bounds for film refractive index.
        fit_k: If True, also search film absorption k_film over [0, 2] on a
            coarse fixed grid (not refined per-round). Leave False for the
            common transparent-film case, which is otherwise well posed.
        refine_rounds: Number of coarse-to-fine grid passes.

    Returns:
        FilmFit with the best (thickness, n_film, k_film), its RMS residual
        in degrees, and the alternative thickness-axis branches found in the
        first (coarsest) pass.

    Raises:
        ValueError: if no AOI points are given.
    """
    aoi = np.asarray(aoi_deg, dtype=float)
    psi_m = np.asarray(psi_deg, dtype=float)
    delta_m = np.asarray(delta_deg, dtype=float)
    n_meas = aoi.size
    if n_meas == 0:
        raise ValueError("fit_film requires at least one AOI point")

    n_free = 3 if fit_k else 2
    dof = max(2 * n_meas - n_free, 1)
    k_vals = np.array([0.0]) if not fit_k else np.linspace(0.0, 2.0, 21)

    d_lo, d_hi = d_range
    n_lo, n_hi = n_range
    n_grid_d, n_grid_n = 150, 90

    branches: list[tuple[float, float, float]] = []
    best_d = best_n = best_k = best_mse = float("nan")

    for round_idx in range(max(refine_rounds, 1)):
        d_vals = np.linspace(d_lo, d_hi, n_grid_d)
        n_vals = np.linspace(n_lo, n_hi, n_grid_n)
        d_grid, n_grid = np.meshgrid(d_vals, n_vals, indexing="ij")

        best_mse_grid = np.full(d_grid.shape, np.inf)
        best_k_grid = np.zeros(d_grid.shape)

        for kf in k_vals:
            mse_grid = np.zeros(d_grid.shape)
            for i in range(n_meas):
                psi_mod, delta_mod = psi_delta_three_phase(
                    float(aoi[i]), wavelength_nm, d_grid, n_grid, kf, n_sub, k_sub, n_ambient
                )
                delta_mod_folded = _fold_delta_deg(delta_mod)
                mse_grid += (psi_mod - psi_m[i]) ** 2 + (delta_mod_folded - delta_m[i]) ** 2
            mse_grid = np.sqrt(mse_grid / dof)
            better = mse_grid < best_mse_grid
            best_mse_grid = np.where(better, mse_grid, best_mse_grid)
            best_k_grid = np.where(better, kf, best_k_grid)

        flat_idx = int(np.argmin(best_mse_grid))
        idx = np.unravel_index(flat_idx, d_grid.shape)
        best_d = float(d_grid[idx])
        best_n = float(n_grid[idx])
        best_k = float(best_k_grid[idx])
        best_mse = float(best_mse_grid[idx])

        if round_idx == 0:
            mse_along_d = best_mse_grid.min(axis=1)
            n_idx_along_d = best_mse_grid.argmin(axis=1)
            branches = _local_minima_branches(d_vals, mse_along_d, n_vals[n_idx_along_d])

        d_step = (d_hi - d_lo) / (n_grid_d - 1)
        n_step = (n_hi - n_lo) / (n_grid_n - 1)
        d_lo = max(d_range[0], best_d - 4 * d_step)
        d_hi = min(d_range[1], best_d + 4 * d_step)
        n_lo = max(n_range[0], best_n - 4 * n_step)
        n_hi = min(n_range[1], best_n + 4 * n_step)

    return FilmFit(
        thickness_nm=best_d, n_film=best_n, k_film=best_k, mse=best_mse, branches=branches
    )
