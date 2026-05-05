# PySide6 UI Files

This directory contains the PySide6 UI files for the project. These files define the graphical user interface (GUI) components and layouts for the application. Each `.ui` file corresponds to a specific window or dialog in the application, and they can be edited using Qt Designer, a visual design tool for creating GUIs.
The `.ui` files are converted to Python code using the `pyside6-uic` tool, alternative with the script `pyuic.sh`. The generated Python files are then imported and used in the main application code to create and display the GUI.

## Files

- `mainwindow.ui`: Defines the main window of the application, including the layout, widgets, and their properties. Primary interface.
  - converts to `ui_mainwindow.py`.
- `mock_main.py`: Mock implementation without backend logic, used for testing and development of the UI components.
