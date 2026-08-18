# CLAUDE.md

Guidance for Claude Code when working in this repository. Read this first every session.

## Project Overview

PySide6 desktop app for a **polarisation / Malus-law goniometer bench** built around an Arduino Nano ESP32 firmware.

Hardware surface (fixed — no sensors beyond these are planned):

| Role                 | Device                               | Transport      |
| -------------------- | ------------------------------------ | -------------- |
| Sample angle         | AS5048A #A (14-bit magnetic encoder) | SPI → Arduino  |
| Detector-arm angle   | AS5048A #B                           | SPI → Arduino  |
| Intensity (PD-TIA)   | ADS1220 24-bit ADC                   | SPI → Arduino  |
| PD-TIA discrete gain | 4 GPIO lines, high/low combinations  | Arduino GPIO   |
| Polariser rotation   | Thorlabs KDC101 + PRM1-Z8            | USB (pylablib) |

`calibration_tool/` is a sibling PySide6 app using a KDC101 reference stage to calibrate AS5048A eccentricity/ellipticity errors.

## Phased overhaul in progress

A broad SCPI redesign + UI abstraction is rolling out in phases. Phase tracking lives in the plan file at `~/.claude/plans/analyse-the-current-state-swift-cocoa.md` — `ARCHITECTURE.md` is a project-agnostic architectural blueprint (deliberately reusable elsewhere) and does not track phase status. Items marked **(planned Phase N)** below do not yet exist — do not reference them as implemented code.

## Architecture

Strict 3-layer separation — violations are architecture failures.

```
ui/  →  infrastructure/  →  core/
ui/  →  core/                 (direct when needed)
```

**Forbidden**: `core/ → ui/`, `core/ → infrastructure/`, `infrastructure/ → ui/`.

### UI / Qt Designer separation rule — MANDATORY

**Every visual element in a window or dialog must be declared in its `.ui` file. Python code must never construct Qt widgets, layouts, or dialogs.**

Rules:

- All `QWidget`, `QLabel`, `QPushButton`, `QLayout`, `QGroupBox`, `QLCDNumber`, `QComboBox`, `QTableWidget`, `QAction` (menus), etc. go in `.ui` → regenerate with `pyuic.sh`.
- Python files (`mainwindow.py`, `encoder_debug_window.py`, `acq_settings.py`, `log_window.py`, …) contain **only signal connections, slot logic, and state manipulation** — no widget construction.
- Qt imports in those files are restricted to: base classes (`QMainWindow`, `QDialog`), modal helpers (`QFileDialog`, `QMessageBox`), event types (`QCloseEvent`), and `@Slot` / `QTimer`.
- `QButtonGroup` may be constructed in Python because it is a non-visual logical helper; its buttons must still be declared in the `.ui` file.

**Exceptions (explicitly permitted to build widgets in Python):**

| File                                                                                                           | Reason                                                                                                                                                                                                        |
| -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `power_calibration_window.py`                                                                                  | User-approved exception — no `.ui` counterpart by design                                                                                                                                                      |
| `brewster_curve_plot.py`, `brewster_detector_plot.py`, `malus_curve_plot.py`, `multi_gain_calibration_plot.py` | pyqtgraph custom widgets — Qt Designer cannot host third-party custom widgets                                                                                                                                 |
| `PlotTabBase` subclasses (`brewster_tab.py`, `malus_tab.py`, …)                                                | Not an exception — these load a `Ui_*Tab` from a `.ui` file inside `build()` and promote pyqtgraph plots via `<customwidget>`; `build()` is the wiring hook, not a licence to construct widgets                |
| `log_window.py`                                                                                                | Sanctioned exception: imports `QObject, Qt, Signal, QTextCursor` beyond the usual whitelist for a cross-thread logging bridge (log records arrive off the Qt main thread and must be marshalled via a signal) |

`auto_power_calibration_window.py` now has a `.ui` counterpart (`ui_auto_power_calibration.py`) and is **not** an exception — it follows the normal Designer-first rule.

**Known pre-existing violation** (to be migrated, do not extend further):

