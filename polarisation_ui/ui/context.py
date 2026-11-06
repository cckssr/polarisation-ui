"""Application context: configuration, shared status hub and every controller."""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject

from polarisation_ui.core.auto_calibration_settings import AutoCalibrationConnectionSettings
from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.infrastructure.devices.kdc101_polariser import KDC101Polariser
from polarisation_ui.infrastructure.devices.pm400 import PM400PowerMeter
from polarisation_ui.infrastructure.session_state import SESSION_STATE_PATH
from polarisation_ui.ui.controllers.connection_controller import ConnectionController
from polarisation_ui.ui.controllers.data_controller import DataController
from polarisation_ui.ui.controllers.detector_controller import DetectorController
from polarisation_ui.ui.controllers.kdc_controller import KdcController
from polarisation_ui.ui.controllers.measurement_controller import MeasurementController
from polarisation_ui.ui.controllers.pm400_controller import PM400Controller
from polarisation_ui.ui.controllers.session_controller import SessionController
from polarisation_ui.ui.controllers.status import StatusHub

if TYPE_CHECKING:  # the mocks are not part of the production wheel, see create()
    from polarisation_ui.infrastructure.simulation import SimulatedBench


def simulation_available() -> bool:
    """Whether the mock devices for ``--simulate`` are installed (not in the release wheel)."""
    from importlib.util import find_spec

    return find_spec("polarisation_ui.infrastructure.mocks") is not None


def _simulated_bench() -> SimulatedBench:
    # Imported here: the production wheel leaves out infrastructure.mocks, and a normal start
    # must not depend on them.
    from polarisation_ui.infrastructure.simulation import SimulatedBench

    return SimulatedBench()


@dataclass
class AppContext:
    """Everything the main window and the tabs share. Build it with :meth:`create`."""

    config: AppConfig
    status: StatusHub
    data: DataController
    connection: ConnectionController
    detector: DetectorController
    kdc: KdcController
    pm400: PM400Controller
    measurement: MeasurementController
    session: SessionController
    simulation: SimulatedBench | None = None
    _scratch: tempfile.TemporaryDirectory[str] | None = None

    @classmethod
    def create(
        cls,
        config: AppConfig,
        simulate: bool = False,
        persist: bool = True,
        parent: QObject | None = None,
    ) -> AppContext:
        """Build all controllers.

        ``simulate`` swaps every device for the mocks of :class:`SimulatedBench`. ``persist=False``
        reads and writes no user files: no session state, no orphan scan, and the measurement
        journals go to a scratch directory that :meth:`shutdown` removes.
        """
        bench = _simulated_bench() if simulate else None
        scratch = None if persist else tempfile.TemporaryDirectory(prefix="polarisation-ui-")
        journal_base = Path(scratch.name) if scratch is not None else None

        status = StatusHub(parent)
        device_manager = GoniometerDeviceManager(use_mock=simulate)
        data = DataController(device_manager, parent, config=config, journal_base=journal_base)
        connection = ConnectionController(
            config,
            device_manager,
            data,
            status,
            fixed_ports=[bench.port] if bench is not None else None,
            parent=parent,
        )
        detector = DetectorController(config, data, status, connection, parent=parent)
        measurement = MeasurementController(config, data, status, detector, parent=parent)
        saved = AutoCalibrationConnectionSettings.load() if persist else None
        kdc_device = bench.kdc if bench is not None else KDC101Polariser()
        pm400_device = bench.pm400 if bench is not None else PM400PowerMeter()
        kdc = KdcController(
            config,
            data,
            detector,
            status,
            kdc=kdc_device,
            list_devices=kdc_device.list_devices,
            parent=parent,
        )
        pm400 = PM400Controller(
            config,
            data,
            status,
            pm400=pm400_device,
            list_resources=pm400_device.list_resources,
            preferred_resource=saved.pm400_visa_resource if saved else "",
            wavelength_nm=(saved.wavelength_nm if saved and saved.wavelength_nm else 633.0),
            parent=parent,
        )
        session = SessionController(
            config,
            status,
            data,
            connection,
            kdc,
            pm400,
            detector,
            measurement,
            state_path=SESSION_STATE_PATH if persist else None,
            journal_base=journal_base,
            parent=parent,
        )
        return cls(
            config=config,
            status=status,
            data=data,
            connection=connection,
            detector=detector,
            kdc=kdc,
            pm400=pm400,
            measurement=measurement,
            session=session,
            simulation=bench,
            _scratch=scratch,
        )

    def shutdown(self) -> None:
        """Stop measurement, polling and workers, close all devices (window close)."""
        self.session.shutdown()
        if self.data.is_measuring():
            self.data.stop_measurement()
        self.connection.shutdown()
        self.pm400.shutdown()
        self.kdc.shutdown()
        if self.simulation is not None:
            self.simulation.stop()
        if self._scratch is not None:
            self._scratch.cleanup()
