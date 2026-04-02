"""
Status LED utility for connection indicator widgets.

Provides a reusable function for updating LED + label pairs that
indicate device connection state across different device rows
(Arduino, sample stage, detector, etc.).

LED style constants are built from config.json → ui.status_led.
"""

from PySide6.QtWidgets import QLabel

from polarisation_ui.infrastructure.config import import_config

_led_cfg = import_config().get("ui", {}).get("status_led", {})


def _style(color: str) -> str:
    return f"background-color: {color}; border: 0px; padding: 4px; border-radius: 10px"


LED_GREEN = _style(_led_cfg.get("connected", "#00ff00"))
LED_RED = _style(_led_cfg.get("disconnected", "#ff0b03"))
LED_YELLOW = _style(_led_cfg.get("connecting", "#ffc800"))
LED_GRAY = _style(_led_cfg.get("inactive", "#808080"))


def set_connection_status(led: QLabel, label: QLabel, text: str, style: str) -> None:
    """
    Update a status LED and its accompanying label.

    Args:
        led: QLabel used as a circular LED indicator (styled via stylesheet)
        label: QLabel showing the status text
        text: Status string to display
        style: LED stylesheet string — use LED_GREEN / LED_RED / LED_YELLOW / LED_GRAY
    """
    led.setStyleSheet(style)
    label.setText(text)
