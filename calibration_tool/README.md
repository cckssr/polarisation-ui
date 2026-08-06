# AS5048A Encoder Calibration Tool

Standalone tool for calibrating AS5048A magnetic encoders using a Thorlabs KDC101-controlled reference stage.

## Purpose

When the magnet on an AS5048A encoder is not perfectly centered, systematic angular errors occur. This tool helps:

1. **Measure** the error pattern over a full rotation
2. **Analyze** the error components (eccentricity, ellipticity)
3. **Visualize** in a polar plot showing where to adjust the magnet
4. **Recommend** the direction to move the magnet for better alignment

## Requirements

```bash
pip install pyserial numpy matplotlib PySide6 pylablib
```

`analyze_detector.py` (see below) additionally needs `scipy` — included in `requirements.txt`.

## Hardware Setup

- **Arduino** with AS5048A encoder connected (running the firmware from `src_arduino/`)
- **Thorlabs KDC101** controller with PRM1/MZ8 rotation stage
- Both stages mechanically coupled (your manual stage mounted on the motorized stage)

## Configuration

Edit `config.py` to set your serial ports:

```python
# Arduino port (use `ls /dev/cu.*` to find)
ARDUINO_PORT = "/dev/cu.usbmodem1101"

# KDC101 port
KDC101_PORT = "/dev/cu.usbserial-27000001"
KDC101_SERIAL = "27000001"  # Your controller's serial number
```

## Usage

### 1. Start the Application

```bash
cd calibration_tool
python main.py
```

### 2. Connect Devices

1. Enter the correct ports in the connection panel
2. Click "Connect All"
3. Use "Identify KDC" to verify the correct Thorlabs controller

### 3. Perform Calibration

1. Set a unique run name
2. Click "▶ Start"
3. **Manually rotate** the stage using the Thorlabs controller (the jog wheel or software)
4. Rotate through at least one full revolution (360°)
5. Click "■ Stop"

### 4. Analyze Results

- Click "Analyze" to compute error statistics
- The **polar plot** shows error magnitude vs. angle:
  - Large radius = large error at that angle
  - The arrow indicates the recommended direction to move the magnet
- The **Cartesian plot** shows error vs. reference angle:
  - Sinusoidal patterns indicate eccentricity (1x) or ellipticity (2x)

### 5. Save/Export

- **Save CSV**: Store measurement data for later analysis
- **Export Plot**: Save the visualization as PNG/PDF

## Interpreting Results

### 1x Component (Eccentricity)

- Caused by magnet center offset from rotation axis
- Shows as single sinusoidal wave per revolution
- **Fix**: Move magnet in the indicated direction

### 2x Component (Ellipticity)

- Caused by non-uniform magnetic field
- Shows as two waves per revolution
- **Fix**: Replace magnet or improve mounting

### Error Magnitude Guide

| 1x Amplitude | Assessment                        |
| ------------ | --------------------------------- |
| < 0.1°       | Excellent                         |
| 0.1° - 0.5°  | Good                              |
| 0.5° - 1.0°  | Moderate (adjustment recommended) |
| 1.0° - 2.0°  | Significant (adjustment needed)   |
| > 2.0°       | Large (major adjustment required) |

## Detector Calibration Analysis

`analyze_detector.py` is a standalone CLI script (no GUI, unrelated to the encoder
calibration workflow above) that analyzes a saved PD-TIA power-calibration profile —
the JSON produced by `polarisation_ui.core.power_calibration.PowerCalibrationProfile.save()`
in the main app's power-calibration tools.

For each PD-TIA gain stage present in the file, it fits a watts-per-volt linear
regression via `scipy.stats.linregress` and reports:

- Slope (W/V) and intercept (dark/zero-light offset, W)
- R² and RMSE of the fit, plus max residual
- Dynamic range in dB
- Cross-gain sensitivity ratios and voltage-range overlap/gaps between adjacent gain
  stages

By default it also renders a 6-panel figure (linear- and log-scale linearity, fit
residuals, and bar charts for dynamic range, R², and slope per gain stage).

### Usage

```bash
cd calibration_tool
python analyze_detector.py Det_A.json                     # report + interactive plot
python analyze_detector.py Det_A.json --no-plot            # report only
python analyze_detector.py Det_A.json --save-plot Det_A_analysis.png
```

## File Structure

```
calibration_tool/
├── main.py                       # GUI application
├── config.py                     # Configuration
├── requirements.txt              # Dependencies
├── manual_calibration_dialog.py  # Manual (jog-wheel) calibration dialog
├── analyze_detector.py           # Standalone CLI: PD-TIA power-calibration fit/report
├── devices/
│   ├── arduino_encoder.py        # AS5048A via Arduino
│   └── kdc101_stage.py           # Thorlabs KDC101 serial
├── calibration/
│   ├── measurement.py            # Data acquisition
│   ├── manual_runner.py          # Manual-calibration run controller
│   └── analysis.py               # Error analysis
├── plotting/
│   └── polar_plot.py             # Visualization
└── tests/                        # pytest suite (same venv as the main app)
```

## Notes for macOS

- Thorlabs Kinesis DLLs are Windows-only
- This tool uses direct APT serial protocol communication
- KDC101 requires RTS/CTS hardware flow control
- Use `ls /dev/cu.*` to find available serial ports
