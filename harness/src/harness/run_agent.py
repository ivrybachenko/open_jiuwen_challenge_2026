#!/usr/bin/env python3
"""Harness entrypoint.

The jury runs:

    python /app/run_agent.py --tasks-dir /data/tasks

In the image the ``harness`` package is installed into the venv and this file
is exposed as ``/app/run_agent.py``.
"""

from __future__ import annotations

from harness.application.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
