"""Logging and debugging utility module for the applications.

This module provides a centralized Debug class that handles logging to both console
and file outputs with configurable debug levels. It supports systematic logging of
errors and program flow, and can globally handle unhandled exceptions.

Features:
    - Multiple debug levels (OFF, ERROR, INFO, VERBOSE)
    - Dual output to console and file with customizable formatters
    - Automatic caller information tracking (class and function names)
    - Platform-independent temporary directory handling
    - Global exception hook for unhandled exceptions
    - UTF-8 encoded log file output

Debug Levels:
    - DEBUG_OFF (0): No debug output
    - DEBUG_ERROR (1): Only errors are shown
    - DEBUG_INFO (2): Errors and important information are shown
    - DEBUG_VERBOSE (3): All information is shown, including caller details

Debug methods:
    - Debug.error(message, exc_info=None): Log an error message
    - Debug.info(message): Log an informational message
    - Debug.debug(message): Log detailed debug information
    - Debug.warning(message): Log a warning message
    - Debug.critical(message): Log a critical error message
    - Debug.flush(): Force-flush any buffered log records
    - Debug.shutdown(): Detach and close all handlers, reset to pre-init state

Usage:
    Import the Debug class and initialize it before use:

    >>> Debug.init(debug_level=Debug.DEBUG_VERBOSE, log_dir="/path/to/logs")
    >>> Debug.info("Application started")
    >>> Debug.error("An error occurred", exc_info=True)

    To handle global exceptions add the following line after initialization:
    >>> sys.excepthook = Debug.exception_hook
"""

import logging
import logging.handlers
import os
import sys
import tempfile
import traceback
from datetime import datetime
from types import TracebackType


