"""Qt worker threads for infrastructure-layer blocking operations.

Qt is allowed in this module only. All other infrastructure modules must remain
free of PySide6 imports.
"""

import bisect
import dataclasses
import math
import time
from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import QThread, Signal

from polarisation_ui.core.auto_calibration_settings import (
    AutoCalibrationParams,
    build_angle_grid,
)
from polarisation_ui.core.exceptions import KDC101Error, PM400Error
from polarisation_ui.core.power_calibration import (
    PowerCalibrationProfile,
)
from polarisation_ui.core.utils import linear_angle_grid
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.infrastructure.logging import Debug

if TYPE_CHECKING:
    from polarisation_ui.core.models import Frame
    from polarisation_ui.infrastructure.devices.kdc101_polariser import KDC101Polariser
    from polarisation_ui.infrastructure.devices.pm400 import PM400PowerMeter


_SENSOR_INFO_KEYS = (
    "name",
    "serial",
    "calibration_message",
    "type",
    "subtype",
    "flags",
)


def _parse_sensor_info(raw: list) -> dict:
    """Convert the flat PM400 sensor_info list to a labelled dict."""
    return {
        key: str(raw[i]).strip() if i < len(raw) else "" for i, key in enumerate(_SENSOR_INFO_KEYS)
    }


class ReconnectWorker(QThread):
    """Off-main-thread reconnection worker.

    Calls ``device_manager.reconnect_encoders()`` (which contains blocking
    ``sleep()`` calls) on a dedicated QThread so the Qt event loop — and the
    UI — stay responsive during every backoff window.

    Signals are delivered to the main thread via Qt's automatic queued-connection
    mechanism because the receiver objects live on the main thread.
    """

    succeeded = Signal()
    failed = Signal()

    def __init__(
        self,
        device_manager: GoniometerDeviceManager,
        parent=None,
    ) -> None:
        """Store the device manager whose reconnect_encoders() this worker will call."""
        super().__init__(parent)
        self._device_manager = device_manager

    def run(self) -> None:
        """Attempt one reconnect and emit succeeded or failed."""
        Debug.info("ReconnectWorker: attempting reconnect on worker thread")
        try:
            success = self._device_manager.reconnect_encoders()
        except Exception as exc:
            Debug.error(f"ReconnectWorker: exception during reconnect: {exc}")
            self.failed.emit()
            return

        if success:
            Debug.info("ReconnectWorker: reconnect succeeded")
            self.succeeded.emit()
        else:
            Debug.info("ReconnectWorker: reconnect failed")
            self.failed.emit()


