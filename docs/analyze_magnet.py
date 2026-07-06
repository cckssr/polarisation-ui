#!/usr/bin/env python3
"""Magnet calibration and symmetry analysis.

The script supports one angle column and multiple magnet columns in the same
CSV file. Each magnet column is analysed independently, while the measurement
uncertainties are applied to every series:

- angle reading: +/- 0.3 deg
- teslameter reading: +/- 0.1 mT
"""

import argparse
import csv
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.projections.polar import PolarAxes
from scipy.optimize import curve_fit


@dataclass
class Measurement:
    """Single measurement point."""

    angle: float  # degrees
    field: float  # mT
    field_uncertainty: float = 0.1


@dataclass
class MagnetSeries:
    """One magnet measurement series from a CSV column."""

    name: str
    measurements: list[Measurement]


@dataclass
class AnalysisResults:
    """Results of magnet analysis for one series."""

    series_name: str
    point_count: int
    symmetry_score: float  # 0-1, where 1 is perfect
    north_pole_strength: float  # mT
    south_pole_strength: float  # mT
    pole_balance: float  # ratio, ideally 1.0
    model_fit_r2: float  # R² goodness of fit
    fit_amplitude: float  # mT
    fit_phase: float  # radians
    is_calibrated: bool  # Based on pole balance
    is_symmetric: bool  # Based on symmetry score
    residuals_within_tolerance: bool  # All residuals within measurement error
    mean_combined_uncertainty: float  # mT, propagated from angle and field error
    max_residual: float  # mT


