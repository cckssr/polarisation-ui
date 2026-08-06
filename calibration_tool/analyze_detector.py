"""Detector calibration analysis.

Reads a power-calibration JSON profile (as produced by
``polarisation_ui.core.power_calibration.PowerCalibrationProfile.save``) and
fits a watts-per-volt linear regression for each PD-TIA gain stage present in
the file, reporting slope, intercept, R², residuals, RMSE, and dynamic range.

Usage:
    python analyze_detector.py Det_A.json
    python analyze_detector.py Det_A.json --no-plot
    python analyze_detector.py Det_A.json --save-plot Det_A_analysis.png
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats


@dataclass
class GainAnalysis:
    """Linear-fit results for one PD-TIA gain stage's calibration points."""

    gain_id: str
    voltages: np.ndarray
    powers: np.ndarray
    slope: float  # W/V  (optical power per sensor volt)
    intercept: float  # W    (dark / zero-light power offset)
    r_squared: float
    residuals: np.ndarray
    rmse: float  # W
    max_abs_residual: float  # W
    v_range: tuple[float, float]
    p_range: tuple[float, float]
    dynamic_range_db: float


def _load_points(path: Path) -> dict[str, list[list[float]]]:
    """Extract only the gain->points mapping from the JSON, ignoring all other fields."""
    with path.open() as f:
        data = json.load(f)
    gains_raw: dict = data.get("gains", {})
    return {gain_id: entry["points"] for gain_id, entry in gains_raw.items() if entry.get("points")}


def _analyze_gain(gain_id: str, points: list[list[float]]) -> GainAnalysis:
    """Fit a watts-per-volt linear regression to one gain stage's (V, W) points."""
    arr = np.asarray(points, dtype=float)
    voltages = arr[:, 0]
    powers = arr[:, 1]

    result = stats.linregress(voltages, powers)
    slope = result.slope
    intercept = result.intercept
    r_squared = result.rvalue**2

    fitted = slope * voltages + intercept
    residuals = powers - fitted
    rmse = float(np.sqrt(np.mean(residuals**2)))
    max_abs_residual = float(np.max(np.abs(residuals)))

    v_range = (float(voltages.min()), float(voltages.max()))
    p_range = (float(powers.min()), float(powers.max()))

    p_max = powers.max()
    # Dark power estimate: use the intercept if physically meaningful (>0),
    # otherwise fall back to the minimum measured power.
    dark = max(intercept, powers.min())
    dynamic_range_db = 20 * np.log10(p_max / dark) if dark > 0 else float("inf")

    return GainAnalysis(
        gain_id=gain_id,
        voltages=voltages,
        powers=powers,
        slope=slope,
        intercept=intercept,
        r_squared=r_squared,
        residuals=residuals,
        rmse=rmse,
        max_abs_residual=max_abs_residual,
        v_range=v_range,
        p_range=p_range,
        dynamic_range_db=dynamic_range_db,
    )