class AutoPowerCalibrationWorker(QThread):
    """Off-main-thread worker that runs a full automated power calibration sweep.

    The caller is responsible for pausing DataController polling before
    calling ``start()`` and for resuming it after ``finished`` or ``failed``
    is emitted.  This worker interacts directly with *device_manager* for
    PDTIA gain and ADC reads; no QTimer involvement here.

    Signals are delivered to the main thread via Qt's queued-connection
    mechanism because the receiver objects live on the main thread.
    """

    gain_started = Signal(int)
    point_recorded = Signal(
        int, float, float, float
    )  # gain, angle_deg, detector_voltage, pm_power_W
    progress = Signal(int, int)
    finished = Signal(object)  # PowerCalibrationProfile
    failed = Signal(str)
    log = Signal(str)

    def __init__(
        self,
        device_manager: "GoniometerDeviceManager",
        kdc: "KDC101Polariser",
        pm: "PM400PowerMeter",
        params: AutoCalibrationParams,
        parent=None,
    ) -> None:
        """Store the devices and sweep parameters this worker will drive."""
        super().__init__(parent)
        self._device_manager = device_manager
        self._kdc = kdc
        self._pm = pm
        self._params = params
        self._abort: bool = False

    def abort(self) -> None:
        """Request a clean stop.  The worker will emit ``failed`` with an abort message."""
        self._abort = True

    def run(self) -> None:
        """Run the full calibration sweep, catching and reporting unexpected errors."""
        Debug.info("AutoPowerCalibrationWorker: starting sweep")
        try:
            self._run_sweep()
        except Exception as exc:
            Debug.error(f"AutoPowerCalibrationWorker: unexpected error: {exc}", exc_info=True)
            self.failed.emit(str(exc))

    def _run_sweep(self) -> None:
        p = self._params

        # Configure PM400 for this run
        self.log.emit(
            f"PM400: wavelength={p.wavelength_nm} nm, "
            f"attenuation={p.beamsplitter_attenuation_dB:.2f} dB"
        )
        try:
            self._pm.set_wavelength_nm(p.wavelength_nm)
            self._pm.set_attenuation_dB(p.beamsplitter_attenuation_dB)
            self._pm.set_averaging(p.pm_averaging)
        except PM400Error as exc:
            self.failed.emit(f"PM400 configuration failed: {exc}")
            return

        # Collect sensor identification for metadata
        raw_sensor = self._pm.sensor_info()
        sensor_meta = _parse_sensor_info(raw_sensor)
        if sensor_meta:
            self.log.emit(
                f"PM400 sensor: {sensor_meta.get('name', '?')} "
                f"S/N {sensor_meta.get('serial', '?')} "
                f"({sensor_meta.get('type', '?')})"
            )

        # Home the stage
        self.log.emit("KDC101: homing…")
        try:
            self._kdc.home()
        except KDC101Error as exc:
            self.failed.emit(f"KDC101 homing failed: {exc}")
            return

        angles = build_angle_grid(p)
        total = len(angles) * len(p.selected_gains)
        done = 0
        profile = PowerCalibrationProfile(
            name=p.profile_name,
            wavelength_nm=p.wavelength_nm,
            beamsplitter_attenuation_dB=p.beamsplitter_attenuation_dB,
            adc_saturation_threshold_V=p.adc_saturation_threshold_V,
            sensor=sensor_meta,
        )

        sat_threshold = p.adc_saturation_threshold_V
        self.log.emit(
            f"Saturation threshold: {sat_threshold:.2f} V — "
            f"points at or above this voltage will be skipped."
        )

        for gain in p.selected_gains:
            if self._abort:
                self.failed.emit("Aborted by user")
                return

            self.gain_started.emit(gain)
            self.log.emit(f"Gain {gain}: starting ({len(angles)} angles)")

            ok = self._device_manager.set_pdtia_gain(gain - 1)  # firmware is 0-based
            if not ok:
                self.failed.emit(f"Could not set PDTIA gain stage {gain}")
                return
            time.sleep(p.gain_settle_s)

            # Mutable per-gain angle list: allows tail redistribution after
            # the first non-saturated point when the sweep starts in saturation.
            gain_angles: list[float] = list(angles)
            first_valid_found = False
            idx = 0
            while idx < len(gain_angles):
                if self._abort:
                    self.failed.emit("Aborted by user")
                    return

                angle = gain_angles[idx]

                try:
                    self._kdc.move_to(angle + p.angle_offset_deg)
                except KDC101Error as exc:
                    self.failed.emit(f"KDC101 move failed: {exc}")
                    return

                time.sleep(p.point_settle_s)

                # Average N detector readings
                voltages: list[float] = []
                for _ in range(p.detector_samples):
                    v = self._device_manager.read_adc_voltage()
                    if v is not None:
                        voltages.append(v)
                if not voltages:
                    self.log.emit(f"  Warning: no ADC readings at θ={angle:.2f}°, skipping")
                    done += 1
                    self.progress.emit(done, total)
                    idx += 1
                    continue
                voltage_mean = sum(voltages) / len(voltages)

                # Saturation guard — skip PM400 read and don't record the point
                if voltage_mean >= sat_threshold:
                    profile.gains[gain].n_saturated_skipped += 1
                    self.log.emit(
                        f"  θ={angle:.1f}° | V={voltage_mean:.4f} V — "
                        f"SATURATED (≥{sat_threshold:.2f} V), skipping"
                    )
                    done += 1
                    self.progress.emit(done, total)
                    idx += 1
                    continue

                # First valid point after a saturated prefix: rebuild the full
                # p.n_points grid from this angle to angle_end so the usable
                # range is sampled at the originally requested density.
                # Example: 30 steps over 0–90°, first 10 saturated → rebuild
                # 30 steps over 30–90°, giving 2° spacing instead of 3°.
                if not first_valid_found and profile.gains[gain].n_saturated_skipped > 0:
                    sub = dataclasses.replace(
                        p,
                        angle_start_deg=angle,
                        angle_end_deg=p.angle_end_deg,
                    )
                    new_grid = build_angle_grid(sub)  # p.n_points points from `angle`
                    gain_angles[idx + 1 :] = new_grid[1:]
                    # Tail grew by idx entries; keep progress denominator consistent.
                    total += idx
                    self.log.emit(
                        f"  Grid recalculated: {p.n_points} points from "
                        f"{angle:.1f}° to {p.angle_end_deg:.1f}°"
                    )
                first_valid_found = True

                try:
                    power_W = self._pm.read_power_W()
                except PM400Error as exc:
                    self.failed.emit(f"PM400 read failed: {exc}")
                    return

                profile.gains[gain].add_point(voltage_mean, power_W)
                done += 1
                self.point_recorded.emit(gain, angle, voltage_mean, power_W)
                self.progress.emit(done, total)
                self.log.emit(f"  θ={angle:.1f}° | V={voltage_mean:.6f} V | P={power_W:.3e} W")
                idx += 1

            n_sat = profile.gains[gain].n_saturated_skipped
            n_rec = len(profile.gains[gain].points)
            if n_sat:
                self.log.emit(f"Gain {gain}: {n_rec} points recorded, {n_sat} skipped (saturated)")

        self.log.emit("Sweep complete.")
        self.finished.emit(profile)


