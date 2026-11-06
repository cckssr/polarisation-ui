# PySide6 UI Files

This directory contains the PySide6 UI files for the project. These files define the graphical user interface (GUI) components and layouts for the application. Each `.ui` file corresponds to a specific window or dialog in the application, and they can be edited using Qt Designer, a visual design tool for creating GUIs.
The `.ui` files are converted to Python code using the `pyside6-uic` tool, alternative with the script `pyuic.sh`. The generated Python files are then imported and used in the main application code to create and display the GUI.

## Files

- `main_window.ui` → `ui_main_window.py` — main window: toolbar, left dock (device panels), right dock (readout / measurement / save), bottom event-log dock and the central experiment tab widget.
- `arduino_panel.ui`, `stage_panel.ui` (used for the sample and the detector stage), `kdc_panel.ui`, `detector_panel.ui` (PD-TIA | PM400 pages), `readout_panel.ui`, `measurement_panel.ui`, `save_panel.ui` → `ui_<form>.py` — the dock panels, promoted in `main_window.ui` (classes in `polarisation_ui/ui/widgets/panels/`).
- `acq_settings.ui` → `ui_acq_settings.py` — acquisition averaging settings dialog.
- `auto_power_calibration.ui` → `ui_auto_power_calibration.py` — automated power-calibration wizard dialog.
- `brewster_tab.ui` → `ui_brewster_tab.py` — Brewster-angle experiment tab.
- `malus_tab.ui` → `ui_malus_tab.py` — Malus-law experiment tab.
- `waveplate_tab.ui` → `ui_waveplate_tab.py` — Wave plate (λ/4, λ/2) experiment tab.
- `encoder_debug.ui` → `ui_encoder_debug.py` — encoder/ADC debug dialog (SCPI terminal, diagnostics); several tabs are still built programmatically on top of this (tracked as tech-debt in `CLAUDE.md`).
- `event_log_panel.ui` → `ui_event_log_panel.py` — collapsible event-log dock panel.
- `log_window.ui` → `ui_log_window.py` — application log viewer window.

Regenerate every generated file after editing its `.ui` source via `pyuic.sh` (or `pyside6-uic` directly) — never hand-edit `ui_*.py`.
