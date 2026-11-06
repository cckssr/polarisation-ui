"""Opens the auxiliary windows of the main window: settings dialog, calibration, debug, log."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QWidget

from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.ui.context import AppContext
from polarisation_ui.ui.dialogs.acq_settings import AcquisitionSettingsDialog
from polarisation_ui.ui.windows.encoder_debug_window import EncoderDebugDialog


class AuxiliaryWindows:
    """Creates the dialogs on the shared :class:`AppContext`; all are children of ``parent``.

    ``profiles_changed`` is called when a calibration window saved a power-calibration profile.
    """

    def __init__(
        self,
        parent: QWidget,
        ctx: AppContext,
        config: AppConfig,
        profiles_changed: Callable[[], None],
    ) -> None:
        """Remember the shared state; windows are created on demand."""
        self._parent = parent
        self._ctx = ctx
        self._config = config
        self._profiles_changed = profiles_changed
        self._log_window: QDialog | None = None

    def open_acq_settings(self) -> None:
        """Open the acquisition settings dialog (spike filter + inversion settings)."""
        measurement = self._ctx.measurement
        dialog = AcquisitionSettingsDialog(
            measurement.acq_settings, parent=self._parent, config=self._config
        )
        # Without this the dialog's C++ object stays parented to the main window forever (Qt only
        # auto-deletes on close), so re-opening would leak one QDialog per open.
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        # exec() makes the dialog application-modal; setEnabled(False) is NOT used because it
        # propagates to child QObjects and would disable the dialog itself.
        if dialog.exec() == QDialog.DialogCode.Accepted:
            measurement.replace_acq_settings(dialog.get_settings())

    def open_power_calibration(self) -> None:
        """Open the manual power-calibration window."""
        from polarisation_ui.ui.windows.power_calibration_window import PowerCalibrationWindow

        self._open_calibration(PowerCalibrationWindow)

    def open_auto_power_calibration(self) -> None:
        """Open the automatic power-calibration wizard."""
        from polarisation_ui.ui.windows.auto_power_calibration_window import (
            AutoPowerCalibrationWindow,
        )

        self._open_calibration(AutoPowerCalibrationWindow)

    def _open_calibration(self, window_class: type[QDialog]) -> None:
        dialog = window_class(
            data_controller=self._ctx.data,
            pm400=self._ctx.pm400.pm400,
            parent=self._parent,
            config=self._config,
        )
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.profile_saved.connect(self._profiles_changed)  # type: ignore[attr-defined]
        dialog.show()

    def open_encoder_debug(self) -> None:
        """Open the encoder debug dialog (non-modal)."""
        dialog = EncoderDebugDialog(
            self._ctx.connection.device_manager,
            sample_inverted=self._ctx.measurement.acq_settings.sample_stage_inverted,
            data_controller=self._ctx.data,
            pm400=self._ctx.pm400.pm400,
            parent=self._parent,
            config=self._config,
        )
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.show()

    def open_log_window(self) -> None:
        """Open or raise the live log output window."""
        if self._log_window is None:
            from polarisation_ui.ui.windows.log_window import LogWindow

            self._log_window = LogWindow(parent=self._parent, config=self._config)
            self._log_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            self._log_window.destroyed.connect(self._on_log_window_closed)
        self._log_window.show()
        self._log_window.raise_()
        self._log_window.activateWindow()

    def _on_log_window_closed(self) -> None:
        self._log_window = None