class AlignPolariserWorker(QThread):
    """Off-main-thread worker to find the physical angle of maximum transmission.

    The result (``angle_max_deg``) is the stage position where the mounted
    polariser is parallel to the reference analyser — i.e. the physical angle
    that corresponds to logical 0°.  Store it in
    ``AutoCalibrationConnectionSettings.angle_offset_deg`` and pass it to
    ``AutoCalibrationParams`` so subsequent sweeps are referenced correctly.

    Signals are delivered to the main thread via Qt's queued-connection
    mechanism.
    """

    point_scanned = Signal(float, float)  # (angle_deg, power_W)
    progress = Signal(int, int)  # (done, total)
    finished = Signal(float)  # angle_max_deg
    failed = Signal(str)
    log = Signal(str)

    def __init__(
        self,
        kdc: "KDC101Polariser",
        pm: "PM400PowerMeter",
        start_deg: float,
        end_deg: float,
        n_points: int,
        settle_s: float,
        parent=None,
    ) -> None:
        """Store the devices and scan parameters this worker will drive."""
        super().__init__(parent)
        self._kdc = kdc
        self._pm = pm
        self._start = start_deg
        self._end = end_deg
        self._n_points = max(n_points, 3)
        self._settle = settle_s
        self._abort: bool = False

    def abort(self) -> None:
        """Request a clean stop."""
        self._abort = True

    def run(self) -> None:
        """Run the alignment scan, catching and reporting unexpected errors."""
        Debug.info("AlignPolariserWorker: starting alignment scan")
        try:
            self._run_scan()
        except Exception as exc:
            Debug.error(f"AlignPolariserWorker: unexpected error: {exc}", exc_info=True)
            self.failed.emit(str(exc))

    def _run_scan(self) -> None:
        n = self._n_points
        angles = linear_angle_grid(self._start, self._end, n)
        step = (self._end - self._start) / (n - 1) if n > 1 else 0.0

        self.log.emit(
            f"Ausrichtungsscan: {self._start:.1f}°…{self._end:.1f}° ({n} Punkte, Δθ={step:.2f}°)"
        )

        scan: list[tuple[float, float]] = []  # (angle_deg, power_W)

        for i, angle in enumerate(angles):
            if self._abort:
                self.failed.emit("Abgebrochen")
                return

            try:
                self._kdc.move_to(angle)
            except KDC101Error as exc:
                self.failed.emit(f"KDC101 Bewegung fehlgeschlagen: {exc}")
                return

            time.sleep(self._settle)

            try:
                power = self._pm.read_power_W()
            except PM400Error as exc:
                self.failed.emit(f"PM400 Lesefehler: {exc}")
                return

            scan.append((angle, power))
            self.point_scanned.emit(angle, power)
            self.progress.emit(i + 1, n)
            self.log.emit(f"  θ={angle:.1f}° | P={power:.3e} W")

        # Find the angle at peak power
        max_idx = max(range(len(scan)), key=lambda k: scan[k][1])
        angle_max, power_max = scan[max_idx]
        self.log.emit(
            f"Maximum: θ={angle_max:.2f}° (P={power_max:.3e} W) "
            f"→ Polarisator-Versatz auf {angle_max:.2f}° gesetzt"
        )
        self.finished.emit(angle_max)


