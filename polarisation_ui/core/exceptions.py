"""
Domain-specific exceptions for goniometer control system.

These exceptions represent business logic errors and should only
be raised and handled in the core layer.
"""


class GoniometerError(Exception):
    """Base exception for goniometer-related errors."""
    pass


class AngleLimitError(GoniometerError):
    """Raised when angle exceeds mechanical limits."""
    pass


class AngleMismatchError(GoniometerError):
    """
    Raised when detector and probe angles don't follow the 2x relationship.
    
    This indicates either a mechanical misalignment or encoder malfunction.
    """
    pass


class InvalidEncoderReading(GoniometerError):
    """Raised when encoder returns invalid or out-of-range values."""
    pass


class IncompatibleFirmwareError(GoniometerError):
    """Raised when firmware version is incompatible with the Python client (requires >= 2.0.0)."""
    pass
