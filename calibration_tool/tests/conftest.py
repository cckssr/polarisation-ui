"""
Pytest configuration for calibration_tool tests.
"""

import pytest


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--hardware",
        action="store_true",
        default=False,
        help="Run tests that require actual hardware connected",
    )


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "hardware: mark test as requiring actual hardware (deselect with '-k not hardware')",
    )


def pytest_collection_modifyitems(config, items):
    """Skip hardware tests unless --hardware flag is provided."""
    if config.getoption("--hardware"):
        # --hardware given: don't skip hardware tests
        return

    skip_hardware = pytest.mark.skip(reason="need --hardware option to run")
    for item in items:
        if "hardware" in item.keywords:
            item.add_marker(skip_hardware)
