# Copilot Instructions – Polarisation-UI

Polarisation-UI is a desktop application for controlling and monitoring polarisation experiments with manual goniometers, built with PySide6 and Python. This document guides AI agents in maintaining clean architecture and consistency.

---

## AI Agent Constraints (Critical)

**Documentation Language**

- All documentation must be written in **English only**, regardless of the language used in requests or prompts
- Exception: Code comments may reflect variable/function names in any language; documentation (READMEs, guides, instructions) must be English

**Documentation File Creation Policy**

- **Only create new documentation files if:**
  - Explicitly requested by the user, OR
  - Absolutely necessary for the project (e.g., architectural gaps that block development)
- **Never** auto-generate summary documents, changelogs, or similar artifacts
- **Prefer** updating existing documentation over creating new files
- Keep documentation minimal and focused; avoid redundancy with existing docs

---

## Project Context & Phase

- **Project**: Polarisation-UI – Hardware sensor interface + experiment control GUI
- **Current Phase**: **Phase 0 – Architecture & Foundations** (Establishing clean layered structure, mockable device adapters, UI scaffolding)
- **Stack**: Python 3.9+, PySide6 6.5+, NumPy, PyQtGraph, matplotlib, pyserial
- **Key Architecture**: **Strict 3-layer separation** (Core → Infrastructure → UI)
- **Location**: All work in `polarisation-ui/` package and root `main.py`

**Phase 0 Reality Check** – Architecture-first development:

- ✅ Establish clear layer boundaries NOW (before implementation scales)
- ✅ Mockable device adapters from day one
- ✅ Core business logic completely independent of PySide6
- ❌ No PySide6 imports in `core/` or `infrastructure/`
- ❌ No business logic in UI code (`ui/`)

---

## Architecture: The 3-Layer Model (Non-Negotiable)

### Layer Responsibilities

```
┌─────────────────────────────────────────┐
│         UI Layer (ui/)                  │
│    ↓ Displays, user interaction        │
│    ↑ Model state updates (via Qt)      │
└──────────────────┬──────────────────────┘
                   │ (calls, emits signals)
┌──────────────────▼──────────────────────┐
│   Infrastructure Layer (infrastructure/)│
│    ↓ Device adapters, config, threads  │
│    ↑ Structured data to core/          │
└──────────────────┬──────────────────────┘
                   │ (Pure Python I/O)
┌──────────────────▼──────────────────────┐
│         Core Layer (core/)              │
│    Business logic, models, validation   │
│    NO PySide6, NO Qt, Pure Python      │
└─────────────────────────────────────────┘
```

**The Golden Rule**: Data flows UP (core → infrastructure → ui). Business logic lives DOWN (core).

### Layer Definitions

#### Core Layer (`polarisation-ui/core/`)

**Purpose**: Business logic, data models, domain rules. NO framework dependencies.

**What lives here**:

- Data models (measurement points, experiment runs, device settings)
- Business logic (calculations, validation, state management)
- Pure Python services (no PySide6, no Qt, no hardware calls)
- Domain-specific exceptions

**What NEVER lives here**:

- PySide6 imports
- Qt imports
- Hardware I/O (serial, files, network)
- UI code

**Example structure**:

```
core/
├── __init__.py
├── models.py        # Dataclasses: Measurement, ExperimentRun, etc.
├── services.py      # MeasurementService, ExportService, etc.
├── exceptions.py    # DomainError, ValidationError, etc.
└── utils.py         # Pure Python utilities (no domain knowledge)
```

#### Infrastructure Layer (`polarisation-ui/infrastructure/`)

**Purpose**: External interactions, device abstraction, threading, configuration.

**What lives here**:

- Device adapter interfaces (abstract, mockable)
- Concrete hardware implementations (serial I/O, USB, etc.)
- Qt threading helpers (only threading, not UI)
- Configuration management
- File I/O (if not handled by services)

**What NEVER lives here**:

- Business logic
- UI code
- Direct model manipulation

**Example structure**:

```
infrastructure/
├── __init__.py
├── config.py                # Config loading/management
├── devices/
│   ├── __init__.py
│   ├── base.py              # Abstract adapter interfaces
│   ├── encoder.py           # EncoderAdapter implementations
│   ├── photodetector.py     # PhotodetectorAdapter implementations
│   └── mock.py              # Mock implementations for testing
├── threading.py             # Qt threading utilities only
└── serial_io.py             # Serial communication wrapper
```

