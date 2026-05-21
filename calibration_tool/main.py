#!/usr/bin/env python3
"""
AS5048A Encoder Calibration Tool

A standalone tool for calibrating AS5048A magnetic encoders using a
Thorlabs KDC101-controlled reference stage (PRM1/MZ8).

Usage:
    1. Configure ports in config.py
    2. Run: python main.py
    3. Connect to devices
    4. Use the Thorlabs controller to rotate the stage manually
    5. Start measurement to record data
    6. Stop and analyze when complete

Requirements:
    pip install pyserial numpy matplotlib PySide6
"""

from __future__ import annotations

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Optional
from datetime import datetime

# PySide6 imports
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QComboBox,
    QProgressBar,
    QTextEdit,
    QSplitter,
    QMessageBox,
    QFileDialog,
    QStatusBar,
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, Slot
from PySide6.QtGui import QAction, QFont

# Matplotlib for embedded plots
import matplotlib

matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# Local imports
from config import ARDUINO_BAUDRATE, POLL_INTERVAL
from devices.arduino_encoder import ArduinoEncoder
from devices.kdc101_stage import KDC101Stage
from serial.tools import list_ports
from pylablib.devices import Thorlabs
from calibration.measurement import (
    CalibrationMeasurement,
    CalibrationRun,
    MeasurementPoint,
)
from calibration.analysis import CalibrationAnalysis
from manual_calibration_dialog import ManualCalibrationDialog
from plotting.polar_plot import CalibrationPlotter


class MeasurementWorker(QThread):
    """Background thread for continuous measurement."""

    point_recorded = Signal(MeasurementPoint)
    error_occurred = Signal(str)

    def __init__(
        self, measurement: CalibrationMeasurement, interval: float, parent=None
    ):
        super().__init__(parent)
        self.measurement = measurement
        self.interval = interval
        self._running = True

    def run(self):
        """Main measurement loop."""
        import time

        while self._running and self.measurement:
            try:
                point = self.measurement.take_single_measurement()
                if point:
                    self.point_recorded.emit(point)
                time.sleep(self.interval)
            except Exception as e:
                self.error_occurred.emit(str(e))

    def stop(self):
        """Stop the measurement loop."""
        self._running = False


class AutoCalibrationWorker(QThread):
    """
    Background thread for motorised angle sweep.

    Moves the KDC101 to each target angle in sequence, waits for it to stop,
    waits an additional settle delay, then takes a single encoder reading.
    """

    point_recorded = Signal(MeasurementPoint)
    progress_updated = Signal(int, int)  # (completed_steps, total_steps)
    error_occurred = Signal(str)
    finished = Signal()

    def __init__(
        self,
        measurement: "CalibrationMeasurement",
        kdc101: "KDC101Stage",
        angles: list,
        settle_ms: int = 300,
        parent=None,
    ):
        super().__init__(parent)
        self.measurement = measurement
        self.kdc101 = kdc101
        self.angles = angles
        self.settle_ms = settle_ms
        self._running = True

    def run(self) -> None:
        import time

        total = len(self.angles)
        for i, angle in enumerate(self.angles):
            if not self._running:
                break
            try:
                if not self.kdc101.move_to_degrees(angle):
                    self.error_occurred.emit(f"Move to {angle:.1f}° failed")
                    break

                if not self.kdc101.wait_until_stopped(timeout=60.0):
                    self.error_occurred.emit(
                        f"Stage did not stop within 60 s at {angle:.1f}°"
                    )
                    break

                time.sleep(self.settle_ms / 1000.0)

                point = self.measurement.take_single_measurement()
                if point:
                    self.point_recorded.emit(point)

                self.progress_updated.emit(i + 1, total)

            except Exception as e:
                self.error_occurred.emit(str(e))
                break

        self.finished.emit()

    def stop(self) -> None:
        self._running = False


