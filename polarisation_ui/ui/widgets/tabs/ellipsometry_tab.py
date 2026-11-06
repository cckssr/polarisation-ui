"""Rotating-analyser ellipsometry (RAE) experiment tab.

Bench geometry: fixed polariser -> sample (angle of incidence, manual) ->
rotating analyser (KDC101, optional — manual rotation also supported) ->
PD-TIA detector. See ``polarisation_ui.core.ellipsometry`` for the physics.

Workflow, mirroring MalusTab's manual-entry + optional-KDC-sweep pattern:
  1. Set AOI by hand, then "set AOI zero" to reference it.
  2. Collect analyser-azimuth samples for the current AOI, either manually
     ("add point", analyser rotated by hand) or via a KDC101 sweep.
     Each new sample re-fits I(A) = I0*(1 + alpha*cos(2A) + beta*sin(2A))
     live, converting a valid fit to (Psi, Delta) and a pseudo (n, k).
  3. "Accept into series" commits the current AOI's fit as one row of the
     (theta, Psi, Delta) series and clears the sample buffer for the next AOI.
  4. "Fit model" fits either a bare-substrate (2-phase, reports mean
     pseudo n/k) or film-on-substrate (3-phase, reports thickness/n/k) model
     to the whole series.

Fitting requires calibrated power (frame.power_W, from either a loaded
PD-TIA calibration profile or an active PM400 — see core.detector) on every
sample, so a gain change mid-sweep cannot silently scale part of the curve
(power is gain-normalised) — see the module/tab docs for why. Both the
sweep and manual-entry groups are disabled, with an explanatory tooltip,
until a power measurement is active.
"""

from __future__ import annotations

import math
import time
from collections import deque
from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtCore import QMutex, QMutexLocker, Signal, Slot
from PySide6.QtWidgets import QHeaderView, QTableWidgetItem, QWidget

from polarisation_ui.core.detector import point_power
from polarisation_ui.core.ellipsometry import (
    FilmFit,
    RaeFit,
    fit_film,
    fit_rae,
    n_k_two_phase,
    psi_delta_from_fit,
    psi_delta_three_phase,
    rho_from_psi_delta,
)
from polarisation_ui.core.formatting import export_angle, export_intensity, fmt_angle, fmt_intensity
from polarisation_ui.core.models import EllipsometryPoint, EllipsometrySeriesPoint, Frame, TabExport
from polarisation_ui.core.utils import windowed_average_intensity
from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.infrastructure.qt_threads import KDCSweepWorker
from polarisation_ui.pyqt.ui_ellipsometry_tab import Ui_EllipsometryTab
from polarisation_ui.ui.i18n import apply_strings
from polarisation_ui.ui.widgets.plot_tab_base import ConnState, PlotTabBase
from polarisation_ui.ui.widgets.tab_title import TabTitle
from polarisation_ui.ui.widgets.vscroll import lock_vertical_scroll

if TYPE_CHECKING:
    from polarisation_ui.infrastructure.devices.kdc101_polariser import KDC101Polariser

_BUFFER_MAXLEN = 20
_AVERAGE_WINDOW_MS = 500
_KDC_POLL_INTERVAL_S = 0.5  # How often to refresh the KDC position in the live label
_MODEL_TOKENS = ["2phase", "3phase"]


