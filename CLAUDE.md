# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the application
python main.py

# Install (development mode)
pip install -e .
pip install -e ".[dev]"   # includes Black, flake8, pytest-cov

# Run all tests
pytest tests/

# Run a single test file
pytest tests/test_goniometer_system.py
pytest tests/infrastructure/test_dual_encoder_with_mock.py

# Calibration tool tests
cd calibration_tool && pytest tests/
```

## Architecture

Strict 3-layer separation — violations are architecture failures:

```
ui/  →  infrastructure/  →  core/
ui/  →  core/               (direct when needed)
```

**Forbidden**: `core/ → ui/`, `core/ → infrastructure/`, `infrastructure/ → ui/`

### Core (`polarisation_ui/core/`)
Pure Python — no PySide6, no Qt, no hardware I/O. Contains:
- `models.py` — dataclasses (`GoniometerState`, `EncoderReading`, `MeasurementPoint`)
- `services.py` — business logic (`GoniometerService`)
- `exceptions.py` — domain errors

Key constraint: `GoniometerState` enforces `detector_angle = 2 × sample_angle` (physical geometry).

### Infrastructure (`polarisation_ui/infrastructure/`)
Device adapters, serial I/O, threading, config. No business logic, no UI imports. Contains:
- `device_manager.py` — lifecycle management for encoder connections
- `devices/base.py` — abstract `EncoderAdapter` interface
- `devices/dual_encoder.py` — `DualEncoderArduino` (real hardware, SCPI-conformant serial)
- `devices/mock_arduino.py` — `MockArduino` for testing without hardware
- `qt_threads.py` — Qt threading helpers only

### UI (`polarisation_ui/ui/`)
PySide6 widgets only. Thin event handlers — delegate logic to core services. Uses Qt Designer `.ui` files (under `ui/pyqt/`). Data acquisition runs at ~10 Hz via `controllers/data_controller.py` using Qt signals for thread-safe UI updates.

## Data Flow

```
Arduino (serial/SCPI) → DualEncoderArduino → DataController (Qt thread)
  → Qt signals → MainWindow → GoniometerService → GoniometerState → UI widgets
```

## Naming Conventions

| Item | Convention |
|------|-----------|
| Abstract interfaces | `{Name}Adapter` or `{Name}Base` |
| Mock implementations | `{Name}Mock` or `Mock{Name}` |
| Real implementations | `{Name}{Transport}` (e.g. `EncoderSerial`) |
| Type hints | Always required; no unqualified `Any` |

## New Feature Workflow

1. Define domain model in `core/models.py`
2. Add service method in `core/services.py`
3. Create adapter interface + mock in `infrastructure/devices/`
4. Build UI component and integrate into `ui/windows/mainwindow.py`

## Calibration Tool

Standalone app in `calibration_tool/` for correcting AS5048A magnetic encoder misalignment using a Thorlabs KDC101 motorized reference stage. Has its own `main.py`, `config.py`, `devices/`, `calibration/`, `plotting/`, and `tests/`.

## Arduino Firmware

Located in `src_arduino/`, built with PlatformIO (Arduino Nano ESP32). Uses SCPI-conformant serial protocol for dual AS5048A encoder readout.