- `encoder_debug_window.py` — builds several programmatic tabs/panels on top of `encoder_debug.ui`; scope is large, tracked as tech-debt.

### `polarisation_ui/core/`

Pure Python — **no PySide6, no Qt, no hardware I/O, no serial imports**.

- `models.py` — dataclasses: `AcquisitionSettings`, `DualEncoderReading`, `Frame`, `BrewsterPoint`, `MalusPoint`, `TabExport`.
- `exceptions.py` — `GoniometerError`, `AngleLimitError`, `AngleMismatchError`, `InvalidEncoderReading`, `IncompatibleFirmwareError`, `KDC101Error`, `KDC101TimeoutError`, `PM400Error`.
- `utils.py` — `circular_mean_deg`, `linear_angle_grid`, `windowed_average_intensity`.
- `auto_calibration_settings.py`, `power_calibration.py` — auto-calibration settings and power-calibration logic.
- `ellipsometry.py` — rotating-analyser ellipsometry physics: RAE harmonic fit → (Ψ, Δ), two-phase pseudo-(n, k) inversion, three-phase ambient/film/substrate model fit (numpy grid search, no scipy dependency).

### `polarisation_ui/infrastructure/`

Device adapters, serial I/O, Qt threading helpers, config, logging. No business logic, no UI imports. Qt is **allowed here only inside `qt_threads.py`** — nowhere else in infrastructure.

- `device_manager.py` — `GoniometerDeviceManager` (connect, reconnect, read_angles, diagnostics).
- `devices/dual_encoder.py` — `DualEncoderArduino` SCPI client.
- `devices/kdc101_polariser.py` — KDC101 polariser stage adapter.
- `devices/pm400.py` — PM400 power-meter adapter.
- `mocks/mock_arduino.py` — PTY-based SCPI-speaking simulator for tests.
- `mocks/mock_kdc101_polariser.py`, `mocks/mock_pm400.py` — device mocks.
- `mocks/mock_port_registry.py` — PTY port registry for mock discovery.
- `serial_device.py` — low-level serial/text/PTY I/O with auto-reconnect helpers.
- `qt_threads.py` — `QThread`-based workers (the only Qt usage in this layer).
- `logging.py`, `config.py`, `save_service.py`, `utils.py`.
- `session_journal.py` — append-only autosave (`~/.polarisation-ui/sessions/<ts>/journal.csv`).
- `modules/` — `HostModule` protocol + `ModuleRegistry` singleton; `kdc101_adapter.py` (real adapter wrapping `KDC101Polariser`), `kdc101_stub.py` (always-connected stub for UI development without hardware), `pm400.py` stubs.

### `polarisation_ui/ui/`

PySide6 widgets. Thin event handlers — delegate all logic to core/infrastructure.

- `windows/mainwindow.py` — `MainWindow`.
- `windows/encoder_debug_window.py` — `EncoderDebugDialog` (SCPI terminal, diagnostics).
- `windows/auto_power_calibration_window.py` — automated power-calibration wizard.
- `controllers/data_controller.py` — `DataController` polls at 10 Hz via `QTimer`, emits Qt signals (`angles_updated`, `intensity_updated`, `diagnostics_updated`, `error_occurred`, `retry_connecting`, `reconnect_succeeded`, `connection_lost`, `measurement_started/stopped`).
- `widgets/brewster_curve_plot.py`, `widgets/brewster_detector_plot.py`, `widgets/malus_curve_plot.py`, `widgets/ellipsometry_fit_plot.py`, `widgets/ellipsometry_curve_plot.py` — pyqtgraph plots.
- `widgets/event_log_panel.py` — collapsible event-log panel.
- `widgets/plot_tab_base.py` — `PlotTabBase` abstract base class for experiment tabs.
- `widgets/tab_registry.py` — `TabRegistry` singleton; hides tabs whose `required_modules` are absent.
- `widgets/tabs/brewster_tab.py` — Brewster-angle tab (sample scan + peak finding).
- `widgets/tabs/malus_tab.py` — Malus-law tab (manual analyser-angle entry, averaged intensity).
- `widgets/tabs/waveplate_tab.py` — Wave plate tab (λ/4, λ/2); requires `kdc101` module; drives `KDCSweepWorker` for automated angle sweep.
- `widgets/tabs/ellipsometry_tab.py` — Rotating-analyser ellipsometry tab (manual or `KDCSweepWorker`-driven analyser sweep at a hand-set angle of incidence); requires calibrated power, `kdc101` optional. Physics in `core/ellipsometry.py`.
- `dialogs/`, `common/`.
- Qt Designer files live under `polarisation_ui/pyqt/` (`*.ui` sources, `ui_*.py` generated by `pyuic.sh`).

