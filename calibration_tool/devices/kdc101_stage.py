"""
Thorlabs KDC101 via pylablib.

Uses pylablib's KinesisMotor for APT serial communication.
Works on macOS/Linux/Windows without requiring Kinesis DLLs.
"""

import struct
import time
from typing import Optional

from pylablib.devices import Thorlabs
from pylablib.devices.Thorlabs import ThorlabsError, ThorlabsTimeoutError


class KDC101Stage:
    """
    Interface to Thorlabs KDC101 via pylablib KinesisMotor.

    Example:
        >>> stage = KDC101Stage("/dev/cu.usbserial-27000001")
        >>> stage.connect()
        >>> position = stage.get_position_degrees()
        >>> print(f"Position: {position:.2f}°")
        >>> stage.disconnect()
    """

    # APT message IDs for operations not exposed by pylablib
    _MSG_MOD_SET_CHANENABLESTATE = 0x0210
    _MSG_MOT_REQ_ENCCOUNTER = 0x040A
    _MSG_MOT_GET_ENCCOUNTER = 0x040B

    CHANNEL = 1

    # PRM1-Z8 stage parameters
    ENCODER_COUNTS_PER_DEG = 1919.64186

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        """
        Args:
            port: Serial port path or Kinesis device serial number
            baudrate: Kept for API compatibility; pylablib configures this internally.
            timeout: Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._stage: Thorlabs.KinesisMotor

    @property
    def connected(self) -> bool:
        """Check if connected to KDC101."""
        return self._stage is not None and self._stage.is_opened()

    def connect(self) -> bool:
        """
        Open serial connection to KDC101.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._stage = Thorlabs.KinesisMotor(self.port, scale="step")
            self._stage.open()
            # Discard any unsolicited status frames that arrive on open
            self._stage.flush_comm()
            info = self._stage.get_device_info()
            print(f"[KDC101] Connected to {self.port}, SN: {info.serial_no}")
            return True
        except (ThorlabsError, ThorlabsTimeoutError, Exception) as e:
            print(f"[KDC101] Failed to connect: {e}")
            self._stage = None
            return False

    def disconnect(self) -> None:
        """Close serial connection."""
        if self._stage is not None:
            try:
                self._stage.close()
            except Exception:
                pass
            self._stage = None
        print("[KDC101] Disconnected")

    def identify(self) -> None:
        """Flash the device's identification LED."""
        if not self.connected:
            return
        self._stage.blink(channel=self.CHANNEL)
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
        self._stage.send_comm(
            self._MSG_MOD_SET_CHANENABLESTATE, param1=self.CHANNEL, param2=state
        )
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
            # Flush unsolicited background frames (e.g. periodic status 0x0612,
            # info replies 0x0004) before issuing a position query so pylablib
            # does not mistake them for the expected reply (0x0412).
            self._stage.flush_comm()
            return self._stage.get_position(scale=False)
        except (ThorlabsError, ThorlabsTimeoutError) as e:
            print(f"[KDC101] Position read failed: {e}")
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
            self._stage.flush_comm()
            reply = self._stage.query(
                self._MSG_MOT_REQ_ENCCOUNTER,
                param1=self.CHANNEL,
                replyID=self._MSG_MOT_GET_ENCCOUNTER,
            )
            # CommData.data: 2 bytes channel + 4 bytes signed encoder count
            return struct.unpack("<i", reply.data[2:6])[0]
        except (ThorlabsError, ThorlabsTimeoutError) as e:
            print(f"[KDC101] Encoder read failed: {e}")
            return None

    # ── Motor control ─────────────────────────────────────────────────────────

    def move_to_degrees(self, angle_deg: float) -> bool:
        """
        Move stage to an absolute position in degrees.

        Args:
            angle_deg: Target angle in degrees

        Returns:
            True if command was sent successfully
        """
        if not self.connected:
            return False
        try:
            counts = int(round(angle_deg * self.ENCODER_COUNTS_PER_DEG))
            self._stage.flush_comm()
            self._stage.move_to(counts, channel=self.CHANNEL)
            return True
        except (ThorlabsError, ThorlabsTimeoutError) as e:
            print(f"[KDC101] Move failed: {e}")
            return False

    def is_moving(self) -> bool:
        """Return True if the stage is currently moving."""
        if not self.connected:
            return False
        try:
            self._stage.flush_comm()
            return bool(self._stage.is_moving(channel=self.CHANNEL))
        except (ThorlabsError, ThorlabsTimeoutError):
            return False

    def wait_until_stopped(self, timeout: float = 60.0) -> bool:
        """
        Poll position counts until stable for 3 consecutive reads (200 ms apart).

        Avoids is_moving() and wait_move() entirely — both issue APT queries that
        race with the KDC101's unsolicited background frames (0x0412, 0x0612) and
        produce "read returned less data than expected" / "unexpected command"
        errors. get_position_counts() already handles flush_comm() and silently
        returns None on transient framing errors, so position-stability polling
        is naturally tolerant of those glitches.

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            True if stopped within timeout, False if timed out
        """
        if not self.connected:
            return False
        deadline = time.time() + timeout
        prev_pos: Optional[int] = None
        stable_count = 0
        while True:
            if time.time() > deadline:
                print(f"[KDC101] wait_until_stopped: timed out after {timeout}s")
                return False
            time.sleep(0.2)
            pos = self.get_position_counts()
            if pos is None:
                # Transient read error — keep waiting
                continue
            if pos == prev_pos:
                stable_count += 1
                if stable_count >= 3:
                    return True
            else:
                stable_count = 0
                prev_pos = pos

    def stop_motion(self) -> None:
        """Stop any ongoing motion immediately."""
        if not self.connected:
            return
        try:
            self._stage.stop(immediate=True, channel=self.CHANNEL)
        except (ThorlabsError, ThorlabsTimeoutError):
            pass

    def home(self, timeout: float = 120.0) -> bool:
        """
        Home the stage (moves to hardware reference position).

        Args:
            timeout: Maximum time allowed for homing in seconds

        Returns:
            True if homing completed successfully
        """
        if not self.connected:
            return False
        try:
            self._stage.home(sync=True, channel=self.CHANNEL, timeout=timeout)
            print("[KDC101] Homing complete")
            return True
        except ThorlabsTimeoutError:
            print(f"[KDC101] Homing timed out after {timeout}s")
            return False
        except (ThorlabsError, Exception) as e:
            print(f"[KDC101] Homing failed: {e}")
            return False


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
