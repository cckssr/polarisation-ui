"""Active-detector identifiers and the shared point-power derivation.

The bench has two mutually-exclusive power detectors: the PD-TIA photodiode
(always present, driven through the Arduino) and an optional Thorlabs PM400
power meter. When the PM400 is connected its sensor head physically replaces
the PD-TIA on the detector arm, so it takes precedence — see
``DataController.set_pm400`` / ``_poll_sensors``. ``Frame.detector`` (and the
matching field on every saved point dataclass) records which one produced
``power_W`` for that sample, so plots, exports and session restore always
agree on provenance.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from polarisation_ui.core.models import Frame

DETECTOR_PDTIA = "pdtia"
DETECTOR_PM400 = "pm400"


def point_power(frame: Frame | None, intensity_V: float) -> tuple[float | None, float | None]:
    """Return ``(power_W, conv_factor_W_per_V)`` for a point measured at *intensity_V*.

    *intensity_V* is the (possibly windowed-averaged) PD-TIA voltage the
    caller has already computed for this point; it is only used when
    *frame* is on the PD-TIA path.

    - ``frame`` is ``None`` or has no usable calibration → ``(None, None)``
    - ``frame.detector == DETECTOR_PM400`` → ``(frame.power_W, None)`` — the
      PM400 measures power directly, so there is no per-volt conversion
      factor to report
    - PD-TIA with a loaded calibration profile → ``(intensity_V * conv, conv)``
    """
    if frame is None:
        return None, None
    if frame.detector == DETECTOR_PM400:
        return frame.power_W, None
    conv = frame.conv_factor_W_per_V
    if conv is None:
        return None, None
    return intensity_V * conv, conv