### Data flow

```
Arduino (SCPI 2.0.x over serial)
  → DualEncoderArduino (parses responses)
  → GoniometerDeviceManager (lifecycle, reconnect)
  → DataController (QTimer 10 Hz, circular averaging)
  → Qt signals
  → MainWindow / plot widgets / PlotTabBase subclasses
```

## Build & Run

**The project uses a `.venv` at the repo root.** Either activate it (`source .venv/bin/activate`) or invoke the interpreter explicitly (`.venv/bin/python`, `.venv/bin/pytest`, …). Do not call the system `python` or `pytest`.

```bash
# Install (dev extras include ruff, pytest-cov)
.venv/bin/pip install -e ".[dev]"

# Run the app
.venv/bin/python main.py

# Run all tests
.venv/bin/pytest tests/

# Single test file
.venv/bin/pytest tests/infrastructure/test_dual_encoder_with_mock.py

# Calibration-tool tests (shared venv)
cd calibration_tool && ../.venv/bin/pytest tests/
```

Firmware (code lives in `./src_arduino/`; PlatformIO is globally available):

```bash
cd src_arduino
pio run                    # build
pio run -t upload          # flash
pio device monitor         # serial monitor (for manual SCPI)
```

## SCPI Reference

The Arduino firmware (v2.1.0) speaks SCPI-style commands over USB serial. **Source of truth: `src_arduino/src/scpi.cpp`** — do not duplicate the full tree here; full documentation is in `docs/scpi-reference.md`. Clients must check `SYST:VERS?` on connect and reject firmware `< 2.0.0` with `IncompatibleFirmwareError`.

Top-level subsystems (as implemented in firmware 2.1.0):

| Subsystem                                                           | Purpose                            | Example                 |
| ------------------------------------------------------------------- | ---------------------------------- | ----------------------- |
| `*IDN?`, `*RST`, `*CLS`, `*TST?`, `*OPC`, `*OPC?`, `*WAI`           | IEEE 488.2 common                  | `*IDN?`                 |
| `MEAS:ENC:ANGL?`, `MEAS:ENC:MAGN?`                                  | One-shot encoder reads             | `MEAS:ENC:ANGL? BOTH`   |
| `MEAS:ADC:VOLT?`, `MEAS:ADC:TEMP?`, `MEAS:ALL?`                     | One-shot ADC reads                 | `MEAS:ADC:VOLT?`        |
| `CONF:ENC:ZERO`, `CONF:ENC:ERR`                                     | Encoder config (zero, error-clear) | `CONF:ENC:ZERO A`       |
| `CONF:ADC:MUX/GAIN/RATE/MODE/FIR/VREF/TEMP/PWR`                     | ADS1220 config                     | `CONF:ADC:VREF EXT`     |
| `CONF:PDTIA:GAIN`                                                   | PD-TIA discrete gain stage         | `CONF:PDTIA:GAIN 2`     |
| `CONF:SRC`, `CONF:RATE`                                             | Streaming sources and rate         | `CONF:SRC ENC:BOTH,ADC` |
| `INIT:CONT ON/OFF`, `INIT`, `ABOR`                                  | Stream control                     | `INIT:CONT ON`          |
| `FETC:ENC:ANGL?`, `FETC:ADC:VOLT?`, `FETC:ALL?`                     | Fetch last frame (aliases MEAS:*)  | `FETC:ALL?`             |
| `READ?`, `READ? ADC`, `READ? ADC:T`                                 | Arm and fetch                      | `READ?`                 |
| `SENS:ADC:*?`, `SENS:PDTIA:GAIN?`, `SENS:SRC?`, `SENS:RATE?`        | Query current config               | `SENS:ADC:VREF?`        |
| `SYST:ERR?`, `SYST:VERS?`, `SYST:UPTIME?`, `SYST:HELP?`, `SYST:DEB` | System/error/version               | `SYST:ERR?`             |
| `DIAG:ENC?`, `DIAG:ADC?`, `DIAG:PDTIA?`, `DIAG:SELF?`               | Diagnostics                        | `DIAG:ADC?`             |

