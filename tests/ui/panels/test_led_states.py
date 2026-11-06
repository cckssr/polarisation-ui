"""The LED vocabulary of the controllers maps to the project's LED styles."""

from __future__ import annotations

from polarisation_ui.ui.common.status_led import LED_STATE_STYLES
from polarisation_ui.ui.controllers import status


def test_every_controller_led_state_has_a_style() -> None:
    states = {status.LED_OFF, status.LED_OK, status.LED_BUSY, status.LED_WARN, status.LED_ERROR}
    assert states == set(LED_STATE_STYLES)