class Debug:
    """Debug utility class for application-wide logging.

    This class provides central debug and logging functions, to systematically
    log errors and program flow.
    The logger will log messages to both the console and a file if debugging is enabled.
    It also provides a method to handle unhandled exceptions globally.

    Attribute:
        logger: The logger used for debug output
        DEBUG_LEVEL: Current debug level (0 (Off) - 3 (Verbose))
        LOG_FILE: Path to the log file
    """

    # Debug level constants
    DEBUG_OFF = 0  # No debug output
    DEBUG_ERROR = 1  # Only errors are shown
    DEBUG_INFO = 2  # Errors and important information are shown
    DEBUG_VERBOSE = 3  # All information is shown

    # Default values - debugging disabled by default
    DEBUG_LEVEL = DEBUG_OFF
    LOG_FILE = None
    logger = None

    @classmethod
    def init(
        cls,
        debug_level: int = DEBUG_LEVEL,
        log_dir: "str | None" = None,
        app_name: str = "Application",
        suppress_logfile: bool = False,
        memory_capacity: int = 1000,
        memory_flush_level: int = logging.ERROR,
    ) -> None:
        """Initialise the logger with the specified debug level and log directory.

        If no log directory is specified, a platform-specific temp directory is used.

        Safe to call more than once: any handlers left over from a previous
        init() call (including ones attached via add_handler()) are detached
        and closed first, so re-initialising never duplicates log output.

        Args:
            debug_level: Debug level (0 (Off) - 3 (Verbose))
            log_dir: Directory where logs should be stored
            app_name: Application name used for the log file
            suppress_logfile: If True, no log file will be created even if debug_level > 0
            memory_capacity: Buffered records held in memory before an automatic
                flush to the log file (see logging.handlers.MemoryHandler)
            memory_flush_level: Minimum record level that triggers an immediate
                flush of the buffered records to the log file
        """
        cls._detach_handlers()
        cls.LOG_FILE = None
        cls.DEBUG_LEVEL = debug_level

        # Create logger
        cls.logger = logging.getLogger(app_name)
        cls.logger.setLevel(logging.DEBUG)

        # Handler for console output
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)

        # Set debug level accordingly
        if debug_level >= cls.DEBUG_VERBOSE:
            console_handler.setLevel(logging.DEBUG)
        elif debug_level >= cls.DEBUG_INFO:
            console_handler.setLevel(logging.INFO)
        elif debug_level >= cls.DEBUG_ERROR:
            console_handler.setLevel(logging.ERROR)
        else:
            console_handler.setLevel(logging.CRITICAL)  # No output

        cls.logger.addHandler(console_handler)

        # Only set up log file if debugging is enabled
        if debug_level == cls.DEBUG_OFF or suppress_logfile:
            return

        # Use provided directory if given, otherwise use platform-specific temp directory
        if log_dir:
            log_directory = log_dir
        else:
            # Creates: /tmp/app_name_logs (Linux/Mac) or %TEMP%\app_name_logs (Windows)
            log_directory = os.path.join(tempfile.gettempdir(), app_name.lower() + "_logs")

        if not os.path.exists(log_directory):
            try:
                os.makedirs(log_directory)
                print(f"Log directory created: {log_directory}")
            except Exception as e:  # pylint: disable=broad-except
                print(f"Error creating log directory: {e}")
                return

        # Create log file with timestamp and application name
        cls.LOG_FILE = os.path.join(
            log_directory,
            f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{app_name}.txt",
        )

        file_handler = logging.FileHandler(cls.LOG_FILE, encoding="utf-8", delay=True)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)  # Log verbose to file
        # Wrap handler with MemoryHandler for better performance with fast apps
        memory_handler = logging.handlers.MemoryHandler(
            capacity=memory_capacity, flushLevel=memory_flush_level, target=file_handler
        )
        cls.logger.addHandler(memory_handler)

        cls.info(f"Log file created: {cls.LOG_FILE}")

    @classmethod
    def _log(
        cls,
        level: int,
        label: str,
        message: str,
        *,
        exc_info: bool = False,
        min_print_level: "int | None" = None,
    ) -> None:
        """Shared implementation behind error/info/debug/warning/critical.

        Args:
            level: logging level to emit at (logging.INFO, logging.ERROR, ...)
            label: prefix used for the console fallback when no logger is configured
            message: message to log
            exc_info: if True, attach the current exception traceback
            min_print_level: minimum DEBUG_LEVEL required for the fallback print
                to happen when no logger is configured; None means always print
        """
        if cls.DEBUG_LEVEL >= cls.DEBUG_VERBOSE:
            message = f"{cls._get_caller_info()} {message}"

        if cls.logger is None:
            if min_print_level is None or cls.DEBUG_LEVEL >= min_print_level:
                print(f"{label}: {message}")
            return

        cls.logger.log(level, message, exc_info=exc_info)

    @classmethod
    def error(cls, message: str, exc_info: bool = False) -> None:
        """Log an error message.

        Args:
            message (str): Error message to log
            exc_info (bool): If True, attach current exception traceback (default False)
        """
        cls._log(logging.ERROR, "ERROR", message, exc_info=exc_info)

    @classmethod
    def info(cls, message: str) -> None:
        """Log an informational message.

        Args:
            message (str): Information to log
        """
        cls._log(logging.INFO, "INFO", message, min_print_level=cls.DEBUG_INFO)

    @classmethod
    def debug(cls, message: str) -> None:
        """Log detailed debug information.

        Args:
            message (str): Debug information to log
        """
        cls._log(logging.DEBUG, "DEBUG", message, min_print_level=cls.DEBUG_VERBOSE)

    @classmethod
    def warning(cls, message: str) -> None:
        """Log information as warning for non critical issues.

        Args:
            message (str): Warning information to log
        """
        cls._log(logging.WARNING, "WARNING", message, min_print_level=cls.DEBUG_INFO)

    @classmethod
    def critical(cls, message: str) -> None:
        """Log a critical error message.

        Args:
            message (str): Critical error message to log
        """
        cls._log(logging.CRITICAL, "CRITICAL", message)

    @classmethod
    def exception_hook(
        cls, exc_type: type, exc_value: BaseException, exc_traceback: TracebackType | None
    ) -> None:
        """Callback function for unhandled exceptions.

        Logs the exception and forwards it to sys.__excepthook__.

        Args:
            exc_type (type): The exception type
            exc_value (BaseException): The exception value
            exc_traceback (TracebackType | None): The traceback
        """
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        cls.critical(f"UNEXPECTED: {error_msg}")

        # Preserve the default exception handling (prints traceback, exits non-zero)
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    @classmethod
    def add_handler(cls, handler: logging.Handler) -> None:
        """Attach an additional logging.Handler at runtime (e.g. a log-window handler)."""
        if cls.logger is not None:
            cls.logger.addHandler(handler)

    @classmethod
    def remove_handler(cls, handler: logging.Handler) -> None:
        """Detach a previously added handler."""
        if cls.logger is not None:
            cls.logger.removeHandler(handler)

    @classmethod
    def flush(cls) -> None:
        """Force-flush any buffered log records (e.g. before bundling logs for a report)."""
        if cls.logger is None:
            return
        for handler in cls.logger.handlers:
            handler.flush()

    @classmethod
    def shutdown(cls) -> None:
        """Detach and close all handlers, then reset to the pre-init default state.

        Mainly useful for tests (to avoid state leaking between test cases)
        and for applications that want to fully re-configure logging from
        scratch rather than relying on init()'s implicit re-init behaviour.
        """
        cls._detach_handlers()
        cls.logger = None
        cls.DEBUG_LEVEL = cls.DEBUG_OFF
        cls.LOG_FILE = None

    @classmethod
    def _detach_handlers(cls) -> None:
        """Remove and fully close every handler currently on the logger, if any."""
        if cls.logger is None:
            return
        for handler in list(cls.logger.handlers):
            # Grab the MemoryHandler's target before close() detaches it,
            # so it can close the underlying file handle too (it isn't closed for us).
            target = getattr(handler, "target", None)
            cls.logger.removeHandler(handler)
            handler.close()
            if target is not None:
                target.close()

    @classmethod
    def _get_caller_info(cls) -> str:
        """Identify the class and function that made the original log call.

        Walks the frame chain directly via f_back rather than using
        inspect.stack(), which reads and caches source context for every
        frame on the stack (real file I/O) even though only the class/function
        name of a single frame is needed here.

        Returns:
            str: Formatted information about the caller in the format [Class.Function]
        """
        # Skip this frame, _log(), and the public method (error/info/...) that
        # called _log(), to reach the frame that actually triggered the log call.
        frame = sys._getframe(0)
        for _ in range(3):
            if frame.f_back is None:
                return ""
            frame = frame.f_back

        class_name = ""
        instance = frame.f_locals.get("self")
        if instance is not None:
            class_name = instance.__class__.__name__

        function_name = frame.f_code.co_name

        if class_name:
            return f"[{class_name}.{function_name}]"

        return f"[{function_name}]"