class KDCSweepWorker(QThread):
    """Off-main-thread worker for an automated KDC101 analyser-angle sweep.

    Shared by the Malus and Waveplate tabs. Sequence:
        1. Home the KDC stage, unless it is already homed (``is_homed()``) —
           the zero offset was established against the last homing, so a stage
           that never lost its reference doesn't need to re-home every sweep.
        2. For each angle in [start, end] with the given step: move to
           ``kdc.zero_offset_deg + angle`` via ``move_to_logical()``, wait for
           a frame timestamped after the move completed (not just a fixed
           settle), call ``read_average()`` to get (intensity_V, Frame|None),
           emit ``point_scanned(angle, kdc_pos, intensity_V, frame)``.

    The zero offset itself is no longer found here — see
    ``KDCZeroFindWorker`` — it is set once from the Configuration tab and read
    from the shared ``KDC101Polariser`` instance.
    """

    point_scanned = Signal(float, float, float, object)  # (angle, kdc_pos, intensity_V, Frame|None)
    progress = Signal(int, int)
    finished = Signal()
    failed = Signal(str)
    log = Signal(str)

    _FRESH_FRAME_MAX_WAIT_S = 1.0
    _FRESH_FRAME_POLL_S = 0.02

    def __init__(
        self,
        kdc: "KDC101Polariser",
        read_average: Callable[[], "tuple[float, Frame | None]"],
        start_deg: float,
        end_deg: float,
        step_deg: float,
        settle_ms: int = 150,
        parent=None,
    ) -> None:
        """Store the KDC handle, intensity-reader callback, and sweep parameters."""
        super().__init__(parent)
        self._kdc = kdc
        self._read_average = read_average
        self._start = start_deg
        self._end = end_deg
        self._step = step_deg
        self._settle_ms = settle_ms / 1000.0
        self._abort: bool = False

    def abort(self) -> None:
        """Request a clean stop."""
        self._abort = True

    def run(self) -> None:
        """Run the full home(-if-needed) → sweep sequence, reporting errors via failed."""
        try:
            self._run()
        except KDC101Error as exc:
            self.failed.emit(f"KDC101 Fehler: {exc}")
        except Exception as exc:
            Debug.error(f"KDCSweepWorker: unexpected error: {exc}", exc_info=True)
            self.failed.emit(str(exc))

    def _run(self) -> None:
        if not self._kdc.is_homed():
            self.log.emit("Referenzfahrt (Home) läuft…")
            self._kdc.home()
        if self._abort:
            self.failed.emit("Abgebrochen")
            return

        n = max(2, round((self._end - self._start) / self._step) + 1)
        angles = linear_angle_grid(self._start, self._end, n)
        self.log.emit(
            f"Sweep: {self._start:.1f}° bis {self._end:.1f}°, Schritt {self._step:.1f}°, {n} Punkte"
        )
        for i, angle_set in enumerate(angles):
            if self._abort:
                self.failed.emit("Abgebrochen")
                return
            self._kdc.move_to_logical(angle_set)
            actual_pos = self._kdc.get_position_deg()
            move_done_ts = time.monotonic()
            intensity_V, frame = self._read_settled(move_done_ts)
            if self._abort:
                self.failed.emit("Abgebrochen")
                return
            self.point_scanned.emit(angle_set, actual_pos, intensity_V, frame)
            self.progress.emit(i + 1, n)
            self.log.emit(f"  θ={angle_set:.1f}° | pos={actual_pos:.2f}° | I={intensity_V:.4f} V")

        self.finished.emit()

    def _read_settled(self, after_ts: float) -> "tuple[float, Frame | None]":
        """Wait out the settle time, then keep polling ``read_average()`` until it
        reflects a frame taken after *after_ts* (i.e. after the move completed)
        or a bounded timeout elapses — avoids recording a point from a
        pre-move reading still sitting in the tab's averaging buffer.
        """
        time.sleep(self._settle_ms)
        deadline = time.monotonic() + self._FRESH_FRAME_MAX_WAIT_S
        intensity_V, frame = self._read_average()
        while (
            frame is not None
            and frame.ts_ms / 1000.0 < after_ts
            and not self._abort
            and time.monotonic() < deadline
        ):
            time.sleep(self._FRESH_FRAME_POLL_S)
            intensity_V, frame = self._read_average()
        return intensity_V, frame