class MagnetAnalyzer:
    """Analyzes diametral magnet calibration and symmetry."""

    ANGLE_UNCERTAINTY = 0.3  # degrees
    FIELD_UNCERTAINTY = 0.1  # mT
    SYMMETRY_THRESHOLD = 0.95  # 95% symmetry required
    BALANCE_THRESHOLD = 0.10  # 10% tolerance on pole strength ratio
    FIT_THRESHOLD = 0.98  # R² > 0.98 considered good fit
    OPPOSITE_ANGLE_TOLERANCE = 10.0  # degrees

    ANGLE_COLUMN_ALIASES = (
        "angle",
        "angle (degree)",
        "angle (degrees)",
        "angle_deg",
        "angle degree",
    )
    UNCERTAINTY_SUFFIXES = (
        " uncertainty (mT)",
        " uncertainty",
        " sigma (mT)",
        " sigma",
        " error (mT)",
        " error",
    )

    def __init__(self, csv_path: str):
        """Load and parse measurement data."""
        self.series = self._load_csv(csv_path)
        if not self.series:
            raise ValueError("No valid data loaded from CSV")

    def _load_csv(self, csv_path: str) -> list[MagnetSeries]:
        """Load one angle column and multiple magnet columns from CSV."""
        with open(csv_path, encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                return []

            fieldnames = [name.strip() for name in reader.fieldnames if name]
            angle_column = self._find_angle_column(fieldnames)
            if angle_column is None:
                raise ValueError(
                    "Could not find an angle column. Expected one of: "
                    f"{', '.join(self.ANGLE_COLUMN_ALIASES)}"
                )

            series_columns = [
                column
                for column in fieldnames
                if column != angle_column and not self._is_uncertainty_column(column)
            ]
            if not series_columns:
                raise ValueError("CSV must contain at least one magnet measurement column.")

            parsed_rows: list[dict[str, str]] = []
            for row in reader:
                normalized_row = {
                    (key.strip() if key else ""): (value.strip() if value else "")
                    for key, value in row.items()
                }
                if normalized_row.get(angle_column, ""):
                    parsed_rows.append(normalized_row)

        series_list: list[MagnetSeries] = []
        for column in series_columns:
            measurements: list[Measurement] = []
            uncertainty_column = self._find_uncertainty_column(column, fieldnames)
            for row in parsed_rows:
                angle_text = row.get(angle_column, "")
                field_text = row.get(column, "")
                if not angle_text or not field_text:
                    continue

                angle = float(angle_text)
                field = float(field_text)
                field_uncertainty = self._parse_optional_float(
                    row.get(uncertainty_column, "") if uncertainty_column else ""
                )
                measurements.append(
                    Measurement(
                        angle=angle,
                        field=field,
                        field_uncertainty=(
                            field_uncertainty
                            if field_uncertainty is not None
                            else self.FIELD_UNCERTAINTY
                        ),
                    )
                )

            if measurements:
                series_list.append(MagnetSeries(name=column, measurements=measurements))

        return series_list

    def _find_angle_column(self, fieldnames: list[str]) -> str | None:
        """Return the first column that looks like an angle column."""
        normalized = {name.lower().strip(): name for name in fieldnames}
        for alias in self.ANGLE_COLUMN_ALIASES:
            if alias in normalized:
                return normalized[alias]
        return None

    def _is_uncertainty_column(self, column_name: str) -> bool:
        """Return True when the column stores uncertainty values."""
        lower_name = column_name.lower()
        return any(suffix.strip() in lower_name for suffix in self.UNCERTAINTY_SUFFIXES)

    def _find_uncertainty_column(self, data_column: str, fieldnames: list[str]) -> str | None:
        """Find a matching uncertainty column for one magnet series."""
        candidates = [f"{data_column}{suffix}" for suffix in self.UNCERTAINTY_SUFFIXES]
        normalized = {name.lower().strip(): name for name in fieldnames}
        for candidate in candidates:
            if candidate.lower().strip() in normalized:
                return normalized[candidate.lower().strip()]
        return None

    def _parse_optional_float(self, value: str) -> float | None:
        """Parse a numeric cell if it exists."""
        if value == "":
            return None
        return float(value)

    def _diametral_model(self, angle: float, amplitude: float, phase: float) -> float:
        """Ideal sinusoidal model for a diametral magnet."""
        angle_rad = math.radians(angle)
        return amplitude * math.sin(angle_rad + phase)

    def analyze(self) -> list[AnalysisResults]:
        """Perform complete analysis for every magnet series."""
        return [self._analyze_series(series) for series in self.series]

    def _analyze_series(self, series: MagnetSeries) -> AnalysisResults:
        """Analyse one magnet series from the CSV."""
        angles = np.array([measurement.angle for measurement in series.measurements])
        fields = np.array([measurement.field for measurement in series.measurements])
        field_uncertainties = np.array(
            [measurement.field_uncertainty for measurement in series.measurements]
        )

        # 1. Fit sinusoidal model
        fit_result = self._fit_model(angles, fields, field_uncertainties)

        # 2. Calculate symmetry
        symmetry, symmetry_residuals = self._check_symmetry(
            angles,
            fields,
            field_uncertainties,
        )

        # 3. Calculate pole balance
        north_strength, south_strength, balance = self._check_pole_balance(fields)

        # 4. Check residuals vs uncertainty
        residuals_ok = self._check_residual_tolerance(
            angles,
            fields,
            field_uncertainties,
            fit_result["amplitude"],
            fit_result["phase"],
        )

        combined_uncertainty = fit_result["combined_uncertainties"]
        max_residual = float(np.max(np.abs(fit_result["residuals"])))

        # Determine calibration and symmetry status
        is_calibrated = abs(balance - 1.0) < self.BALANCE_THRESHOLD
        is_symmetric = symmetry > self.SYMMETRY_THRESHOLD

        return AnalysisResults(
            series_name=series.name,
            point_count=len(series.measurements),
            symmetry_score=symmetry,
            north_pole_strength=abs(north_strength),
            south_pole_strength=abs(south_strength),
            pole_balance=balance,
            model_fit_r2=fit_result["r2"],
            fit_amplitude=fit_result["amplitude"],
            fit_phase=fit_result["phase"],
            is_calibrated=is_calibrated,
            is_symmetric=is_symmetric,
            residuals_within_tolerance=residuals_ok,
            mean_combined_uncertainty=float(np.mean(combined_uncertainty)),
            max_residual=max(max_residual, float(np.max(np.abs(symmetry_residuals)))),
        )

    def _fit_model(
        self, angles: np.ndarray, fields: np.ndarray, field_uncertainties: np.ndarray
    ) -> dict:
        """Fit a sinusoidal model A*sin(θ + φ) with uncertainty weighting."""

        def model(angle: np.ndarray, amp: float, phase: float) -> np.ndarray:
            return amp * np.sin(np.radians(angle) + phase)

        try:
            amplitude_guess = (np.max(fields) - np.min(fields)) / 2
            phase_guess = 0

            sigma = np.maximum(field_uncertainties, 1e-6)
            popt, _ = curve_fit(
                model,
                angles,
                fields,
                p0=[amplitude_guess, phase_guess],
                sigma=sigma,
                absolute_sigma=True,
                maxfev=5000,
            )

            # Refine the fit once with the propagated angle uncertainty included.
            combined_sigma = self._combined_uncertainty(
                angles,
                field_uncertainties,
                popt[0],
                popt[1],
            )
            popt, _ = curve_fit(
                model,
                angles,
                fields,
                p0=popt,
                sigma=np.maximum(combined_sigma, 1e-6),
                absolute_sigma=True,
                maxfev=5000,
            )

            y_pred = model(angles, *popt)
            ss_res = np.sum((fields - y_pred) ** 2)
            ss_tot = np.sum((fields - np.mean(fields)) ** 2)
            r2 = 1 - (ss_res / ss_tot)
            residuals = fields - y_pred

            return {
                "amplitude": popt[0],
                "phase": popt[1],
                "r2": r2,
                "residuals": residuals,
                "combined_uncertainties": self._combined_uncertainty(
                    angles,
                    field_uncertainties,
                    popt[0],
                    popt[1],
                ),
            }
        except (RuntimeError, ValueError, TypeError, np.linalg.LinAlgError) as e:
            print(f"Warning: Model fitting failed: {e}")
            return {
                "amplitude": 0,
                "phase": 0,
                "r2": 0,
                "residuals": np.array([]),
                "combined_uncertainties": np.array([]),
            }

    def _combined_uncertainty(
        self,
        angles: np.ndarray,
        field_uncertainties: np.ndarray,
        amplitude: float,
        phase: float,
    ) -> np.ndarray:
        """Propagate angle and field uncertainties into the field axis."""
        angle_term = np.abs(
            amplitude * np.cos(np.radians(angles) + phase) * np.radians(self.ANGLE_UNCERTAINTY)
        )
        return np.sqrt(field_uncertainties**2 + angle_term**2)

    def _check_symmetry(
        self,
        angles: np.ndarray,
        fields: np.ndarray,
        field_uncertainties: np.ndarray,
    ) -> tuple[float, np.ndarray]:
        """Check symmetry by comparing opposite poles (180° apart).

        Returns a score in [0, 1] and the signed symmetry residuals.
        """
        pair_scores = []
        pair_residuals = []
        field_scale = max(float(np.max(np.abs(fields))), 1e-6)

        for i, angle in enumerate(angles):
            opposite_angle = (angle + 180) % 360
            diffs = np.abs(angles - opposite_angle)
            j = np.argmin(diffs)

            if diffs[j] < self.OPPOSITE_ANGLE_TOLERANCE and i < j:
                pair_difference = fields[i] + fields[j]
                pair_uncertainty = math.sqrt(
                    field_uncertainties[i] ** 2 + field_uncertainties[j] ** 2
                )
                if pair_uncertainty <= 0:
                    continue

                normalized_error = abs(pair_difference) / (field_scale + 3.0 * pair_uncertainty)
                pair_scores.append(max(0.0, 1.0 - normalized_error))
                pair_residuals.append(pair_difference / field_scale)

        if not pair_scores:
            return 0.0, np.array([])

        return float(np.mean(pair_scores)), np.array(pair_residuals)

    def _check_pole_balance(self, fields: np.ndarray) -> tuple[float, float, float]:
        """Calculate north and south pole strengths and their balance ratio.

        Returns: (north_strength, south_strength, balance_ratio)
        """
        # Positive fields = north pole, negative = south pole
        north_fields = fields[fields > 0]
        south_fields = np.abs(fields[fields < 0])

        north_strength = float(np.mean(north_fields)) if len(north_fields) > 0 else 0
        south_strength = float(np.mean(south_fields)) if len(south_fields) > 0 else 0

        if north_strength > 0 and south_strength > 0:
            balance_ratio = min(north_strength, south_strength) / max(
                north_strength, south_strength
            )
        else:
            balance_ratio = 0.0

        return north_strength, south_strength, balance_ratio

    def _check_residual_tolerance(
        self,
        angles: np.ndarray,
        fields: np.ndarray,
        field_uncertainties: np.ndarray,
        amplitude: float,
        phase: float,
    ) -> bool:
        """Check if model residuals are within measurement tolerance."""

        def model(angle):
            return amplitude * np.sin(np.radians(angle) + phase)

        y_pred = np.array([model(a) for a in angles])
        residuals = np.abs(fields - y_pred)

        combined_tolerance = self._combined_uncertainty(
            angles,
            field_uncertainties,
            amplitude,
            phase,
        )
        residuals_ok = np.all(residuals <= combined_tolerance * 2.0)

        return bool(residuals_ok)

    def plot_analysis(
        self,
        results: list[AnalysisResults],
        output_dir: Path | None = None,
    ) -> None:
        """Generate one detailed plot per magnet series."""
        output_dir = output_dir or Path.cwd()
        output_dir.mkdir(parents=True, exist_ok=True)

        for series, result in zip(self.series, results, strict=True):
            angles = np.array([m.angle for m in series.measurements])
            fields = np.array([m.field for m in series.measurements])
            field_uncertainties = np.array([m.field_uncertainty for m in series.measurements])

            fit = self._fit_model(angles, fields, field_uncertainties)
            angle_smooth = np.linspace(0, 360, 720)
            y_pred = fit["amplitude"] * np.sin(np.radians(angles) + fit["phase"])
            residuals = fields - y_pred
            fields_smooth = fit["amplitude"] * np.sin(np.radians(angle_smooth) + fit["phase"])
            combined_uncertainty = self._combined_uncertainty(
                angles,
                field_uncertainties,
                fit["amplitude"],
                fit["phase"],
            )
            mean_combined_uncertainty = float(np.mean(combined_uncertainty))

            figure = plt.figure(figsize=(18, 11))
            grid = figure.add_gridspec(2, 3, height_ratios=[1, 1], width_ratios=[1, 1.2, 1])

            ax_raw = figure.add_subplot(grid[0, 0])
            ax_summary = figure.add_subplot(grid[1, 0])

            ax_sym = figure.add_subplot(grid[0, 1])
            ax_residuals = figure.add_subplot(grid[1, 1])

            ax_polar_raw = cast(PolarAxes, figure.add_subplot(grid[0, 2], projection="polar"))
            ax_polar_residuals = cast(PolarAxes, figure.add_subplot(grid[1, 2], projection="polar"))

            ax_raw.errorbar(
                angles,
                fields,
                xerr=self.ANGLE_UNCERTAINTY,
                yerr=field_uncertainties,
                fmt="o",
                capsize=3,
                label="Measurements",
                alpha=0.85,
                color="blue",
            )
            ax_raw.plot(angle_smooth, fields_smooth, "r-", label="Model fit", linewidth=2)
            ax_raw.fill_between(
                angle_smooth,
                fields_smooth - mean_combined_uncertainty,
                fields_smooth + mean_combined_uncertainty,
                color="red",
                alpha=0.12,
                linewidth=0,
                label="Fit uncertainty band",
            )
            ax_raw.axhline(0.0, color="k", linestyle="--", alpha=0.3)
            ax_raw.set_xlabel("Angle (degrees)")
            ax_raw.set_ylabel("Field strength (mT)")
            ax_raw.set_title(f"{result.series_name}: field vs angle")
            ax_raw.legend()
            ax_raw.grid(True, alpha=0.3)

            opposite_fields = []
            same_fields = []
            same_uncertainties = []
            opposite_uncertainties = []
            for index, angle in enumerate(angles):
                opposite_angle = (angle + 180) % 360
                diffs = np.abs(angles - opposite_angle)
                if np.min(diffs) < self.OPPOSITE_ANGLE_TOLERANCE:
                    j = int(np.argmin(diffs))
                    same_fields.append(fields[index])
                    opposite_fields.append(-fields[j])
                    same_uncertainties.append(field_uncertainties[index])
                    opposite_uncertainties.append(field_uncertainties[j])

            if opposite_fields:
                ax_sym.errorbar(
                    same_fields,
                    opposite_fields,
                    xerr=same_uncertainties,
                    yerr=opposite_uncertainties,
                    fmt="o",
                    capsize=3,
                    alpha=0.85,
                    color="green",
                    label="Opposite pairs",
                )
                max_val = max(
                    float(np.max(np.abs(fields))),
                    float(np.max(np.abs(opposite_fields))),
                )
                ax_sym.plot(
                    [-max_val, max_val],
                    [-max_val, max_val],
                    "r--",
                    label="Perfect symmetry",
                )
            ax_sym.set_xlabel("Field at angle θ (mT)")
            ax_sym.set_ylabel("Expected field at θ + 180° (mT)")
            ax_sym.set_title("Symmetry check")
            ax_sym.legend()
            ax_sym.set_xlim(-60, 60)
            ax_sym.set_ylim(-60, 60)
            ax_sym.grid(True, alpha=0.3)

            ax_residuals.errorbar(
                angles,
                residuals,
                yerr=combined_uncertainty,
                fmt="o",
                capsize=3,
                alpha=0.8,
                color="orange",
                label="Residuals",
            )
            ax_residuals.axhline(0.0, color="k", linestyle="-", alpha=0.5)
            ax_residuals.axhline(
                float(mean_combined_uncertainty * 2.0),
                color="r",
                linestyle="--",
                label="~2σ combined uncertainty",
            )
            ax_residuals.axhline(
                float(-mean_combined_uncertainty * 2.0),
                color="r",
                linestyle="--",
            )
            ax_residuals.set_xlabel("Angle (degrees)")
            ax_residuals.set_ylabel("Residual (mT)")
            ax_residuals.set_title(f"Model residuals (R² = {fit['r2']:.4f})")
            ax_residuals.legend(loc="upper right")
            ax_residuals.grid(True, alpha=0.3)

            # Find angle at minimum field strength
            min_idx = int(np.argmin(np.abs(fields)))
            theta_min = float(angles[min_idx])
            # Calculate rotation so minimum points downward (South/270°)
            rotation_deg = (270.0 - theta_min) % 360.0

            # Rotate all angles and smooth curve
            rotated_angles = (angles + rotation_deg) % 360.0
            rotated_smooth = (angle_smooth + rotation_deg) % 360.0

            polar_angles = np.radians(rotated_angles)
            ax_polar_raw.errorbar(
                polar_angles,
                fields,
                yerr=field_uncertainties,
                xerr=np.radians(self.ANGLE_UNCERTAINTY),
                fmt="o",
                capsize=3,
                alpha=0.75,
                color="purple",
                label="Raw data",
            )
            polar_smooth_rad = np.radians(rotated_smooth)
            ax_polar_raw.plot(
                polar_smooth_rad,
                fit["amplitude"] * np.sin(np.radians(angle_smooth) + fit["phase"]),
                color="crimson",
                linewidth=2,
                label="Sinusoidal fit",
            )
            ax_polar_raw.set_theta_zero_location("N")
            ax_polar_raw.set_theta_direction(-1)
            # Set custom theta labels showing original angles
            original_angles = np.array([0, 90, 180, 270])
            rotated_tick_angles = (original_angles + rotation_deg) % 360.0
            ax_polar_raw.set_thetagrids(
                rotated_tick_angles, labels=[f"{int(a)}°" for a in original_angles]
            )
            ax_polar_raw.set_title("Polar: raw data and fit")
            ax_polar_raw.legend(loc="upper right", bbox_to_anchor=(1.2, 1.15))

            ax_polar_residuals.errorbar(
                polar_angles,
                residuals,
                yerr=combined_uncertainty,
                xerr=np.radians(self.ANGLE_UNCERTAINTY),
                fmt="o",
                capsize=3,
                alpha=0.8,
                color="orange",
                label="Residuals",
            )
            ax_polar_residuals.axhline(0.0, color="k", linestyle="-", linewidth=0.5, alpha=0.5)
            ax_polar_residuals.set_theta_zero_location("N")
            ax_polar_residuals.set_theta_direction(-1)
            # Set custom theta labels showing original angles
            ax_polar_residuals.set_thetagrids(
                rotated_tick_angles, labels=[f"{int(a)}°" for a in original_angles]
            )
            ax_polar_residuals.set_title("Polar: residual distribution")
            ax_polar_residuals.legend(loc="upper right", bbox_to_anchor=(1.2, 1.15))

            ax_summary.axis("off")
            symmetry_text = (
                f"{result.symmetry_score:.1%}\nmax symmetry residual: {result.max_residual:.2f} mT"
            )
            overall_text = (
                "CALIBRATED & SYMMETRIC"
                if result.is_calibrated and result.is_symmetric
                else "REQUIRES ADJUSTMENT"
            )
            summary_text = f"""
SERIES: {result.series_name}

Points: {result.point_count}
Angle uncertainty: ±{self.ANGLE_UNCERTAINTY:.1f}°
Field uncertainty: ±{self.FIELD_UNCERTAINTY:.1f} mT

Symmetry score: {symmetry_text}
  → {"SYMMETRIC" if result.is_symmetric else "ASYMMETRIC"}

Pole balance: {result.pole_balance:.3f}
  → North: {result.north_pole_strength:.1f} mT
  → South: {result.south_pole_strength:.1f} mT
  → {"BALANCED" if result.is_calibrated else "UNBALANCED"}

Fit R²: {result.model_fit_r2:.4f}
  → Amplitude: {result.fit_amplitude:.1f} mT
  → Max residual: {result.max_residual:.2f} mT
  → Mean combined uncertainty: {result.mean_combined_uncertainty:.2f} mT

Residuals within tolerance:
  → {"YES" if result.residuals_within_tolerance else "NO"}

Overall:
  → {overall_text}
            """
            ax_summary.text(
                0.02,
                0.5,
                summary_text.strip(),
                fontsize=11,
                family="monospace",
                verticalalignment="center",
            )

            figure.tight_layout()
            output_path = output_dir / f"{self._slugify(result.series_name)}_analysis.png"
            figure.savefig(output_path, dpi=150, bbox_inches="tight")
            plt.close(figure)
            print(f"Plot saved to {output_path}")

    def _slugify(self, text: str) -> str:
        """Create a filesystem-friendly name from a column label."""
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip()).strip("_")
        return slug.lower() or "magnet"


