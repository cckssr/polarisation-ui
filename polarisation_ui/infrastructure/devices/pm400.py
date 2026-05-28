"""
Thorlabs PM400 power meter adapter.

Thin wrapper around the pymeasure ThorlabsPM400 driver so no other module in
this package needs to import pymeasure directly.  The PM400 is connected over
USB-TMTC (VISA resource string, e.g. ``"USB0::0x1313::0x8078::P0000001::INSTR"``).

Beamsplitter compensation is applied via the PM400's built-in attenuation
register (SENS:CORR:LOSS:INP:MAGN) so the ``power`` property already returns
the corrected value — no extra maths in the Python client.
"""

import sys
from typing import Optional

from polarisation_ui.core.exceptions import PM400Error
from polarisation_ui.infrastructure.logging import Debug

_ThorlabsPM400 = None
_PYMEASURE_AVAILABLE = False
_PYMEASURE_IMPORT_ERROR: str = ""

# Prefer the bundled local copy (avoids version-skew with the pymeasure package);
# fall back to the installed pymeasure package if the local copy itself can't
# import its base classes (e.g. different pymeasure version).
try:
    from polarisation_ui.infrastructure.modules.pm400 import (
        ThorlabsPM400 as _ThorlabsPM400,
    )

    _PYMEASURE_AVAILABLE = True
except ImportError as _local_exc:
    # Local copy failed — probably because pymeasure base classes differ.
    # Try the installed package directly.
    try:
        from pymeasure.instruments.thorlabs import ThorlabsPM400 as _ThorlabsPM400

        _PYMEASURE_AVAILABLE = True
    except ImportError as _pkg_exc:
        _PYMEASURE_IMPORT_ERROR = (
            f"Local driver: {_local_exc} | pymeasure package: {_pkg_exc}"
        )

_PYVISA_AVAILABLE = False
_PYVISA_IMPORT_ERROR: str = ""

try:
    import pyvisa as _pyvisa

    _PYVISA_AVAILABLE = True
except ImportError as _visa_exc:
    _PYVISA_IMPORT_ERROR = str(_visa_exc)

# Thorlabs vendor ID used to filter VISA resource list
_THORLABS_VID = "0x1313"


class PM400PowerMeter:
    """
    Wrapper around ThorlabsPM400 for use in the auto-calibration routine.

    Usage::

        pm = PM400PowerMeter()
        pm.connect("USB0::0x1313::0x8078::P0000001::INSTR")
        pm.set_wavelength_nm(633.0)
        pm.set_attenuation_dB(3.0)  # beamsplitter loss
        pm.set_averaging(100)
        print(pm.read_power_W())
        pm.disconnect()
    """

    def __init__(self) -> None:
        self._inst: Optional[object] = None

    # ── Connection ────────────────────────────────────────────────────────────

    def connect(self, visa_resource: str) -> None:
        """Open connection to the PM400 at *visa_resource*.

        Raises ``PM400Error`` on failure.
        """
        if not _PYMEASURE_AVAILABLE:
            raise PM400Error(
                f"PM400-Treiber nicht verfügbar — Import fehlgeschlagen:\n"
                f"  {_PYMEASURE_IMPORT_ERROR}\n"
                f"pymeasure in diesem Python-Umgebung installieren:\n"
                f"  {sys.executable} -m pip install pymeasure"
            )
        try:
            inst = _ThorlabsPM400(visa_resource)
            inst.configure = "POW"
            inst.power_unit = "W"
            inst.power_autorange = True
            self._inst = inst
            info = self.sensor_info()
            Debug.info(f"PM400: connected — sensor: {info}")
        except Exception as exc:
            self._inst = None
            raise PM400Error(f"PM400 connect failed ({visa_resource}): {exc}") from exc

    def disconnect(self) -> None:
        if self._inst is not None:
            try:
                self._inst.shutdown()
            except Exception as exc:
                Debug.warning(f"PM400: error during disconnect: {exc}")
            finally:
                self._inst = None
        Debug.info("PM400: disconnected")

    def is_connected(self) -> bool:
        return self._inst is not None

    # ── Measurement ───────────────────────────────────────────────────────────

    def read_power_W(self) -> float:
        """Return the current optical power in watts.

        The value already incorporates the attenuation correction set via
        :meth:`set_attenuation_dB`.

        Raises ``PM400Error`` on communication failure.
        """
        self._require_connected()
        try:
            return float(self._inst.power)
        except Exception as exc:
            raise PM400Error(f"PM400 read_power_W failed: {exc}") from exc

    # ── Configuration ─────────────────────────────────────────────────────────

    def set_wavelength_nm(self, nm: float) -> None:
        """Set the operating wavelength for spectral responsivity correction."""
        self._require_connected()
        try:
            self._inst.wavelength = nm
        except Exception as exc:
            raise PM400Error(f"PM400 set_wavelength_nm({nm}) failed: {exc}") from exc

    def get_wavelength_nm(self) -> float:
        self._require_connected()
        try:
            return float(self._inst.wavelength)
        except Exception as exc:
            raise PM400Error(f"PM400 get_wavelength_nm failed: {exc}") from exc

    def set_attenuation_dB(self, db: float) -> None:
        """Set the user attenuation correction in dB.

        Use this to account for the beamsplitter loss so that *read_power_W*
        returns the power at the detector arm, not the PM400 arm.
        """
        self._require_connected()
        try:
            self._inst.attenuation = db
        except Exception as exc:
            raise PM400Error(f"PM400 set_attenuation_dB({db}) failed: {exc}") from exc

    def get_attenuation_dB(self) -> float:
        self._require_connected()
        try:
            return float(self._inst.attenuation)
        except Exception as exc:
            raise PM400Error(f"PM400 get_attenuation_dB failed: {exc}") from exc

    def set_averaging(self, n: int) -> None:
        """Set the number of samples the PM400 averages per reading."""
        self._require_connected()
        try:
            self._inst.averaging_count = n
        except Exception as exc:
            raise PM400Error(f"PM400 set_averaging({n}) failed: {exc}") from exc

    def zero(self) -> None:
        """Start the dark-current zero adjustment routine."""
        self._require_connected()
        try:
            self._inst.zero()
        except Exception as exc:
            raise PM400Error(f"PM400 zero failed: {exc}") from exc

    def sensor_info(self) -> list:
        """Return sensor identification (name, serial, cal_msg, type, …)."""
        if self._inst is None:
            return []
        try:
            return list(self._inst.sensor_info)
        except Exception:
            return []

    # ── Discovery ─────────────────────────────────────────────────────────────

    @staticmethod
    def list_resources() -> list[str]:
        """Return all VISA resource strings that look like Thorlabs instruments.

        Returns an empty list if pyvisa is not installed or no devices found.
        """
        if not _PYVISA_AVAILABLE:
            Debug.warning(
                f"PM400.list_resources: pyvisa not available ({_PYVISA_IMPORT_ERROR}). "
                f"Install with: {sys.executable} -m pip install pyvisa pyvisa-py"
            )
            return []
        try:
            rm = _pyvisa.ResourceManager()
            resources = rm.list_resources()
            return [r for r in resources if _THORLABS_VID.lower() in r.lower()]
        except Exception as exc:
            Debug.warning(f"PM400.list_resources: {exc}")
            return []

    # ── Internal ──────────────────────────────────────────────────────────────

    def _require_connected(self) -> None:
        if self._inst is None:
            raise PM400Error("PM400 is not connected")
