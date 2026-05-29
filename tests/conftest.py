"""Shared pytest fixtures and CLI option registration.

Hardware tests are opt-in: pass --kdc101-port and/or --pm400-visa on the
command line to enable them.  Without those flags every hardware test is
skipped automatically.

Examples:
--------
# Mock-only tests (default):
    pytest tests/

# With a real KDC101 connected:
    pytest tests/ --kdc101-port=27266999

# With a real PM400:
    pytest tests/ --pm400-visa="USB0::0x1313::0x8078::P0000001::INSTR"

# Both:
    pytest tests/ --kdc101-port=27266999 \
                  --pm400-visa="USB0::0x1313::0x8078::P0000001::INSTR"
"""

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--kdc101-port",
        default=None,
        metavar="PORT",
        help=(
            "Serial-number or port path for a connected KDC101+PRM1-Z8 stage "
            "(e.g. '27266999' or '/dev/cu.usbserial-27266999').  "
            "Required to run hardware tests in test_kdc101_polariser_hw.py."
        ),
    )
    parser.addoption(
        "--pm400-visa",
        default=None,
        metavar="VISA",
        help=(
            "VISA resource string for a connected Thorlabs PM400 "
            "(e.g. 'USB0::0x1313::0x8078::P0000001::INSTR').  "
            "Required to run hardware tests in test_pm400_hw.py."
        ),
    )


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def kdc101_port(request: pytest.FixtureRequest) -> str | None:
    """Return the --kdc101-port value, or None if not provided."""
    return request.config.getoption("--kdc101-port")


@pytest.fixture(scope="session")
def pm400_visa(request: pytest.FixtureRequest) -> str | None:
    """Return the --pm400-visa value, or None if not provided."""
    return request.config.getoption("--pm400-visa")


@pytest.fixture
def connected_kdc(kdc101_port: str | None):
    """Yield a connected KDC101Polariser for hardware tests.

    Skips the test automatically if --kdc101-port was not provided.
    Disconnects after the test regardless of outcome.
    """
    if kdc101_port is None:
        pytest.skip("--kdc101-port not provided; skipping hardware test")

    from polarisation_ui.infrastructure.devices.kdc101_polariser import KDC101Polariser

    kdc = KDC101Polariser()
    kdc.connect(kdc101_port)
    yield kdc
    kdc.disconnect()


@pytest.fixture
def connected_pm400(pm400_visa: str | None):
    """Yield a connected PM400PowerMeter for hardware tests.

    Skips the test automatically if --pm400-visa was not provided.
    Disconnects after the test regardless of outcome.
    """
    if pm400_visa is None:
        pytest.skip("--pm400-visa not provided; skipping hardware test")

    from polarisation_ui.infrastructure.devices.pm400 import PM400PowerMeter

    pm = PM400PowerMeter()
    pm.connect(pm400_visa)
    yield pm
    pm.disconnect()