#### UI Layer (`polarisation-ui/ui/`)

**Purpose**: PySide6 widgets, windows, dialogs. User-facing interface only.

**What lives here**:

- Main window and sub-windows
- Widgets and custom widgets
- Dialogs and pop-ups
- Signal/slot handlers (thin, delegate to core services)
- Qt layouts, styling, rendering

**What NEVER lives here**:

- Business logic (exception: thin event handlers)
- Device I/O (use infrastructure adapters)
- Model creation/manipulation directly

**Example structure**:

```
ui/
├── __init__.py
├── windows/
│   ├── __init__.py
│   └── main_window.py       # Top-level window
├── dialogs/
│   ├── __init__.py
│   ├── experiment_settings.py
│   └── export_dialog.py
├── widgets/
│   ├── __init__.py
│   ├── measurement_display.py
│   ├── plot_widget.py
│   ├── control_panel.py
│   └── status_panel.py
├── common/
│   ├── __init__.py
│   ├── dialogs.py           # Standard Qt dialogs (info, error, etc.)
│   └── utils.py             # UI utilities (icons, colors, etc.)
└── resources/
    └── icons/               # SVG/PNG icons
```

---

## Architectural Patterns

### 1. Device Adapters (Pluggable Hardware Abstraction)

Define **abstract interfaces** in `infrastructure/devices/base.py`:

```python
# infrastructure/devices/base.py
from abc import ABC, abstractmethod
from typing import Optional

class EncoderAdapter(ABC):
    """Abstract interface for angle encoders."""

    @abstractmethod
    def read(self) -> float:
        """Return current angle in degrees."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset to zero."""
        pass
```

Implement **concrete versions** in same module:

```python
# infrastructure/devices/encoder.py
from .base import EncoderAdapter
import serial

class EncoderSerial(EncoderAdapter):
    """Real hardware via serial."""
    def __init__(self, port: str, baudrate: int = 9600):
        self.serial = serial.Serial(port, baudrate)

    def read(self) -> float:
        # Read from hardware
        pass

class EncoderMock(EncoderAdapter):
    """Mock for testing."""
    def __init__(self, start_angle: float = 0.0):
        self.angle = start_angle

    def read(self) -> float:
        return self.angle
```

**Benefits**:

- Easy to test UI without hardware
- Hardware can be swapped or updated
- Clear dependencies

### 2. Core Services (Business Logic Orchestration)

Services in `core/services.py` expose domain operations WITHOUT UI concerns:

```python
# core/services.py
from dataclasses import dataclass
from typing import List
from .models import Measurement, ExperimentRun

class MeasurementService:
    """Manages measurement sessions and data points."""

    def __init__(self):
        self.current_run: Optional[ExperimentRun] = None

    def start_run(self, name: str) -> ExperimentRun:
        """Start a new measurement run."""
        self.current_run = ExperimentRun(name=name)
        return self.current_run

    def add_measurement(self, angle_a: float, angle_b: float,
                       detection: float) -> Measurement:
        """Add a measurement point (no UI, no hardware)."""
        if self.current_run is None:
            raise RuntimeError("No active run")
        point = Measurement(angle_a, angle_b, detection)
        self.current_run.add_point(point)
        return point
```

UI calls these services via slots:

```python
# ui/windows/main_window.py
from polarisation_ui.core.services import MeasurementService

class MainWindow(QMainWindow):
    def __init__(self):
        self.service = MeasurementService()

    def on_capture_button_clicked(self):
        """UI event handler (thin)."""
        angle_a = self.read_angle_a_from_display()  # or from model
        angle_b = self.read_angle_b_from_display()
        detection = self.read_detector_from_display()

        # Delegate to service
        try:
            point = self.service.add_measurement(angle_a, angle_b, detection)
            self.update_display(point)  # Update UI
        except Exception as e:
            self.show_error(str(e))
```

### 3. Data Models (Core Domain Objects)

Simple, immutable (or dataclass-based) models in `core/models.py`:

