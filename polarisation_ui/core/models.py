"""Core domain models for goniometer control system.

This module contains pure Python dataclasses representing the
goniometer state without any Qt or UI dependencies.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AcquisitionSettings:
    """Acquisition settings for the current session.

    Loaded from config at startup; changes made in the settings dialog
    are kept in memory only and are never written back to config.json.
    """

    det_average_on: bool = True
    det_averages: int = 5
    samp_average_on: bool = True
    samp_averages: int = 5
    pdtia_average_on: bool = True
    pdtia_averages: int = 5
    # Hardware flag: the sample-stage magnet is mounted diametrically flipped,
    # so the raw angle increases in the wrong direction.  When True the
    # DataController applies  corrected = (360 - raw) % 360  before emitting.
    sample_stage_inverted: bool = True
    spike_filter_enabled: bool = True
    spike_max_delta_deg: float = 10.0  # 100 °/s at default 10 Hz — rejects glitches

    @classmethod
    def from_config(cls, acq: dict) -> "AcquisitionSettings":
        return cls(
            det_average_on=acq.get("det_average_on", True),
            det_averages=acq.get("det_averages", 5),
            samp_average_on=acq.get("samp_average_on", True),
            samp_averages=acq.get("samp_averages", 5),
            pdtia_average_on=acq.get("pdtia_average_on", True),
            pdtia_averages=acq.get("pdtia_averages", 5),
            sample_stage_inverted=acq.get("sample_stage_inverted", True),
            spike_filter_enabled=acq.get("spike_filter_enabled", True),
            spike_max_delta_deg=acq.get("spike_max_delta_deg", 10.0),
        )


@dataclass
class DualEncoderReading:
    """Semantic paired-angle reading from the device manager (manager layer).

    Uses domain names ``sample_angle`` / ``detector_angle`` rather than the
    raw ``angle_a`` / ``angle_b`` names in ``infrastructure.devices.DualEncoderValue``.
    The device manager maps raw → semantic after reading from the firmware.
    """

    sample_angle: float
    detector_angle: float


@dataclass
class Frame:
    """Consolidated per-sample data frame emitted by DataController at the polling rate.

    ``stat`` is the raw status bitmask from ``DATA:FRAME stat=<n>``:
      bit 0 — Encoder A parity error (transient)
      bit 1 — Encoder B parity error (transient)
      bit 2 — Encoder A persistent error flag (self-latching; clear via CONF:ENC:ERR A)
      bit 3 — Encoder B persistent error flag (self-latching; clear via CONF:ENC:ERR B)
    """

    ts_ms: int
    sample_angle: float
    detector_angle: float
    intensity: float
    pdtia_gain: int = 0
    power_W: Optional[float] = None
    conv_factor_W_per_V: Optional[float] = None
    stat: int = 0  # streaming stat bitmask (see docstring)


@dataclass
class BrewsterPoint:
    """One saved point in the Brewster-angle curve, including power calibration columns."""

    sample_angle: float
    detector_angle: float
    intensity_V: float
    pdtia_gain: int = 0
    power_W: Optional[float] = None
    conv_factor_W_per_V: Optional[float] = None


@dataclass
class MalusPoint:
    """One saved point in the Malus-law curve (manual analyser-angle entry)."""

    analyser_angle: float
    polariser_angle: float
    intensity_V: float
    pdtia_gain: int = 0
    power_W: Optional[float] = None
    conv_factor_W_per_V: Optional[float] = None


@dataclass
class TabExport:
    """Bundle returned by a tab's build_export() for schema-agnostic CSV writing."""

    filename_hint: str
    columns: list[str]
    rows: list[list[str]]
    metadata: dict[str, object]
    filename_tokens: list[str] = field(default_factory=list)
