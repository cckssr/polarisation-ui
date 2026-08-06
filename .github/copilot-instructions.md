# Copilot Instructions – Polarisation-UI

This repository's authoritative agent guidance lives in [`CLAUDE.md`](../CLAUDE.md)
at the repository root — read it before making changes. It covers the 3-layer
architecture (`core/` → `infrastructure/` → `ui/`), the Qt Designer separation
rule, the SCPI protocol reference, build/test commands, and naming conventions.

Key points to internalise before editing:

- **Strict layering**: `core/` is pure Python (no Qt, no hardware I/O);
  `infrastructure/` adapts devices/config/threading (Qt only in
  `infrastructure/qt_threads.py`); `ui/` holds PySide6 widgets that delegate
  logic to the layers below. See `CLAUDE.md` → **Architecture**.
- **UI widgets are declared in Qt Designer `.ui` files**, not constructed in
  Python — see `CLAUDE.md` → **UI / Qt Designer separation rule** for the
  full rule and its documented exceptions.
- **Tests**: `.venv/bin/pytest tests/` at the repo root; `calibration_tool/`
  has its own suite in the same venv. Mock hardware via `MockArduino`
  (`polarisation_ui/infrastructure/mocks/mock_arduino.py`).
- **SCPI protocol**: source of truth is `src_arduino/src/scpi.cpp`; see
  `docs/scpi-reference.md` for the full command reference.

Do not duplicate that guidance here — if it drifts, fix `CLAUDE.md` and this
file stays a stable pointer.
