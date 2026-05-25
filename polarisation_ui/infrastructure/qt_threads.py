"""
Qt worker threads for infrastructure-layer blocking operations.

Qt is allowed in this module only. All other infrastructure modules must remain
free of PySide6 imports.
"""

import dataclasses
import time
from typing import TYPE_CHECKING

from PySide6.QtCore import QThread, Signal

from polarisation_ui.core.auto_calibration_settings import (
    AutoCalibrationParams,
    build_angle_grid,
)
from polarisation_ui.core.exceptions import KDC101Error, PM400Error
from polarisation_ui.core.power_calibration import (
    GainCalibration,
    PowerCalibrationProfile,
)
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.infrastructure.logging import Debug

if TYPE_CHECKING:
    from polarisation_ui.infrastructure.devices.kdc101_polariser import KDC101Polariser
    from polarisation_ui.infrastructure.devices.pm400 import PM400PowerMeter


_SENSOR_INFO_KEYS = ("name", "serial", "calibration_message", "type", "subtype", "flags")


def _parse_sensor_info(raw: list) -> dict:
    """Convert the flat PM400 sensor_info list to a labelled dict."""
    return {
        key: str(raw[i]).strip() if i < len(raw) else ""
        for i, key in enumerate(_SENSOR_INFO_KEYS)
    }


class ReconnectWorker(QThread):
    """
    Off-main-thread reconnection worker.

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
        super().__init__(parent)
        self._device_manager = device_manager

    def run(self) -> None:
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
    """
    Off-main-thread worker that runs a full automated power calibration sweep.

    The caller is responsible for pausing DataController polling before
    calling ``start()`` and for resuming it after ``finished`` or ``failed``
    is emitted.  This worker interacts directly with *device_manager* for
    PDTIA gain and ADC reads; no QTimer involvement here.

    Signals are delivered to the main thread via Qt's queued-connection
    mechanism because the receiver objects live on the main thread.
    """

    gain_started = Signal(int)
    point_recorded = Signal(int, float, float, float, float)
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
        Debug.info("AutoPowerCalibrationWorker: starting sweep")
        try:
            self._run_sweep()
        except Exception as exc:
            Debug.error(
                f"AutoPowerCalibrationWorker: unexpected error: {exc}", exc_info=True
            )
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

            ok = self._device_manager.set_pdtia_gain(gain)
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
                    self.log.emit(
                        f"  Warning: no ADC readings at θ={angle:.2f}°, skipping"
                    )
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

                # First valid point after a saturated prefix: redistribute the
                # remaining angles so they span evenly from here to angle_end.
                if not first_valid_found and profile.gains[gain].n_saturated_skipped > 0:
                    n_left = len(gain_angles) - idx - 1
                    if n_left > 0:
                        sub = dataclasses.replace(
                            p,
                            angle_start_deg=angle,
                            angle_end_deg=p.angle_end_deg,
                            n_points=n_left + 1,
                        )
                        gain_angles[idx + 1 :] = build_angle_grid(sub)[1:]
                        self.log.emit(
                            f"  Grid recalculated: {n_left} remaining points "
                            f"redistributed from {angle:.1f}° to {p.angle_end_deg:.1f}°"
                        )
                first_valid_found = True

                try:
                    power_W = self._pm.read_power_W()
                except PM400Error as exc:
                    self.failed.emit(f"PM400 read failed: {exc}")
                    return

                profile.gains[gain].add_point(voltage_mean, power_W)
                done += 1
                # point_recorded(gain, angle_deg, detector_voltage, pm_power_W, corrected_power_W)
                self.point_recorded.emit(gain, angle, voltage_mean, power_W, power_W)
                self.progress.emit(done, total)
                self.log.emit(
                    f"  θ={angle:.1f}° | V={voltage_mean:.6f} V | P={power_W:.3e} W"
                )
                idx += 1

            n_sat = profile.gains[gain].n_saturated_skipped
            n_rec = len(profile.gains[gain].points)
            if n_sat:
                self.log.emit(
                    f"Gain {gain}: {n_rec} points recorded, "
                    f"{n_sat} skipped (saturated)"
                )

        self.log.emit("Sweep complete.")
        self.finished.emit(profile)


class AlignPolariserWorker(QThread):
    """
    Off-main-thread worker that scans the PM400 while rotating the KDC stage
    to find the physical angle of maximum transmission.

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
        Debug.info("AlignPolariserWorker: starting alignment scan")
        try:
            self._run_scan()
        except Exception as exc:
            Debug.error(f"AlignPolariserWorker: unexpected error: {exc}", exc_info=True)
            self.failed.emit(str(exc))

    def _run_scan(self) -> None:
        n = self._n_points
        step = (self._end - self._start) / (n - 1)
        angles = [self._start + i * step for i in range(n)]

        self.log.emit(
            f"Ausrichtungsscan: {self._start:.1f}°…{self._end:.1f}° "
            f"({n} Punkte, Δθ={step:.2f}°)"
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
