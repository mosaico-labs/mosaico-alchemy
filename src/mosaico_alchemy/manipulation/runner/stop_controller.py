"""
Cooperative stop handling for long-running ingestion sessions.

This module centralizes the Ctrl-C behavior used by the CLI and runner. The first
interrupt requests a graceful stop after the current unit of work, while the second
interrupt exits immediately.
"""

from __future__ import annotations

import logging
import signal
from types import FrameType

LOGGER = logging.getLogger(__name__)


class StopController:
    """
    Tracks and coordinates user stop requests across the ingestion pipeline.

    The controller is callable so it can be passed directly where a `stop_requested`
    callback is expected. It also owns temporary SIGINT handler installation for the
    duration of a CLI ingestion run.
    """

    def __init__(self) -> None:
        """Initializes the controller with no pending stop request."""
        self._interrupt_count = 0
        self._stop_requested = False
        self._previous_handler = None

    def __call__(self) -> bool:
        """Returns whether a stop has been requested."""
        return self._stop_requested

    @property
    def stop_requested(self) -> bool:
        """Returns whether a graceful stop has been requested."""
        return self._stop_requested

    def request_stop(self) -> None:
        """Marks the current run for graceful termination."""
        self._stop_requested = True

    def install(self) -> None:
        """Installs the controller's SIGINT handler, preserving the previous one."""
        self._previous_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self._handle_sigint)

    def restore(self) -> None:
        """Restores the previously installed SIGINT handler, if any."""
        if self._previous_handler is None:
            return

        signal.signal(signal.SIGINT, self._previous_handler)
        self._previous_handler = None

    def _handle_sigint(self, _signum: int, _frame: FrameType | None) -> None:
        """Escalates the first Ctrl-C to a graceful stop and the second to an immediate exit."""
        self._interrupt_count += 1
        self._stop_requested = True

        if self._interrupt_count == 1:
            LOGGER.warning(
                "Ctrl-C received. Stopping after the current operation and printing a final recap."
            )
            raise KeyboardInterrupt

        LOGGER.error("Second Ctrl-C received. Exiting immediately.")
        raise SystemExit(130)