def main():
    """Main analysis routine."""
    parser = argparse.ArgumentParser(
        description="Analyse magnet symmetry and calibration from a CSV file."
    )
    parser.add_argument(
        "csv",
        nargs="?",
        default=str(Path(__file__).parent / "magnet_strength.csv"),
        help="CSV file with one angle column and one or more magnet columns.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for generated plots. Defaults to the CSV folder.",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)

    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        return

    print("=" * 70)
    print("DIAMETRAL MAGNET CALIBRATION & SYMMETRY ANALYSIS")
    print("=" * 70)
    print(f"\nAnalyzing: {csv_path}")
    print(f"Angle uncertainty: ±{MagnetAnalyzer.ANGLE_UNCERTAINTY}°")
    print(f"Field uncertainty: ±{MagnetAnalyzer.FIELD_UNCERTAINTY} mT")
    print()

    analyzer = MagnetAnalyzer(str(csv_path))
    results = analyzer.analyze()

    for result in results:
        print("-" * 70)
        print(f"Series: {result.series_name}")
        print(f"Points: {result.point_count}")
        print(f"Symmetry score: {result.symmetry_score:.1%}")
        print(f"  → Threshold: {MagnetAnalyzer.SYMMETRY_THRESHOLD:.0%}")
        print(f"  → Status: {'✓ SYMMETRIC' if result.is_symmetric else '✗ ASYMMETRIC'}")
        print()

        print(f"Pole strength balance: {result.pole_balance:.3f}")
        print(f"  → North pole (positive): {result.north_pole_strength:.2f} mT")
        print(f"  → South pole (negative): {result.south_pole_strength:.2f} mT")
        print(
            f"  → Difference: {abs(result.north_pole_strength - result.south_pole_strength):.2f} mT"
        )
        print(f"  → Threshold: {MagnetAnalyzer.BALANCE_THRESHOLD:.1%} imbalance tolerance")
        print(f"  → Status: {'✓ BALANCED' if result.is_calibrated else '✗ UNBALANCED'}")
        print()

        print(f"Model fit (R²): {result.model_fit_r2:.4f}")
        print(f"  → Threshold: {MagnetAnalyzer.FIT_THRESHOLD:.2f}")
        fit_status = (
            "✓ GOOD FIT" if result.model_fit_r2 > MagnetAnalyzer.FIT_THRESHOLD else "✗ POOR FIT"
        )
        print(f"  → Status: {fit_status}")
        print(f"  → Amplitude: {result.fit_amplitude:.2f} mT")
        print(f"  → Max residual: {result.max_residual:.2f} mT")
        print(f"  → Mean combined uncertainty: {result.mean_combined_uncertainty:.2f} mT")
        print()

        residuals_status = (
            "✓ Within measurement tolerance"
            if result.residuals_within_tolerance
            else "✗ Exceed measurement tolerance"
        )
        print(f"Residuals: {residuals_status}")
        print()

        print("Final verdict")
        if result.is_calibrated and result.is_symmetric and result.model_fit_r2 > 0.95:
            print("  ✓ Magnet is well calibrated and symmetric")
        elif result.is_symmetric and result.model_fit_r2 > 0.95:
            print("  ⚠ Symmetric and good fit, but poles are unbalanced")
        elif result.is_calibrated and result.model_fit_r2 > 0.95:
            print("  ⚠ Balanced poles, but shows asymmetry")
        else:
            print("  ✗ Magnet requires adjustment")
            if not result.is_symmetric:
                print(f"    → Asymmetry detected (score: {result.symmetry_score:.1%})")
            if not result.is_calibrated:
                print(f"    → Pole imbalance detected (ratio: {result.pole_balance:.3f})")
            if result.model_fit_r2 < 0.95:
                print(f"    → Poor sinusoidal fit (R²: {result.model_fit_r2:.4f})")

    print("-" * 70)

    output_dir = Path(args.output_dir) if args.output_dir else csv_path.parent
    analyzer.plot_analysis(results, output_dir=output_dir)