class CalibrationApp(QMainWindow):
    """
    Main application window for encoder calibration.

    Provides:
        - Device connection management
        - Live position display
        - Measurement recording
        - Analysis and visualization
    """

    def __init__(self):
        """Initialize the application."""
        super().__init__()

        self.setWindowTitle("AS5048A Encoder Calibration Tool")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        # Device instances
        self.arduino: Optional[ArduinoEncoder] = None
        self.kdc101: Optional[KDC101Stage] = None
        self.measurement: Optional[CalibrationMeasurement] = None

        # State
        self._measuring = False
        self._measurement_worker: Optional[MeasurementWorker] = None
        self._auto_worker: Optional[AutoCalibrationWorker] = None
        self._current_run: Optional[CalibrationRun] = None

        # Single-shot timer for live position polling.
        # Single-shot means it fires once and stops; _update_positions reschedules
        # it only after the serial I/O completes, preventing queue build-up.
        self._live_timer = QTimer(self)
        self._live_timer.setSingleShot(True)
        self._live_timer.timeout.connect(self._update_positions)

        # Build UI
        self._create_menu()
        self._create_main_layout()
        self._create_status_bar()

        # Start with demo data
        self._load_demo_data()

    def _create_menu(self):
        """Create application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        load_action = QAction("Load CSV...", self)
        load_action.triggered.connect(self._load_csv)
        file_menu.addAction(load_action)

        save_action = QAction("Save CSV...", self)
        save_action.triggered.connect(self._save_csv)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        export_action = QAction("Export Plot...", self)
        export_action.triggered.connect(self._export_plot)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        demo_action = QAction("Show Demo", self)
        demo_action.triggered.connect(self._load_demo_data)
        help_menu.addAction(demo_action)

    def _create_main_layout(self):
        """Create main application layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel (controls)
        left_panel = QWidget()
        left_panel.setFixedWidth(350)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        left_layout.addWidget(self._create_connection_panel())
        left_layout.addWidget(self._create_position_panel())
        left_layout.addWidget(self._create_measurement_panel())
        left_layout.addWidget(self._create_analysis_panel())

        splitter.addWidget(left_panel)

        # Right panel (plots)
        right_panel = self._create_plot_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

    def _create_connection_panel(self) -> QGroupBox:
        """Create device connection controls."""
        group = QGroupBox("Device Connection")
        layout = QVBoxLayout(group)

        # Arduino row
        arduino_layout = QHBoxLayout()
        arduino_layout.addWidget(QLabel("Arduino:"))
        self.arduino_port_combo = QComboBox()
        self.arduino_port_combo.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToContents
        )
        self.arduino_port_combo.setMinimumWidth(180)
        arduino_layout.addWidget(self.arduino_port_combo, stretch=1)
        arduino_refresh_btn = QPushButton("⟳")
        arduino_refresh_btn.setFixedWidth(28)
        arduino_refresh_btn.setToolTip("Refresh serial ports")
        arduino_refresh_btn.clicked.connect(self._refresh_arduino_ports)
        arduino_layout.addWidget(arduino_refresh_btn)
        self.arduino_status = QLabel("●")
        self.arduino_status.setStyleSheet("color: gray; font-size: 16px;")
        arduino_layout.addWidget(self.arduino_status)
        layout.addLayout(arduino_layout)

        # Encoder selector row
        enc_layout = QHBoxLayout()
        enc_layout.addWidget(QLabel("Encoder:"))
        self.encoder_combo = QComboBox()
        self.encoder_combo.addItem("A — Sample angle", userData="A")
        self.encoder_combo.addItem("B — Detector angle", userData="B")
        enc_layout.addWidget(self.encoder_combo)
        enc_layout.addStretch()
        layout.addLayout(enc_layout)

        # KDC101 row
        kdc_layout = QHBoxLayout()
        kdc_layout.addWidget(QLabel("KDC101:"))
        self.kdc_device_combo = QComboBox()
        self.kdc_device_combo.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToContents
        )
        self.kdc_device_combo.setMinimumWidth(180)
        kdc_layout.addWidget(self.kdc_device_combo, stretch=1)
        kdc_refresh_btn = QPushButton("⟳")
        kdc_refresh_btn.setFixedWidth(28)
        kdc_refresh_btn.setToolTip("Refresh Kinesis devices")
        kdc_refresh_btn.clicked.connect(self._refresh_kdc_devices)
        kdc_layout.addWidget(kdc_refresh_btn)
        self.kdc_status = QLabel("●")
        self.kdc_status.setStyleSheet("color: gray; font-size: 16px;")
        kdc_layout.addWidget(self.kdc_status)
        layout.addLayout(kdc_layout)

        # Populate dropdowns on first load
        self._refresh_arduino_ports()
        self._refresh_kdc_devices()

        # Connect buttons
        btn_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Connect All")
        self.connect_btn.clicked.connect(self._connect_devices)
        btn_layout.addWidget(self.connect_btn)

        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self._disconnect_devices)
        self.disconnect_btn.setEnabled(False)
        btn_layout.addWidget(self.disconnect_btn)

        identify_btn = QPushButton("Identify KDC")
        identify_btn.clicked.connect(self._identify_kdc)
        btn_layout.addWidget(identify_btn)

        layout.addLayout(btn_layout)

        return group

    def _refresh_arduino_ports(self) -> None:
        """Repopulate the Arduino port combo from available serial ports."""
        self.arduino_port_combo.clear()
        ports = sorted(list_ports.comports(), key=lambda p: p.device)
        if ports:
            for p in ports:
                desc = p.description or "Serial device"
                self.arduino_port_combo.addItem(
                    f"{p.device} — {desc}", userData=p.device
                )
            self.arduino_port_combo.setEnabled(True)
        else:
            self.arduino_port_combo.addItem("No serial ports found")
            self.arduino_port_combo.setEnabled(False)

    def _refresh_kdc_devices(self) -> None:
        """Repopulate the KDC101 combo from connected Kinesis devices."""
        self.kdc_device_combo.clear()
        try:
            devices = Thorlabs.list_kinesis_devices()
        except Exception:
            devices = []
        if devices:
            for conn, desc in devices:
                self.kdc_device_combo.addItem(f"{desc}  [{conn}]", userData=conn)
            self.kdc_device_combo.setEnabled(True)
        else:
            self.kdc_device_combo.addItem("No Kinesis devices found")
            self.kdc_device_combo.setEnabled(False)

    def _create_position_panel(self) -> QGroupBox:
        """Create live position display."""
        group = QGroupBox("Live Position")
        layout = QVBoxLayout(group)

        # Font for position display
        pos_font = QFont("Courier", 14)
        pos_font.setBold(True)

        # Reference position
        ref_layout = QHBoxLayout()
        ref_layout.addWidget(QLabel("Reference (KDC101):"))
        self.ref_pos_label = QLabel("---")
        self.ref_pos_label.setFont(pos_font)
        self.ref_pos_label.setStyleSheet("color: blue;")
        self.ref_pos_label.setMinimumWidth(100)
        ref_layout.addWidget(self.ref_pos_label)
        ref_layout.addWidget(QLabel("°"))
        ref_layout.addStretch()
        layout.addLayout(ref_layout)

        # Measured position
        meas_layout = QHBoxLayout()
        meas_layout.addWidget(QLabel("Measured (AS5048A):"))
        self.meas_pos_label = QLabel("---")
        self.meas_pos_label.setFont(pos_font)
        self.meas_pos_label.setStyleSheet("color: green;")
        self.meas_pos_label.setMinimumWidth(100)
        meas_layout.addWidget(self.meas_pos_label)
        meas_layout.addWidget(QLabel("°"))
        meas_layout.addStretch()
        layout.addLayout(meas_layout)

        # Error
        error_layout = QHBoxLayout()
        error_layout.addWidget(QLabel("Current Error:"))
        self.error_label = QLabel("---")
        self.error_label.setFont(pos_font)
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setMinimumWidth(100)
        error_layout.addWidget(self.error_label)
        error_layout.addWidget(QLabel("°"))
        error_layout.addStretch()
        layout.addLayout(error_layout)

        # Live update toggle
        self.live_checkbox = QCheckBox("Live Update")
        self.live_checkbox.stateChanged.connect(self._toggle_live)
        layout.addWidget(self.live_checkbox)

        return group

    def _create_measurement_panel(self) -> QGroupBox:
        """Create measurement controls."""
        group = QGroupBox("Measurement")
        layout = QVBoxLayout(group)

        # Run name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Run Name:"))
        self.run_name_edit = QLineEdit(datetime.now().strftime("cal_%Y%m%d_%H%M"))
        name_layout.addWidget(self.run_name_edit)
        layout.addLayout(name_layout)

        # Interval
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Interval (ms):"))
        self.interval_edit = QLineEdit(str(int(POLL_INTERVAL * 1000)))
        self.interval_edit.setMaximumWidth(60)
        interval_layout.addWidget(self.interval_edit)
        interval_layout.addStretch()
        layout.addLayout(interval_layout)

        # Status
        points_layout = QHBoxLayout()
        points_layout.addWidget(QLabel("Points:"))
        self.points_label = QLabel("0")
        self.points_label.setFont(QFont("Courier", 12))
        points_layout.addWidget(self.points_label)
        points_layout.addStretch()
        layout.addLayout(points_layout)

        # Buttons
        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶ Start")
        self.start_btn.clicked.connect(self._start_measurement)
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("■ Stop")
        self.stop_btn.clicked.connect(self._stop_measurement)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)

        zero_btn = QPushButton("Zero Arduino")
        zero_btn.clicked.connect(self._zero_arduino)
        btn_layout.addWidget(zero_btn)

        layout.addLayout(btn_layout)

        # Manual calibration (alternative to KDC101)
        manual_btn = QPushButton("Manual Cal...")
        manual_btn.setToolTip(
            "Step-by-step calibration without a motorized reference stage.\n"
            "You set each angle manually; the tool records the encoder reading."
        )
        manual_btn.clicked.connect(self._start_manual_calibration)
        layout.addWidget(manual_btn)

        # ── Auto sweep ──────────────────────────────────────────────────────
        layout.addWidget(self._make_separator("Automatic Full Sweep (KDC101)"))

        auto_desc = QLabel(
            "Moves the KDC101 through 0–360° automatically,\n"
            "reads the encoder at each step, and records all points."
        )
        auto_desc.setStyleSheet("color: #555; font-size: 9px;")
        layout.addWidget(auto_desc)

        params_layout = QHBoxLayout()
        params_layout.addWidget(QLabel("Step:"))
        self.auto_step_edit = QLineEdit("5.0")
        self.auto_step_edit.setMaximumWidth(48)
        self.auto_step_edit.setToolTip("Angular step between positions (degrees)")
        params_layout.addWidget(self.auto_step_edit)
        params_layout.addWidget(QLabel("°  Settle:"))
        self.auto_settle_edit = QLineEdit("300")
        self.auto_settle_edit.setMaximumWidth(48)
        self.auto_settle_edit.setToolTip(
            "Wait time after motor stops before reading (ms)"
        )
        params_layout.addWidget(self.auto_settle_edit)
        params_layout.addWidget(QLabel("ms"))
        params_layout.addStretch()
        layout.addLayout(params_layout)

        auto_btn_layout = QHBoxLayout()
        self.auto_start_btn = QPushButton("▶ Run Full Auto Sweep")
        self.auto_start_btn.setToolTip(
            "Connect both devices first, then click here to\n"
            "automatically sweep through all angles and record calibration data."
        )
        self.auto_start_btn.clicked.connect(self._start_auto_calibration)
        auto_btn_layout.addWidget(self.auto_start_btn)
        self.auto_stop_btn = QPushButton("■ Stop")
        self.auto_stop_btn.clicked.connect(self._stop_auto_calibration)
        self.auto_stop_btn.setEnabled(False)
        auto_btn_layout.addWidget(self.auto_stop_btn)
        layout.addLayout(auto_btn_layout)

        self.auto_progress = QProgressBar()
        self.auto_progress.setRange(0, 100)
        self.auto_progress.setValue(0)
        self.auto_progress.setTextVisible(True)
        self.auto_progress.setFormat("%v / %m steps")
        layout.addWidget(self.auto_progress)

        return group

    @staticmethod
    def _make_separator(text: str) -> QLabel:
        label = QLabel(f"─── {text} ───")
        label.setStyleSheet("color: gray; font-size: 9px;")
        return label

    def _create_analysis_panel(self) -> QGroupBox:
        """Create analysis controls and results."""
        group = QGroupBox("Analysis")
        layout = QVBoxLayout(group)

        # Buttons
        btn_layout = QHBoxLayout()
        analyze_btn = QPushButton("Analyze")
        analyze_btn.clicked.connect(self._analyze)
        btn_layout.addWidget(analyze_btn)

        plot_btn = QPushButton("Update Plot")
        plot_btn.clicked.connect(self._update_plot)
        btn_layout.addWidget(plot_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Results text
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Courier", 9))
        layout.addWidget(self.results_text)

        return group

    def _create_plot_panel(self) -> QGroupBox:
        """Create matplotlib plot area."""
        group = QGroupBox("Visualization")
        layout = QVBoxLayout(group)

        # Create figure
        self.fig = Figure(figsize=(10, 7), dpi=100)

        # Create canvas
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        # Navigation toolbar
        toolbar = NavigationToolbar(self.canvas, group)
        layout.addWidget(toolbar)

        return group

    def _create_status_bar(self):
        """Create status bar at bottom."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Configure ports and connect devices.")

    # =========================================================================
    # Device Management
    # =========================================================================

    @Slot()
    def _connect_devices(self):
        """Connect to both devices."""
        self.status_bar.showMessage("Connecting to devices...")
        QApplication.processEvents()

        # Connect Arduino
        arduino_port = self.arduino_port_combo.currentData()
        if arduino_port is None:
            QMessageBox.warning(self, "Arduino", "No serial port selected.")
            self.arduino_status.setStyleSheet("color: red; font-size: 16px;")
        else:
            try:
                self.arduino = ArduinoEncoder(arduino_port, ARDUINO_BAUDRATE)
                if self.arduino.connect():
                    self.arduino_status.setStyleSheet("color: green; font-size: 16px;")
                else:
                    self.arduino_status.setStyleSheet("color: red; font-size: 16px;")
                    QMessageBox.warning(self, "Arduino", "Failed to connect to Arduino")
            except Exception as e:
                self.arduino_status.setStyleSheet("color: red; font-size: 16px;")
                QMessageBox.critical(self, "Arduino Error", str(e))

        # Connect KDC101
        kdc_conn = self.kdc_device_combo.currentData()
        if kdc_conn is None:
            QMessageBox.warning(self, "KDC101", "No Kinesis device selected.")
            self.kdc_status.setStyleSheet("color: red; font-size: 16px;")
        else:
            try:
                self.kdc101 = KDC101Stage(kdc_conn)
                if self.kdc101.connect():
                    self.kdc_status.setStyleSheet("color: green; font-size: 16px;")
                else:
                    self.kdc_status.setStyleSheet("color: red; font-size: 16px;")
                    QMessageBox.warning(
                        self,
                        "KDC101",
                        "Failed to connect to KDC101\nCheck device and try again.",
                    )
            except Exception as e:
                self.kdc_status.setStyleSheet("color: red; font-size: 16px;")
                QMessageBox.critical(self, "KDC101 Error", str(e))

        # Create measurement instance if both connected
        if (
            self.arduino
            and self.arduino.connected
            and self.kdc101
            and self.kdc101.connected
        ):
            encoder_id = self.encoder_combo.currentData() or "A"
            self.measurement = CalibrationMeasurement(
                self.arduino, self.kdc101, encoder_id=encoder_id
            )
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.status_bar.showMessage(
                "Connected to both devices. Ready for measurement."
            )
        else:
            self.status_bar.showMessage("Connection incomplete. Check devices.")

    @Slot()
    def _disconnect_devices(self):
        """Disconnect from devices."""
        self._measuring = False

        if self._auto_worker:
            self._auto_worker.stop()
            self._auto_worker.wait()
            self._auto_worker = None

        if self._measurement_worker:
            self._measurement_worker.stop()
            self._measurement_worker.wait()
            self._measurement_worker = None

        self._live_timer.stop()
        self.live_checkbox.setChecked(False)

        if self.arduino:
            self.arduino.disconnect()
            self.arduino_status.setStyleSheet("color: gray; font-size: 16px;")

        if self.kdc101:
            self.kdc101.disconnect()
            self.kdc_status.setStyleSheet("color: gray; font-size: 16px;")

        self.measurement = None
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.status_bar.showMessage("Disconnected.")

    @Slot()
    def _identify_kdc(self):
        """Flash KDC101 LED."""
        if self.kdc101 and self.kdc101.connected:
            self.kdc101.identify()

    @Slot()
    def _zero_arduino(self):
        """Set Arduino encoder zero position."""
        if self.arduino and self.arduino.connected:
            encoder_id = self.encoder_combo.currentData() or "A"
            self.arduino.set_zero(encoder_id)
            self.status_bar.showMessage(f"Encoder {encoder_id} zeroed.")

    # =========================================================================
    # Live Update
    # =========================================================================

    @Slot(int)
    def _toggle_live(self, state: int):
        """Toggle live position update."""
        if state == Qt.Checked.value:
            self._live_timer.start(100)
        else:
            self._live_timer.stop()

    @Slot()
    def _update_positions(self):
        """Update live position display, then reschedule the next poll."""
        try:
            ref_deg = None
            meas_deg = None

            if self.kdc101 and self.kdc101.connected:
                ref_deg = self.kdc101.get_position_degrees()
                if ref_deg is not None:
                    self.ref_pos_label.setText(f"{ref_deg:8.3f}")
                else:
                    self.ref_pos_label.setText("ERROR")

            if self.arduino and self.arduino.connected:
                encoder_id = self.encoder_combo.currentData() or "A"
                meas_deg = self.arduino.read_angle(encoder_id)
                if meas_deg is not None:
                    self.meas_pos_label.setText(f"{meas_deg:8.3f}")
                else:
                    self.meas_pos_label.setText("ERROR")

            # Calculate error
            if ref_deg is not None and meas_deg is not None:
                error = meas_deg - ref_deg
                while error > 180:
                    error -= 360
                while error < -180:
                    error += 360
                self.error_label.setText(f"{error:+8.3f}")
            else:
                self.error_label.setText("---")

        except Exception as e:
            print(f"Live update error: {e}")
        finally:
            # Reschedule only after I/O is done; checkbox guards against
            # the timer firing after the user unchecks or disconnects.
            if self.live_checkbox.isChecked():
                self._live_timer.start(100)

    # =========================================================================
    # Measurement
    # =========================================================================

    @Slot()
    def _start_measurement(self):
        """Start calibration measurement."""
        if not self.measurement:
            QMessageBox.warning(self, "Not Ready", "Connect to devices first!")
            return

        self._measuring = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # Start run
        run_name = self.run_name_edit.text()
        self._current_run = self.measurement.start_run(run_name)

        # Get interval
        try:
            interval_ms = int(self.interval_edit.text())
            interval_sec = interval_ms / 1000.0
        except ValueError:
            interval_sec = POLL_INTERVAL

        # Start measurement worker thread
        self._measurement_worker = MeasurementWorker(
            self.measurement, interval_sec, self
        )
        self._measurement_worker.point_recorded.connect(self._on_point_recorded)
        self._measurement_worker.error_occurred.connect(self._on_measurement_error)
        self._measurement_worker.start()

        self.status_bar.showMessage(
            "Measuring... Rotate the stage using the Thorlabs controller."
        )

    @Slot(MeasurementPoint)
    def _on_point_recorded(self, point: MeasurementPoint):
        """Handle new measurement point (called from main thread via signal)."""
        if self._current_run:
            self.points_label.setText(str(self._current_run.num_points))

        # Update position displays
        self.ref_pos_label.setText(f"{point.reference_deg:8.3f}")
        self.meas_pos_label.setText(f"{point.measured_deg:8.3f}")
        self.error_label.setText(f"{point.error_deg:+8.3f}")

    @Slot(str)
    def _on_measurement_error(self, error_msg: str):
        """Handle measurement error."""
        print(f"Measurement error: {error_msg}")

    @Slot()
    def _stop_measurement(self):
        """Stop calibration measurement."""
        self._measuring = False

        if self._measurement_worker:
            self._measurement_worker.stop()
            self._measurement_worker.wait()
            self._measurement_worker = None

        if self.measurement:
            self.measurement.stop_run()

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        if self._current_run:
            self.status_bar.showMessage(
                f"Measurement stopped. {self._current_run.num_points} points collected."
            )
            self._update_plot()

    @Slot()
    def _start_auto_calibration(self):
        """Start motorised angle sweep."""
        if not self.measurement:
            QMessageBox.warning(self, "Not Ready", "Connect to devices first!")
            return
        if not (self.kdc101 and self.kdc101.connected):
            QMessageBox.warning(
                self, "Not Ready", "KDC101 must be connected for auto sweep."
            )
            return

        try:
            step_deg = float(self.auto_step_edit.text())
            settle_ms = int(self.auto_settle_edit.text())
        except ValueError:
            QMessageBox.warning(
                self, "Invalid Parameters", "Step and settle must be numbers."
            )
            return

        if step_deg <= 0 or step_deg > 360:
            QMessageBox.warning(
                self, "Invalid Parameters", "Step must be between 0° and 360°."
            )
            return

        import numpy as np

        angles = list(np.arange(0.0, 360.0, step_deg))
        total = len(angles)

        run_name = self.run_name_edit.text()
        self._current_run = self.measurement.start_run(run_name)
        self.points_label.setText("0")
        self.auto_progress.setRange(0, total)
        self.auto_progress.setValue(0)
        self.auto_progress.setFormat(f"%v / {total} steps")

        self._auto_worker = AutoCalibrationWorker(
            self.measurement, self.kdc101, angles, settle_ms=settle_ms, parent=self
        )
        self._auto_worker.point_recorded.connect(self._on_point_recorded)
        self._auto_worker.progress_updated.connect(self._on_auto_progress)
        self._auto_worker.error_occurred.connect(self._on_auto_error)
        self._auto_worker.finished.connect(self._on_auto_finished)
        self._auto_worker.start()

        self.auto_start_btn.setEnabled(False)
        self.auto_stop_btn.setEnabled(True)
        self.start_btn.setEnabled(False)
        self.status_bar.showMessage(
            f"Auto sweep started: {total} positions, {step_deg}° step, {settle_ms} ms settle."
        )

    @Slot()
    def _stop_auto_calibration(self):
        """Stop the ongoing auto sweep."""
        if self._auto_worker:
            self._auto_worker.stop()
            if self.kdc101 and self.kdc101.connected:
                self.kdc101.stop_motion()
            self._auto_worker.wait()
            self._auto_worker = None

        if self.measurement:
            self.measurement.stop_run()

        self.auto_start_btn.setEnabled(True)
        self.auto_stop_btn.setEnabled(False)
        self.start_btn.setEnabled(True)

        if self._current_run:
            self.status_bar.showMessage(
                f"Auto sweep stopped. {self._current_run.num_points} points collected."
            )
            self._update_plot()

    @Slot(int, int)
    def _on_auto_progress(self, completed: int, total: int) -> None:
        self.auto_progress.setValue(completed)
        self.points_label.setText(str(completed))

    @Slot(str)
    def _on_auto_error(self, error_msg: str) -> None:
        print(f"Auto sweep error: {error_msg}")
        self.status_bar.showMessage(f"Auto sweep error: {error_msg}")

    @Slot()
    def _on_auto_finished(self) -> None:
        self._auto_worker = None
        if self.measurement:
            self.measurement.stop_run()
        self.auto_start_btn.setEnabled(True)
        self.auto_stop_btn.setEnabled(False)
        self.start_btn.setEnabled(True)
        pts = self._current_run.num_points if self._current_run else 0
        self.status_bar.showMessage(f"Auto sweep complete. {pts} points collected.")
        if self._current_run and pts >= 2:
            self._update_plot()
            self._analyze()

    @Slot()
    def _start_manual_calibration(self):
        """Open the manual step-through calibration dialog."""
        dialog = ManualCalibrationDialog(arduino=self.arduino, parent=self)
        if dialog.exec() == ManualCalibrationDialog.DialogCode.Accepted:
            run = dialog.get_run()
            if run and run.num_points > 0:
                self._current_run = run
                self.points_label.setText(str(run.num_points))
                self.run_name_edit.setText(run.name)
                self.status_bar.showMessage(
                    f"Manual calibration complete: {run.num_points} points loaded."
                )
                self._update_plot()
                self._analyze()

    # =========================================================================
    # Analysis
    # =========================================================================

    @Slot()
    def _analyze(self):
        """Run analysis on current data."""
        if not self._current_run or self._current_run.num_points < 10:
            QMessageBox.warning(self, "No Data", "Need at least 10 measurement points!")
            return

        try:
            analysis = CalibrationAnalysis(self._current_run)
            result = analysis.analyze()

            # Display results
            self.results_text.clear()
            self.results_text.setText(result.summary())

            self.status_bar.showMessage("Analysis complete.")

            # Update plot
            self._update_plot()

        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", str(e))

    @Slot()
    def _update_plot(self):
        """Update the plot with current data."""
        if not self._current_run or self._current_run.num_points < 2:
            return

        try:
            self.fig.clear()

            plotter = CalibrationPlotter(self._current_run)

            # Polar plot
            ax1 = self.fig.add_subplot(121, projection="polar")
            plotter.plot_polar(ax=ax1)

            # Error vs angle plot
            ax2 = self.fig.add_subplot(122)
            plotter.plot_error_vs_angle(ax=ax2)

            self.fig.tight_layout()
            self.canvas.draw()

        except Exception as e:
            print(f"Plot error: {e}")

    # =========================================================================
    # File Operations
    # =========================================================================

    @Slot()
    def _load_csv(self):
        """Load calibration data from CSV."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Load Calibration Data",
            "",
            "CSV files (*.csv);;All files (*.*)",
        )

        if filepath:
            try:
                self._current_run = CalibrationMeasurement.load_from_csv(filepath)
                self.points_label.setText(str(self._current_run.num_points))
                self.run_name_edit.setText(self._current_run.name)
                self._update_plot()
                self._analyze()
                self.status_bar.showMessage(
                    f"Loaded {self._current_run.num_points} points from {filepath}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Load Error", str(e))

    @Slot()
    def _save_csv(self):
        """Save calibration data to CSV."""
        if not self._current_run:
            QMessageBox.warning(self, "No Data", "No data to save!")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Calibration Data",
            f"{self._current_run.name}.csv",
            "CSV files (*.csv)",
        )

        if filepath:
            try:
                # Temporarily assign to measurement for save
                if self.measurement:
                    self.measurement.current_run = self._current_run
                    self.measurement.save_to_csv(filepath)
                else:
                    # Manual save
                    import csv

                    with open(filepath, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(
                            [
                                "timestamp",
                                "reference_deg",
                                "measured_deg",
                                "error_deg",
                                "reference_counts",
                            ]
                        )
                        for p in self._current_run.points:
                            writer.writerow(
                                [
                                    p.timestamp,
                                    f"{p.reference_deg:.4f}",
                                    f"{p.measured_deg:.4f}",
                                    f"{p.error_deg:.4f}",
                                    p.reference_counts,
                                ]
                            )
                    print(f"Saved to {filepath}")

                self.status_bar.showMessage(f"Saved to {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", str(e))

    @Slot()
    def _export_plot(self):
        """Export plot to image file."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Plot",
            "calibration_plot.png",
            "PNG files (*.png);;PDF files (*.pdf);;SVG files (*.svg)",
        )

        if filepath:
            try:
                self.fig.savefig(filepath, dpi=150, bbox_inches="tight")
                self.status_bar.showMessage(f"Plot exported to {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

    # =========================================================================
    # Misc
    # =========================================================================

    def _load_demo_data(self):
        """Load demonstration data."""
        import numpy as np

        # Create synthetic data with realistic error pattern
        run = CalibrationRun(name="demo_data", start_time=datetime.now())

        np.random.seed(42)
        for i in range(360):
            ref_angle = float(i)

            # Simulate realistic encoder errors:
            # - 1x error (eccentricity): ~1.2° amplitude at 60° phase
            # - 2x error (ellipticity): ~0.25° amplitude
            # - Random noise: ~0.05° std dev
            error_1x = 1.2 * np.sin(np.deg2rad(ref_angle + 60))
            error_2x = 0.25 * np.sin(np.deg2rad(2 * ref_angle + 30))
            noise = np.random.normal(0, 0.05)

            measured = ref_angle + error_1x + error_2x + noise

            point = MeasurementPoint(
                timestamp=float(i), reference_deg=ref_angle, measured_deg=measured
            )
            run.add_point(point)

        self._current_run = run
        self.points_label.setText(str(run.num_points))
        self.run_name_edit.setText("demo_data")

        self._update_plot()
        self._analyze()

        self.status_bar.showMessage(
            "Demo data loaded. Connect devices to perform real measurement."
        )

    @Slot()
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About",
            "AS5048A Encoder Calibration Tool\n\n"
            "Measures encoder error using a Thorlabs\n"
            "KDC101-controlled reference stage.\n\n"
            "The polar plot shows error magnitude\n"
            "vs. rotation angle to help align the\n"
            "magnetic encoder.\n\n"
            "© 2026",
        )

    def closeEvent(self, event):
        """Handle window close."""
        self._measuring = False

        if self._auto_worker:
            self._auto_worker.stop()
            if self.kdc101 and self.kdc101.connected:
                self.kdc101.stop_motion()
            self._auto_worker.wait()

        if self._measurement_worker:
            self._measurement_worker.stop()
            self._measurement_worker.wait()

        self._live_timer.stop()
        self._disconnect_devices()

        event.accept()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)

    # Set application info
    app.setApplicationName("AS5048A Encoder Calibration Tool")
    app.setApplicationVersion("1.0.0")

    window = CalibrationApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
