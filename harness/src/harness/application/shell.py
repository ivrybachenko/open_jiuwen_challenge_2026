"""Run external processes without letting them take the harness down.

Agent replies are arbitrary bash scripts, and task test suites are arbitrary
Python.  Both can hang, print gigabytes, or fail to start.  This module keeps
the output bounded and always returns a result instead of raising.
"""

from __future__ import annotations

import os
import signal
import subprocess
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProcessResult:
    command: list[str] = field(default_factory=list)
    exit_code: int | None = None
    output: str = ""
    duration_seconds: float = 0.0
    timed_out: bool = False
    error: str = ""
    script_path: str = ""

    @property
    def ok(self) -> bool:
        return self.error == "" and not self.timed_out and self.exit_code == 0


def _decode(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def _read_stream(stream, head_limit: int, tail_limit: int, sink: dict) -> None:
    head = bytearray()
    tail: deque[bytes] = deque()
    tail_len = 0
    total = 0
    try:
        while True:
            chunk = stream.read(8192)
            if not chunk:
                break
            total += len(chunk)
            if len(head) < head_limit:
                take = min(head_limit - len(head), len(chunk))
                head.extend(chunk[:take])
                chunk = chunk[take:]
            if chunk:
                tail.append(chunk)
                tail_len += len(chunk)
                while tail_len > tail_limit and tail:
                    removed = tail.popleft()
                    tail_len -= len(removed)
    except (OSError, ValueError):
        pass
    finally:
        try:
            stream.close()
        except OSError:
            pass
    sink["head"] = bytes(head)
    sink["tail"] = b"".join(tail)
    sink["total"] = total


def _combine_streams(stdout: dict, stderr: dict, max_chars: int) -> str:
    def render(label: str, data: dict) -> str:
        head = _decode(data.get("head", b""))
        tail = _decode(data.get("tail", b""))
        total = int(data.get("total", 0))
        text = head
        if total > len(head.encode("utf-8", errors="replace")) + len(
            tail.encode("utf-8", errors="replace")
        ):
            text += "\n...[output truncated]...\n" + tail
        if label and text:
            return f"[{label}]\n{text}"
        return text

    parts = [part for part in (render("stdout", stdout), render("stderr", stderr)) if part]
    output = "\n".join(parts)
    if len(output) > max_chars:
        head_len = max(1, int(max_chars * 0.4))
        tail_len = max(1, max_chars - head_len)
        output = (
            output[:head_len]
            + "\n...[output truncated]...\n"
            + output[-tail_len:]
        )
    return output


def run_process(
    command: list[str],
    *,
    cwd: str | Path,
    timeout: float,
    max_output_chars: int = 4000,
    env: dict[str, str] | None = None,
) -> ProcessResult:
    """Run ``command`` with a hard timeout and bounded output."""
    started = time.monotonic()
    child_env = dict(os.environ)
    child_env.setdefault("PYTHONUNBUFFERED", "1")
    child_env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    child_env.setdefault("MPLBACKEND", "Agg")
    if env:
        child_env.update({str(key): str(value) for key, value in env.items()})

    max_bytes = max(1000, int(max_output_chars) * 4)
    head_limit = int(max_bytes * 0.4)
    tail_limit = max_bytes - head_limit
    stdout_sink: dict = {}
    stderr_sink: dict = {}

    try:
        process = subprocess.Popen(
            command,
            cwd=str(cwd),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=child_env,
            start_new_session=True,
        )
    except (OSError, ValueError) as exc:
        return ProcessResult(
            command=list(command),
            exit_code=None,
            output="",
            duration_seconds=time.monotonic() - started,
            error=f"{type(exc).__name__}: {exc}",
        )

    out_thread = threading.Thread(
        target=_read_stream,
        args=(process.stdout, head_limit, tail_limit, stdout_sink),
        daemon=True,
    )
    err_thread = threading.Thread(
        target=_read_stream,
        args=(process.stderr, head_limit, tail_limit, stderr_sink),
        daemon=True,
    )
    out_thread.start()
    err_thread.start()

    timed_out = False
    try:
        process.wait(timeout=max(0.1, float(timeout)))
    except subprocess.TimeoutExpired:
        timed_out = True
        _kill_group(process)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass

    out_thread.join(timeout=5)
    err_thread.join(timeout=5)
    output = _combine_streams(stdout_sink, stderr_sink, max_output_chars)
    exit_code = 124 if timed_out else process.returncode
    return ProcessResult(
        command=list(command),
        exit_code=exit_code,
        output=output,
        duration_seconds=time.monotonic() - started,
        timed_out=timed_out,
    )


def _kill_group(process: subprocess.Popen) -> None:
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            process.kill()
        except (ProcessLookupError, OSError):
            pass


def shell_quote(value: str) -> str:
    """Small helper for prompt/transcript rendering."""
    if value and all(ch.isalnum() or ch in "/._-+" for ch in value):
        return value
    return "'" + value.replace("'", "'\\''") + "'"
