"""openJiuwen bootstrap.

The SDK initialises its logger on the first import and, by default, writes to
``./logs`` relative to the process CWD.  The jury runs the harness with a
read-only root filesystem and ``WORKDIR /app``, so that default crashes with
``OSError: [Errno 30] Read-only file system: '/app/logs'``.

Configure an in-memory logging setup with console-only output *before* any
other ``openjiuwen`` module is imported.
"""

from __future__ import annotations

import copy
import logging
from pathlib import Path

_LOG_DIR = Path("/tmp/openjiuwen-logs")
_configured = False


def configure_logging(level: str = "WARNING") -> None:
    """Make openJiuwen logging safe for a read-only root filesystem."""
    global _configured
    if _configured:
        return

    from openjiuwen.core.common.logging.default.constant import (
        DEFAULT_INNER_LOG_CONFIG,
    )
    from openjiuwen.core.common.logging.log_config import configure_log_config

    config = copy.deepcopy(DEFAULT_INNER_LOG_CONFIG)
    config["log_path"] = str(_LOG_DIR)
    config["output"] = ["console"]  # no file sinks, nothing to write on disk
    config["level"] = level.upper()
    # Avoid duplicate records through the root stdlib handler.
    config["propagate"] = False
    configure_log_config(config)
    # Some SDK modules use plain stdlib loggers, bypassing the SDK config.
    for name in ("openjiuwen", "alembic", "httpx"):
        logging.getLogger(name).setLevel(level.upper())
    _configured = True
