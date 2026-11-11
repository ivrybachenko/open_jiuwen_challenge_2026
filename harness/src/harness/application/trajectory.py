"""Save complete task trajectories with openJiuwen's built-in recorder.

The harness runs in two modes.  In the jury mode it only solves tasks; when a
trajectory directory is configured it also collects data for the task-difficulty
predictor.  The second mode needs the full agent trace -- model reasoning, LLM
messages and tool calls -- not just the final answer.

openJiuwen already ships that recorder: ``TrajectoryRail`` subscribes to the
observability span processor, drains LLM/tool/event spans on every invoke and
writes one canonical trajectory through ``FileTrajectoryStore``.  This module
only turns observability on, opens the per-task root span the SDK needs to emit
LLM/tool spans, and wires the rail into the agent.

All openJiuwen imports are lazy: the SDK logger must be reconfigured before its
first import (the container runs with a read-only root filesystem).
"""

from __future__ import annotations

import logging
import re
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

log = logging.getLogger(__name__)

TRAJECTORY_FILE_NAME = "trajectories_default.jsonl"
READABLE_DIR_NAME = "readable"
RUN_ID_ATTR = "harness.run_id"

# Attribute cap for one LLM message/tool payload.  The SDK default (40 KiB) can
# cut a long reasoning message; 200 KiB keeps complete traces for training.
_MAX_ATTRIBUTE_VALUE_LENGTH = 200_000


def _safe_stem(value: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value or "unknown")).strip("._-")
    return stem or "unknown"


def _unix_nano(span: Any, key: str) -> int | None:
    try:
        return int(span.get(key))
    except (TypeError, ValueError, AttributeError):
        return None


