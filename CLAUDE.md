# CLAUDE.md

Guidance for Claude Code when working in this repository. Read this first every session.

## Project Overview

PySide6 desktop app for a **polarisation / Malus-law goniometer bench** built around an Arduino Nano ESP32 firmware.

Hardware surface (fixed — no sensors beyond these are planned):

| Role                 | Device                                                           | Transport               |
| -------------------- | ---------------------------------------------------------------- | ----------------------- |
| Sample angle         | AS5048A #A (14-bit magnetic encoder)                             | SPI → Arduino           |
| Detector-arm angle   | AS5048A #B                                                       | SPI → Arduino           |
| Intensity (PD-TIA)   | ADS1220 24-bit ADC                                               | SPI → Arduino           |
| PD-TIA discrete gain | 4 GPIO lines, high/low combinations                              | Arduino GPIO            |
| Polariser rotation   | Thorlabs KDC101 + PRM1-Z8                                        | USB (pylablib)          |
| ND-filter wheel      | Axial variable ND + stepper, ESP32 + DRV8825 (`src_nd_stepper/`) | USB serial (SCPI-style) |

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

### UI rules (oct-ui style) — MANDATORY

The UI follows the cross-project skill **`pyside-designer-ui`** (`~/.claude/skills/pyside-designer-ui/SKILL.md`); load it before any UI work. Project specifics:

- **Designer only.** Every widget, layout, dock, toolbar action and tab page is declared in a `.ui` file under `polarisation_ui/pyqt/`; Python only loads the form, applies strings, wires signals and updates state. Allowed in Python: base classes, `QFileDialog`/`QMessageBox`, event types, `QTimer`, `QSettings`, `QButtonGroup` (buttons in the `.ui`), adding items into Designer-declared containers (tabs, table rows, combo items, plot curves). There are **no exceptions** any more — the former ones (power calibration window, encoder debug dialog) are Designer forms now. pyqtgraph plot wrappers (`widgets/*_plot.py`) build only pyqtgraph content.
- **Object names** use the oct prefixes (`button`, `label` (caption), `value` (live value), `spin`, `combo`, `check`, `radio`, `edit`, `group`, `table`, `scroll`, `dock`, `action`, `led`, `lcd`, `tab`, `*Plot`).
- **Strings.** All user-visible German strings live in `polarisation_ui/config.json`: `ui.<form>.<objectName>[@tooltip|suffix|prefix|placeholder|title|tab]` (applied by `ui/i18n.py::apply_strings`), code-read texts as `ui.<form>.<snake_key>` via `config.text(...)`, status/warning/error texts as `messages.<area>.<key>` via `config.message(...)`, tab titles as `ui.tabs.<tab_id>`, plot labels as `ui.plots.*`. No German literal in Python (tests check this per module); code, logs and tests stay English.
- **Workflow for a form change:** edit the `.ui` → add strings to `config.json` → `polarisation_ui/pyqt/pyuic.sh <form>` (syncs the config texts into the `.ui`, regenerates `ui_<form>.py`) → wire signals. `.venv/bin/python -m polarisation_ui.pyqt.preview <form> --watch` shows a form without logic. `tests/ui/test_designer_forms.py` fails when a form and the config drift apart.
- **Config access:** `infrastructure/config.py` — `load_config(path=None, overrides=None, profile=None) -> AppConfig`, `default_config()` (cached); widgets and dialogs take `config: AppConfig | None = None`. `import_config()` is a deprecated shim.
- **Plots** take background/foreground from the window palette (`ui/plot_style.py::style_plot`) and series colours from `plot_colors`; never hard-code `setBackground("w")`.
- **Profiles** (`profiles` in `config.json`): `expert` (default, full UI) and `student` ("Praktikum", hides the encoder debug window and every entry to the calibration windows). `profiles.<p>.hidden_widgets` names Designer objects per root (`main_window`, panel names, tab ids); typos are reported by `ui/profile.py::apply_profile` and the tests. Code never checks the profile name.
- **Screens:** the main window must fit 1920×1080 with both docks and 1366×768 with the right dock collapsed (`tests/ui/test_small_screens.py`).
- `log_window.py` keeps its cross-thread logging bridge (`QObject`, `Signal`, `QTextCursor` imports).

### `polarisation_ui/core/`

Pure Python — **no PySide6, no Qt, no hardware I/O, no serial imports**.