def _lerp(x: float, xs: "list[float]", ys: "list[float]") -> float:
    """Linearly interpolate *ys* at *x*, clamping outside the [xs[0], xs[-1]] range."""
    i = bisect.bisect_left(xs, x)
    if i <= 0:
        return ys[0]
    if i >= len(xs):
        return ys[-1]
    x0, x1 = xs[i - 1], xs[i]
    y0, y1 = ys[i - 1], ys[i]
    if x1 == x0:
        return y0
    t = (x - x0) / (x1 - x0)
    return y0 + t * (y1 - y0)


class KDCZeroFindWorker(QThread):
    """Off-main-thread worker that finds the KDC101 polariser's extinction angle.

    Sequence:
        1. Home the stage, unless already homed.
        2. Request PDTIA gain 1 (via ``gain_requested`` — see below), then run
           a *continuous* coarse pass: move 0°→180° without waiting for each
           step, sampling stage position and live intensity concurrently while
           the stage travels, and correlating the two by timestamp afterwards
           (``Frame.ts_ms`` and the position samples share the same
           ``time.monotonic()`` clock). This avoids the ~35 s a 37-point
           stop/settle/read sweep would otherwise cost.
        3. Request PDTIA gain 3, then a stepped fine pass: ±8° around the
           coarse minimum in 0.5° steps, waiting at each step for a frame
           timestamped after the move (not a fixed sleep).
        4. Request PDTIA gain 1 again (the agreed rest state), move the stage
           to the fine minimum, and emit ``finished(offset_deg)``.

    Gain changes cannot be applied directly from this thread: setting PDTIA
    gain pauses/resumes ``DataController``'s poll ``QTimer``, which must only
    be touched from the thread that owns it. Instead this worker emits
    ``gain_requested(stage)`` and waits (via the live frame stream itself, not
    a separate synchronisation primitive) for a frame confirming the new gain
    is active before proceeding.
    """

    gain_requested = Signal(int)
    progress = Signal(int, int)
    finished = Signal(float)  # offset_deg
    failed = Signal(str)
    log = Signal(str)

    _COARSE_START_DEG = 0.0
    _COARSE_END_DEG = 180.0
    _COARSE_TIMEOUT_S = 60.0
    _POSITION_POLL_S = 0.05
    _POSITION_ARRIVAL_TOL_DEG = 0.3
    _FINE_HALF_WINDOW_DEG = 8.0
    _FINE_STEP_DEG = 0.5
    _FINE_SETTLE_S = 0.1
    _FRESH_FRAME_TIMEOUT_S = 2.0
    _GAIN_TIMEOUT_S = 5.0
    _GAIN_POLL_S = 0.05

    def __init__(
        self,
        kdc: "KDC101Polariser",
        read_latest: Callable[[], "Frame | None"],
        parent=None,
    ) -> None:
        """Store the KDC handle and a callback returning the most recent Frame."""
        super().__init__(parent)
        self._kdc = kdc
        self._read_latest = read_latest
        self._abort: bool = False
        self._last_seen_ts_ms: int | None = None

    def abort(self) -> None:
        """Request a clean stop; checked between steps and inside both scan loops."""
        self._abort = True

    def run(self) -> None:
        """Run the full home → coarse → fine sequence, reporting errors via failed."""
        try:
            self._run()
        except KDC101Error as exc:
            self.failed.emit(f"KDC101 Fehler: {exc}")
        except Exception as exc:
            Debug.error(f"KDCZeroFindWorker: unexpected error: {exc}", exc_info=True)
            self.failed.emit(str(exc))

    def _run(self) -> None:
        if not self._kdc.is_homed():
            self.log.emit("Referenzfahrt (Home) läuft…")
            self._kdc.home()
        if self._abort:
            self.failed.emit("Abgebrochen")
            return

        self.log.emit("Grobsuche (Gain 1)…")
        if not self._await_gain(1):
            self.failed.emit("PDTIA-Gain 1 konnte nicht gesetzt werden")
            return
        if self._abort:
            self.failed.emit("Abgebrochen")
            return

        positions, intensities = self._scan_continuous(
            self._COARSE_START_DEG, self._COARSE_END_DEG, self._COARSE_TIMEOUT_S
        )
        if self._abort:
            self.failed.emit("Abgebrochen")
            return
        coarse = self._correlate_minimum(positions, intensities)
        if coarse is None:
            self.failed.emit("Grobsuche: keine gültigen Messwerte")
            return
        coarse_angle, coarse_intensity = coarse
        self.log.emit(f"Grobminimum: θ={coarse_angle:.2f}° (I={coarse_intensity:.4f} V)")
        self.progress.emit(1, 2)

        self.log.emit("Feinsuche (Gain 3)…")
        if not self._await_gain(3):
            self.failed.emit("PDTIA-Gain 3 konnte nicht gesetzt werden")
            return
        if self._abort:
            self.failed.emit("Abgebrochen")
            return

        fine_results = self._scan_stepped(coarse_angle)
        if self._abort:
            self.failed.emit("Abgebrochen")
            return
        valid_fine = [(a, v) for a, v in fine_results if not math.isnan(v)]
        if not valid_fine:
            self.failed.emit("Feinsuche: keine gültigen Messwerte")
            return
        fine_angle = min(valid_fine, key=lambda x: x[1])[0]
        self.log.emit(f"Feinminimum: θ={fine_angle:.2f}°")
        self.progress.emit(2, 2)

        if not self._await_gain(1):
            Debug.warning("KDCZeroFindWorker: could not restore gain 1 after tuning")
        if not self._abort:
            self._kdc.move_to(fine_angle)

        self.finished.emit(fine_angle)

    # ── Gain synchronisation ─────────────────────────────────────────────────

    def _await_gain(self, stage: int) -> bool:
        """Ask the main thread to set PDTIA gain *stage*.

        Returns:
            False on timeout or abort.
        """
        self.gain_requested.emit(stage)
        deadline = time.monotonic() + self._GAIN_TIMEOUT_S
        while time.monotonic() < deadline:
            if self._abort:
                return False
            frame = self._read_latest()
            if frame is not None and frame.pdtia_gain == stage:
                return True
            time.sleep(self._GAIN_POLL_S)
        return False

    # ── Coarse pass: continuous move + timestamp correlation ────────────────

    def _sample_frame(self, intensities: "list[tuple[float, float]]") -> None:
        frame = self._read_latest()
        if frame is None or math.isnan(frame.intensity):
            return
        if self._last_seen_ts_ms is not None and frame.ts_ms <= self._last_seen_ts_ms:
            return
        self._last_seen_ts_ms = frame.ts_ms
        intensities.append((frame.ts_ms / 1000.0, frame.intensity))

    def _scan_continuous(
        self, start_deg: float, end_deg: float, timeout_s: float
    ) -> "tuple[list[tuple[float, float]], list[tuple[float, float]]]":
        """Move *start_deg* → *end_deg* without stopping.

        Sampling (ts, position) and (ts, intensity) concurrently.

        Returns:
            Tuple: position_samples, intensity_samples.
        """
        self._kdc.move_to(start_deg, wait=True)
        positions: list[tuple[float, float]] = [(time.monotonic(), start_deg)]
        intensities: list[tuple[float, float]] = []
        self._sample_frame(intensities)
        if self._abort:
            return positions, intensities

        self._kdc.move_to(end_deg, wait=False)
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            if self._abort:
                self._kdc.stop()
                break
            pos = self._kdc.get_position_deg()
            positions.append((time.monotonic(), pos))
            self._sample_frame(intensities)
            if abs(pos - end_deg) <= self._POSITION_ARRIVAL_TOL_DEG:
                break
            time.sleep(self._POSITION_POLL_S)
        return positions, intensities

    def _correlate_minimum(
        self,
        positions: "list[tuple[float, float]]",
        intensities: "list[tuple[float, float]]",
    ) -> "tuple[float, float] | None":
        """Interpolate the stage angle at each intensity sample's timestamp and
        return the (angle, intensity) pair at the minimum, or None if nothing
        usable was collected."""
        if len(positions) < 2 or not intensities:
            return None
        ts_pos = [p[0] for p in positions]
        angles = [p[1] for p in positions]
        best: tuple[float, float] | None = None
        for ts, intensity in intensities:
            if ts < ts_pos[0] or ts > ts_pos[-1]:
                continue
            angle = _lerp(ts, ts_pos, angles)
            if best is None or intensity < best[1]:
                best = (angle, intensity)
        return best

    # ── Fine pass: stepped, waiting for a fresh frame at each step ──────────

    def _read_fresh(self) -> "Frame | None":
        """Block until a frame newer than the last one consumed arrives, after
        the fine-pass settle time, up to a bounded timeout."""
        time.sleep(self._FINE_SETTLE_S)
        deadline = time.monotonic() + self._FRESH_FRAME_TIMEOUT_S
        while time.monotonic() < deadline:
            if self._abort:
                return None
            frame = self._read_latest()
            if frame is not None and (
                self._last_seen_ts_ms is None or frame.ts_ms > self._last_seen_ts_ms
            ):
                self._last_seen_ts_ms = frame.ts_ms
                return frame
            time.sleep(self._GAIN_POLL_S)
        return None

    def _scan_stepped(self, center_deg: float) -> "list[tuple[float, float]]":
        """Step ±_FINE_HALF_WINDOW_DEG around *center_deg*, waiting for a fresh
        frame at each step. Returns (angle, intensity) pairs."""
        lo = max(0.0, center_deg - self._FINE_HALF_WINDOW_DEG)
        hi = min(180.0, center_deg + self._FINE_HALF_WINDOW_DEG)
        n = max(2, round((hi - lo) / self._FINE_STEP_DEG) + 1)
        results: list[tuple[float, float]] = []
        for angle in linear_angle_grid(lo, hi, n):
            if self._abort:
                break
            self._kdc.move_to(angle, wait=True)
            frame = self._read_fresh()
            if frame is not None and not math.isnan(frame.intensity):
                results.append((angle, frame.intensity))
        return results


