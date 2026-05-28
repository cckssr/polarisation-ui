# Polarisation-UI

[![CI](https://github.com/cckssr/polarisation-ui/actions/workflows/ci.yml/badge.svg)](https://github.com/cckssr/polarisation-ui/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

Desktop application for polarisation experiments on a manual goniometer bench. The application reads two absolute magnetic encoder angles (sample stage and detector arm) and an ADS1220 photodiode intensity simultaneously over SCPI from an Arduino Nano ESP32. There is no motor control — all angle changes are manual. The focus is on stable live display, reproducible point capture, and clean export.

Experiments supported out of the box: Malus's Law. Additional experiments (Brewster angle, wave plates, optical rotation, Fresnel coefficients) are planned for Phase 4 as pluggable tab modules.

---

## Table of Contents

- [Hardware](#hardware)
- [Physics Background](#physics-background)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [Development](#development)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Hardware

| Component                  | Role                                                      | Interface         |
| -------------------------- | --------------------------------------------------------- | ----------------- |
| Arduino Nano ESP32         | SCPI 2.0.0 host — runs firmware in `src_arduino/`         | USB serial        |
| AS5048A (encoder A)        | 14-bit magnetic rotary encoder — sample/polariser stage   | SPI → Arduino     |
| AS5048A (encoder B)        | 14-bit magnetic rotary encoder — detector/analyser arm    | SPI → Arduino     |
| ADS1220                    | 24-bit delta-sigma ADC — photodiode transimpedance output | SPI → Arduino     |
| PD-TIA discrete gain       | 4-bit GPIO-controlled transimpedance gain stage           | 4× GPIO → Arduino |
| Thorlabs KDC101 _(future)_ | Motorised rotation stage for automated angle scanning     | USB (Phase 6)     |

The sample and detector stages are mechanically coupled: the detector arm moves at twice the angular velocity of the sample stage (`θ_detector = 2 × θ_sample`), as required by reflection geometry.

### Firmware

Firmware lives under `src_arduino/` and is built with PlatformIO:

```bash
cd src_arduino
pio run            # build
pio run -t upload  # flash to Arduino Nano ESP32
```

---

## Physics Background

### Malus's Law

When linearly polarised light passes through a second polariser (analyser) at angle θ relative to the first, the transmitted intensity follows:

```math
I(θ) = I₀ · cos²(θ)
```

The ADS1220 measures photodiode current proportional to I; Encoder A reads the polariser angle; Encoder B reads the analyser angle. A live cos² fit and peak readout are displayed on the Malus tab.

### Measurement Geometry

```ascii
Light source → Polariser (Encoder A) → Sample/medium → Analyser (Encoder B) → Photodetector (ADS1220)
```

Encoder B is mechanically linked so that a complete detector scan corresponds to a full polarisation state sweep.

---

## Installation

### Production (from GitHub)

```bash
pip install git+https://github.com/cckssr/polarisation-ui.git
```

To pin to a specific release:

```bash
pip install git+https://github.com/cckssr/polarisation-ui.git@v0.1.0
```

The production wheel does **not** include the mock Arduino simulator or test utilities.

### Development

```bash
git clone https://github.com/cckssr/polarisation-ui.git
cd polarisation-ui

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
```

The `dev` extras install `ruff`, `pytest`, `pytest-qt`, and `build`. The mock Arduino simulator is included in editable installs and is used automatically by the test suite.

---

## Usage

```bash
# Launch full measurement UI (connects to real hardware on first run)
polarisation-ui

# Launch encoder debug window only (SCPI terminal, diagnostics)
polarisation-ui --debug-only
```

On first launch the application shows a connection dialog — select the serial port of the Arduino Nano ESP32 and click Connect. The default baud rate is 115200.

### Hardware-Free Testing (Developer Mode)

Run the mock Arduino simulator in one terminal:

```bash
python -m polarisation_ui.infrastructure.mocks.mock_arduino
# Prints: PTY Slave Path: /dev/ttys005
```

Then launch the UI — the mock PTY path appears automatically in the port list (registered via temp file). The simulator generates Malus-law-correct intensity curves.

---

## Configuration

The application is configured via `polarisation_ui/config.json`. Language-specific strings and all tunable parameters live under the `"de"` key. The `"version"` key at the root is managed automatically by CI.

### Key Configuration Parameters

| Key path                            | Type   | Default                           | Description                                             |
| ----------------------------------- | ------ | --------------------------------- | ------------------------------------------------------- |
| `application.name`                  | string | `"Polarisation UI"`               | Window title                                            |
| `debug.level_default`               | string | `"info"`                          | Log level: `verbose`, `info`, `error`, `off`            |
| `connection.max_retry_attempts`     | int    | `10`                              | Serial reconnect attempts before giving up              |
| `connection.backoff_delays_ms`      | list   | `[1000, 2000, 4000, 8000, 15000]` | Exponential backoff sequence                            |
| `timers.acquisition_timer_interval` | int    | `100`                             | Polling interval in ms (10 Hz)                          |
| `timers.gui_update_interval`        | int    | `200`                             | UI refresh interval in ms                               |
| `acquisition.det_averages`          | int    | `5`                               | Circular average window for detector angle              |
| `acquisition.samp_averages`         | int    | `5`                               | Circular average window for sample angle                |
| `acquisition.sample_stage_inverted` | bool   | `true`                            | Invert Encoder A direction                              |
| `acquisition.spike_filter_enabled`  | bool   | `false`                           | Drop readings that jump more than `spike_max_delta_deg` |
| `save.base_folder`                  | string | `"Polarisation"`                  | Root export folder name                                 |
| `ui.theme`                          | string | `"dark"`                          | UI theme: `dark` or `light`                             |

Override the config at runtime by placing a custom `config.json` in the current working directory — it takes priority over the bundled one.

---

## Architecture

The application is organised into three strictly separated layers:

```ascii
┌────────────────────────────────────────────────────────────────────┐
│  polarisation_ui                                                   │
│                                                                    │
│  ┌────────────────┐   ┌───────────────────┐   ┌─────────────────┐  │
│  │ ui/.           │──▶│ infrastructure/   │──▶│ core/           │  │
│  │                │   │                   │   │                 │  │
│  │   windows/     │   │   device_manager  │   │   models.py     │  │
│  │   widgets/     │   │   devices/        │   │   services.py   │  │
│  │   controllers/ │   │     dual_encoder  │   │   exceptions.py │  │
│  │   dialogs/     │   │     base          │   │   utils.py      │  │
│  └────────────────┘   │   serial_device   │   └─────────────────┘  │
│         │             │   qt_threads      │                        │
│         └────────────▶│   config, logging │                        │
│                       │   save_service    │                        │
│                       └───────────────────┘                        │
└────────────────────────────────────────────────────────────────────┘
```

**Allowed dependencies:** `ui → infrastructure → core`, `ui → core` directly when needed.

**Forbidden:** `core → ui`, `core → infrastructure`, `infrastructure → ui`.

**Qt (PySide6)** is allowed only in `ui/` and `infrastructure/qt_threads.py`.

**Core** is pure Python — no Qt, no serial, no hardware I/O.

### Data Flow

```ascii
Arduino Nano ESP32 (SCPI 2.0.0 over USB serial)
  ↓
DualEncoderArduino  ← parses SCPI responses, drives ADCClient
  ↓
GoniometerDeviceManager  ← connection lifecycle, auto-reconnect
  ↓
DataController  ← QTimer 10 Hz, circular angle averaging, Qt signals
  ↓
Qt signals: angles_updated, intensity_updated, measurement_started/stopped
  ↓
MainWindow, MalusCurvePlot, MalusDetectorPlot
  ↓
GoniometerService  ← state transitions (idle → measuring → saving)
```

### Testing

The test suite runs against `MockArduino` — a PTY-based SCPI 2.0.0 simulator that produces Malus-law-correct intensity without real hardware.

```bash
# All tests
QT_QPA_PLATFORM=offscreen .venv/bin/pytest tests/ -v

# Infrastructure tests only
.venv/bin/pytest tests/infrastructure/ -v

# With coverage
.venv/bin/pytest --cov=polarisation_ui --cov-report=term-missing
```

---

## Development

### Prerequisites

- Python 3.9–3.12
- PlatformIO (for firmware builds): `pip install platformio`
- A Unix-like OS for PTY-based tests (macOS / Linux); Windows is supported for the UI but not for the mock simulator

### Project Layout

```ascii
polarisation-ui/
├── polarisation_ui/          # Main Python package
│   ├── core/                 # Pure Python — models, services, exceptions
│   ├── infrastructure/       # Device I/O, config, logging, Qt threads
│   │   ├── devices/          # Encoder, ADC, and optional-module adapters
│   │   ├── mocks/            # MockArduino + mock devices + port registry (dev/test)
│   │   └── modules/          # HostModule protocol + ModuleRegistry singleton
│   └── ui/                   # PySide6 widgets, windows, controllers
│       └── widgets/tabs/     # Experiment tabs (PlotTabBase subclasses)
├── calibration_tool/         # Sibling app — KDC101 encoder calibration
├── src_arduino/              # PlatformIO firmware (Arduino Nano ESP32)
├── tests/                    # pytest suite
├── docs/                     # Technical docs (SCPI reference, encoder debugging)
└── pyproject.toml
```

### Code Style

```bash
ruff format polarisation_ui tests        # format
ruff format --check polarisation_ui tests  # check only (used in CI)
ruff check polarisation_ui tests         # lint
```

### Versioning

Versions follow [PEP 440](https://peps.python.org/pep-0440/) / [Semantic Versioning](https://semver.org/):
`MAJOR.MINOR.PATCH` with optional prerelease suffix (`1.2.3a1`, `1.2.3b2`, `1.2.3rc1`).

To cut a new release, use the **Version Bump** workflow in GitHub Actions:

1. Go to **Actions → Version Bump → Run workflow**
2. Select bump type (`major` / `minor` / `patch`) and optional prerelease suffix
3. The workflow updates `pyproject.toml`, `polarisation_ui/__init__.py`, and `polarisation_ui/config.json`, commits, and pushes a `vX.Y.Z` tag
4. The **Release** workflow fires on the tag and publishes a GitHub Release with wheel and sdist attached

Version is kept in sync across three files automatically:

- `pyproject.toml` — `version = "X.Y.Z"`
- `polarisation_ui/__init__.py` — `__version__ = "X.Y.Z"`
- `polarisation_ui/config.json` — `{"version": "X.Y.Z", "de": {...}}`

---

## Roadmap

### Implemented

- **Malus's Law** — `I = I₀ cos²(θ)`: live cos² fit, peak readout, manual point capture to measurement table, CSV export
- **Brewster's Angle** tab — sample scan, intensity vs. angle display, p/s polarisation selection
- **Plot-Tab extensibility** — `PlotTabBase` + `TabRegistry`; new experiments register as subclasses in `ui/widgets/tabs/`
- **Session journal** — append-only CSV autosave with `fsync` for crash-safe data recovery
- **Module registry** — `HostModule` protocol + `ModuleRegistry` singleton; tabs gate on required modules (e.g. `kdc101`)
- **Connection banner** — non-blocking reconnect status overlay

### Planned: Additional Polarisation Experiments

Each experiment below is a `PlotTabBase` subclass registered in `polarisation_ui/ui/widgets/tabs/`. All work in manual mode immediately; automated scanning requires the KDC101 stage (Phase 6).

| Experiment                                      | Physics                         | Key Observable                                                         |
| ----------------------------------------------- | ------------------------------- | ---------------------------------------------------------------------- |
| **Brewster's Angle**                            | `θ_B = arctan(n₂/n₁)`           | Null in p-polarised reflection → refractive index of sample            |
| **Half-Wave Plate (λ/2)**                       | Output rotation `= 2α`          | Verify Jones matrix: rotate HWP by α → polarisation rotates by 2α      |
| **Quarter-Wave Plate (λ/4)**                    | Linear → elliptical/circular    | Stokes parameters S₁–S₃ from rotating-analyser method                  |
| **Optical Rotation (chiral media)**             | Biot: `[α] = α / (l·c)`         | Specific rotation of sugar solutions at varying concentration          |
| **Fresnel Coefficients**                        | `Rs`, `Rp` vs incidence angle   | Experimental verification with adjustable refractive-index fit overlay |
| **Birefringence / wave plate characterisation** | Retardance `Γ` from ellipticity | Characterise unknown wave plates (λ/4, λ/2, full-wave)                 |
| **Basic Ellipsometry**                          | `Δ`, `Ψ` → film thickness       | Thin film characterisation via Drude approximation                     |

#### Brewster's Angle (Detail)

Place a glass sample on the rotation stage. Sweep incident angle (Encoder A) and record reflected intensity for s- and p-polarisations separately by rotating the analyser (Encoder B) to each orientation. The p-polarised reflection drops to zero at `θ_B`, giving the refractive index directly without a priori knowledge of the material.

#### Half-Wave Plate (Detail)

Insert a λ/2 plate between polariser and analyser. Mount it on Encoder A and rotate it by angle α. The transmitted intensity through a fixed analyser varies as the output polarisation rotates by 2α. A live 2α overlay on the rotation plot allows quick verification of the Jones matrix prediction and determination of the fast-axis orientation.

#### Optical Rotation (Detail)

Fill a cuvette of known path length `l` with a sugar solution of concentration `c`. Set the analyser (Encoder B) to the intensity minimum (null method) — the rotation angle directly gives the optical activity. Repeat at multiple concentrations and apply Biot's law to determine the specific rotation `[α]_λ`. This experiment requires stable monochromatic illumination.

### Planned: Infrastructure

| Feature                  | Description                                                                 |
| ------------------------ | --------------------------------------------------------------------------- |
| HDF5/Zarr export         | Optional dense export for large angle-scan datasets                         |
| KDC101 motorised stage   | Thorlabs USB APT driver, automated angle sweeps for all tab experiments     |
| SCPI 2.0.0 firmware bump | Cleaner subsystem tree, ADS1220 integration, key=value streaming frames     |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Follow the 3-layer architecture (violations are architecture failures, not style issues)
4. Run formatters and linters: `ruff format polarisation_ui tests && ruff check polarisation_ui tests`
5. Run the full test suite: `QT_QPA_PLATFORM=offscreen pytest tests/`
6. Open a PR — the CI workflow runs automatically on push

**Commit style:** `scope: imperative subject` — e.g. `malus: add cos² fit overlay`. One commit per work session (batch related changes).

**New experiments:** Follow the `New Feature Workflow` in `CLAUDE.md` — define a dataclass in `core/models.py`, add a service method, implement a `PlotTabBase` subclass in `ui/widgets/tabs/`, and register it in `TabRegistry`.

---

## License

MIT — see [LICENSE](LICENSE).

---

_Built at TU Berlin — C. Kessler, K. Brandt_
