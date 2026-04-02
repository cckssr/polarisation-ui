"""
Quick demo script to test the goniometer system.

Run as module (recommended):
    python -m polarisation_ui.ui.windows.goniometer_demo

Or run directly:
    python polarisation_ui/ui/windows/goniometer_demo.py
"""

import sys
from pathlib import Path

# Handle both direct script execution and module imports
# If running as a direct script, add parent to path
if __name__ == "__main__":
    # Add project root to path for direct execution
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from polarisation_ui.ui.windows.goniometer_main_window import GoniometerMainWindow


def main():
    """Run the goniometer demo."""
    app = QApplication(sys.argv)

    window = GoniometerMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
