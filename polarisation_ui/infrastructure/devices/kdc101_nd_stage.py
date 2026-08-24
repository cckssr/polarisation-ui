"""KDC101 motorised ND-filter stage adapter using pylablib.

Wraps pylablib's KinesisMotor with a simple connect/home/move/read API for a
Thorlabs MTS50/M-Z8 linear stage carrying a gradient neutral-density filter,
used as the beam-intensity actuator in place of (or alongside) a rotating
polariser. Positions are always in millimetres at this class's public API.

pylablib's built-in "MTS50-Z8" scale reports position in *metres*
(``get_scale_units()`` returns ``"m"`` for this stage — see
``pylablib.devices.Thorlabs.kinesis._get_step_scale``), unlike "PRM1-Z8"
which is natively in degrees. So this class converts at the boundary: the
shared base's ``_move_to``/``_get_position*`` always talk metres to
pylablib, and the mm-named methods here do the ×1000 / ÷1000 conversion.

Do NOT use raw APT messages here — all communication goes through pylablib.
"""

from __future__ import annotations

from polarisation_ui.infrastructure.devices.kdc101_base import KDC101MotorBase
from polarisation_ui.infrastructure.logging import Debug

_MTS50_Z8_SCALE = (
    "MTS50-Z8"  # built-in pylablib scale for the MTS50/M-Z8 stage; native unit is metres
)

_MM_PER_M = 1000.0

_POSITION_STABLE_M = 5e-6  # 5 µm — positions within this delta count as "the same"

TRAVEL_MM = 50.0  # full mechanical travel of the MTS50/M-Z8


class KDC101NDStage(KDC101MotorBase):
    """Drive a Thorlabs KDC101 + MTS50/M-Z8 linear stage with a gradient ND filter mounted.

    All positions at this class's public API are expressed in millimetres
    (pylablib's native unit for this scale is metres; conversion happens
    here). Unlike the continuous PRM1-Z8 rotation stage, the MTS50/M-Z8 has
    hard travel limits, so ``move_to_mm`` clamps its target to
    ``[0, TRAVEL_MM]``.

    Usage::

        nd = KDC101NDStage()
        nd.connect("27123456")
        nd.home()
        nd.move_to_mm(25.0)
        print(nd.get_position_mm())
        nd.disconnect()
    """

    _SCALE = _MTS50_Z8_SCALE
    _POSITION_STABLE_DELTA = _POSITION_STABLE_M

    # ── Motion ────────────────────────────────────────────────────────────────

    def move_to_mm(self, position_mm: float, wait: bool = True, timeout: float = 60.0) -> None:
        """Move to *position_mm*, clamped to the stage's ``[0, TRAVEL_MM]`` travel.

        Raises ``KDC101TimeoutError`` on timeout, ``KDC101Error`` on other errors.
        """
        clamped = max(0.0, min(TRAVEL_MM, position_mm))
        if clamped != position_mm:
            Debug.warning(
                f"KDC101NDStage: move_to_mm({position_mm:.3f}) clamped to "
                f"{clamped:.3f} (travel is [0, {TRAVEL_MM}] mm)"
            )
        self._move_to(clamped / _MM_PER_M, wait=wait, timeout=timeout)

    def get_position_mm(self) -> float:
        """Return the current position in millimetres."""
        return self._get_position() * _MM_PER_M

    def get_position_mm_nowait(self) -> float | None:
        """Non-blocking position read for UI polling.

        Returns ``None`` instead of blocking when the stage is currently busy
        servicing another call, so a Qt main-thread display timer never stalls
        the GUI waiting on serial I/O.
        """
        pos_m = self._get_position_nowait()
        return None if pos_m is None else pos_m * _MM_PER_M
