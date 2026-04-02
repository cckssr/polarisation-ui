# Polarisation-UI – Polarisation Experiment Control GUI

A GUI application for polarisation experiments with manual goniometers. The application passively reads two angles (e.g. polariser/analyser) exclusively via magnetic encoders and simultaneously captures the current detection value from a photodetector. There is no motorised control of the rotation stages.

## Design Goals

- **Experiment-agnostic**: UI and backend are designed to support other experiments with angle + sensor signals
- **Clear separation of concerns**: Device I/O, data acquisition, logging, and UI are cleanly decoupled
- **Manual experiments first**: Focus on live display, stability monitoring, and explicit measurement point capture
- **Reproducibility**: Complete metadata (encoder offsets, units, sampling rates, device IDs)

## GUI Layout (Main Window)

### Left Panel – Devices & Status

- **Encoder A/B**: Angle (deg), update rate, zero/tare, health/errors
- **Photodetector**: Current value, range/gain/integration time, overrange status
- **Acquisition**: Start/stop stream, sampling rate

### Center Panel – Live View (Main Area)

- **Large numerical displays**: Angle A, Angle B, Detection value
- **Tabs**:
  - Time series (detection value vs. time)
  - Scatter / Polar plot (detection value vs. angle)
- **Visual status indicators**: Signal OK / Overrange / Dropouts

### Right Panel – Logging

- **Run control**: New run, start/stop logging, export
- **Manual point capture ("Capture Point")**:
  - Saves Angle A/B + detection value + timestamp
  - Optional averaging / stability checking
  - Table of measurement points + event log

### Bottom – Status Bar

- RUNNING / IDLE / ERROR, sampling rate, dropped samples, timestamp

## Data

- **Per measurement point**: Timestamp, Encoder A/B (raw + calibrated), detection value, flags
- **Per run**: Device IDs, firmware, calibration parameters, units, user/project
- **Export**: CSV + JSON metadata (optional HDF5/Zarr)

## Scope

- No motor control
- No automated scanning (movement is manual)
- Focus on robust live display, clean logging, and extensibility

This repository provides the UI and architectural foundation; specific devices are integrated via exchangeable adapters.
