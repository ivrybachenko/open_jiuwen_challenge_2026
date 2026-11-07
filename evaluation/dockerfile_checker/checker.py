"""Build the Docker image, check its size and run a small task set in it."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from evaluation.common.reporting import format_size, tail
from evaluation.common.runner import (
    DEFAULT_LLM_BASE_URL,
    missing_llm_env,
    read_solutions,
)
from evaluation.common.suite import (
    PreparedSuite,
    SuiteSummary,
    TaskOutcome,
    evaluate_suite,
    outcome_to_dict,
    prepare_suite,
    summarize,
)
from evaluation.common.tasks import load_task_set, resolve_task_set

DEFAULT_MAX_IMAGE_BYTES = 4_000_000_000  # 4 GB, competition limit
DEFAULT_MAX_REPO_BYTES = 100_000_000  # 100 MB without .git
DEFAULT_BUILD_TIMEOUT = 1000.0  # seconds, competition limit
DEFAULT_RUN_TIMEOUT = 3600.0  # seconds, competition limit


@dataclass
class CommandResult:
    command: list[str]
    returncode: int
    duration_seconds: float
    stdout: str
    stderr: str
    timed_out: bool = False

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def to_dict(self) -> dict:
        return {
            "command": self.command,
            "returncode": self.returncode,
            "duration_seconds": round(self.duration_seconds, 3),
            "duration_minutes": round(self.duration_seconds / 60.0, 3),
            "timed_out": self.timed_out,
            "stdout_tail": tail(self.stdout),
            "stderr_tail": tail(self.stderr),
        }


@dataclass
class DockerCheckReport:
    image: str
    max_image_bytes: int
    max_repo_bytes: int
    build: CommandResult | None = None
    image_size_bytes: int | None = None
    repo_size_bytes: int = 0
    run: CommandResult | None = None
    task_set: str | None = None
    task_set_source: str | None = None
    outcomes: list[TaskOutcome] = field(default_factory=list)
    summary: SuiteSummary | None = None
    work_dir: Path | None = None
    cpus: str = "8"

    @property
    def image_size_ok(self) -> bool:
        return (
            self.image_size_bytes is not None
            and self.image_size_bytes <= self.max_image_bytes
        )

    @property
    def repo_size_ok(self) -> bool:
        return self.repo_size_bytes <= self.max_repo_bytes

    def to_dict(self) -> dict:
        return {
            "image": self.image,
            "build": self.build.to_dict() if self.build else None,
            "sizes": {
                "image_bytes": self.image_size_bytes,
                "image_human": format_size(self.image_size_bytes),
                "image_limit_bytes": self.max_image_bytes,
                "image_ok": self.image_size_ok,
                "repo_bytes": self.repo_size_bytes,
                "repo_human": format_size(self.repo_size_bytes),
                "repo_limit_bytes": self.max_repo_bytes,
                "repo_ok": self.repo_size_ok,
            },
            "run": self.run.to_dict() if self.run else None,
            "cpus": self.cpus,
            "task_set": self.task_set,
            "task_set_source": self.task_set_source,
            "summary": self.summary.to_dict() if self.summary else None,
            "tasks": [outcome_to_dict(outcome) for outcome in self.outcomes],
            "work_dir": str(self.work_dir) if self.work_dir else None,
        }


def check_dockerfile(
    *,
    repo: str | Path,
    image: str = "hack:latest",
    task_set_path: str | Path,
    tasks_root: str | Path,
    build: bool = True,
    skip_run: bool = False,
    no_cache: bool = False,
    network: str | None = None,
    cpus: str = "8",
    python: str | None = None,
    strict: bool = False,
    forbid_test_edits: bool = True,
    max_image_bytes: int = DEFAULT_MAX_IMAGE_BYTES,
    max_repo_bytes: int = DEFAULT_MAX_REPO_BYTES,
    build_timeout: float = DEFAULT_BUILD_TIMEOUT,
    run_timeout: float = DEFAULT_RUN_TIMEOUT,
    model: str | None = None,
    budget: int | None = None,
    max_iterations: int | None = None,
    work_dir: str | Path | None = None,
    keep: bool = False,
) -> DockerCheckReport:
    repo = Path(repo).resolve()
    if work_dir is not None:
        base_dir = Path(work_dir).resolve()
    else:
        # Docker Desktop on macOS does not always share /var/folders, which is
        # where tempfile.mkdtemp() puts directories by default.  Use a path
        # under the repository instead; it is inside the shared /Users tree.
        docker_tmp = repo / "out"
        docker_tmp.mkdir(parents=True, exist_ok=True)
        base_dir = Path(tempfile.mkdtemp(prefix="ojw-docker-", dir=docker_tmp))
    report = DockerCheckReport(
        image=image,
        max_image_bytes=max_image_bytes,
        max_repo_bytes=max_repo_bytes,
        cpus=cpus,
    )

    try:
        if build:
            report.build = build_image(
                repo=repo,
                image=image,
                no_cache=no_cache,
                timeout=build_timeout,
            )
            if not report.build.ok:
                return report

        report.image_size_bytes = docker_image_size(image)
        report.repo_size_bytes = repo_size(repo)

        if skip_run:
            return report

        missing = missing_llm_env()
        if missing:
            raise RuntimeError(
                "set LLM_API_KEY before running the container, e.g. "
                'LLM_API_KEY="$NEURAL_DEEP_API_KEY"'
            )

        spec = load_task_set(task_set_path)
        tasks = resolve_task_set(spec, tasks_root)
        report.task_set = spec.name
        report.task_set_source = str(spec.source)

        prepared = prepare_suite(tasks, base_dir)
        report.run = run_in_docker(
            prepared=prepared,
            base_dir=base_dir,
            image=image,
            network=network,
            cpus=cpus,
            timeout=run_timeout,
            model=model,
            budget=budget,
            max_iterations=max_iterations,
        )
        report.outcomes = evaluate_suite(
            prepared,
            read_solutions(base_dir / "out" / "solutions.json"),
            python=python,
            strict=strict,
            forbid_test_edits=forbid_test_edits,
        )
        report.summary = summarize(report.outcomes)
        return report
    finally:
        if work_dir is None and not keep:
            shutil.rmtree(base_dir, ignore_errors=True)
            report.work_dir = None
        else:
            report.work_dir = base_dir


def build_image(
    *,
    repo: Path,
    image: str,
    no_cache: bool = False,
    timeout: float = DEFAULT_BUILD_TIMEOUT,
) -> CommandResult:
    command = ["docker", "build", "-t", image]
    if no_cache:
        command.append("--no-cache")
    command.append(str(repo))
    return run_command(command, cwd=repo, timeout=timeout)


def docker_image_size(image: str) -> int | None:
    """Size of the image in bytes, matching the jury's ``docker images`` view.

    ``docker image inspect --format {{.Size}}`` reports the compressed image
    size on some engines, so it is only a fallback.
    """
    listed = run_command(
        ["docker", "images", "--format", "{{.Size}}", image],
        timeout=60.0,
    )
    if listed.ok:
        for line in listed.stdout.splitlines():
            size = parse_human_size(line)
            if size is not None:
                return size

    inspected = run_command(
        ["docker", "image", "inspect", "--format", "{{.Size}}", image],
        timeout=60.0,
    )
    if inspected.ok:
        raw = inspected.stdout.strip()
        if raw.isdigit():
            return int(raw)
    return None


_SIZE_UNITS = {
    "B": 1,
    "KB": 1000,
    "MB": 1000**2,
    "GB": 1000**3,
    "TB": 1000**4,
    "PB": 1000**5,
    "KIB": 1024,
    "MIB": 1024**2,
    "GIB": 1024**3,
    "TIB": 1024**4,
}


def parse_human_size(text: str) -> int | None:
    text = text.strip().upper().replace(" ", "")
    if not text:
        return None
    number = ""
    unit = ""
    for char in text:
        if char.isdigit() or char in {".", ","}:
            number += char
        else:
            unit += char
    if not number:
        return None
    try:
        value = float(number.replace(",", "."))
    except ValueError:
        return None
    factor = _SIZE_UNITS.get(unit or "B")
    if factor is None:
        return None
    return int(value * factor)


def repo_size(repo: str | Path) -> int:
    """Size of the repository without ``.git`` (tracked files when possible)."""
    repo = Path(repo)
    listed = run_command(
        ["git", "-C", str(repo), "ls-files", "-z"],
        timeout=60.0,
    )
    if listed.ok and listed.stdout:
        total = 0
        for relative in listed.stdout.split("\0"):
            if not relative:
                continue
            path = repo / relative
            try:
                total += path.stat().st_size
            except OSError:
                continue
        return total

    skip_dirs = {".git", ".venv", "venv", "__pycache__", "out", ".mypy_cache", ".pytest_cache"}
    total = 0
    for root, dirs, files in os.walk(repo):
        dirs[:] = [name for name in dirs if name not in skip_dirs]
        for name in files:
            try:
                total += (Path(root) / name).stat().st_size
            except OSError:
                continue
    return total


def run_in_docker(
    *,
    prepared: PreparedSuite,
    base_dir: Path,
    image: str,
    network: str | None,
    cpus: str,
    timeout: float,
    model: str | None,
    budget: int | None,
    max_iterations: int | None,
) -> CommandResult:
    out_dir = base_dir / "out"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    container_name = f"ojw-check-{uuid.uuid4().hex[:8]}"

    command = ["docker", "run", "--rm", "--name", container_name]
    if network:
        command += ["--network", network]
    command += [
        "-e",
        f"LLM_BASE_URL={DEFAULT_LLM_BASE_URL}",
        "-e",
        "LLM_API_KEY",
        "-e",
        "HOME=/tmp",
        "-e",
        "OUT=/data/out/solutions.json",
        "-v",
        f"{prepared.tasks_dir}:/data/tasks:rw",
        "-v",
        f"{out_dir}:/data/out:rw",
        "--read-only",
        "--tmpfs",
        "/tmp:rw,size=2g",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--cpus",
        str(cpus),
        "--memory",
        "16g",
        "--pids-limit",
        "512",
        "--workdir",
        "/app",
        "--entrypoint",
        "python",
        image,
        "/app/run_agent.py",
        "--tasks-dir",
        "/data/tasks",
    ]
    if model:
        command += ["--model", model]
    if budget is not None:
        command += ["--budget", str(budget)]
    if max_iterations is not None:
        command += ["--max-iterations", str(max_iterations)]

    result = run_command(command, timeout=timeout)
    if result.timed_out:
        # Killing the CLI may leave the container running.
        run_command(["docker", "rm", "-f", container_name], timeout=60.0)
    return result


def run_command(
    command: list[str],
    *,
    cwd: str | Path | None = None,
    timeout: float | None = None,
    env: dict[str, str] | None = None,
) -> CommandResult:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd) if cwd is not None else None,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return CommandResult(
            command=command,
            returncode=completed.returncode,
            duration_seconds=time.monotonic() - started,
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
        )
    except subprocess.TimeoutExpired as exc:
        return CommandResult(
            command=command,
            returncode=124,
            duration_seconds=time.monotonic() - started,
            stdout=_as_text(exc.stdout),
            stderr=_as_text(exc.stderr) + f"\n[timeout after {timeout}s]",
            timed_out=True,
        )
    except FileNotFoundError as exc:
        return CommandResult(
            command=command,
            returncode=127,
            duration_seconds=time.monotonic() - started,
            stdout="",
            stderr=f"{type(exc).__name__}: {exc}",
        )


def _as_text(value: bytes | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value
