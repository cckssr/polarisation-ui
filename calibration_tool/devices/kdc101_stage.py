"""
Thorlabs KDC101 Serial Communication.

Reads position from KDC101 using the APT serial protocol.
This works on macOS/Linux without requiring Kinesis DLLs.

Reference: APT Communications Protocol (Thorlabs)
"""

import serial
import time
import struct
from typing import Optional


class KDC101Stage:
    """
    Interface to Thorlabs KDC101 via serial APT protocol.

    APT Protocol Basics:
        - Messages have 6-byte header (or longer with data)
        - Header format: [msg_id_lo, msg_id_hi, param1, param2, dest, source]
        - For KCube: dest=0x50, source=0x01

    Key messages:
        - MGMSG_HW_REQ_INFO (0x0005): Request hardware info
        - MGMSG_MOD_SET_CHANENABLESTATE (0x0210): Enable/disable channel
        - MGMSG_MOT_REQ_POSCOUNTER (0x0411): Request position counter
        - MGMSG_MOT_GET_POSCOUNTER (0x0412): Receive position counter

    Example:
        >>> stage = KDC101Stage("/dev/cu.usbserial-27000001")
        >>> stage.connect()
        >>> position = stage.get_position_degrees()
        >>> print(f"Position: {position:.2f}°")
        >>> stage.disconnect()
    """

    # APT Protocol constants
    HOST = 0x01  # Host (PC) address
    DEVICE = 0x50  # Generic USB device address
    CHANNEL = 0x01  # Channel 1

    # Message IDs
    MSG_HW_REQ_INFO = 0x0005
    MSG_HW_GET_INFO = 0x0006
    MSG_MOD_IDENTIFY = 0x0223
    MSG_MOD_SET_CHANENABLESTATE = 0x0210
    MSG_MOT_REQ_POSCOUNTER = 0x0411
    MSG_MOT_GET_POSCOUNTER = 0x0412
    MSG_MOT_REQ_ENCCOUNTER = 0x040A
    MSG_MOT_GET_ENCCOUNTER = 0x040B
    MSG_MOT_REQ_USTATUSUPDATE = 0x0490
    MSG_MOT_GET_USTATUSUPDATE = 0x0491

    # PRM1-Z8 stage parameters
    # Encoder counts per degree for PRM1-Z8
    ENCODER_COUNTS_PER_DEG = 1919.64186

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        """
        Initialize KDC101 connection.

        Args:
            port: Serial port (e.g., /dev/cu.usbserial-27000001)
            baudrate: Baud rate (115200 for APT)
            timeout: Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial: Optional[serial.Serial] = None
        self._connected = False

    @property
    def connected(self) -> bool:
        """Check if connected to KDC101."""
        return self._connected and self._serial is not None and self._serial.is_open

    def connect(self) -> bool:
        """
        Open serial connection to KDC101.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                rtscts=True,  # KDC101 requires RTS/CTS hardware flow control
            )

            # Clear buffers
            time.sleep(0.5)
            self._serial.reset_input_buffer()
            self._serial.reset_output_buffer()

            # Try to get hardware info to verify connection
            if self._request_hw_info():
                self._connected = True
                print(f"[KDC101] Connected to {self.port}")
                return True
            else:
                print(f"[KDC101] Device not responding on {self.port}")
                self._serial.close()
                return False

        except serial.SerialException as e:
            print(f"[KDC101] Failed to connect: {e}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Close serial connection."""
        if self._serial and self._serial.is_open:
            self._serial.close()
        self._connected = False
        print("[KDC101] Disconnected")

    def _build_short_msg(self, msg_id: int, param1: int = 0, param2: int = 0) -> bytes:
        """
        Build a short (6-byte) APT message.

        Args:
            msg_id: 16-bit message ID
            param1: First parameter byte
            param2: Second parameter byte

        Returns:
            6-byte message
        """
        return struct.pack(
            "<HBBBB",
            msg_id,
            param1,
            param2,
            self.DEVICE | 0x80,  # Destination with "data follows" bit
            self.HOST,
        )

    def _build_short_msg_simple(
        self, msg_id: int, param1: int = 0, param2: int = 0
    ) -> bytes:
        """
        Build a short (6-byte) APT message without data flag.

        Args:
            msg_id: 16-bit message ID
            param1: First parameter byte
            param2: Second parameter byte

        Returns:
            6-byte message
        """
        return struct.pack(
            "<HBBBB",
            msg_id,
            param1,
            param2,
            self.DEVICE,  # Destination without flag
            self.HOST,
        )

    def _send_msg(self, msg: bytes) -> None:
        """Send message to device."""
        if not self.connected:
            raise RuntimeError("Not connected to KDC101")
        self._serial.write(msg)
        self._serial.flush()

    def _read_msg(
        self, expected_len: int, timeout: Optional[float] = None
    ) -> Optional[bytes]:
        """
        Read message from device.

        Args:
            expected_len: Expected message length
            timeout: Optional override for read timeout

        Returns:
            Message bytes or None if timeout
        """
        if not self.connected:
            return None

        old_timeout = self._serial.timeout
        if timeout is not None:
            self._serial.timeout = timeout

        try:
            data = self._serial.read(expected_len)
            return data if len(data) == expected_len else None
        finally:
            self._serial.timeout = old_timeout

    def _request_hw_info(self) -> bool:
        """
        Request hardware info to verify connection.

        Returns:
            True if device responds
        """
        try:
            # Send request
            msg = self._build_short_msg_simple(self.MSG_HW_REQ_INFO, 0, 0)
            self._serial.write(msg)
            self._serial.flush()

            # Read response (90 bytes for HW_GET_INFO)
            time.sleep(0.1)
            response = self._serial.read(90)

            if len(response) >= 10:
                # Check message ID
                msg_id = struct.unpack("<H", response[0:2])[0]
                if msg_id == self.MSG_HW_GET_INFO:
                    serial_num = struct.unpack("<I", response[6:10])[0]
                    print(f"[KDC101] Found device SN: {serial_num}")
                    return True
            return False
        except Exception as e:
            print(f"[KDC101] Hardware info request failed: {e}")
            return False

    def identify(self) -> None:
        """
        Flash the device's identification LED.
        Useful for verifying the right device is connected.
        """
        if not self.connected:
            return
        msg = self._build_short_msg_simple(self.MSG_MOD_IDENTIFY, self.CHANNEL, 0)
        self._send_msg(msg)
        print("[KDC101] Identify LED should flash")

    def enable(self, enabled: bool = True) -> None:
        """
        Enable or disable the motor channel.

        Args:
            enabled: True to enable, False to disable
        """
        if not self.connected:
            return
        state = 0x01 if enabled else 0x02
        msg = self._build_short_msg_simple(
            self.MSG_MOD_SET_CHANENABLESTATE, self.CHANNEL, state
        )
        self._send_msg(msg)
        time.sleep(0.1)
        print(f"[KDC101] Channel {'enabled' if enabled else 'disabled'}")

    def get_position_counts(self) -> Optional[int]:
        """
        Get current position in encoder counts.

        Returns:
            Position in encoder counts or None if error
        """
        if not self.connected:
            return None

        try:
            # Clear input buffer
            self._serial.reset_input_buffer()

            # Request position counter
            msg = self._build_short_msg_simple(
                self.MSG_MOT_REQ_POSCOUNTER, self.CHANNEL, 0
            )
            self._send_msg(msg)

            # Read response (12 bytes: 6 header + 2 channel + 4 position)
            time.sleep(0.05)
            response = self._serial.read(12)

            if len(response) >= 12:
                msg_id = struct.unpack("<H", response[0:2])[0]
                if msg_id == self.MSG_MOT_GET_POSCOUNTER:
                    # Position is bytes 8-11 (signed 32-bit)
                    position = struct.unpack("<i", response[8:12])[0]
                    return position

            # Try reading status update which also contains position
            return self._get_position_from_status()

        except Exception as e:
            print(f"[KDC101] Position read failed: {e}")
            return None

    def _get_position_from_status(self) -> Optional[int]:
        """
        Get position from status update message.

        Returns:
            Position in encoder counts or None if error
        """
        try:
            self._serial.reset_input_buffer()

            # Request status update
            msg = self._build_short_msg_simple(
                self.MSG_MOT_REQ_USTATUSUPDATE, self.CHANNEL, 0
            )
            self._send_msg(msg)

            # Read response (20 bytes for status update)
            time.sleep(0.05)
            response = self._serial.read(20)

            if len(response) >= 16:
                msg_id = struct.unpack("<H", response[0:2])[0]
                if msg_id == self.MSG_MOT_GET_USTATUSUPDATE:
                    # Position is bytes 8-11 (signed 32-bit)
                    position = struct.unpack("<i", response[8:12])[0]
                    return position
            return None
        except Exception:
            return None

    def get_position_degrees(self) -> Optional[float]:
        """
        Get current position in degrees.

        Returns:
            Position in degrees or None if error
        """
        counts = self.get_position_counts()
        if counts is not None:
            return counts / self.ENCODER_COUNTS_PER_DEG
        return None

    def get_encoder_counts(self) -> Optional[int]:
        """
        Get encoder counter value.

        Returns:
            Encoder count or None if error
        """
        if not self.connected:
            return None

        try:
            self._serial.reset_input_buffer()

            # Request encoder counter
            msg = self._build_short_msg_simple(
                self.MSG_MOT_REQ_ENCCOUNTER, self.CHANNEL, 0
            )
            self._send_msg(msg)

            # Read response
            time.sleep(0.05)
            response = self._serial.read(12)

            if len(response) >= 12:
                msg_id = struct.unpack("<H", response[0:2])[0]
                if msg_id == self.MSG_MOT_GET_ENCCOUNTER:
                    encoder = struct.unpack("<i", response[8:12])[0]
                    return encoder
            return None
        except Exception as e:
            print(f"[KDC101] Encoder read failed: {e}")
            return None


# Simple test
if __name__ == "__main__":
    from config import KDC101_PORT

    stage = KDC101Stage(KDC101_PORT)

    if stage.connect():
        print("\nIdentifying device...")
        stage.identify()
        time.sleep(1)

        print("\nReading position 5 times...")
        for i in range(5):
            pos_deg = stage.get_position_degrees()
            pos_counts = stage.get_position_counts()
            if pos_deg is not None:
                print(f"  Sample {i + 1}: {pos_deg:.2f}° ({pos_counts} counts)")
            else:
                print(f"  Sample {i + 1}: Read failed")
            time.sleep(0.5)

        stage.disconnect()
    else:
        print("Failed to connect. Check port in config.py")
        print("Hint: Use 'ls /dev/cu.*' to find available ports")
