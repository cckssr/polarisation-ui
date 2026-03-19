#!/bin/bash

# Convert UI files to Python using pyside6-uic
.venv/bin/pyside6-uic ./polarisation_ui/pyqt/mainwindow.ui -o ./polarisation_ui/pyqt/ui_mainwindow.py
.venv/bin/pyside6-uic ./polarisation_ui/pyqt/acq_settings.ui -o ./polarisation_ui/pyqt/ui_acq_settings.py

if [ $? -ne 0 ]; then
    echo "Error converting UI files"
    exit 1
fi
echo "UI files converted successfully"