Streaming frame format: `DATA:FRAME seq=<n>,tsMs=<ms>,angA=<deg>,angB=<deg>,adcV=<V>,adcT=<C>,pdGain=<n>,stat=<flags>` (only sources enabled by `CONF:SRC` are included; `seq`, `tsMs`, and `stat` are always present).

## Plot-Tab Extensibility

Experiment tabs will each own their controls + plots and subscribe to the data streams they need.

```python
# polarisation_ui/ui/widgets/tabs/my_experiment.py
class MyExperimentTab(PlotTabBase):
    tab_id = "my_experiment"
    tab_title = "My Experiment"
    required_sources = {"ENC:BOTH", "ADC"}
    required_modules: set[str] = set()   # e.g. {"kdc101"} when KDC is required

    def build(self) -> None:
        # construct layout, plots, controls
        ...

    def on_frame(self, frame: Frame) -> None:
        # per-sample update
        ...
```

Register once in `widgets/tabs/__init__.py`:

```python
TabRegistry.register(MyExperimentTab)
```

Registry hides tabs whose `required_modules` are not currently injected. Malus and Brewster tabs are already registered; `MainWindow` drives tab instantiation through the registry.

## Connection Resilience Policy

- On read failure, poll pauses and `error_occurred` is emitted.
- Reconnect attempts use exponential backoff: 1 s → 2 s → 4 s → 8 s, cap 15 s.
- Reconnect state is surfaced via the status bar; controls are **not** disabled during `RECONNECTING`.
- **Measurement session and buffers survive reconnect** — a gap marker is written to the journal.
- All `CONF:*` state (ADC gain, mux, PD-TIA stage, stream sources/rate) is reapplied automatically on reconnect from a `DesiredState` snapshot.
- Every `frame_ready` is flushed to an append-only session journal (`~/.polarisation-ui/sessions/<ts>/journal.csv`) with `fsync` every ~1 s, so recorded data is durable across crashes or unrecoverable disconnects. Explicit Save exports the journal to the user's chosen file.
- `connection_lost` (backoff cap exhausted) is terminal → modal dialog with "Export partial data" pointing at the journal.
- Orphan journals are detected on startup and surfaced for recovery export.

## Git Workflow

Branch naming: `feat/…`, `fix/…`, `refactor/…`, `docs/…`. Base branch: `main`.

Commits:

- **Batch all changes from one work session into a single commit.** Do not split by file or by sub-step.
- Style: `scope: imperative subject` (e.g. `scpi: bump to 2.0.0 and route ADS1220`), body explains the why.
- Never `push --force` to `main`.
- Never amend unless the user explicitly asks.
- Never skip hooks (`--no-verify`) unless the user explicitly asks.

PRs via `gh pr create`. Use `/review` for code review and `/security-review` for a security pass before opening a PR. Keep the title short; put details in the body.

## Claude Pro — Rate-Limit & Session Directives

Keep main context lean so Pro-plan rate limits go further:

- **Prefer `Grep` / `Glob`** over spawning an `Agent` for targeted lookups. Spawn subagents only for genuinely parallel exploration or multi-file refactors.
- **Never re-read a file you just edited** — the harness tracks state; re-reading only burns cache.
- **Do not generate report / summary `.md` files** unless the user explicitly asks. Work from conversation context.
- Use absolute paths; use `TodoWrite` for multi-step tasks; keep inter-tool narration short.
- **Remind the user to `/clear` or start a new conversation** at the end of a completed task or when the conversation grows long — this drops cache tokens and keeps the next session fast and cheap. Natural boundaries: end of each phase in the plan file, after a commit, after a long debugging session.
- After any phase that changes public APIs or the SCPI tree, run `/update-docs` **(planned Phase 7)** before moving on.

