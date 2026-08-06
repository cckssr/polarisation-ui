"""Serial communication module for embedded device control.

This module provides a generic serial communication handler for interfacing with
microcontroller-based devices via serial ports. It handles connection management,
data transmission/reception, and automatic reconnection on connection loss.

Features:
    - Generic serial port communication (not limited to Arduino)
    - Automatic reconnection on connection loss
    - Text and binary data handling
    - Configurable timeouts and packet formats
    - Pseudo-terminal (PTY) support for virtual devices
    - Logging of all operations

Classes:
    SerialDevice: Low-level serial communication handler for any microcontroller device.

Usage:
    Initialize and connect to a serial device:

    >>> device = SerialDevice(port="/dev/ttyUSB0", baudrate=115200)
    >>> device.reconnect()
    >>> if device.connected:
    ...     device.send_command("Hello")
    ...     response = device.read_line()

    For virtual devices (testing):

    >>> device = SerialDevice(port="/dev/pts/1", baudrate=115200)
    >>> device.reconnect()  # PTY devices don't require baudrate configuration
"""

from time import sleep, time

import serial

from .logging import Debug


class SerialDevice:
    """Generic serial communication handler for microcontroller devices.

    Provides a flexible interface for serial communication with any embedded device
    via standard serial ports or virtual PTY devices. Handles connection lifecycle,
    data exchange, and automatic reconnection on failures.
    """

    # Class constants
    DEFAULT_READ_TIMEOUT = 1.0

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        """Initialize serial device connection.

        Args:
            port (str): Serial port identifier (e.g., '/dev/ttyUSB0', 'COM3').
            baudrate (int): Communication speed in bits per second. Default 115200.
            timeout (float): Read timeout in seconds. Default 1.0.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial: serial.Serial | None = None
        self.connected = False

    def reconnect(self) -> bool:
        """Establish or re-establish connection to the serial device.

        Closes any existing connection and opens a fresh one. Handles both
        standard serial ports and pseudo-terminals (PTY) transparently.

        Returns:
            bool: True if connection successful, False otherwise.

        Raises:
            serial.SerialException: If connection attempt fails.
        """
        # Close existing connection if any
        if self.serial and self.serial.is_open:
            self.serial.close()
            Debug.debug(f"Closed existing connection to {self.port}")
            sleep(0.5)  # Give the port time to close properly

        try:
            Debug.info(f"Attempting to connect to {self.port} at {self.baudrate} baud")

            # Check if this is a PTY (pseudo-terminal) - used by mock devices
            # PTYs don't support baudrate setting via ioctl
            is_pty = self.port.startswith("/dev/ttys") or self.port.startswith("/dev/pts")

            if is_pty:
                # For PTYs, open without baudrate configuration
                Debug.debug("Detected PTY device, using raw serial access")
                self.serial = serial.Serial()
                self.serial.port = self.port
                self.serial.timeout = self.timeout
                # Don't set baudrate for PTYs - it causes ioctl errors
                self.serial.open()
            else:
                # Normal serial port with full configuration
                self.serial = serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    timeout=self.timeout,
                )

            if not is_pty:
                # Real UART: wait for the Arduino bootloader to finish resetting
                # after the DTR pulse that opening the port triggers.
                sleep(2.0)
            # PTY (mock / test): no hardware reset occurs — skip the delay.
            # Clear buffers - wrapped in try/except for compatibility with
            # virtual ports and some USB-Serial adapters that don't support
            # certain ioctl operations
            try:
                self.serial.reset_input_buffer()
                self.serial.reset_output_buffer()
            except OSError as e:
                Debug.debug(f"Could not reset buffers (non-critical): {e}")
            self.connected = True
            Debug.info(f"Successfully connected to {self.port}")
            return True
        except (serial.SerialException, OSError) as e:
            self.connected = False
            Debug.error(f"Failed to connect to {self.port}: {e}")
            raise serial.SerialException(str(e)) from e

    def close(self) -> None:
        """Close the serial connection.

        Safe to call even if connection is not open.
        """
        if self.serial and self.serial.is_open:
            self.serial.close()
            Debug.debug(f"Connection to {self.port} closed")
        self.connected = False

    def send_command(self, command: str, add_newline: bool = True) -> bool:
        """Send a text command to the device.

        Automatically appends a newline if not present. Returns False on any
        I/O failure — callers are responsible for routing failures through
        ReconnectWorker; no silent retry happens here.

        Args:
            command (str): Command text to send.
            add_newline (bool): If True, append newline if not present. Default True.

        Returns:
            bool: True if command sent successfully, False otherwise.
        """
        if not self.serial or not self.serial.is_open:
            Debug.error("Cannot send command: Serial connection not open")
            return False

        try:
            cmd = command
            if add_newline and not cmd.endswith("\n"):
                cmd += "\n"

            self.serial.write(cmd.encode("utf-8"))
            self.serial.flush()
            Debug.debug(f"Sent command: {repr(cmd.strip())}")
            return True

        except (serial.SerialException, OSError) as e:
            Debug.error(f"Serial error sending command: {e}", exc_info=True)
            self.connected = False
            return False
        except Exception as e:  # pylint: disable=broad-except
            Debug.error(f"Unexpected error sending command: {e}", exc_info=True)
            return False

    def _wait_for_data(self, timeout: float) -> bool:
        """Wait for data to arrive in the serial buffer."""
        if not self.serial:
            return False
        start_time = time()
        while (time() - start_time) < timeout:
            if self.serial.in_waiting > 0:
                return True
            sleep(0.01)
        return False

    def _decode_bytes_to_string(self, raw_data: bytes, strip: bool) -> str | None:
        """Decode bytes to UTF-8 string, filtering invalid responses."""
        decoded = raw_data.decode("utf-8")
        if strip:
            decoded = decoded.strip()

        if decoded.lower() == "invalid":
            Debug.info("'invalid' response received")
            return None

        if not decoded:
            Debug.debug("Empty string after decoding")
            return None

        return decoded

    def read_value(
        self,
        timeout: float = 1.0,
        return_type: str = "auto",
        strip_whitespace: bool = True,
    ) -> str | bytes | None:
        """Unified method to read a single value from the Arduino.

        This is the standard read method. It automatically handles both text and binary
        data. Use this for general-purpose reading unless you need extreme speed.

        Args:
            timeout (float): Maximum time to wait for a complete line in seconds. Default 1.0.
            return_type (str): One of "auto", "str", or "bytes":
                - "auto": Attempt to decode as UTF-8 string; return bytes if decode fails.
                - "str": Force string return; discard non-UTF-8 data.
                - "bytes": Return raw bytes without decoding.
            strip_whitespace (bool): If True and return_type is "str", strip whitespace.

        Returns:
            Union[str, bytes, None]: The value read, or None if reading failed or no data available.
        """
        if not self.serial or not self.serial.is_open:
            Debug.error("Serial connection not open")
            return None

        try:
            # Wait for data with timeout
            if not self._wait_for_data(timeout):
                Debug.debug("Timeout: No data available to read")
                return None

            # Read raw data
            raw_data = self.serial.readline()
            if not raw_data:
                Debug.debug("Empty data read")
                return None

            # Return bytes directly if requested
            if return_type == "bytes":
                Debug.debug(f"Received {len(raw_data)} bytes")
                return raw_data

            # Try to decode as string
            try:
                decoded = self._decode_bytes_to_string(raw_data, strip_whitespace)
                if decoded:
                    Debug.debug(f"Received string: '{decoded}'")
                return decoded

            except UnicodeDecodeError:
                if return_type == "auto":
                    Debug.debug(f"Could not decode as UTF-8, returning {len(raw_data)} raw bytes")
                    return raw_data
                Debug.info("Could not decode as UTF-8 (return_type='str'), returning None")
                return None

        except serial.SerialException as e:
            Debug.error(f"Serial read error: {e}", exc_info=True)
            return None
        except Exception as e:  # pylint: disable=broad-except
            Debug.error(f"Unexpected error in read_value: {e}", exc_info=True)
            return None

    def flush_input_buffer(self) -> bool:
        """Clear the input buffer for a clean state.

        Reads and discards all pending data. Useful before expecting a
        specific response or to clear stale data.

        Returns:
            bool: True on success, False on error.
        """
        if not self.serial or not self.serial.is_open:
            Debug.error("Serial connection not open")
            return False

        try:
            discarded_bytes = 0

            # Read and discard all available data
            while self.serial.in_waiting > 0:
                try:
                    chunk = self.serial.read(min(self.serial.in_waiting, 256))
                    discarded_bytes += len(chunk)
                    sleep(0.001)  # Brief wait for more data to arrive
                except serial.SerialException:
                    break

            # Reset input buffer
            try:
                self.serial.reset_input_buffer()
            except (OSError, serial.SerialException):
                # Some virtual ports don't support this
                pass

            if discarded_bytes > 0:
                Debug.debug(f"Flushed {discarded_bytes} bytes from input buffer")

            return True

        except Exception as e:  # pylint: disable=broad-except
            Debug.error(f"Error flushing input buffer: {e}", exc_info=True)
            return False
