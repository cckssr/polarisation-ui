#!/bin/bash

# Convert UI files to Python using pyside6-uic
.venv/bin/pyside6-uic ./polarisation_ui/pyqt/mainwindow.ui -o ./polarisation_ui/pyqt/ui_mainwindow.py
.venv/bin/pyside6-uic ./polarisation_ui/pyqt/acq_settings.ui -o ./polarisation_ui/pyqt/ui_acq_settings.py
.venv/bin/pyside6-uic ./polarisation_ui/pyqt/encoder_debug.ui -o ./polarisation_ui/pyqt/ui_encoder_debug.py
.venv/bin/pyside6-uic ./polarisation_ui/pyqt/log_window.ui -o ./polarisation_ui/pyqt/ui_log_window.py
.venv/bin/pyside6-uic ./polarisation_ui/pyqt/auto_power_calibration.ui -o ./polarisation_ui/pyqt/ui_auto_power_calibration.py

if [ $? -ne 0 ]; then
    echo "Error converting UI files"
    exit 1
fi
echo "UI files converted successfully"