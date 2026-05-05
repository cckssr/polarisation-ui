"""
Configuration for AS5048A Calibration Tool.

Edit the serial numbers and ports below to match your setup.
"""

# ============================================================================
# ARDUINO ENCODER CONFIGURATION
# ============================================================================

# Serial port for Arduino (AS5048A encoder)
# macOS: typically /dev/cu.usbmodem* or /dev/cu.usbserial*
# Use `ls /dev/cu.*` to find your port
ARDUINO_PORT = "/dev/cu.usbmodem1101"  # <-- EDIT THIS
ARDUINO_BAUDRATE = 115200

# ============================================================================
# THORLABS KDC101 CONFIGURATION
# ============================================================================

# Serial number of your KDC101 controller (8 digits)
# Find this on the label of your controller
KDC101_SERIAL = "27266999"  # <-- EDIT THIS

# Serial port for KDC101
# macOS: typically /dev/cu.usbserial-* (FTDI chip)
# The port name often contains the serial number
KDC101_PORT = "/dev/cu.usbserial-27266999"  # <-- EDIT THIS
KDC101_BAUDRATE = 115200

# ============================================================================
# MEASUREMENT SETTINGS
# ============================================================================

# Polling interval in seconds (how often to read both encoders)
POLL_INTERVAL = 0.1  # 100ms = 10 readings per second

# Number of full rotations for calibration
NUM_ROTATIONS = 1

# Expected encoder resolution
ENCODER_RESOLUTION = 16384  # 14-bit encoder

# ============================================================================
# STAGE PARAMETERS (PRM1-Z8)
# ============================================================================

# Encoder counts per revolution for PRM1-Z8 stage
# From Thorlabs documentation: 1919.64 encoder counts per degree
PRM1Z8_ENCODER_COUNTS_PER_DEG = 1919.64
PRM1Z8_ENCODER_COUNTS_PER_REV = PRM1Z8_ENCODER_COUNTS_PER_DEG * 360  # ~691,070
