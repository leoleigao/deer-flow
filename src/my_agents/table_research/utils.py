"""Utility helpers for Table-Deep-Research agents."""

from __future__ import annotations

import logging
import os

_logged_stub = False


def log_stub_once(logger: logging.Logger) -> None:
    """Log the Glean stub mode at most once."""
    global _logged_stub
    if not _logged_stub:
        mode = "stub" if os.getenv("USE_GLEAN_STUB", "true").lower() == "true" else "live"
        logger.info(f"Operating in Glean {mode} mode")
        _logged_stub = True