- `models.py` — dataclasses: `AcquisitionSettings`, `DualEncoderReading`, `Frame`, `BrewsterPoint`, `MalusPoint`, `TabExport`.
- `exceptions.py` — `GoniometerError`, `AngleLimitError`, `AngleMismatchError`, `InvalidEncoderReading`, `IncompatibleFirmwareError`, `KDC101Error`, `KDC101TimeoutError`, `PM400Error`.
- `utils.py` — `circular_mean_deg`, `linear_angle_grid`, `windowed_average_intensity`.
- `auto_calibration_settings.py`, `power_calibration.py` — auto-calibration settings and power-calibration logic.
- `nd_filter.py`, `nd_linearity.py` — ND-wheel usable-range analysis and OD-vs-angle linearity / repeatability analysis over several scans.
- `ellipsometry.py` — rotating-analyser ellipsometry physics: RAE harmonic fit → (Ψ, Δ), two-phase pseudo-(n, k) inversion, three-phase ambient/film/substrate model fit (numpy grid search, no scipy dependency).

### `polarisation_ui/infrastructure/`

Device adapters, serial I/O, Qt threading helpers, config, logging. No business logic, no UI imports. Qt is **allowed here only inside `qt_threads.py`** — nowhere else in infrastructure.

- `device_manager.py` — `GoniometerDeviceManager` (connect, reconnect, read_angles, diagnostics).
- `devices/dual_encoder.py` — `DualEncoderArduino` SCPI client.
- `devices/kdc101_polariser.py` — KDC101 polariser stage adapter.
- `devices/nd_stepper.py` — `NDStepperStage` client for the ND-filter wheel controller (angles in degrees, negative angles allowed — zero is only a reference; protocol documented in `src_nd_stepper/src/main.cpp`).
- `devices/intensity_actuator.py` — `PolariserActuator` / `NDFilterActuator` used by the power-calibration sweeps; device failures derive from `ActuatorError`.
- `devices/pm400.py` — PM400 power-meter adapter.
- `mocks/mock_arduino.py` — PTY-based SCPI-speaking simulator for tests.
- `mocks/mock_kdc101_polariser.py`, `mocks/mock_pm400.py`, `mocks/mock_nd_stage.py` — in-memory device mocks.
- `mocks/mock_nd_stepper_firmware.py` — PTY-based simulator of the ND-stepper firmware, for `NDStepperStage` protocol tests.
- `mocks/mock_port_registry.py` — PTY port registry for mock discovery.
- `serial_device.py` — low-level serial/text/PTY I/O with auto-reconnect helpers.
- `qt_threads.py` — `QThread`-based workers (the only Qt usage in this layer).
- `logging.py`, `config.py`, `save_service.py`, `utils.py`.
- `session_journal.py` — append-only autosave (`~/.polarisation-ui/sessions/<ts>/journal.csv`).
- `modules/` — `HostModule` protocol + `ModuleRegistry` singleton; `kdc101_adapter.py` (real adapter wrapping `KDC101Polariser`), `kdc101_stub.py` (always-connected stub for UI development without hardware), `pm400.py` stubs.

### `polarisation_ui/ui/`

PySide6 widgets and controllers. Thin event handlers — logic lives in controllers, core and infrastructure.

