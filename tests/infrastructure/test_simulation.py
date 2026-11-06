"""SimulatedBench: the hardware-free bench behind ``--simulate``."""

from __future__ import annotations

import sys
import time

import pytest

from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.infrastructure.simulation import SimulatedBench

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="PTY not available on Windows")


@pytest.fixture
def bench():
    bench = SimulatedBench(poll_interval_ms=20)
    yield bench
    bench.stop()


def test_the_bench_serves_a_port_the_real_client_can_connect_to(bench) -> None:
    manager = GoniometerDeviceManager(use_mock=True)
    assert manager.connect_encoders(port=bench.port)
    manager.disconnect_all()


def test_the_encoders_keep_turning_without_streaming(bench) -> None:
    first = bench.arduino.encoder_a.current_angle
    time.sleep(0.3)
    assert bench.arduino.encoder_a.current_angle != first


def test_the_drift_can_be_switched_off() -> None:
    bench = SimulatedBench(drift=False)
    try:
        time.sleep(0.2)
        assert bench.arduino.encoder_a.current_angle == 0.0
    finally:
        bench.stop()


def test_the_pm400_mock_reads_power_while_the_stage_is_disconnected(bench) -> None:
    bench.pm400.connect("any")
    assert not bench.kdc.is_connected()
    assert bench.pm400.read_power_W() > 0.0


def test_the_pm400_mock_follows_the_connected_stage_angle(bench) -> None:
    bench.kdc.connect("any")
    bench.pm400.connect("any")
    bench.kdc.move_to(90.0)  # crossed polariser: Malus minimum
    dark = bench.pm400.read_power_W()
    bench.kdc.move_to(0.0)
    assert bench.pm400.read_power_W() > dark


def test_stopping_twice_is_harmless(bench) -> None:
    bench.stop()
    bench.stop()
