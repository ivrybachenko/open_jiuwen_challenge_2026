#!/usr/bin/env python3
"""Kill harness scripts that outlive their timeout.

The stock harness kills the script process group on timeout, but in practice a
child (`python3 -c ...`) can survive and keep a CPU core busy for many minutes,
slowing every later task.  This research watchdog scans ``ps`` for
``.harness_step_*`` processes older than a threshold and kills their group.

Usage::

    python research/experiments/0006-predict-cost-before-solve/script_watchdog.py &
"""

from __future__ import annotations

import os
import re
import signal
import subprocess
import time

MAX_AGE_SECONDS = 300
PATTERN = re.compile(r"\.harness_step_")


def _age_seconds(etime: str) -> int:
    days = 0
    if "-" in etime:
        day_part, etime = etime.split("-", 1)
        days = int(day_part)
    parts = [int(p) for p in etime.split(":")]
    if len(parts) == 3:
        hours, minutes, seconds = parts
    elif len(parts) == 2:
        hours, minutes, seconds = 0, parts[0], parts[1]
    else:
        hours, minutes, seconds = 0, 0, parts[0]
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def main() -> None:
    while True:
        try:
            output = subprocess.check_output(
                ["ps", "-eo", "pid=,pgid=,etime=,command="],
                text=True, errors="replace",
            )
            for line in output.splitlines():
                parts = line.strip().split(None, 3)
                if len(parts) < 4:
                    continue
                pid, pgid, etime, command = parts
                if not PATTERN.search(command):
                    continue
                age = _age_seconds(etime)
                if age < MAX_AGE_SECONDS:
                    continue
                try:
                    os.killpg(int(pgid), signal.SIGKILL)
                except (ProcessLookupError, PermissionError, OSError):
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                    except (ProcessLookupError, PermissionError, OSError):
                        pass
                print(f"killed {pid} (age {age}s): {command[:120]}", flush=True)
        except Exception as exc:  # noqa: BLE001 - watchdog must not die
            print(f"watchdog error: {exc}", flush=True)
        time.sleep(10)


if __name__ == "__main__":
    main()