class KDC101HomeWorker(QThread):
    """Runs KDC101 homing off the main thread.

    Shared between MainWindow, Malus tab worker, and Waveplate tab worker so
    each caller does not duplicate the same four lines.
    """

    done = Signal()
    error = Signal(str)

    def __init__(self, kdc: "KDC101Polariser", parent=None) -> None:
        """Store the KDC handle to home when run() executes."""
        super().__init__(parent)
        self._kdc = kdc

    def run(self) -> None:
        """Home the stage, emitting done on success or error on failure."""
        try:
            self._kdc.home()
            self.done.emit()
        except KDC101Error as exc:
            self.error.emit(str(exc))


class PM400PollWorker(QThread):
    """Continuously polls a connected PM400 for power readings off the main thread.

    ``PM400PowerMeter.read_power_W()`` is a blocking VISA call; at the 10 Hz
    acquisition rate ``DataController`` runs at, doing that on the Qt main
    thread (as ``PowerCalibrationWindow`` does at its slower 250 ms rate)
    would stutter the UI. This worker owns the read loop instead and hands
    readings back via a signal.

    A transient read glitch does not stop the loop — only
    ``_DISCONNECT_THRESHOLD`` *consecutive* failures are treated as the meter
    having been unplugged, mirroring ``MainWindow``'s
    ``_KDC_DISCONNECT_THRESHOLD`` for the same reason: a single dropped VISA
    transaction is not proof the device is gone.

    Signals are delivered to the main thread via Qt's automatic queued-connection
    mechanism because the receiver objects live on the main thread.
    """

    power_read = Signal(float)  # watts
    connection_lost = Signal(str)  # last error message

    _POLL_INTERVAL_S = 0.1
    _DISCONNECT_THRESHOLD = 3

    def __init__(self, pm: "PM400PowerMeter", parent=None) -> None:
        """Store the PM400 handle to poll when run() executes."""
        super().__init__(parent)
        self._pm = pm
        self._abort: bool = False

    def abort(self) -> None:
        """Request a clean stop; checked at the top of every poll iteration."""
        self._abort = True

    def run(self) -> None:
        """Poll read_power_W() in a loop until aborted or the meter is declared lost."""
        consecutive_failures = 0
        last_error = ""
        while not self._abort:
            try:
                power_W = self._pm.read_power_W()
            except PM400Error as exc:
                consecutive_failures += 1
                last_error = str(exc)
                Debug.warning(f"PM400PollWorker: read failed ({consecutive_failures}): {exc}")
                if consecutive_failures >= self._DISCONNECT_THRESHOLD:
                    self.connection_lost.emit(last_error)
                    return
            except Exception as exc:
                Debug.error(f"PM400PollWorker: unexpected error: {exc}", exc_info=True)
                self.connection_lost.emit(str(exc))
                return
            else:
                consecutive_failures = 0
                self.power_read.emit(power_W)
            self.msleep(int(self._POLL_INTERVAL_S * 1000))