## Testing Conventions

- `pytest` at repo root for `tests/`; `calibration_tool/tests/` has its own suite (same venv).
- **Mock hardware via `MockArduino`** (PTY-based SCPI simulator at `polarisation_ui/infrastructure/mocks/mock_arduino.py`) — do not invent new mock transports.
- **Every resilience change gets a disconnection-path test.** Use `MockArduino.kill_pty()` to tear down the PTY mid-stream and simulate a sudden disconnect.
- Type hints required on new code; no unqualified `Any`.

## Troubleshooting

- **Serial port busy** on connect → close `pio device monitor`, Arduino IDE, or other serial clients; replug USB if the TTY is orphaned.
- **ADS1220 no response** → check CS/DRDY pins in `src_arduino/src/config.h`; `DIAG:ADC?` dumps registers when reachable.
- **Firmware version mismatch** → client queries `*IDN?` on connect and refuses incompatible firmware (< 2.0.0) with `IncompatibleFirmwareError`.
- **PTY mock tests hang on macOS** → confirm `select.select()` path in `MockArduino`; check `mock_arduino.py` daemon thread lifecycle.

## New Feature Workflow

1. Define / extend domain dataclass in `core/models.py`.
2. Add adapter method in `infrastructure/devices/*` (and its mock counterpart in `mocks/mock_arduino.py`).
3. Surface via `DataController` signals or a dedicated controller method.
4. Consume from the owning `PlotTabBase` subclass or existing widget.
5. Add tests alongside: core → pure unit; infrastructure → against `MockArduino`; ui → with `QTest`.
6. Run `/update-docs` (Phase 7+) if the change touches public APIs or SCPI.

## Naming Conventions

| Item                 | Convention                                      |
| -------------------- | ----------------------------------------------- |
| Abstract interfaces  | `{Name}Adapter` or `{Name}Base`                 |
| Mock implementations | `{Name}Mock` or `Mock{Name}`                    |
| Real implementations | `{Name}{Transport}` (e.g. `DualEncoderArduino`) |
| Type hints           | Required; no unqualified `Any`                  |

## Calibration Tool

`calibration_tool/` is a standalone sibling PySide6 app correcting AS5048A misalignment against a Thorlabs KDC101 reference stage. Its own `main.py`, `config.py`, `devices/`, `calibration/`, `plotting/`, `tests/`.

It currently **duplicates** the encoder-client concept (`calibration_tool/devices/arduino_encoder.py` vs. `polarisation_ui/infrastructure/devices/dual_encoder.py`). Consolidation onto the main-app's infrastructure is a deferred follow-up — don't pick it up incidentally. The host-side KDC101 driver is now implemented at `polarisation_ui/infrastructure/devices/kdc101_polariser.py` (using pylablib); `calibration_tool/devices/kdc101_stage.py` is the calibration tool's independent copy.

## Arduino Firmware

PlatformIO project under `./src_arduino/` (Arduino Nano ESP32). All builds and tests execute from within `src_arduino/`. PlatformIO (`pio`) is globally available via `.zshrc`.

Key files:

- `src/main.cpp` — setup/loop dispatcher.
- `src/scpi.cpp` / `scpi.h` — SCPI parser and command dispatcher (source of truth for the protocol).
- `src/encoder.cpp` / `encoder.h` — AS5048A handlers.
- `src/state.cpp` / `state.h` — `ErrorQueue`, `AcqStats`, `StreamConfig`, `AppState`.
- `src/config.h` — pins, firmware identity, baud rate, `FW_VERSION`.
- `lib/AS5048A/` — SPI encoder driver.
- `lib/ADS1220/` — ADS1220 driver (wired into SCPI; all `CONF:ADC:*` / `MEAS:ADC:*` / `DIAG:ADC?` commands are implemented).