- `windows/main_window.py` — `MainWindow(config, simulate, persist)`: toolbar, left dock `dockControls` (Arduino, sample/detector stage, KDC101, detector panels), right dock `dockMeasurement` (readouts + gain, measurement, save panels), central experiment tabs, bottom `dockEventLog`; layout persisted per profile in `QSettings`. `windows/auxiliary_windows.py` opens the dialogs below.
- `launcher.py` — `Launcher` builds the window for a profile and rebuilds it on a profile switch (reconnects devices). `profile.py` — `apply_profile`, `profile_roots`.
- `context.py` — `AppContext` (config + all controllers), `create(config, simulate, persist)`; `simulate=True` runs on `infrastructure/simulation.py::SimulatedBench` (mocks), also via `main.py --simulate`.
- `controllers/` — `connection_controller.py` (Arduino), `kdc_controller.py`, `pm400_controller.py`, `detector_controller.py` (PD-TIA gain + auto-switch, calibration profile, dark tare), `measurement_controller.py` (start/stop/reset, file name, save), `session_controller.py` (session state, orphan journals), `status.py` (`StatusHub`), `data_controller.py` (`DataController`, 10 Hz poll, Qt signals `frame_ready`, `angles_updated`, `intensity_updated`, `power_updated`, `error_occurred`, `retry_connecting`, `reconnect_succeeded`, `connection_lost`, …). Controllers never touch widgets.
- `widgets/panels/` — one Designer form + thin `QGroupBox` class per dock panel (signals + setters, no device access).
- `widgets/tab_host.py` — tab creation, module gating, `hidden_tabs`, required stream sources, event fan-out. `widgets/plot_tab_base.py`, `widgets/tab_registry.py`, `widgets/tab_title.py` (`TabTitle` descriptor → `ui.tabs.<tab_id>`).
- `widgets/tabs/` — `brewster_tab.py`, `malus_tab.py`, `waveplate_tab.py` (requires `kdc101`), `ellipsometry_tab.py` (physics in `core/ellipsometry.py`), `power_drift_tab.py`.
- `widgets/*_plot.py` — pyqtgraph plots (labels from `ui.plots`); `widgets/event_log_panel.py`, `elided_label.py`, `vscroll.py` (`lock_vertical_scroll`).
- `windows/encoder_debug_window.py` (SCPI terminal, diagnostics), `power_calibration_window.py`, `auto_power_calibration_window.py`, `log_window.py`; `dialogs/acq_settings.py`; `common/` (status LED, status bar, dialogs, PM400 combo, busy check, session prompts).
- `i18n.py` (`apply_strings`), `plot_style.py` (`style_plot`, `plot_colors`).
- Qt Designer files live under `polarisation_ui/pyqt/` (`*.ui` sources, `ui_*.py` generated by `pyuic.sh`, plus `sync_texts.py` and `preview.py`).

### Data flow

```
Arduino (SCPI 2.0.x over serial)
  → DualEncoderArduino (parses responses)
  → GoniometerDeviceManager (lifecycle, reconnect)
  → DataController (QTimer 10 Hz, circular averaging)
  → Qt signals
  → controllers (connection, detector, measurement, …) / TabHost
  → MainWindow panels / plot widgets / PlotTabBase subclasses
```

## Build & Run

**The project uses a `.venv` at the repo root.** Either activate it (`source .venv/bin/activate`) or invoke the interpreter explicitly (`.venv/bin/python`, `.venv/bin/pytest`, …). Do not call the system `python` or `pytest`.

```bash
# Install (dev extras include ruff, pytest-cov)
.venv/bin/pip install -e ".[dev]"

# Run the app (--simulate: mock devices, --profile expert|student)
.venv/bin/python main.py
.venv/bin/python main.py --simulate --profile student

# Regenerate Designer modules (all forms or the named ones) / preview a form
polarisation_ui/pyqt/pyuic.sh [form ...]
.venv/bin/python -m polarisation_ui.pyqt.preview main_window --watch

# Run all tests (Qt tests headless)
QT_QPA_PLATFORM=offscreen .venv/bin/pytest tests/

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
    tab_title = TabTitle()               # German title from config.json ui.tabs.my_experiment
    required_sources = {"ENC:BOTH", "ADC"}
    required_modules: set[str] = set()   # e.g. {"kdc101"} when KDC is required

    def build(self) -> None:
        # load Ui_MyExperimentTab from my_experiment_tab.ui, apply_strings, wire signals
        ...

    def on_frame(self, frame: Frame) -> None:
        # per-sample update
        ...
```

Register once in `widgets/tabs/__init__.py`:

```python
TabRegistry.register(MyExperimentTab)
```

`TabHost` instantiates registered tabs, hides those whose `required_modules` are not injected or that the active profile lists in `hidden_tabs`; `MainWindow` never names a concrete tab. Add the tab's form strings under `ui.my_experiment_tab` and its title under `ui.tabs.my_experiment`.

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
- UI tests use the `window` / `connected` fixtures of `tests/ui/conftest.py` (`MainWindow(config, simulate=True, persist=False)`, QSettings redirected) — hardware is never required. Controller tests live in `tests/ui/controllers/`, panel tests in `tests/ui/panels/`.
- Required UI guards: `test_designer_forms.py` (forms ↔ config), string-key resolution per form, `test_small_screens.py`, `test_profile.py`.

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

## ND-Stepper Firmware

Separate PlatformIO project under `./src_nd_stepper/` (generic ESP32 + DRV8825) that turns the axial ND-filter wheel. Build/flash from that directory (`pio run`, `pio run -t upload`). Pin map, microstepping, gear ratio and the optional home switch live in `src/config.h`; it reuses the SCPI line parser from `src_arduino/src/scpi_parse.inc`. This is a different device from the encoder/ADC Arduino below.

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
