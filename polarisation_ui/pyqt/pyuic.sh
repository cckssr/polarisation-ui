#!/bin/bash

# Convert UI files to Python using pyside6-uic
.venv/bin/pyside6-uic ./polarisation_ui/pyqt/mainwindow.ui -o ./polarisation_ui/pyqt/ui_mainwindow.py
.venv/bin/pyside6-uic ./polarisation_ui/pyqt/connection.ui -o ./polarisation_ui/pyqt/ui_connection.py

if [ $? -ne 0 ]; then
    echo "Error converting mainwindow.ui"
    exit 1
fi
echo "UI files converted successfully"