```python
# core/models.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Measurement:
    """Single measurement point."""
    timestamp: datetime
    angle_a: float
    angle_b: float
    detection_value: float
    flags: dict[str, bool] = None

    def __post_init__(self):
        if self.flags is None:
            self.flags = {"ok": True}

@dataclass
class ExperimentRun:
    """Complete measurement session."""
    name: str
    created_at: datetime
    measurements: list[Measurement] = None

    def __post_init__(self):
        if self.measurements is None:
            self.measurements = []

    def add_point(self, m: Measurement) -> None:
        self.measurements.append(m)
```

**No PySide6 signals or Qt dependencies.**

---

## File & Naming Conventions

| Item              | Convention                         | Examples                             |
| ----------------- | ---------------------------------- | ------------------------------------ |
| **Folders**       | `snake_case`                       | `core/`, `infrastructure/`, `ui/`    |
| **Classes**       | `PascalCase` (especially adapters) | `EncoderAdapter`, `MainWindow`       |
| **Functions**     | `snake_case`                       | `read_encoder()`, `start_run()`      |
| **Constants**     | `UPPER_SNAKE_CASE`                 | `MAX_SAMPLES`, `DEFAULT_BAUDRATE`    |
| **Abstract base** | `{Name}Adapter` or `{Name}Base`    | `EncoderAdapter`, `DeviceBase`       |
| **Mock impl.**    | `{Name}Mock` or `Mock{Name}`       | `EncoderMock`, `MockPhotodector`     |
| **Real impl.**    | `{Name}{Transport}` or `{Name}`    | `EncoderSerial`, `PhotodetectorUSB`  |
| **Type hints**    | Always required                    | `def read() -> float:`, `value: int` |

---

## Dependency Flow (Critical Rules)

### ✅ ALLOWED Dependencies

```
ui/ → infrastructure/ → core/
ui/ → core/           (direct when needed)
infrastructure/ → core/
```

### ❌ FORBIDDEN Dependencies

```
core/ → ui/           (NEVER!)
core/ → infrastructure/ (NEVER! except as return values)
infrastructure/ → ui/ (NEVER!)
```

---

## Development Workflow

### 1. New Feature: Start with Core

```python
# Step 1: Define domain model
# core/models.py → add dataclass

# Step 2: Add service method
# core/services.py → add business logic

# Step 3: Create adapter if needed
# infrastructure/devices/ → define interface + mocks

# Step 4: Build UI
# ui/widgets/ → create PySide6 component
# ui/windows/main_window.py → integrate
```

### 2. Testing Strategy

```bash
# Test core (no dependencies needed)
pytest tests/core/test_services.py

# Test infrastructure with mocks
pytest tests/infrastructure/test_adapters.py

# Test UI with mock adapters/services
pytest tests/ui/test_main_window.py --mock-devices
```

### 3. Running the Application

```bash
# From repository root
python main.py

# Passes mock adapters or real adapters
# depending on configuration
```

---

## What NOT to Do (Phase 0 Architecture Rules)

- ❌ Put PySide6 imports in `core/` or `infrastructure/`
- ❌ Call hardware directly from UI (use adapters in `infrastructure/`)
- ❌ Hardcode configuration (use `infrastructure/config.py`)
- ❌ Create business logic in UI event handlers (delegate to `core/services.py`)
- ❌ Ignore threading/synchronization (use Qt signals for cross-thread updates)
- ❌ Skip type hints (always annotate)
- ❌ Mix device implementations with adapters (separate interfaces and implementations)

---

## When in Doubt

1. **Ask: "Where does this belong?"**

   - Calculation/validation? → `core/`
   - Hardware I/O? → `infrastructure/`
   - Display/interaction? → `ui/`

2. **Check import patterns**: If an import chain goes "down" (ui → core), it's right. If it goes "up", it's wrong.

3. **Model first**: Always define data models before UI.

4. **Adapter first**: Define device adapter interfaces before implementing them.

5. **Service first**: Define business logic services before building UI.

---

## Summary

- **3-layer architecture**: Core (logic) → Infrastructure (I/O) → UI (interaction)
- **No circular dependencies**: Data flows up, logic stays down
- **Mockable from day one**: Device adapters enable testing without hardware
- **Type-hinted Python**: Modern, strict, self-documenting
- **PySide6-only in UI**: Clean separation of concerns
- **Phase 0 is structural**: Get architecture right now, features follow

This foundation enables safe growth and hardware integration.
