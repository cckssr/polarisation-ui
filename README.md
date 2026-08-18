# Polarisation-UI

[![CI](https://github.com/cckssr/polarisation-ui/actions/workflows/ci.yml/badge.svg)](https://github.com/cckssr/polarisation-ui/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

Desktop application for polarisation experiments on a manual goniometer bench. The application reads two absolute magnetic encoder angles (sample stage and detector arm) and an ADS1220 photodiode intensity simultaneously over SCPI from an Arduino Nano ESP32. Angle changes are manual by default; an optional Thorlabs KDC101 + PRM1-Z8 motorised stage drives the automated wave-plate sweep and power-calibration workflows. The focus is on stable live display, reproducible point capture, and clean export.

Experiments supported out of the box: Malus's Law, Brewster's angle, and wave plates (λ/4, λ/2). Additional experiments (optical rotation, Fresnel coefficients, ellipsometry) are planned as pluggable tab modules — see [Roadmap](#roadmap).

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

| Component            | Role                                                      | Interface         |
| -------------------- | --------------------------------------------------------- | ----------------- |
| Arduino Nano ESP32   | SCPI 2.1.0 host — runs firmware in `src_arduino/`         | USB serial        |
| AS5048A (encoder A)  | 14-bit magnetic rotary encoder — sample/polariser stage   | SPI → Arduino     |
| AS5048A (encoder B)  | 14-bit magnetic rotary encoder — detector/analyser arm    | SPI → Arduino     |
| ADS1220              | 24-bit delta-sigma ADC — photodiode transimpedance output | SPI → Arduino     |
| PD-TIA discrete gain | 4-bit GPIO-controlled transimpedance gain stage           | 4× GPIO → Arduino |
| Thorlabs KDC101      | Motorised rotation stage for automated angle scanning     | USB (pylablib)    |

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

### Ellipsometry

The bench doubles as a rotating-analyser ellipsometer (RAE): fixed polariser (azimuth `P`) → sample at angle of incidence `θ` → rotating analyser (KDC101, optionally rotated by hand) → photodetector. The analyser intensity is a two-harmonic function of its azimuth `A`:

```math
I(A) = I₀ · [1 + α·cos(2A) + β·sin(2A)]
```

fit exactly (linear least squares, no iterative solver) to recover `α, β`, then converted to the ellipsometric angles:

```math
tan(Ψ) = √((1+α)/(1-α)) · |tan(P)|,   cos(Δ) = β / √(1-α²)
```

A rotating-analyser ellipsometer only measures `cos(Δ)`, so the sign of `Δ` is fundamentally undetermined (a compensator would be needed to resolve it) — this is surfaced in the tab and in export metadata, not hidden. `(Ψ, Δ)` at one angle of incidence inverts in closed form to a pseudo refractive index `(n, k)` for a bare sample; a series across several angles of incidence (set by hand, since the sample/detector arm are not motorised) additionally fits a 3-phase ambient/film/substrate model for thickness and film index, reporting alternative thickness solutions where the single-wavelength measurement is periodically ambiguous. See `polarisation_ui/core/ellipsometry.py` for the full derivation and `EllipsometryTab` for the workflow.

---

## Installation

### Production (from GitHub)

```bash
pip install git+https://github.com/cckssr/polarisation-ui.git
```

To pin to a specific release:

```bash
pip install git+https://github.com/cckssr/polarisation-ui.git@v1.0.0
```

The production wheel does **not** include the mock Arduino simulator or test utilities.

### Development Installation

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
┌──────────────────────────────────────────────────────────────────────────────┐
│  polarisation_ui                                                             │
│                                                                              │
│  ┌────────────────┐   ┌──────────────────────┐   ┌────────────────────────┐  │
│  │ ui/.           │──▶│ infrastructure/      │──▶│ core/                  │  │
│  │                │   │                      │   │                        │  │
│  │   windows/     │   │   device_manager     │   │   models.py            │  │
│  │   widgets/     │   │   devices/           │   │   power_calibration.py │  │
│  │   controllers/ │   │     dual_encoder     │   │   exceptions.py        │  │
│  │   dialogs/     │   │     kdc101_polariser │   │   utils.py             │  │
│  └────────────────┘   │     pm400            │   └────────────────────────┘  │
│         │             │   serial_device      │                               │
│         └────────────▶│   qt_threads         │                               │
│                       │   config, logging    │                               │
│                       │   save_service       │                               │
│                       │   session_journal    │                               │
│                       └──────────────────────┘                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Allowed dependencies:** `ui → infrastructure → core`, `ui → core` directly when needed.

**Forbidden:** `core → ui`, `core → infrastructure`, `infrastructure → ui`.

**Qt (PySide6)** is allowed only in `ui/` and `infrastructure/qt_threads.py`.

**Core** is pure Python — no Qt, no serial, no hardware I/O.

### Data Flow

```ascii
Arduino Nano ESP32 (SCPI 2.1.0 over USB serial)
  ↓
DualEncoderArduino  ← parses SCPI responses, drives ADCClient
  ↓
GoniometerDeviceManager  ← connection lifecycle, auto-reconnect
  ↓
DataController  ← QTimer 10 Hz, circular angle averaging, Qt signals
  ↓
Qt signals: angles_updated, intensity_updated, diagnostics_updated,
            error_occurred, retry_connecting, reconnect_succeeded,
            connection_lost, measurement_started/stopped
  ↓
MainWindow, PlotTabBase subclasses (MalusTab, BrewsterTab, WaveplateTab, EllipsometryTab)
```

### Testing

The test suite runs against `MockArduino` — a PTY-based SCPI 2.1.0 simulator that produces Malus-law-correct intensity without real hardware.

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

- Python 3.10+
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
│       └── widgets/tabs/     # Experiment tabs: malus_tab, brewster_tab, waveplate_tab
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
- **Wave Plate (λ/4, λ/2)** tab — KDC101-driven automated angle sweep; records averaged intensity vs. waveplate angle; exports with `qwp`/`hwp` filename token and sweep metadata
- **Ellipsometry** tab — rotating-analyser ellipsometry (RAE): manual or KDC101-driven analyser sweep at a hand-set angle of incidence, live `I(A) = I₀(1 + α·cos2A + β·sin2A)` fit → (Ψ, Δ) per AOI, multi-AOI series with pseudo-(n, k), and a bare-substrate / film-on-substrate optical-model fit (see [Ellipsometry](#ellipsometry) below)
- **KDC101 motorised stage** — pylablib driver (`KDC101Polariser`): connect by serial number, home, move_to, get_position_deg, enable; `KDC101ModuleAdapter` wires it into `ModuleRegistry`; `MockKDC101Polariser` for headless tests
- **Plot-Tab extensibility** — `PlotTabBase` + `TabRegistry`; new experiments register as subclasses in `ui/widgets/tabs/`
- **Session journal** — append-only CSV autosave with `fsync` for crash-safe data recovery
- **Module registry** — `HostModule` protocol + `ModuleRegistry` singleton; tabs gate on required modules (e.g. `kdc101`)

### Planned: Additional Polarisation Experiments

Brewster's angle, wave plates (λ/4, λ/2), and ellipsometry are already
implemented — see `BrewsterTab` / `WaveplateTab` / `EllipsometryTab` in the
Implemented list above. Each experiment below is a still-planned
`PlotTabBase` subclass to be registered in `polarisation_ui/ui/widgets/tabs/`.
All would work in manual mode immediately; automated scanning can reuse the
KDC101-driven sweep pattern already implemented in `WaveplateTab`.

| Experiment                                      | Physics                         | Key Observable                                                                       |
| ----------------------------------------------- | ------------------------------- | ------------------------------------------------------------------------------------ |
| **Optical Rotation (chiral media)**             | Biot: `[α] = α / (l·c)`         | Specific rotation of sugar solutions at varying concentration                        |
| **Fresnel Coefficients**                        | `Rs`, `Rp` vs incidence angle   | Experimental verification with adjustable refractive-index fit overlay               |
| **Birefringence / wave plate characterisation** | Retardance `Γ` from ellipticity | Characterise unknown wave plates beyond fixed λ/4, λ/2 (full-wave, custom retarders) |

#### Optical Rotation (Detail)

Fill a cuvette of known path length `l` with a sugar solution of concentration `c`. Set the analyser (Encoder B) to the intensity minimum (null method) — the rotation angle directly gives the optical activity. Repeat at multiple concentrations and apply Biot's law to determine the specific rotation `[α]_λ`. This experiment requires stable monochromatic illumination.

### Planned: Infrastructure

| Feature          | Description                                         |
| ---------------- | --------------------------------------------------- |
| HDF5/Zarr export | Optional dense export for large angle-scan datasets |

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
