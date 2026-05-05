"""
Manual Calibration Dialog.

Two-phase dialog:
  1. Setup  — user picks step size and run name.
  2. Step   — for each target angle, the user physically sets the stage,
              then clicks Accept.  A live encoder reading is shown so they
              can verify position before accepting.

On completion the dialog returns a CalibrationRun that is identical to the
one produced by the KDC101 path and can be fed straight into CalibrationAnalysis
/ CalibrationPlotter.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from calibration.manual_runner import ManualCalibrationController
from calibration.measurement import CalibrationRun
from devices.arduino_encoder import ArduinoEncoder


class ManualCalibrationDialog(QDialog):
    """
    Modal dialog that walks the user through a manual angle-by-angle
    calibration run.

    Args:
        arduino:  Connected ArduinoEncoder instance.  May be None — the
                  dialog will open but Accept will be disabled until a
                  live read succeeds.
        parent:   Parent widget.
    """

    def __init__(
        self,
        arduino: Optional[ArduinoEncoder],
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Manual Calibration")
        self.setMinimumWidth(420)

        self._arduino = arduino
        self._controller: Optional[ManualCalibrationController] = None
        self._completed_run: Optional[CalibrationRun] = None
        self._active_encoder_id: str = "A"

        self._live_timer = QTimer(self)
        self._live_timer.setInterval(150)
        self._live_timer.timeout.connect(self._poll_live)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._build_setup_page())
        self._stack.addWidget(self._build_step_page())

        root = QVBoxLayout(self)
        root.addWidget(self._stack)

    # ------------------------------------------------------------------
    # Page builders

    def _build_setup_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        layout.addWidget(
            QLabel(
                "<b>Manual encoder calibration</b><br>"
                "You will be prompted to set the stage to each target angle "
                "manually, then click Accept to record the encoder reading."
            )
        )

        # Step size
        step_row = QHBoxLayout()
        step_row.addWidget(QLabel("Step size (°):"))
        self._step_spin = QDoubleSpinBox()
        self._step_spin.setRange(0.5, 90.0)
        self._step_spin.setDecimals(1)
        self._step_spin.setSingleStep(1.0)
        self._step_spin.setValue(10.0)
        self._step_spin.setToolTip(
            "Angular spacing between measurement points (0.5–90°).\n"
            "10° → 36 steps, 5° → 72 steps, 1° → 360 steps."
        )
        step_row.addWidget(self._step_spin)
        step_row.addStretch()
        layout.addLayout(step_row)

        # Preview
        self._steps_preview = QLabel()
        self._steps_preview.setStyleSheet("color: gray;")
        self._update_step_preview()
        self._step_spin.valueChanged.connect(self._update_step_preview)
        layout.addWidget(self._steps_preview)

        # Encoder selection
        enc_box = QGroupBox("Encoder")
        enc_layout = QVBoxLayout(enc_box)
        self._encoder_btn_group = QButtonGroup(self)
        self._encoder_a_radio = QRadioButton("A — Sample encoder  (reading is reversed)")
        self._encoder_b_radio = QRadioButton("B — Detector encoder")
        self._encoder_a_radio.setChecked(True)
        self._encoder_btn_group.addButton(self._encoder_a_radio, 0)
        self._encoder_btn_group.addButton(self._encoder_b_radio, 1)
        enc_layout.addWidget(self._encoder_a_radio)
        enc_layout.addWidget(self._encoder_b_radio)
        layout.addWidget(enc_box)

        # Run name
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Run name:"))
        from datetime import datetime

        self._run_name_edit = QLineEdit(
            datetime.now().strftime("manual_cal_%Y%m%d_%H%M")
        )
        name_row.addWidget(self._run_name_edit)
        layout.addLayout(name_row)

        layout.addStretch()

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Start")
        buttons.accepted.connect(self._start_calibration)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        return page

    def _build_step_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(14)

        # Progress header
        self._progress_label = QLabel("Step 1 of 36")
        self._progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._progress_label)

        self._progress_bar = QProgressBar()
        self._progress_bar.setTextVisible(False)
        layout.addWidget(self._progress_bar)

        # Instruction
        instruction_label = QLabel("Please set the stage to:")
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instruction_label)

        self._target_label = QLabel("0.0°")
        target_font = QFont()
        target_font.setPointSize(36)
        target_font.setBold(True)
        self._target_label.setFont(target_font)
        self._target_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._target_label.setStyleSheet("color: #2255cc;")
        layout.addWidget(self._target_label)

        # Live encoder reading
        live_row = QHBoxLayout()
        live_row.addStretch()
        live_row.addWidget(QLabel("Live reading:"))
        self._live_label = QLabel("---")
        live_font = QFont("Courier", 13)
        self._live_label.setFont(live_font)
        self._live_label.setMinimumWidth(90)
        live_row.addWidget(self._live_label)
        live_row.addWidget(QLabel("°"))
        live_row.addStretch()
        layout.addLayout(live_row)

        layout.addSpacing(8)

        # Action buttons
        btn_row = QHBoxLayout()

        self._abort_btn = QPushButton("Abort")
        self._abort_btn.setToolTip("Discard all data and close")
        self._abort_btn.clicked.connect(self._abort)
        btn_row.addWidget(self._abort_btn)

        btn_row.addStretch()

        self._skip_btn = QPushButton("Skip")
        self._skip_btn.setToolTip("Skip this angle without recording")
        self._skip_btn.clicked.connect(self._skip_step)
        btn_row.addWidget(self._skip_btn)

        self._accept_btn = QPushButton("Accept")
        self._accept_btn.setToolTip("Record the current encoder reading for this angle")
        self._accept_btn.setDefault(True)
        self._accept_btn.clicked.connect(self._accept_step)
        accept_font = QFont()
        accept_font.setBold(True)
        self._accept_btn.setFont(accept_font)
        btn_row.addWidget(self._accept_btn)

        layout.addLayout(btn_row)

        # Recorded points counter
        self._recorded_label = QLabel("0 points recorded")
        self._recorded_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._recorded_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(self._recorded_label)

        return page

    # ------------------------------------------------------------------
    # Setup → step transition

    @Slot()
    def _update_step_preview(self) -> None:
        step = self._step_spin.value()
        import math

        n = math.floor(360.0 / step)
        self._steps_preview.setText(f"{n} steps, last angle: {(n - 1) * step:.1f}°")

    @Slot()
    def _start_calibration(self) -> None:
        if self._arduino is None or not self._arduino.connected:
            QMessageBox.warning(
                self,
                "Arduino not connected",
                "Connect to the Arduino encoder before starting manual calibration.",
            )
            return

        self._active_encoder_id = "A" if self._encoder_a_radio.isChecked() else "B"

        try:
            self._controller = ManualCalibrationController(
                arduino=self._arduino,
                step_size_deg=self._step_spin.value(),
                run_name=self._run_name_edit.text().strip() or "",
                encoder_id=self._active_encoder_id,
            )
        except ValueError as exc:
            QMessageBox.critical(self, "Invalid settings", str(exc))
            return

        self._progress_bar.setMaximum(self._controller.total_steps)
        self._stack.setCurrentIndex(1)
        self._live_timer.start()
        self._refresh_step_ui()

    # ------------------------------------------------------------------
    # Step page logic

    def _refresh_step_ui(self) -> None:
        ctrl = self._controller
        if ctrl is None:
            return

        if ctrl.is_complete:
            self._finish()
            return

        target = ctrl.current_target
        step = ctrl.step_index
        total = ctrl.total_steps

        self._progress_label.setText(f"Step {step + 1} of {total}")
        self._progress_bar.setValue(step)
        self._target_label.setText(f"{target:.1f}°")
        self._recorded_label.setText(f"{ctrl._run.num_points} point(s) recorded")

    @Slot()
    def _poll_live(self) -> None:
        if self._arduino and self._arduino.connected:
            try:
                angle = self._arduino.read_angle(self._active_encoder_id)
                if angle is not None:
                    if self._active_encoder_id == "A":
                        angle = (-angle) % 360.0
                    self._live_label.setText(f"{angle:8.3f}")
                    self._live_label.setStyleSheet("color: green;")
                    return
            except Exception:
                pass
        self._live_label.setText("---")
        self._live_label.setStyleSheet("color: red;")

    @Slot()
    def _accept_step(self) -> None:
        if self._controller is None:
            return
        try:
            self._controller.accept_current()
        except RuntimeError as exc:
            QMessageBox.warning(self, "Read error", str(exc))
            return
        self._refresh_step_ui()

    @Slot()
    def _skip_step(self) -> None:
        if self._controller is None:
            return
        self._controller.skip_current()
        self._refresh_step_ui()

    @Slot()
    def _abort(self) -> None:
        if self._controller and self._controller._run.num_points > 0:
            reply = QMessageBox.question(
                self,
                "Abort calibration",
                f"{self._controller._run.num_points} point(s) will be discarded. Abort?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        self._live_timer.stop()
        self.reject()

    def _finish(self) -> None:
        self._live_timer.stop()
        ctrl = self._controller
        if ctrl is None:
            self.reject()
            return

        n = ctrl._run.num_points
        total = ctrl.total_steps
        self._progress_bar.setValue(total)

        if n == 0:
            QMessageBox.warning(self, "No data", "No points were recorded.")
            self.reject()
            return

        self._completed_run = ctrl.get_run()

        QMessageBox.information(
            self,
            "Calibration complete",
            f"Recorded {n} of {total} steps.\n"
            "Click OK to load the results into the analysis view.",
        )
        self.accept()

    # ------------------------------------------------------------------
    # Result accessor

    def get_run(self) -> Optional[CalibrationRun]:
        """Return the completed CalibrationRun, or None if aborted."""
        return self._completed_run

    def closeEvent(self, event) -> None:
        self._live_timer.stop()
        super().closeEvent(event)
