"""
Qt worker threads for infrastructure-layer blocking operations.

Qt is allowed in this module only. All other infrastructure modules must remain
free of PySide6 imports.
"""

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
        profile = PowerCalibrationProfile(name=p.profile_name)

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

            for angle in angles:
                if self._abort:
                    self.failed.emit("Aborted by user")
                    return

                try:
                    self._kdc.move_to(angle)
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
                    continue
                voltage_mean = sum(voltages) / len(voltages)

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

        self.log.emit("Sweep complete.")
        self.finished.emit(profile)