def _iso_time(value: int | None) -> str | None:
    if value is None:
        return None
    return (
        datetime.fromtimestamp(value / 1_000_000_000, tz=timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _duration_ms(start: int | None, end: int | None) -> float | None:
    if start is None or end is None or end < start:
        return None
    return round((end - start) / 1_000_000, 3)


def _message_text(message: Any) -> str:
    """Return the text of a flattened or structured message."""
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, str) and content:
        return content
    parts = message.get("parts") or []
    if not isinstance(parts, list):
        return ""
    texts = [
        str(part.get("content"))
        for part in parts
        if isinstance(part, dict)
        and part.get("type") in {"text", "reasoning"}
        and part.get("content")
    ]
    return "\n".join(texts)


def _tool_calls(message: Any) -> list[dict[str, Any]]:
    if not isinstance(message, dict):
        return []
    calls: list[dict[str, Any]] = []
    for call in message.get("tool_calls") or []:
        if not isinstance(call, dict):
            continue
        function = call.get("function") if isinstance(call.get("function"), dict) else {}
        name = call.get("name") or function.get("name") or ""
        arguments = call.get("arguments", function.get("arguments"))
        calls.append({"name": str(name), "arguments": arguments})
    return calls


def _readable_payload(trajectory: Any) -> dict[str, Any]:
    """Project one canonical trajectory into chronological LLM/tool steps.

    This is intentionally a readable view, not a second source of truth: full
    prompt histories and context-event spans stay in the JSONL archive.
    """
    from openjiuwen.agent_evolving.trajectory.spans import (
        iter_spans,
        read_llm_exchange,
        read_tool_call,
        read_usage,
        span_attributes,
        span_sort_key,
    )
    from openjiuwen.agent_evolving.trajectory.team import span_category
    from openjiuwen.extensions.observability import semconv

    steps: list[dict[str, Any]] = []
    task_text: str | None = None
    model: str | None = None
    first_start: int | None = None
    last_end: int | None = None

    for span in sorted(iter_spans(trajectory), key=span_sort_key):
        category = span_category(span)
        if category not in {"llm", "tool"}:
            continue

        start = _unix_nano(span, "startTimeUnixNano")
        end = _unix_nano(span, "endTimeUnixNano")
        if start is not None and (first_start is None or start < first_start):
            first_start = start
        if end is not None and (last_end is None or end > last_end):
            last_end = end

        step: dict[str, Any] = {"kind": category}
        started_at = _iso_time(start)
        if started_at is not None:
            step["started_at"] = started_at
        duration = _duration_ms(start, end)
        if duration is not None:
            step["duration_ms"] = duration

        if category == "llm":
            attributes = span_attributes(span)
            prompts, completions = read_llm_exchange(span)
            if task_text is None:
                task_text = next(
                    (
                        _message_text(message)
                        for message in prompts
                        if isinstance(message, dict)
                        and message.get("role") == "user"
                        and _message_text(message)
                    ),
                    None,
                )
            if model is None and attributes.get(semconv.GEN_AI_REQUEST_MODEL):
                model = str(attributes[semconv.GEN_AI_REQUEST_MODEL])

            reasoning = "\n\n".join(
                text
                for message in completions
                if isinstance(message, dict)
                and (text := _message_text(
                    {"content": message.get("reasoning_content")}
                ))
            )
            if reasoning:
                step["reasoning"] = reasoning

            content = "\n\n".join(
                text
                for message in completions
                if isinstance(message, dict) and (text := _message_text(message))
            )
            if content:
                step["content"] = content

            calls = [
                call
                for message in completions
                for call in _tool_calls(message)
            ]
            if calls:
                step["tool_calls"] = calls

            usage = read_usage(span)
            if usage:
                step["usage"] = usage
        else:
            call = read_tool_call(span)
            step["tool"] = call.get("name", "")
            if "input" in call:
                step["arguments"] = call["input"]
            if "output" in call:
                step["result"] = call["output"]
            if call.get("error"):
                step["error"] = call["error"]

        steps.append(step)

    payload: dict[str, Any] = {
        "task_id": trajectory.session_id,
        "trajectory_id": trajectory.trajectory_id,
    }
    run_id = trajectory.resource_attributes.get(RUN_ID_ATTR)
    if run_id:
        payload["run_id"] = str(run_id)
    if model is not None:
        payload["model"] = model
    started_at = _iso_time(first_start)
    if started_at is not None:
        payload["started_at"] = started_at
    duration = _duration_ms(first_start, last_end)
    if duration is not None:
        payload["duration_ms"] = duration
    if task_text:
        payload["task"] = task_text
    payload["steps"] = steps
    return payload


def _yaml_dump(payload: dict[str, Any], stream: Any) -> None:
    """Write YAML with literal blocks for multi-line reasoning and tool text."""
    import yaml

    class ReadableDumper(yaml.SafeDumper):
        pass

    def represent_str(dumper: Any, data: str) -> Any:
        style = "|" if "\n" in data else None
        return dumper.represent_scalar(
            "tag:yaml.org,2002:str", data, style=style
        )

    ReadableDumper.add_representer(str, represent_str)
    yaml.dump(
        payload,
        stream,
        Dumper=ReadableDumper,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=100,
    )


class ReadableTrajectoryStore:
    """Write the canonical JSONL archive plus one readable YAML view."""

    def __init__(self, base_dir: Path, run_id: str | None = None) -> None:
        from openjiuwen.agent_evolving.trajectory.store import (
            FileTrajectoryStore,
        )

        self._archive = FileTrajectoryStore(base_dir)
        self._base_dir = Path(base_dir)
        self._run_id = run_id

    def _yaml_path(self, trajectory: Any, version: str | None) -> Path:
        session = _safe_stem(trajectory.session_id or "unknown")
        trajectory_id = _safe_stem(trajectory.trajectory_id)
        suffix = f".{_safe_stem(version)}" if version else ""
        return (
            self._base_dir
            / READABLE_DIR_NAME
            / f"{session}__{trajectory_id}{suffix}.yaml"
        )

    def save(self, trajectory: Any, version: str | None = None) -> None:
        if self._run_id:
            trajectory = trajectory.with_resource_attributes(
                {RUN_ID_ATTR: self._run_id}
            )
        self._archive.save(trajectory, version)
        try:
            payload = _readable_payload(trajectory)
            path = self._yaml_path(trajectory, version)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as stream:
                _yaml_dump(payload, stream)
        except Exception:  # noqa: BLE001 - JSONL is already safely written
            log.warning(
                "failed to write readable trajectory YAML; JSONL archive is kept",
                exc_info=True,
            )


class TrajectoryRecorder:
    """Own the openJiuwen observability lifecycle for one harness run."""

    def __init__(self, directory: Path, run_id: str | None = None) -> None:
        self.directory = Path(directory)
        self.run_id = run_id
        self._enabled = False
        self._observability_acquired = False
        self._processor = None
        self._store = None

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def trajectory_file(self) -> Path:
        return self.directory / TRAJECTORY_FILE_NAME

    def start(self) -> None:
        """Enable tracing and prepare the trajectory store.

        Collection is best-effort: a broken observability setup must not stop
        the harness from solving (and reporting) the tasks.
        """
        try:
            self.directory.mkdir(parents=True, exist_ok=True)

            from openjiuwen.extensions.observability.config import (
                ObservabilityConfig,
            )
            from openjiuwen.extensions.observability.demand import (
                get_trajectory_span_processor,
            )
            from openjiuwen.harness.observability.setup import (
                acquire_observability,
            )

            # The provider requires an exporter, but the canonical trajectory
            # is written by TrajectoryRail/ReadableTrajectoryStore below.  Raw
            # OTLP spans would duplicate it, so keep that file sink in /tmp.
            acquire_observability(
                ObservabilityConfig(
                    service_name="openjiuwen-harness",
                    exporter="file",
                    traces_dir=str(
                        Path(tempfile.gettempdir()) / "openjiuwen-harness-otel"
                    ),
                    sample_rate=1.0,
                    attribute_value_max_length=_MAX_ATTRIBUTE_VALUE_LENGTH,
                )
            )
            self._observability_acquired = True
            self._processor = get_trajectory_span_processor()
            self._store = ReadableTrajectoryStore(self.directory, self.run_id)
        except Exception:  # noqa: BLE001 - capture must not break a run
            log.warning(
                "trajectory capture disabled: cannot initialize openJiuwen "
                "observability",
                exc_info=True,
            )
            self._enabled = False
            self._release_observability()
            return

        self._enabled = True
        log.info(
            "saving task trajectories to %s (readable YAML: %s, run_id: %s)",
            self.trajectory_file,
            self.directory / READABLE_DIR_NAME,
            self.run_id or "-",
        )

    def rail(self):
        """Return an openJiuwen rail that saves one trajectory per invoke."""
        if not self._enabled:
            return None
        from openjiuwen.harness.rails.evolution.trajectory_rail import (
            TrajectoryRail,
        )

        return TrajectoryRail(
            trajectory_span_processor=self._processor,
            trajectory_store=self._store,
        )

    @contextmanager
    def task_span(self, task_id: str) -> Iterator[None]:
        """Open the root span that makes LLM/tool spans visible to the rail."""
        if not self._enabled:
            yield
            return

        from openjiuwen.harness.observability.run_span import (
            close_agent_run_span,
            open_agent_run_span,
        )

        handle = open_agent_run_span(session_id=task_id, mode="harness.task")
        try:
            yield
        finally:
            close_agent_run_span(handle, session_id=task_id)

    def close(self) -> None:
        """Flush and release the shared observability provider."""
        self._enabled = False
        self._release_observability()

    def _release_observability(self) -> None:
        if not self._observability_acquired:
            return
        self._observability_acquired = False
        try:
            from openjiuwen.harness.observability.setup import (
                release_observability,
            )

            release_observability()
        except Exception:  # noqa: BLE001 - teardown is best-effort
            log.warning("failed to release trajectory observability", exc_info=True)
        finally:
            self._processor = None
            self._store = None
