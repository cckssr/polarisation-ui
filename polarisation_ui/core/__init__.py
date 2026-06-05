"""Core domain logic layer - pure Python, no Qt/PySide6 dependencies."""

from .exceptions import (
    AngleLimitError,
    AngleMismatchError,
    GoniometerError,
    IncompatibleFirmwareError,
    InvalidEncoderReading,
)

__all__ = [
    "GoniometerError",
    "AngleLimitError",
    "AngleMismatchError",
    "InvalidEncoderReading",
    "IncompatibleFirmwareError",
]