def _print_report(results: list[GainAnalysis], source_name: str) -> None:
    """Print a human-readable calibration report to stdout."""
    sep = "=" * 72
    hyphen_sep = "-" * 72

    print(sep)
    print(f"  DETECTOR CALIBRATION ANALYSIS  —  {source_name}")
    print(sep)
    print()

    # Summary table
    col = "{:>6}  {:>6}  {:>12}  {:>12}  {:>8}  {:>10}  {:>10}"
    print(col.format("Gain", "Points", "Slope (W/V)", "Offset (W)", "R²", "RMSE (W)", "DR (dB)"))
    print(hyphen_sep)
    for r in results:
        print(
            col.format(
                r.gain_id,
                len(r.voltages),
                f"{r.slope:.6e}",
                f"{r.intercept:.3e}",
                f"{r.r_squared:.6f}",
                f"{r.rmse:.3e}",
                (f"{r.dynamic_range_db:.1f}" if r.dynamic_range_db != float("inf") else "  inf"),
            )
        )
    print()

    # Per-gain detail
    for r in results:
        print(f"  Gain {r.gain_id}")
        print(f"    Voltage range   : {r.v_range[0]:.4f} V  →  {r.v_range[1]:.4f} V")
        print(f"    Power range     : {r.p_range[0]:.3e} W  →  {r.p_range[1]:.3e} W")
        print(f"    Sensitivity     : {1 / r.slope:.3e} V/W   (= 1/slope)")
        print(f"    Dark offset     : {r.intercept:.3e} W")
        print(f"    Linearity R²    : {r.r_squared:.8f}")
        print(
            f"    RMSE            : {r.rmse:.3e} W  "
            f"({100 * r.rmse / r.p_range[1]:.3f}% of full scale)"
        )
        print(f"    Max residual    : {r.max_abs_residual:.3e} W")
        print(f"    Dynamic range   : {r.dynamic_range_db:.1f} dB")
        print()

    # Cross-gain comparison
    if len(results) > 1:
        ref = results[0]
        print(f"  Cross-gain sensitivity (relative to gain {ref.gain_id})")
        print(hyphen_sep)
        col2 = "{:>6}  {:>14}  {:>10}  {:>10}"
        print(col2.format("Gain", "Sens. (V/W)", "Ratio", "Ratio (dB)"))
        for r in results:
            sens = 1.0 / r.slope
            ratio = r.slope / ref.slope
            ratio_db = 20 * np.log10(ratio)
            print(col2.format(r.gain_id, f"{sens:.4e}", f"{ratio:.4f}", f"{ratio_db:.2f}"))
        print()
        print("  Voltage range overlap between adjacent gains")
        for i in range(len(results) - 1):
            a, b = results[i], results[i + 1]
            overlap_lo = max(a.v_range[0], b.v_range[0])
            overlap_hi = min(a.v_range[1], b.v_range[1])
            if overlap_lo <= overlap_hi:
                print(
                    f"    Gain {a.gain_id} ↔ Gain {b.gain_id}: "
                    f"overlap {overlap_lo:.3f} – {overlap_hi:.3f} V"
                )
            else:
                gap = overlap_lo - overlap_hi
                print(f"    Gain {a.gain_id} ↔ Gain {b.gain_id}: gap of {gap:.3f} V (no overlap)")
        print()

    print(sep)


