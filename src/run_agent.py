#!/usr/bin/env python3
"""Container entrypoint.

The jury runs:

    python /app/run_agent.py --tasks-dir /data/tasks

Keep this file tiny: all harness code lives next to it in ``harness/``.

Inside the image this directory is copied to ``/app``, so the path the jury
runs (``/app/run_agent.py``) stays the same.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from harness.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
