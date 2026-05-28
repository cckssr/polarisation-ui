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

from typing import Optional, Union, Dict, Any
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
    BINARY_PACKET_START_BYTE = 0xAA
    DEFAULT_PACKET_SIZE = 6
    DEFAULT_READ_TIMEOUT = 1.0
    FAST_READ_TIMEOUT_MS = 100

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
        self.serial: Optional[serial.Serial] = None
        self.connected = False
        self._config: Dict[str, Any] = {}

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
            is_pty = self.port.startswith("/dev/ttys") or self.port.startswith(
                "/dev/pts"
            )

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

            sleep(2.0)  # Allow Arduino to reset after connection
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

    def _decode_bytes_to_string(self, raw_data: bytes, strip: bool) -> Optional[str]:
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
    ) -> Union[str, bytes, None]:
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
                    Debug.debug(
                        f"Could not decode as UTF-8, returning {len(raw_data)} raw bytes"
                    )
                    return raw_data
                Debug.info(
                    "Could not decode as UTF-8 (return_type='str'), returning None"
                )
                return None

        except serial.SerialException as e:
            Debug.error(f"Serial read error: {e}", exc_info=True)
            return None
        except Exception as e:  # pylint: disable=broad-except
            Debug.error(f"Unexpected error in read_value: {e}", exc_info=True)
            return None

    def _skip_binary_packets(
        self,
        timeout_remaining: float,
        packet_size: int = DEFAULT_PACKET_SIZE,
        start_byte: int = BINARY_PACKET_START_BYTE,
    ) -> Optional[str]:
        """Skip binary packets and return the first text character found.

        Args:
            timeout_remaining (float): Remaining timeout in seconds.
            packet_size (int): Size of binary packets to skip (default 6 bytes).
            start_byte (int): Start byte of binary packets (default 0xAA).
        Returns:
            Optional[str]: The first text character found, or None if none found.
        """
        if not self.serial:
            return None

        # Quick check - if no data available immediately, return early
        initial_wait = min(0.1, timeout_remaining)
        if not self._wait_for_data(initial_wait):
            return None

        start_time = time()
        while (time() - start_time) < timeout_remaining and self.serial.in_waiting > 0:
            peek = self.serial.read(1)
            if not peek:
                return None

            # Skip binary packet start byte (0xAA)
            if peek[0] == start_byte:
                try:
                    self.serial.read(packet_size - 1)
                except Exception:  # pylint: disable=broad-except
                    pass
                continue

            # Try to decode as text
            try:
                char = peek.decode("utf-8")
                if char.isprintable() or char in "\r\n\t":
                    return char
            except UnicodeDecodeError:
                continue
        return None

    def _try_read_single_line(self, result_parts: list) -> bool:
        """Try to read a single line. Returns True if data was read.

        Args:
            result_parts (list): List to append read lines to.
        Returns:
            bool: True if data was read, False otherwise.
        """
        if not self.serial or self.serial.in_waiting == 0:
            return False

        try:
            line = self.serial.readline()
            if not line:
                return False

            decoded = line.decode("utf-8", errors="ignore").strip()
            if decoded and decoded.lower() != "invalid":
                result_parts.append(decoded)

                # Check if we should wait for more
                if line.endswith(b"\n") or line.endswith(b"\r"):
                    sleep(0.05)
                    return self.serial.in_waiting > 0
            return True

        except (UnicodeDecodeError, serial.SerialException) as e:
            Debug.debug(f"Error reading line: {e}")
            return False

    def _read_text_lines(self, timeout_remaining: float, result_parts: list) -> None:
        """Read text lines until timeout or no more data.

        Args:
            timeout_remaining (float): Remaining timeout in seconds.
            result_parts (list): List to append read lines to.
        """
        if not self.serial:
            return

        start_time = time()
        while (time() - start_time) < timeout_remaining:
            if not self._try_read_single_line(result_parts):
                # No data available, check if we're done
                sleep(0.05)
                if result_parts and self.serial.in_waiting == 0:
                    sleep(0.1)  # Extra wait
                    if self.serial.in_waiting == 0:
                        break

    def read_text_response(
        self,
        timeout: float = DEFAULT_READ_TIMEOUT,
        packet_size: int = DEFAULT_PACKET_SIZE,
    ) -> str:
        """Read a multi-line text response, filtering out binary data.

        More lenient than read_value(); designed for multi-line responses from devices
        that may intersperse binary and text data (e.g., version info, copyright).
        Automatically skips binary packets and collects text until timeout.

        Args:
            timeout (float): Maximum time to wait for response in seconds. Default 1.0.
            packet_size (int): Size of binary packets to skip. Default 6 bytes.

        Returns:
            str: Collected text response, or empty string if no data or only binary found.
        """
        if not self.serial or not self.serial.is_open:
            Debug.error("Serial connection not open")
            return ""

        result_parts = []
        start_time = time()

        try:
            # Skip binary packets and get first text character
            first_char = self._skip_binary_packets(timeout, packet_size)
            if first_char:
                result_parts.append(first_char)

            # Read remaining text data
            remaining_time = timeout - (time() - start_time)
            if remaining_time > 0:
                self._read_text_lines(remaining_time, result_parts)

            # Join without spaces - data comes from Arduino without spaces
            response = "".join(result_parts).strip()
            Debug.debug(f"Text response: '{response}'")
            return response

        except Exception as e:  # pylint: disable=broad-except
            Debug.error(f"Error in read_text_response: {e}", exc_info=True)
            return ""

    def _read_with_delimiter(self, max_bytes: int, delimiter: bytes) -> bytes:
        """Read bytes until delimiter found or max_bytes reached.

        Args:
            max_bytes (int): Maximum number of bytes to read.
            delimiter (bytes): Byte sequence marking end of message.

        Returns:
            bytes: The bytes read including the delimiter, or empty bytes if none.
        """
        if not self.serial:
            return b""

        buffer = bytearray()
        while len(buffer) < max_bytes:
            chunk = self.serial.read(1)
            if not chunk:
                break

            buffer.extend(chunk)

            # Check if delimiter found
            if delimiter in bytes(buffer):
                pos = buffer.find(delimiter)
                result = bytes(buffer[: pos + len(delimiter)])
                Debug.debug(f"Fast read complete: {len(result)} bytes with delimiter")
                return result

        # No delimiter found
        if buffer:
            Debug.debug(f"Fast read timeout: {len(buffer)} bytes without delimiter")
        return bytes(buffer)

    def read_fast(
        self,
        max_bytes: int = 1024,
        timeout_ms: int = FAST_READ_TIMEOUT_MS,
        delimiter: Optional[bytes] = None,
    ) -> Optional[bytes]:
        r"""Read raw bytes with minimal overhead, optimized for performance.

        Best for bulk data transfer and high-frequency sampling. Bypasses
        text decoding and multi-line handling for maximum speed.

        Args:
            max_bytes (int): Maximum bytes to read. Default 1024.
            timeout_ms (int): Timeout in milliseconds. Default 100.
            delimiter (Optional[bytes]): If set, read until this sequence found
                                         (e.g., b"\\n"). Default None.

        Returns:
            Optional[bytes]: Raw bytes read, or None on error.
                           Empty bytes if no data received.
        """
        if not self.serial or not self.serial.is_open:
            Debug.error("Serial connection not open")
            return None

        original_timeout = self.serial.timeout

        try:
            self.serial.timeout = timeout_ms * 0.001

            # Read with delimiter if specified
            if delimiter:
                return self._read_with_delimiter(max_bytes, delimiter)

            # Simple read without delimiter
            buffer = self.serial.read(max_bytes)
            return buffer if buffer else b""

        except serial.SerialException as e:
            Debug.error(f"Serial error in fast read: {e}", exc_info=True)
            return None
        except Exception as e:  # pylint: disable=broad-except
            Debug.error(f"Unexpected error in fast read: {e}", exc_info=True)
            return None
        finally:
            self.serial.timeout = original_timeout

    def _check_delimiter_in_buffer(
        self, buffer: bytearray, delimiter: bytes
    ) -> Optional[bytes]:
        """Check if delimiter is in buffer and extract message if found."""
        delimiter_pos = buffer.find(delimiter)
        if delimiter_pos == -1:
            return None

        message = bytes(buffer[:delimiter_pos])
        remaining = buffer[delimiter_pos + len(delimiter) :]

        if remaining:
            Debug.debug(f"Found delimiter, {len(remaining)} bytes remain in buffer")

        Debug.debug(f"Read complete message: {len(message)} bytes")
        return message

    def read_until_delimiter(
        self,
        delimiter: bytes = b"\n",
        max_buffer: int = 4096,
        timeout: float = DEFAULT_READ_TIMEOUT,
    ) -> Optional[bytes]:
        r"""Read bytes until a delimiter sequence is found.

        Optimized for streaming data where messages are delimited (e.g., newline).
        Reads and buffers data until delimiter found, timeout, or buffer limit.

        Args:
            delimiter (bytes): Byte sequence marking end of message. Default b"\\n".
            max_buffer (int): Maximum buffer size before giving up. Default 4096.
            timeout (float): Total timeout in seconds. Default 2.0.

        Returns:
            Optional[bytes]: Message bytes excluding delimiter, or None on error.
                           Empty bytes if no data received.
        """
        if not self.serial or not self.serial.is_open:
            Debug.error("Serial connection not open")
            return None

        buffer = bytearray()
        start_time = time()

        try:
            while len(buffer) < max_buffer:
                # Check timeout
                if (time() - start_time) > timeout:
                    Debug.info(
                        f"Timeout reading until delimiter (collected {len(buffer)} bytes)"
                    )
                    return bytes(buffer) if buffer else None

                # Read available data
                chunk = self.read_fast(max_bytes=64, timeout_ms=50)
                if chunk is None:
                    Debug.error("read_fast() returned None")
                    return None

                if not chunk:
                    sleep(0.01)
                    continue

                buffer.extend(chunk)

                # Check if delimiter found
                message = self._check_delimiter_in_buffer(buffer, delimiter)
                if message is not None:
                    return message

            # Buffer full without finding delimiter
            Debug.info(
                f"Buffer limit ({max_buffer} bytes) reached without finding delimiter"
            )
            return bytes(buffer) if buffer else None

        except Exception as e:  # pylint: disable=broad-except
            Debug.error(f"Error reading until delimiter: {e}", exc_info=True)
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

    def set_config(self, key: str, value: Any) -> bool:
        """Set a device configuration parameter.

        Args:
            key (str): Configuration parameter name.
            value (Any): Configuration parameter value.

        Returns:
            bool: True if set successfully, False otherwise.
        """
        self._config[key] = value
        return self.send_command(f"CONFIG {key}={value}")

    def get_config(self, key: str) -> Any:
        """Get a device configuration parameter.

        Args:
            key (str): Configuration parameter name.

        Returns:
            Any: The configuration parameter value, or None if not found.
        """
        return self._config.get(key, None)


# Backward compatibility alias
Arduino = SerialDevice