class EllipsometryTab(PlotTabBase):
    """Rotating-analyser ellipsometry tab: manual/KDC101 analyser sweep + AOI series."""

    tab_id = "ellipsometry"
    tab_title = TabTitle()  # ui.tabs.ellipsometry
    required_sources: set[str] = {"ENC:BOTH", "ADC"}
    required_modules: set[str] = set()  # KDC101 optional — groupSweep is the module gate

    points_changed = Signal(int)  # emits len(series) after every accept/delete/clear

    def __init__(self, parent: QWidget | None = None, config: AppConfig | None = None) -> None:
        """Initialise empty buffers/state; build() constructs the widgets."""
        super().__init__(parent, config)
        self._buffer: deque[Frame] = deque(maxlen=_BUFFER_MAXLEN)
        self._buffer_mutex = QMutex()
        self._is_measuring: bool = False
        self._kdc: KDC101Polariser | None = None
        self._sweep_worker: KDCSweepWorker | None = None
        self._latest_frame: Frame | None = None
        self._power_calibrated: bool = False
        self._aoi_zero_sample: float | None = None
        self._aoi_zero_detector: float | None = None
        self._offset_auto: bool = True  # spinAnalyserOffset tracks P+90 until user edits it
        self._last_fit: RaeFit | None = None
        self._last_psi_delta: tuple[float, float, float, float] | None = None  # (psi, delta, n, k)
        self._series: list[EllipsometrySeriesPoint] = []
        self._model_fit: FilmFit | None = None
        self._kdc_pos_cache: float | None = None
        self._kdc_last_poll_ts: float = 0.0

    def build(self) -> None:
        """Construct the tab's widgets and wire up signal connections."""
        self._ui = Ui_EllipsometryTab()
        self._ui.setupUi(self)
        apply_strings(self, self.config.section("ui").get("ellipsometry_tab", {}))
        self._ui.fitPlot.apply_config(self.config)
        self._ui.ellipsoCurvePlot.apply_config(self.config)
        self._ui.comboModel.addItems(
            [self.config.text(f"ellipsometry_tab.model_{kind}") for kind in ("substrate", "film")]
        )
        self._ui.tableSeries.setHorizontalHeaderLabels(
            [
                self.config.text(f"ellipsometry_tab.column_{key}")
                for key in ("aoi", "psi", "delta", "n", "k", "samples", "rms", "modulation")
            ]
        )
        self._ui.tableSeries.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._ui.buttonSetAoiZero.clicked.connect(self._set_aoi_zero)
        self._ui.spinPolariser.valueChanged.connect(self._on_polariser_changed)
        self._ui.spinAnalyserOffset.valueChanged.connect(self._on_analyser_offset_changed)
        self._ui.spinAnalyserManual.lineEdit().returnPressed.connect(self._add_point)
        self._ui.buttonAddPoint.clicked.connect(self._add_point)
        self._ui.buttonClearSweep.clicked.connect(self._clear_sweep_buffer)
        self._ui.checkAnalyserPlaced.toggled.connect(lambda _checked: self._update_gates())
        self._ui.buttonStartSweep.clicked.connect(self._start_sweep)
        self._ui.buttonAbortSweep.clicked.connect(self._abort_sweep)
        self._ui.buttonAcceptPoint.clicked.connect(self._accept_point)
        self._ui.buttonFitModel.clicked.connect(self._fit_model)
        self._ui.comboModel.currentIndexChanged.connect(self._on_model_changed)
        self._ui.tableSeries.itemSelectionChanged.connect(self._on_table_selection_changed)
        self._ui.buttonDeleteSelected.clicked.connect(self._delete_selected_series_point)
        self._ui.buttonDeleteLast.clicked.connect(self._delete_last_series_point)
        self._ui.buttonClear.clicked.connect(self._clear_series)
        # the side column never scrolls horizontally; the width set in the form is its floor
        form_min_width = self._ui.scrollSide.minimumWidth()
        width = lock_vertical_scroll(self._ui.scrollSide)
        self._ui.scrollSide.setMinimumWidth(max(width, form_min_width))

    # ── PlotTabBase lifecycle ─────────────────────────────────────────────────

    def on_frame(self, frame: Frame) -> None:
        """Buffer the frame, gate on power calibration, and refresh the live labels."""
        with QMutexLocker(self._buffer_mutex):
            self._buffer.append(frame)
        self._latest_frame = frame
        # A PM400 frame carries power_W directly (no conv_factor_W_per_V —
        # see core.detector), so gate on power_W itself rather than on a
        # PD-TIA-specific calibration profile.
        calibrated = frame.power_W is not None
        if calibrated != self._power_calibrated:
            self._power_calibrated = calibrated
            if not calibrated:
                self.status_message.emit(
                    "warning", self.config.message("tabs.ellipsometry_power_required")
                )
            self._update_gates()
        self._update_live_labels(frame)

    def on_reset(self) -> None:
        """Clear both plots, the sample buffer, and the whole AOI series."""
        self._ui.fitPlot.clear()
        self._ui.ellipsoCurvePlot.clear()
        with QMutexLocker(self._buffer_mutex):
            self._buffer.clear()
        self._series.clear()
        self._last_fit = None
        self._last_psi_delta = None
        self._model_fit = None
        self._clear_result_labels()
        self._clear_model_labels()
        self._refresh_series_table()
        self._ui.buttonFitModel.setEnabled(False)
        self._update_delete_buttons()
        self.points_changed.emit(0)
        self._update_live_labels(None)

    def on_connection_state(self, state: ConnState) -> None:
        """No-op — this tab has no connection-state-dependent UI."""

    def on_activated(self) -> None:
        """No-op — this tab has no activation-dependent UI."""

    def on_deactivated(self) -> None:
        """No-op — this tab has no deactivation-dependent UI."""

    def on_measurement_started(self) -> None:
        """Enable entry/sweep controls (subject to the power-calibration gate) for the session."""
        self._is_measuring = True
        with QMutexLocker(self._buffer_mutex):
            self._buffer.clear()
        self._update_gates()
        self._update_delete_buttons()

    def on_measurement_stopped(self) -> None:
        """Abort any running sweep and disable entry/sweep/accept controls."""
        self._is_measuring = False
        if self._sweep_worker is not None:
            self._sweep_worker.abort()
        self._ui.buttonAcceptPoint.setEnabled(False)
        self._update_gates()
        self._update_delete_buttons()

    def inject_modules(self, modules: dict[str, object]) -> None:
        """Store the injected kdc101 module (or clear it) and refresh sweep gating."""
        kdc = modules.get("kdc101")
        self._kdc = kdc if kdc is not None else None  # type: ignore[assignment]
        self._ui.groupSweep.setEnabled(self._kdc is not None)
        self._update_gates()

    # ── Export contract ───────────────────────────────────────────────────────

    def get_saved_points(self) -> list[EllipsometrySeriesPoint]:
        """Return every completed angle-of-incidence measurement in the series."""
        return list(self._series)

    def build_export(self) -> TabExport:
        """Build a tidy-format CSV: one row per raw analyser sample, AOI results repeated."""
        columns = [
            "aoi_deg",
            "analyser_logical_deg",
            "azimuth_deg",
            "intensity_V",
            "power_W",
            "pdtia_gain",
            "conv_factor_W_per_V",
            "detector",
            "psi_deg",
            "delta_deg",
            "alpha",
            "beta",
            "i0_W",
            "residual_rms",
            "modulation",
            "n_pseudo",
            "k_pseudo",
        ]
        rows: list[list[str]] = []
        for sp in self._series:
            for sample in sp.samples:
                rows.append(
                    [
                        export_angle(sp.aoi_deg),
                        export_angle(sample.analyser_angle),
                        export_angle(sample.azimuth_deg),
                        export_intensity(sample.intensity_V),
                        f"{sample.power_W:.6e}" if sample.power_W is not None else "",
                        str(sample.pdtia_gain) if sample.pdtia_gain else "",
                        (
                            f"{sample.conv_factor_W_per_V:.6e}"
                            if sample.conv_factor_W_per_V is not None
                            else ""
                        ),
                        sample.detector,
                        export_angle(sp.psi_deg),
                        export_angle(sp.delta_deg),
                        f"{sp.alpha:.6f}",
                        f"{sp.beta:.6f}",
                        f"{sp.i0:.6e}",
                        f"{sp.residual_rms:.6e}",
                        f"{sp.modulation:.6f}",
                        f"{sp.n_pseudo:.6f}",
                        f"{sp.k_pseudo:.6f}",
                    ]
                )
        model_idx = self._ui.comboModel.currentIndex()
        metadata: dict = {
            "wavelength_nm": self._ui.spinWavelength.value(),
            "polariser_azimuth_deg": self._ui.spinPolariser.value(),
            "analyser_offset_deg": self._ui.spinAnalyserOffset.value(),
            "n_ambient": self._ui.spinAmbientIndex.value(),
            "n_substrate": self._ui.spinSubstrateN.value(),
            "k_substrate": self._ui.spinSubstrateK.value(),
            "model": "3phase" if model_idx == 1 else "2phase",
            "sweep_start_deg": self._ui.spinSweepStart.value(),
            "sweep_end_deg": self._ui.spinSweepEnd.value(),
            "sweep_step_deg": self._ui.spinSweepStep.value(),
            "columns": columns,
            "units": {
                "aoi_deg": "degrees",
                "azimuth_deg": "degrees",
                "intensity_V": "volts",
                "power_W": "watts",
                "detector": "pdtia or pm400",
                "psi_deg": "degrees",
                "delta_deg": "degrees",
                "i0_W": "watts",
            },
            # RAE only measures cos(Delta) — see core.ellipsometry module docs.
            "delta_sign_ambiguous": True,
        }
        if self._kdc is not None:
            metadata["kdc_zero_offset_deg"] = self._kdc.zero_offset_deg
        if self._model_fit is not None:
            metadata["fit_thickness_nm"] = self._model_fit.thickness_nm
            metadata["fit_n_film"] = self._model_fit.n_film
            metadata["fit_k_film"] = self._model_fit.k_film
            metadata["fit_mse"] = self._model_fit.mse
            metadata["fit_branches"] = self._model_fit.branches
        token = _MODEL_TOKENS[1] if model_idx == 1 else _MODEL_TOKENS[0]
        return TabExport(
            filename_hint="ellipsometry",
            columns=columns,
            rows=rows,
            metadata=metadata,
            filename_tokens=[token],
        )

    def restore_points(self, points: list[dict]) -> None:
        """Reload a previously-saved AOI series (including nested raw samples)."""
        for p in points:
            try:
                samples = [
                    EllipsometryPoint(
                        analyser_angle=float(s["analyser_angle"]),
                        azimuth_deg=float(s["azimuth_deg"]),
                        intensity_V=float(s["intensity_V"]),
                        power_W=s.get("power_W"),
                        pdtia_gain=int(s.get("pdtia_gain") or 0),
                        conv_factor_W_per_V=s.get("conv_factor_W_per_V"),
                        aoi_deg=float(s.get("aoi_deg", float("nan"))),
                        detector_angle=float(s.get("detector_angle", float("nan"))),
                        detector=s.get("detector") or "pdtia",
                    )
                    for s in (p.get("samples") or [])
                ]
                self._series.append(
                    EllipsometrySeriesPoint(
                        aoi_deg=float(p["aoi_deg"]),
                        psi_deg=float(p["psi_deg"]),
                        delta_deg=float(p["delta_deg"]),
                        i0=float(p["i0"]),
                        alpha=float(p["alpha"]),
                        beta=float(p["beta"]),
                        residual_rms=float(p["residual_rms"]),
                        modulation=float(p["modulation"]),
                        n_pseudo=float(p["n_pseudo"]),
                        k_pseudo=float(p["k_pseudo"]),
                        wavelength_nm=float(p["wavelength_nm"]),
                        polariser_azimuth_deg=float(p["polariser_azimuth_deg"]),
                        samples=samples,
                    )
                )
            except (KeyError, TypeError, ValueError):
                pass
        self._after_series_mutated()

    # ── AOI zero / live labels ────────────────────────────────────────────────

    @Slot()
    def _set_aoi_zero(self) -> None:
        if self._latest_frame is None:
            self.status_message.emit("warning", self.config.message("tabs.ellipsometry_no_frame"))
            return
        self._aoi_zero_sample = self._latest_frame.sample_angle
        self._aoi_zero_detector = self._latest_frame.detector_angle
        self.status_message.emit("info", self.config.message("tabs.ellipsometry_aoi_zero_set"))
        self._update_live_labels(self._latest_frame)

    def _fmt(self, kind: str, value: str) -> str:
        """``value`` inside the configured template ``ui.ellipsometry_tab.fmt_<kind>`` (unit)."""
        return self.config.text(f"ellipsometry_tab.fmt_{kind}", value=value)

    def _aoi_from_frame(self, frame: Frame | None) -> float:
        if frame is None or self._aoi_zero_sample is None:
            return float("nan")
        return frame.sample_angle - self._aoi_zero_sample

    def _update_live_labels(self, frame: Frame | None) -> None:
        if frame is None or math.isnan(frame.intensity):
            self._ui.valueLiveIntensity.setText("—")
            self._ui.valueLivePower.setText("—")
            self._ui.valueLiveAoi.setText("—")
            self._ui.valueLiveDetector.setText("—")
            self._ui.valueSpecularError.setText("—")
        else:
            self._ui.valueLiveIntensity.setText(
                self._fmt("voltage", fmt_intensity(frame.intensity))
            )
            if frame.power_W is not None:
                self._ui.valueLivePower.setText(self._fmt("power_mw", f"{frame.power_W * 1e3:.3f}"))
            else:
                self._ui.valueLivePower.setText("—")
            self._ui.valueLiveDetector.setText(self._fmt("angle", fmt_angle(frame.detector_angle)))

            aoi = self._aoi_from_frame(frame)
            if math.isnan(aoi):
                self._ui.valueLiveAoi.setText("—")
                self._ui.valueSpecularError.setText("—")
            else:
                self._ui.valueLiveAoi.setText(self._fmt("angle", fmt_angle(aoi)))
                if self._aoi_zero_detector is not None:
                    err = (frame.detector_angle - self._aoi_zero_detector) - 2 * aoi
                    self._ui.valueSpecularError.setText(self._fmt("angle", f"{err:+.2f}"))
                else:
                    self._ui.valueSpecularError.setText("—")
        self._update_kdc_position_label()
        self._update_kdc_zero_label()

    def _update_kdc_position_label(self) -> None:
        if self._kdc is None or not self._kdc.is_connected():
            self._ui.valueKdcPosition.setText("—")
            return
        now = time.monotonic()
        if now - self._kdc_last_poll_ts >= _KDC_POLL_INTERVAL_S:
            try:
                self._kdc_pos_cache = self._kdc.get_position_deg()
                self._kdc_last_poll_ts = now
            except Exception as exc:  # noqa: BLE001
                from polarisation_ui.infrastructure.logging import Debug

                Debug.warning(f"EllipsometryTab: KDC position read failed: {exc}")
        if self._kdc_pos_cache is not None:
            self._ui.valueKdcPosition.setText(self._fmt("angle", fmt_angle(self._kdc_pos_cache)))
        else:
            self._ui.valueKdcPosition.setText("—")

    def _update_kdc_zero_label(self) -> None:
        if self._kdc is None:
            self._ui.valueKdcZeroOffset.setText("—")
            return
        self._ui.valueKdcZeroOffset.setText(
            self._fmt("angle", fmt_angle(self._kdc.zero_offset_deg))
        )

    # ── Polariser / analyser-offset auto-default ────────────────────────────────

    @Slot(float)
    def _on_polariser_changed(self, value: float) -> None:
        if self._offset_auto:
            self._ui.spinAnalyserOffset.blockSignals(True)
            self._ui.spinAnalyserOffset.setValue((value + 90.0) % 360.0)
            self._ui.spinAnalyserOffset.blockSignals(False)

    @Slot(float)
    def _on_analyser_offset_changed(self, _value: float) -> None:
        self._offset_auto = False

    @Slot(int)
    def _on_model_changed(self, _index: int) -> None:
        self.filename_hint_changed.emit()

    # ── Gating ─────────────────────────────────────────────────────────────────

    def _update_gates(self) -> None:
        self._ui.groupManual.setEnabled(self._is_measuring and self._power_calibrated)

        reasons: list[str] = []
        if not self._power_calibrated:
            reasons.append(self.config.text("ellipsometry_tab.reason_power_required"))
        if not self._is_measuring:
            reasons.append(self.config.text("ellipsometry_tab.reason_not_measuring"))
        if self._kdc is None or not self._kdc.is_connected():
            reasons.append(self.config.text("ellipsometry_tab.reason_kdc_missing"))
        if not self._ui.checkAnalyserPlaced.isChecked():
            reasons.append(self.config.text("ellipsometry_tab.reason_analyser_missing"))
        if self._sweep_worker is not None:
            reasons.append(self.config.text("ellipsometry_tab.reason_sweep_running"))
        can_start = not reasons
        self._ui.buttonStartSweep.setEnabled(can_start)
        self._ui.buttonStartSweep.setToolTip(
            self.config.text("ellipsometry_tab.tooltip_start_sweep")
            if can_start
            else " / ".join(reasons)
        )
        self._ui.buttonAbortSweep.setEnabled(
            self._sweep_worker is not None and self._sweep_worker.isRunning()
        )

    # ── Sample collection (manual + sweep share _add_sample / _refit_current) ──

    def _compute_average(self) -> tuple[float, Frame | None]:
        """Mutex-guarded windowed average — safe from both the main thread and KDCSweepWorker."""
        with QMutexLocker(self._buffer_mutex):
            return windowed_average_intensity(self._buffer, _AVERAGE_WINDOW_MS)

    @Slot()
    def _add_point(self) -> None:
        avg_intensity, latest_frame = self._compute_average()
        if math.isnan(avg_intensity):
            self.status_message.emit(
                "warning", self.config.message("tabs.ellipsometry_no_valid_intensity")
            )
            return
        self._add_sample(self._ui.spinAnalyserManual.value(), avg_intensity, latest_frame)

    @Slot(float, float, float, object)
    def _on_sweep_point(
        self, analyser_angle: float, _kdc_pos: float, intensity_V: float, frame: Frame | None
    ) -> None:
        self._add_sample(analyser_angle, intensity_V, frame)

    def _add_sample(self, analyser_angle: float, intensity_V: float, frame: Frame | None) -> None:
        azimuth = analyser_angle + self._ui.spinAnalyserOffset.value()
        power_W, conv_factor = point_power(frame, intensity_V)
        pdtia_gain = frame.pdtia_gain if frame is not None else 0
        detector = frame.detector if frame is not None else "pdtia"
        ref_frame = frame if frame is not None else self._latest_frame
        aoi = self._aoi_from_frame(ref_frame)
        detector_angle = ref_frame.detector_angle if ref_frame is not None else float("nan")
        self._ui.fitPlot.add_point(
            analyser_angle=analyser_angle,
            azimuth_deg=azimuth,
            intensity_V=intensity_V,
            power_W=power_W,
            pdtia_gain=pdtia_gain,
            conv_factor_W_per_V=conv_factor,
            aoi_deg=aoi,
            detector_angle=detector_angle,
            detector=detector,
        )
        self._refit_current()

    @Slot()
    def _clear_sweep_buffer(self) -> None:
        self._ui.fitPlot.clear()
        self._last_fit = None
        self._last_psi_delta = None
        self._clear_result_labels()
        self._ui.buttonAcceptPoint.setEnabled(False)

    # ── Live RAE fit ───────────────────────────────────────────────────────────

    def _refit_current(self) -> None:
        points = self._ui.fitPlot.get_points()
        if len(points) < 3 or any(p.power_W is None for p in points):
            self._last_fit = None
            self._last_psi_delta = None
            self._ui.fitPlot.set_fit(None)
            self._clear_result_labels()
            self._ui.buttonAcceptPoint.setEnabled(False)
            return
        fit = fit_rae([p.azimuth_deg for p in points], [p.power_W for p in points])
        self._last_fit = fit
        self._ui.fitPlot.set_fit(fit)
        self._update_result_labels(fit, points[-1].aoi_deg)

    def _clear_result_labels(self) -> None:
        for lbl in (
            self._ui.valueAlpha,
            self._ui.valueBeta,
            self._ui.valueI0,
            self._ui.valueResidual,
            self._ui.valueModulation,
            self._ui.valuePsi,
            self._ui.valueDelta,
            self._ui.valueNPseudo,
            self._ui.valueKPseudo,
        ):
            lbl.setText("—")

    def _update_result_labels(self, fit: RaeFit, aoi_deg: float) -> None:
        self._ui.valueAlpha.setText(f"{fit.alpha:.4f}" if math.isfinite(fit.alpha) else "—")
        self._ui.valueBeta.setText(f"{fit.beta:.4f}" if math.isfinite(fit.beta) else "—")
        self._ui.valueI0.setText(
            self._fmt("power_uw", f"{fit.i0 * 1e6:.3f}") if math.isfinite(fit.i0) else "—"
        )
        self._ui.valueResidual.setText(self._fmt("power_uw", f"{fit.residual_rms * 1e6:.3f}"))
        mod_text = f"{fit.modulation:.4f}" if math.isfinite(fit.modulation) else "—"
        self._ui.valueModulation.setText(mod_text)

        self._last_psi_delta = None
        self._ui.valuePsi.setText("—")
        self._ui.valueDelta.setText("—")
        self._ui.valueNPseudo.setText("—")
        self._ui.valueKPseudo.setText("—")
        can_accept = False
        if fit.valid and not math.isnan(aoi_deg):
            try:
                psi, delta = psi_delta_from_fit(fit, self._ui.spinPolariser.value())
                rho = rho_from_psi_delta(psi, delta)
                n, k = n_k_two_phase(rho, aoi_deg, self._ui.spinAmbientIndex.value())
            except ValueError as exc:
                self.status_message.emit(
                    "warning", self.config.message("tabs.ellipsometry_psi_delta_failed", error=exc)
                )
            else:
                self._ui.valuePsi.setText(self._fmt("angle", fmt_angle(psi)))
                self._ui.valueDelta.setText(self._fmt("angle", fmt_angle(delta)))
                self._ui.valueNPseudo.setText(f"{n:.4f}")
                self._ui.valueKPseudo.setText(f"{k:.4f}")
                self._last_psi_delta = (psi, delta, n, k)
                can_accept = True
        self._ui.buttonAcceptPoint.setEnabled(can_accept and self._is_measuring)

    @Slot()
    def _accept_point(self) -> None:
        if self._last_fit is None or self._last_psi_delta is None:
            return
        points = self._ui.fitPlot.get_points()
        if not points:
            return
        aoi_deg = points[-1].aoi_deg
        if math.isnan(aoi_deg):
            self.status_message.emit(
                "warning", self.config.message("tabs.ellipsometry_aoi_zero_missing")
            )
            return
        psi, delta, n, k = self._last_psi_delta
        self._series.append(
            EllipsometrySeriesPoint(
                aoi_deg=aoi_deg,
                psi_deg=psi,
                delta_deg=delta,
                i0=self._last_fit.i0,
                alpha=self._last_fit.alpha,
                beta=self._last_fit.beta,
                residual_rms=self._last_fit.residual_rms,
                modulation=self._last_fit.modulation,
                n_pseudo=n,
                k_pseudo=k,
                wavelength_nm=self._ui.spinWavelength.value(),
                polariser_azimuth_deg=self._ui.spinPolariser.value(),
                samples=list(points),
            )
        )
        self._ui.fitPlot.clear()
        self._last_fit = None
        self._last_psi_delta = None
        self._clear_result_labels()
        self._ui.buttonAcceptPoint.setEnabled(False)
        self._after_series_mutated()
        self.status_message.emit(
            "info",
            self.config.message("tabs.ellipsometry_point_accepted", aoi=fmt_angle(aoi_deg)),
        )

    # ── AOI series table / delete ────────────────────────────────────────────

    def _after_series_mutated(self) -> None:
        self._refresh_series_table()
        self._ui.ellipsoCurvePlot.set_series(self._series)
        self._ui.buttonFitModel.setEnabled(len(self._series) >= 1)
        self._update_delete_buttons()
        self.points_changed.emit(len(self._series))

    def _refresh_series_table(self) -> None:
        self._ui.tableSeries.setRowCount(len(self._series))
        for row, p in enumerate(self._series):
            self._ui.tableSeries.setItem(row, 0, QTableWidgetItem(f"{p.aoi_deg:.2f}"))
            self._ui.tableSeries.setItem(row, 1, QTableWidgetItem(f"{p.psi_deg:.3f}"))
            self._ui.tableSeries.setItem(row, 2, QTableWidgetItem(f"{p.delta_deg:.3f}"))
            self._ui.tableSeries.setItem(row, 3, QTableWidgetItem(f"{p.n_pseudo:.4f}"))
            self._ui.tableSeries.setItem(row, 4, QTableWidgetItem(f"{p.k_pseudo:.4f}"))
            self._ui.tableSeries.setItem(row, 5, QTableWidgetItem(str(len(p.samples))))
            self._ui.tableSeries.setItem(row, 6, QTableWidgetItem(f"{p.residual_rms * 1e6:.3f}"))
            self._ui.tableSeries.setItem(row, 7, QTableWidgetItem(f"{p.modulation:.4f}"))
        self._on_table_selection_changed()

    def _update_delete_buttons(self) -> None:
        has_points = bool(self._series)
        self._ui.buttonDeleteLast.setEnabled(self._is_measuring and has_points)
        self._ui.buttonClear.setEnabled(self._is_measuring and has_points)
        self._on_table_selection_changed()

    @Slot()
    def _on_table_selection_changed(self) -> None:
        has_selection = bool(self._ui.tableSeries.selectedItems())
        self._ui.buttonDeleteSelected.setEnabled(self._is_measuring and has_selection)

    @Slot()
    def _delete_last_series_point(self) -> None:
        if not self._series:
            self.status_message.emit(
                "warning", self.config.message("tabs.ellipsometry_no_points_to_delete")
            )
            return
        self._series.pop()
        self._after_series_mutated()

    @Slot()
    def _delete_selected_series_point(self) -> None:
        selected = self._ui.tableSeries.selectedItems()
        if not selected:
            return
        row = self._ui.tableSeries.currentRow()
        if 0 <= row < len(self._series):
            del self._series[row]
            self._after_series_mutated()

    @Slot()
    def _clear_series(self) -> None:
        self._series.clear()
        self._after_series_mutated()

    # ── KDC101 analyser sweep ─────────────────────────────────────────────────

    @Slot()
    def _start_sweep(self) -> None:
        if self._kdc is None or not self._kdc.is_connected():
            return
        self._sweep_worker = KDCSweepWorker(
            kdc=self._kdc,
            read_average=self._compute_average,
            start_deg=self._ui.spinSweepStart.value(),
            end_deg=self._ui.spinSweepEnd.value(),
            step_deg=self._ui.spinSweepStep.value(),
            settle_ms=self._ui.spinSettleMs.value(),
            parent=self,
        )
        self._sweep_worker.point_scanned.connect(self._on_sweep_point)
        self._sweep_worker.progress.connect(self._on_sweep_progress)
        self._sweep_worker.finished.connect(self._on_sweep_finished)
        self._sweep_worker.failed.connect(self._on_sweep_failed)
        self._sweep_worker.log.connect(lambda msg: self.status_message.emit("info", msg))
        self._update_gates()
        self._sweep_worker.start()

    @Slot()
    def _abort_sweep(self) -> None:
        if self._sweep_worker is not None:
            self._sweep_worker.abort()

    @Slot(int, int)
    def _on_sweep_progress(self, current: int, total: int) -> None:
        self.status_message.emit(
            "info",
            self.config.message("tabs.ellipsometry_sweep_progress", current=current, total=total),
        )

    @Slot()
    def _on_sweep_finished(self) -> None:
        self._sweep_worker = None
        self._update_gates()
        self.status_message.emit("info", self.config.message("tabs.ellipsometry_sweep_finished"))

    @Slot(str)
    def _on_sweep_failed(self, msg: str) -> None:
        self._sweep_worker = None
        self._update_gates()
        self.status_message.emit(
            "error", self.config.message("tabs.ellipsometry_sweep_failed", error=msg)
        )

    # ── Optical model fit ─────────────────────────────────────────────────────

    def _clear_model_labels(self) -> None:
        self._ui.valueThickness.setText("—")
        self._ui.valueNFilm.setText("—")
        self._ui.valueKFilm.setText("—")
        self._ui.valueMSE.setText("—")
        self._ui.valueBranches.setText("")

    @Slot()
    def _fit_model(self) -> None:
        if not self._series:
            return
        aoi = [p.aoi_deg for p in self._series]
        psi = [p.psi_deg for p in self._series]
        delta = [p.delta_deg for p in self._series]
        wavelength = self._ui.spinWavelength.value()
        n_ambient = self._ui.spinAmbientIndex.value()
        n_sub = self._ui.spinSubstrateN.value()
        k_sub = self._ui.spinSubstrateK.value()
        aoi_dense = np.linspace(min(aoi), max(aoi), 100) if len(aoi) > 1 else np.array(aoi)

        if self._ui.comboModel.currentIndex() == 0:
            model = self._fit_bare_substrate(aoi_dense, wavelength, n_ambient)
        else:
            model = self._fit_film_on_substrate(
                aoi, psi, delta, aoi_dense, wavelength, n_ambient, n_sub, k_sub
            )

        if model is None:
            self._ui.ellipsoCurvePlot.clear_model()
            return
        psi_model, delta_model = model
        self._ui.ellipsoCurvePlot.set_model(
            aoi_dense.tolist(), np.asarray(psi_model).tolist(), np.asarray(delta_model).tolist()
        )

    def _fit_bare_substrate(
        self, aoi_dense: np.ndarray, wavelength: float, n_ambient: float
    ) -> tuple[np.ndarray, np.ndarray] | None:
        """2-phase 'model': average the per-AOI pseudo (n, k), overlay the bare-substrate curve."""
        n_vals = [p.n_pseudo for p in self._series]
        k_vals = [p.k_pseudo for p in self._series]
        n_mean = float(np.mean(n_vals))
        k_mean = float(np.mean(k_vals))
        self._model_fit = None
        self._ui.valueThickness.setText("—")
        self._ui.valueNFilm.setText(self._fmt("mean", f"{n_mean:.4f}"))
        self._ui.valueKFilm.setText(self._fmt("mean", f"{k_mean:.4f}"))
        n_std = float(np.std(n_vals)) if len(n_vals) > 1 else 0.0
        self._ui.valueMSE.setText(self._fmt("sigma_n", f"{n_std:.4f}"))
        self._ui.valueBranches.setText("")
        if n_mean <= 0.0 or not math.isfinite(n_mean):
            self.status_message.emit(
                "warning", self.config.message("tabs.ellipsometry_mean_index_invalid")
            )
            return None
        # thickness=0 makes the film irrelevant — this is exactly the bare
        # (n_sub, k_sub) Fresnel model (see psi_delta_three_phase docstring).
        return psi_delta_three_phase(
            aoi_dense, wavelength, 0.0, n_mean, k_mean, n_mean, k_mean, n_ambient
        )

    def _fit_film_on_substrate(
        self,
        aoi: list[float],
        psi: list[float],
        delta: list[float],
        aoi_dense: np.ndarray,
        wavelength: float,
        n_ambient: float,
        n_sub: float,
        k_sub: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        result = fit_film(
            aoi,
            psi,
            delta,
            wavelength_nm=wavelength,
            n_sub=n_sub,
            k_sub=k_sub,
            n_ambient=n_ambient,
            d_range=(self._ui.spinDMin.value(), self._ui.spinDMax.value()),
            n_range=(self._ui.spinNfMin.value(), self._ui.spinNfMax.value()),
            fit_k=self._ui.checkFitK.isChecked(),
        )
        self._model_fit = result
        self._ui.valueThickness.setText(self._fmt("thickness", f"{result.thickness_nm:.1f}"))
        self._ui.valueNFilm.setText(f"{result.n_film:.4f}")
        if self._ui.checkFitK.isChecked():
            self._ui.valueKFilm.setText(f"{result.k_film:.4f}")
        else:
            self._ui.valueKFilm.setText(self.config.text("ellipsometry_tab.text_k_fixed"))
        self._ui.valueMSE.setText(self._fmt("mse", f"{result.mse:.3f}"))
        if len(result.branches) > 1:
            alt = ", ".join(self._fmt("thickness", f"{d:.0f}") for d, _, _ in result.branches[1:4])
            self._ui.valueBranches.setText(
                self.config.text("ellipsometry_tab.fmt_alternative_thicknesses", thicknesses=alt)
            )
        else:
            self._ui.valueBranches.setText("")
        return psi_delta_three_phase(
            aoi_dense,
            wavelength,
            result.thickness_nm,
            result.n_film,
            result.k_film,
            n_sub,
            k_sub,
            n_ambient,
        )
