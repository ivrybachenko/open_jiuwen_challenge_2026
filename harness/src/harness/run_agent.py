#!/usr/bin/env python3
"""Harness entrypoint.

The jury runs:

    python /app/run_agent.py --tasks-dir /data/tasks

In the image the ``harness`` package is installed into the venv and this file
is exposed as ``/app/run_agent.py``.
"""

from __future__ import annotations

import logging

from harness.cli import parse_args


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, set up logging and run the orchestration."""
    args = parse_args(argv)
    logging.basicConfig(
        level=str(args.log_level).upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    # Import after parsing so --help does not initialize openJiuwen.
    from harness.solving.runner import run

    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
