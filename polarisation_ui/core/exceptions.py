"""Domain-specific exceptions for goniometer control system.

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
    """Raised when detector and probe angles don't follow the 2x relationship.

    This indicates either a mechanical misalignment or encoder malfunction.
    """

    pass


class InvalidEncoderReading(GoniometerError):
    """Raised when encoder returns invalid or out-of-range values."""

    pass


class IncompatibleFirmwareError(GoniometerError):
    """Raised when firmware version is incompatible with the Python client (requires >= 2.0.0)."""

    pass


class ActuatorError(Exception):
    """Base for failures of any intensity actuator (KDC101 polariser, ND stepper).

    Lets sweep workers handle "the thing that varies beam intensity failed"
    without knowing which concrete device they are driving.
    """

    pass


class KDC101Error(ActuatorError):
    """Raised when KDC101 motor controller communication fails."""

    pass


class KDC101TimeoutError(KDC101Error):
    """Raised when a KDC101 move or home operation times out."""

    pass


class NDStageError(ActuatorError):
    """Raised when the ND-filter stepper controller (ESP32 + DRV8825) fails."""

    pass


class NDStageTimeoutError(NDStageError):
    """Raised when an ND-stage move or home operation times out."""

    pass


class PM400Error(Exception):
    """Raised when PM400 power meter communication fails."""

    pass
