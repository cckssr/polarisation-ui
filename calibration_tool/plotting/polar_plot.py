"""
Calibration Plotting Module.

Creates visualization of encoder calibration data:
- Polar plot showing error magnitude vs. angle
- Cartesian plot of error vs. reference angle
- Fitted harmonic components
"""

import math
from typing import Optional, Tuple, List
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from calibration.measurement import CalibrationRun
from calibration.analysis import CalibrationAnalysis, CalibrationResult


class CalibrationPlotter:
    """Creates visualizations for encoder calibration data.

    Main plots:
        1. Polar plot: Shows error magnitude as radius at each angle.
           Good for seeing overall error pattern and asymmetry.

        2. Error vs Angle: Cartesian plot of error over full rotation.
           Good for seeing sinusoidal components.

        3. Combined analysis: Both plots with fitted curves.
    """

    def __init__(
        self, run: CalibrationRun, analysis: Optional[CalibrationAnalysis] = None
    ):
        """
        Initialize plotter with calibration data.

        Args:
            run: CalibrationRun with measurement data
            analysis: Optional CalibrationAnalysis (created if None)
        """
        self.run = run
        self.analysis = analysis or CalibrationAnalysis(run)
        self._result: Optional[CalibrationResult] = None

    def _ensure_analyzed(self) -> CalibrationResult:
        """Ensure analysis has been performed."""
        if self._result is None:
            self._result = self.analysis.analyze()
        return self._result

    def plot_polar(
        self,
        ax: Optional[Axes] = None,
        show_fit: bool = True,
        title: str = "Encoder Error (Polar)",
    ) -> Axes:
        """
        Create polar plot of error vs angle.

        The radius represents error magnitude, showing where
        the encoder has the largest deviations.

        Args:
            ax: Optional matplotlib axes (created if None)
            show_fit: Whether to show fitted curve
            title: Plot title

        Returns:
            Matplotlib axes with plot
        """
        result = self._ensure_analyzed()

        # Create polar axes if needed
        if ax is None:
            fig = plt.figure(figsize=(8, 8))
            ax = fig.add_subplot(111, projection="polar")

        # Get data
        angles_deg = self.run.get_reference_angles()
        errors = self.run.get_errors()
        angles_rad = [math.radians(a) for a in angles_deg]

        # Plot measured data
        ax.scatter(angles_rad, errors, c="blue", alpha=0.6, s=10, label="Measured")

        # Plot fitted curve
        if show_fit:
            fit_angles = np.linspace(0, 2 * np.pi, 360)
            fit_errors = []
            for a in fit_angles:
                a_deg = np.rad2deg(a)
                fit_errors.append(self.analysis.get_error_at_angle(a_deg))
            ax.plot(fit_angles, fit_errors, "r-", linewidth=2, label="Fitted")

        # Mark the direction of maximum error
        max_angle_rad = math.radians(result.phase_1x)
        max_error = result.amplitude_1x
        ax.annotate(
            "",
            xy=(max_angle_rad, max_error),
            xytext=(max_angle_rad, 0),
            arrowprops=dict(arrowstyle="->", color="green", lw=2),
        )

        # Mark recommended offset direction
        offset_rad = math.radians(result.offset_direction)
        ax.annotate(
            "Move\nmagnet",
            xy=(offset_rad, max(abs(min(errors)), max(errors)) * 0.7),
            fontsize=10,
            color="green",
            ha="center",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )

        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.legend(loc="upper right", bbox_to_anchor=(1.1, 1.1))

        # Add grid and adjust
        ax.grid(True, alpha=0.3)
        ax.set_theta_zero_location("N")  # 0° at top
        ax.set_theta_direction(-1)  # Clockwise

        return ax

    def plot_error_vs_angle(
        self,
        ax: Optional[Axes] = None,
        show_fit: bool = True,
        show_components: bool = True,
        title: str = "Error vs Reference Angle",
    ) -> Axes:
        """
        Create Cartesian plot of error vs reference angle.

        Args:
            ax: Optional matplotlib axes (created if None)
            show_fit: Whether to show fitted curve
            show_components: Whether to show individual harmonic components
            title: Plot title

        Returns:
            Matplotlib axes with plot
        """
        result = self._ensure_analyzed()

        # Create axes if needed
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 6))

        # Get data
        angles_deg = self.run.get_reference_angles()
        errors = self.run.get_errors()

        # Sort by angle for clean line plots
        sorted_idx = np.argsort(angles_deg)
        angles_sorted = np.array(angles_deg)[sorted_idx]
        errors_sorted = np.array(errors)[sorted_idx]

        # Plot measured data
        ax.scatter(angles_deg, errors, c="blue", alpha=0.5, s=15, label="Measured")

        if show_fit:
            # Plot fitted total
            fit_angles = np.linspace(0, 360, 360)
            fit_errors = [self.analysis.get_error_at_angle(a) for a in fit_angles]
            ax.plot(fit_angles, fit_errors, "r-", linewidth=2, label="Fitted (total)")

        if show_components:
            fit_angles = np.linspace(0, 360, 360)
            fit_angles_rad = np.deg2rad(fit_angles)

            # 1x component
            comp_1x = result.amplitude_1x * np.sin(
                fit_angles_rad + np.deg2rad(result.phase_1x)
            )
            ax.plot(
                fit_angles,
                comp_1x + result.mean_error,
                "g--",
                linewidth=1.5,
                alpha=0.7,
                label=f"1x component ({result.amplitude_1x:.2f}°)",
            )

            # 2x component
            comp_2x = result.amplitude_2x * np.sin(
                2 * fit_angles_rad + np.deg2rad(result.phase_2x)
            )
            ax.plot(
                fit_angles,
                comp_2x + result.mean_error,
                "m--",
                linewidth=1.5,
                alpha=0.7,
                label=f"2x component ({result.amplitude_2x:.2f}°)",
            )

        # Zero line
        ax.axhline(y=0, color="k", linestyle="-", linewidth=0.5, alpha=0.5)

        # Mean error line
        ax.axhline(
            y=result.mean_error,
            color="orange",
            linestyle=":",
            linewidth=1.5,
            alpha=0.7,
            label=f"Mean ({result.mean_error:.3f}°)",
        )

        ax.set_xlabel("Reference Angle (°)", fontsize=12)
        ax.set_ylabel("Error (°)", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.legend(loc="upper right")
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 360)

        return ax

    def plot_combined(
        self,
        title: str = "Encoder Calibration Analysis",
        figsize: Tuple[int, int] = (16, 8),
    ) -> Figure:
        """
        Create combined figure with polar and Cartesian plots.

        Args:
            title: Overall figure title
            figsize: Figure size (width, height)

        Returns:
            Matplotlib Figure with both plots
        """
        result = self._ensure_analyzed()

        fig = plt.figure(figsize=figsize)
        fig.suptitle(title, fontsize=16, fontweight="bold")

        # Polar plot on left
        ax1 = fig.add_subplot(121, projection="polar")
        self.plot_polar(ax=ax1, title="Error Pattern (Polar)")

        # Cartesian plot on right
        ax2 = fig.add_subplot(122)
        self.plot_error_vs_angle(ax=ax2, title="Error vs Angle")

        # Add analysis summary as text
        summary_text = (
            f"Analysis Summary:\n"
            f"  1x amplitude: {result.amplitude_1x:.3f}° (eccentricity)\n"
            f"  2x amplitude: {result.amplitude_2x:.3f}° (ellipticity)\n"
            f"  Recommended: Move magnet toward {result.offset_direction:.1f}°\n"
            f"  Assessment: {result.offset_magnitude}"
        )

        fig.text(
            0.5,
            0.02,
            summary_text,
            ha="center",
            fontsize=10,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        )

        plt.tight_layout(rect=[0, 0.1, 1, 0.95])

        return fig

    def show(self) -> None:
        """Display the combined plot."""
        self.plot_combined()
        plt.show()

    def save(self, filepath: str, dpi: int = 150) -> None:
        """
        Save combined plot to file.

        Args:
            filepath: Output file path (e.g., "calibration.png")
            dpi: Resolution in dots per inch
        """
        fig = self.plot_combined()
        fig.savefig(filepath, dpi=dpi, bbox_inches="tight")
        print(f"[Plot] Saved to: {filepath}")
        plt.close(fig)


# Demo with synthetic data
def demo():
    """Generate demo plot with synthetic data."""
    from calibration.measurement import MeasurementPoint, CalibrationRun
    from datetime import datetime

    # Create synthetic data with known error pattern
    run = CalibrationRun(name="demo", start_time=datetime.now())

    np.random.seed(42)
    for i in range(360):
        ref_angle = i
        # Simulate 1x error (eccentricity) + 2x error (ellipticity) + noise
        error_1x = 1.5 * np.sin(np.deg2rad(ref_angle + 45))
        error_2x = 0.3 * np.sin(np.deg2rad(2 * ref_angle + 120))
        noise = np.random.normal(0, 0.1)

        measured = ref_angle + error_1x + error_2x + noise

        point = MeasurementPoint(
            timestamp=i, reference_deg=ref_angle, measured_deg=measured
        )
        run.add_point(point)

    # Create plotter and show
    plotter = CalibrationPlotter(run)

    result = plotter.analysis.analyze()
    print(result.summary())

    plotter.show()


if __name__ == "__main__":
    demo()