def _plot(results: list[GainAnalysis], source_name: str, save_path: Path | None) -> None:
    """Render a multi-panel linearity/residual/comparison figure and show or save it."""
    n_gains = len(results)
    colors = plt.cm.tab10(np.linspace(0, 0.9, n_gains))

    fig = plt.figure(figsize=(14, 10))
    fig.suptitle(f"Detector calibration — {source_name}", fontsize=13, fontweight="bold")

    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.35)

    ax_lin = fig.add_subplot(gs[0, 0])  # V vs I (linear)
    ax_log = fig.add_subplot(gs[0, 1])  # V vs I (log current)
    ax_res = fig.add_subplot(gs[0, 2])  # Residuals
    ax_dr = fig.add_subplot(gs[1, 0])  # Dynamic range bar
    ax_r2 = fig.add_subplot(gs[1, 1])  # R² bar
    ax_slope = fig.add_subplot(gs[1, 2])  # Slope comparison

    gain_labels = [f"Gain {r.gain_id}" for r in results]

    for r, color in zip(results, colors, strict=True):
        v_fit = np.linspace(r.v_range[0], r.v_range[1], 200)
        p_fit = r.slope * v_fit + r.intercept

        ax_lin.scatter(
            r.voltages,
            r.powers * 1e6,
            s=18,
            color=color,
            label=f"G{r.gain_id}",
            zorder=3,
        )
        ax_lin.plot(v_fit, p_fit * 1e6, color=color, lw=1.2, alpha=0.7)

        ax_log.scatter(r.voltages, r.powers, s=18, color=color, label=f"G{r.gain_id}", zorder=3)
        ax_log.plot(v_fit, p_fit, color=color, lw=1.2, alpha=0.7)

        ax_res.scatter(
            r.voltages,
            r.residuals * 1e9,
            s=18,
            color=color,
            label=f"G{r.gain_id}",
            zorder=3,
        )
        ax_res.axhline(0, color="gray", lw=0.8, ls="--")

    ax_lin.set_xlabel("Sensor voltage (V)")
    ax_lin.set_ylabel("Power (µW)")
    ax_lin.set_title("Linearity (linear scale)")
    ax_lin.legend(fontsize=8)
    ax_lin.grid(True, alpha=0.3)

    ax_log.set_xlabel("Sensor voltage (V)")
    ax_log.set_ylabel("Power (W)")
    ax_log.set_yscale("log")
    ax_log.set_title("Linearity (log power)")
    ax_log.legend(fontsize=8)
    ax_log.grid(True, alpha=0.3, which="both")

    ax_res.set_xlabel("Sensor voltage (V)")
    ax_res.set_ylabel("Residual (nW)")
    ax_res.set_title("Fit residuals")
    ax_res.legend(fontsize=8)
    ax_res.grid(True, alpha=0.3)

    # Bar charts
    x = np.arange(n_gains)
    dr_vals = [r.dynamic_range_db for r in results]
    ax_dr.bar(x, dr_vals, color=colors)
    ax_dr.set_xticks(x)
    ax_dr.set_xticklabels(gain_labels, fontsize=8)
    ax_dr.set_ylabel("dB")
    ax_dr.set_title("Dynamic range per gain")
    ax_dr.grid(True, axis="y", alpha=0.3)
    for xi, val in zip(x, dr_vals, strict=True):
        ax_dr.text(xi, val + 0.5, f"{val:.1f}", ha="center", va="bottom", fontsize=8)

    r2_vals = [r.r_squared for r in results]
    ax_r2.bar(x, r2_vals, color=colors)
    ax_r2.set_xticks(x)
    ax_r2.set_xticklabels(gain_labels, fontsize=8)
    ax_r2.set_ylabel("R²")
    ax_r2.set_ylim(max(0, min(r2_vals) - 1e-4), 1 + 1e-6)
    ax_r2.set_title("Linearity R² per gain")
    ax_r2.grid(True, axis="y", alpha=0.3)
    for xi, val in zip(x, r2_vals, strict=True):
        ax_r2.text(
            xi,
            val - (1 - min(r2_vals)) * 0.08,
            f"{val:.6f}",
            ha="center",
            va="top",
            fontsize=7,
        )

    slope_vals = [r.slope * 1e6 for r in results]  # µW/V for readability
    ax_slope.bar(x, slope_vals, color=colors)
    ax_slope.set_xticks(x)
    ax_slope.set_xticklabels(gain_labels, fontsize=8)
    ax_slope.set_ylabel("Slope (µW/V)")
    ax_slope.set_title("Sensitivity (slope) per gain")
    ax_slope.grid(True, axis="y", alpha=0.3)
    for xi, val in zip(x, slope_vals, strict=True):
        ax_slope.text(xi, val * 1.01, f"{val:.2f}", ha="center", va="bottom", fontsize=8)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Plot saved to: {save_path}")
    else:
        plt.show()


def main() -> None:
    """Parse CLI arguments, analyze the given detector JSON, and report/plot the results."""
    parser = argparse.ArgumentParser(description="Analyse detector calibration JSON")
    parser.add_argument("file", type=Path, help="Path to detector JSON file")
    parser.add_argument("--no-plot", action="store_true", help="Skip plotting")
    parser.add_argument(
        "--save-plot",
        type=Path,
        metavar="PATH",
        help="Save plot to file instead of showing it",
    )
    args = parser.parse_args()

    if not args.file.exists():
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    gains_points = _load_points(args.file)
    if not gains_points:
        print("No calibration points found in file.", file=sys.stderr)
        sys.exit(1)

    results = [
        _analyze_gain(gid, pts)
        for gid, pts in sorted(gains_points.items(), key=lambda kv: int(kv[0]))
        if pts
    ]

    _print_report(results, args.file.name)

    if not args.no_plot:
        _plot(results, args.file.name, args.save_plot)


if __name__ == "__main__":
    main()
