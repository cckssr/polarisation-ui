"""Infrastructure layer - external I/O, device adapters, threading."""

from .logging import Debug
from .config import get_config, import_config

try:
    from .save_service import MeasurementSaveService, SaveService
except ImportError:
    # SaveService might not be fully implemented yet
    MeasurementSaveService = None
    SaveService = None

try:
    from .devices.base import EncoderAdapter, EncoderMock, EncoderSerial
except ImportError:
    pass

__all__ = [
    "Debug",
    "get_config",
    "import_config",
]

if MeasurementSaveService is not None:
    __all__.extend(["MeasurementSaveService", "SaveService"])

if "EncoderAdapter" in dir():
    __all__.extend(["EncoderAdapter", "EncoderMock", "EncoderSerial"])
