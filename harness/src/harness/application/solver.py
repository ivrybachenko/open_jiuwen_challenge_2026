"""Bash-as-action solver.

The model has no tool schema.  Its whole reply is a bash script; the harness
executes it in the task workspace and returns the output.  One task gets one
turn in wave 1 and, if the heuristic says it is promising, one more turn in
wave 2.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from harness.application.config import Settings
from harness.application.features import (
    AnswerInfo,
    AttemptLogger,
    classify_answer,
    estimate_retry_cost,
    extract_features,
    promise_score,
)
from harness.application.llm import (
    MODELS,
    BudgetExceeded,
    TokenLedger,
    token_cost,
)
from harness.application.ojw import configure_logging
from harness.application.overview import OverviewLimits, build_overview
from harness.application.shell import ProcessResult, run_process
from harness.application.tasks import Task

log = logging.getLogger(__name__)

STATE_FILE = "state.json"
STATE_VERSION = 2
MAX_ANSWER_CHARS = 20_000

SYSTEM_PROMPT = """You are a program generator, not an interactive shell.
For each task, reply with exactly one fenced bash block. The block must contain
one complete self-contained bash script that solves the whole task in a single
execution. Do not write any text before or after the block. The harness runs
the contents of that block as:
    cd <current directory> && bash <script>
and sends you the script output in the next message.

The script is executed once. You will not get a chance to run a second command
in the same turn. Never output only `ls`, `cat`, `grep`, `find` or another
single exploratory command: inspect, compute, edit files and submit in the same
script. A script that only inspects files is a wasted turn.

The script itself must write only the final answer to answer.txt in the current
directory: one number or one short string for math, data and search tasks, and
DONE for coding tasks after the tests pass. Printing the answer or showing the
file content is not a submission. Never put reasoning or intermediate results
in answer.txt.

If the task is impossible, write IMPOSSIBLE as the first line of answer.txt
and briefly explain why on the following lines. If the requested value does
not exist or the conditions contradict each other, do not invent an
approximate or fractional answer. Do not ask questions and do not describe
the script.

Before writing answer.txt, check that the values you extracted are non-empty
and plausible. If a lookup returned nothing, fix the parsing instead of
computing with a default or zero.

The task may be impossible or ambiguous. That is a valid outcome; say so in
answer.txt instead of guessing silently."""


@dataclass
class SolveResult:
    answer: str | None = None
    solved: bool = False
    input_tokens: int = 0
    output_tokens: int = 0
    cost: int = 0
    note: str = ""
    answer_kind: str = "none"
    attempts: int = 0
    promise: float = 0.0


@dataclass
class ModelReply:
    model: str = ""
    content: str = ""
    reasoning: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    finish_reason: str = ""
    duration_seconds: float = 0.0
    error: str = ""


@dataclass
class TaskState:
    task_id: str
    task_root: str
    model: str
    wave2_model: str = ""
    overview: str = ""
    messages: list[dict[str, Any]] = field(default_factory=list)
    turns: list[dict[str, Any]] = field(default_factory=list)
    answer: str | None = None
    answer_kind: str = "none"
    wave1_done: bool = False
    wave2_done: bool = False
    impossible_declared: bool = False
    input_tokens: int = 0
    output_tokens: int = 0
    cost: int = 0
    last_error: str = ""
    selected_wave2: bool = False
    promise: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TaskState":
        known = {item.name for item in fields(cls)}
        return cls(**{key: value for key, value in payload.items() if key in known})


class Solver(ABC):
    name = "base"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.ledger = TokenLedger(settings.budget)
        self._budget_exceeded = False

    @property
    def spent(self) -> int:
        return self.ledger.spent

    @property
    def budget_exceeded(self) -> bool:
        return self._budget_exceeded

    @property
    def abort_requested(self) -> bool:
        return False

    async def start(self) -> None:
        """One-time runtime setup (may be a no-op)."""

    async def close(self) -> None:
        """One-time runtime teardown."""

    @abstractmethod
    async def solve(self, task: Task) -> SolveResult:
        """Solve one task. Must not write the solutions file itself."""


class BashAgentSolver(Solver):
    name = "bash"

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)
        self._runner_started = False
        self._model = None
        self._wave2_model = None
        self._model_failures = 0
        self._abort_requested = False
        self._logger = AttemptLogger(settings.trajectories_dir, settings.run_id)

    @property
    def abort_requested(self) -> bool:
        return self._abort_requested

    def restore_budget(self, input_tokens: int, output_tokens: int, spent: int) -> None:
        """Continue a previous process without losing the budget state."""
        self.ledger.input_tokens = max(0, int(input_tokens))
        self.ledger.output_tokens = max(0, int(output_tokens))
        self.ledger.spent = max(0, int(spent))

    async def start(self) -> None:
        configure_logging()
        if not self.settings.llm_base_url or not self.settings.llm_api_key:
            raise RuntimeError("LLM_BASE_URL and LLM_API_KEY must be set")
        if self.settings.model not in MODELS:
            raise ValueError(
                f"unsupported model {self.settings.model!r}; allowed: {', '.join(MODELS)}"
            )
        if self.settings.wave2_model and self.settings.wave2_model not in MODELS:
            raise ValueError(
                f"unsupported wave2 model {self.settings.wave2_model!r}; "
                f"allowed: {', '.join(MODELS)}"
            )

        from openjiuwen.core.foundation.llm import init_model
        from openjiuwen.core.runner import Runner

        await Runner.start()
        self._runner_started = True
        self._model = init_model(
            provider="OpenAI",
            model_name=self.settings.model,
            api_key=self.settings.llm_api_key or "",
            api_base=self.settings.llm_base_url or "",
            timeout=self.settings.model_timeout,
            max_retries=1,
            verify_ssl=True,
        )
        if (self.settings.wave2_model
                and self.settings.wave2_model != self.settings.model):
            self._wave2_model = init_model(
                provider="OpenAI",
                model_name=self.settings.wave2_model,
                api_key=self.settings.llm_api_key or "",
                api_base=self.settings.llm_base_url or "",
                timeout=self.settings.model_timeout,
                max_retries=1,
                verify_ssl=True,
            )
        else:
            self._wave2_model = self._model
        self.settings.agent_workspace.mkdir(parents=True, exist_ok=True)

    async def close(self) -> None:
        if not self._runner_started:
            return
        try:
            from openjiuwen.core.runner import Runner

            await Runner.stop()
        except Exception:  # noqa: BLE001 - never mask saved results
            log.exception("failed to stop openJiuwen Runner")
        finally:
            self._runner_started = False

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------
    def _task_agent_dir(self, task: Task) -> Path:
        return self.settings.agent_workspace / _safe_name(task.task_id)

    def _state_path(self, task: Task) -> Path:
        return self._task_agent_dir(task) / STATE_FILE

    def _load_state(self, task: Task) -> TaskState | None:
        if not self.settings.resume:
            return None
        path = self._state_path(task)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if payload.get("version") != STATE_VERSION:
            return None
        raw = payload.get("state")
        if not isinstance(raw, dict):
            return None
        if raw.get("task_root") != str(task.root):
            return None
        if raw.get("model") != self.settings.model:
            return None
        state_wave2 = raw.get("wave2_model") or raw.get("model")
        if state_wave2 != (self.settings.wave2_model or self.settings.model):
            return None
        try:
            state = TaskState.from_dict(raw)
        except (TypeError, ValueError):
            return None
        if not state.messages:
            return None
        return state

    def _save_state(self, state: TaskState, task: Task) -> None:
        path = self._state_path(task)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_name(f".{path.name}.tmp")
            tmp.write_text(
                json.dumps(
                    {"version": STATE_VERSION, "state": state.to_dict()},
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            os.replace(tmp, path)
        except (OSError, TypeError, ValueError):
            log.warning("cannot save state for %s", state.task_id, exc_info=True)

    async def prepare(self, task: Task) -> TaskState:
        state = self._load_state(task)
        agent_dir = self._task_agent_dir(task)
        if state is None:
            shutil.rmtree(agent_dir, ignore_errors=True)
            agent_dir.mkdir(parents=True, exist_ok=True)
            state = TaskState(
                task_id=task.task_id,
                task_root=str(task.root),
                model=self.settings.model,
                wave2_model=(self.settings.wave2_model
                             or self.settings.model),
            )
            self._delete_answers(task)
        else:
            agent_dir.mkdir(parents=True, exist_ok=True)

        if not state.overview:
            state.overview = self._build_overview(task)
        if not state.messages:
            state.messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": state.overview},
            ]
        if state.answer is not None:
            try:
                task.write_answer(state.answer)
            except OSError:
                log.debug("cannot restore answer for %s", task.task_id, exc_info=True)
        self._save_state(state, task)
        return state

    def _build_overview(self, task: Task) -> str:
        limits = OverviewLimits(
            max_tokens=self.settings.overview_max_tokens,
            max_test_output_chars=min(2200, self.settings.script_output_max_chars),
        )
        try:
            return build_overview(task.workspace, task.instruction, limits)
        except Exception as exc:  # noqa: BLE001 - fall back to the essentials
            log.warning("overview failed for %s: %s", task.task_id, exc, exc_info=True)
            return (
                f"$ pwd\n{task.workspace}\n"
                f"$ cat task.txt\n{task.instruction[:2500]}"
            )

    @staticmethod
    def _delete_answers(task: Task) -> None:
        for path in task.answer_paths:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                log.debug("cannot remove stale %s", path, exc_info=True)

    # ------------------------------------------------------------------
    # Turns
    # ------------------------------------------------------------------
    async def run_turn(
        self,
        task: Task,
        state: TaskState,
        wave: int,
    ) -> dict[str, Any] | None:
        if wave == 1 and state.wave1_done:
            return None
        if wave == 2 and state.wave2_done:
            return None
        if wave == 2:
            self._prepare_wave2(task, state)

        max_tokens = (
            self.settings.wave1_max_tokens
            if wave == 1
            else self.settings.wave2_max_tokens
        )
        turn_index = len(state.turns) + 1
        started_at = datetime.now(timezone.utc).isoformat()
        started = time.monotonic()

        model_name = (self.settings.wave2_model or self.settings.model
                      if wave == 2 else self.settings.model)
        model = self._wave2_model if wave == 2 else self._model
        reply = await self._call_model(
            state.messages, max_tokens=max_tokens, model=model
        )
        raw_content = reply.content
        script = extract_script(raw_content)

        script_path = self._task_agent_dir(task) / f"turn_{turn_index:02d}.sh"
        write_error = ""
        try:
            script_path.write_text(script, encoding="utf-8")
        except OSError as exc:
            write_error = f"{type(exc).__name__}: {exc}"
            log.warning("cannot write script for %s", task.task_id, exc_info=True)

        if write_error:
            execution = ProcessResult(
                command=[],
                exit_code=None,
                output="",
                error=write_error,
                script_path=str(script_path),
            )
        else:
            execution = self._run_script(task, script_path, turn_index)

        answer_info = self._read_answer(task)
        if answer_info.kind == "impossible":
            state.impossible_declared = True
        if answer_info.text is not None:
            state.answer = answer_info.text
            state.answer_kind = answer_info.kind
        if wave == 2 and answer_info.text is None and state.answer is not None:
            # The retry did not improve on the previous answer; restore it.
            try:
                task.write_answer(state.answer)
            except OSError:
                log.debug("cannot restore answer for %s", task.task_id, exc_info=True)

        features = extract_features(
            task_type=task.task_type,
            reward=task.reward,
            wave=wave,
            turn=turn_index,
            reasoning=reply.reasoning,
            model_duration_seconds=reply.duration_seconds,
            input_tokens=reply.input_tokens,
            output_tokens=reply.output_tokens,
            reasoning_tokens=reply.reasoning_tokens,
            finish_reason=reply.finish_reason,
            max_tokens=max_tokens,
            script=script,
            exit_code=execution.exit_code,
            script_duration_seconds=execution.duration_seconds,
            script_timed_out=execution.timed_out,
            script_error=execution.error,
            output_chars=len(execution.output),
            answer=answer_info,
            tests_in_overview="$ tests" in state.overview,
            output_lines=(execution.output.count("\n")
                          + (1 if execution.output else 0)),
            overview_chars=len(state.overview),
            overview_lines=(state.overview.count("\n")
                            + (1 if state.overview else 0)),
        )

        state.input_tokens += reply.input_tokens
        state.output_tokens += reply.output_tokens
        state.cost += token_cost(reply.input_tokens, reply.output_tokens)
        try:
            self.ledger.charge(reply.input_tokens, reply.output_tokens)
        except BudgetExceeded:
            self._budget_exceeded = True
            log.warning("token budget exceeded after %s", task.task_id)

        if reply.error:
            state.last_error = reply.error
        else:
            state.last_error = ""

        if raw_content or reply.error:
            state.messages.append(
                {
                    "role": "assistant",
                    "content": raw_content if raw_content else "",
                }
            )
        state.messages.append(
            {
                "role": "user",
                "content": execution_message(script_path.name, execution),
            }
        )

        if wave == 1:
            state.wave1_done = True
        else:
            state.wave2_done = True

        turn = {
            "model": model_name,
            "wave": wave,
            "turn": turn_index,
            "started_at": started_at,
            "duration_seconds": round(time.monotonic() - started, 3),
            "model_duration_seconds": reply.duration_seconds,
            "reasoning": reply.reasoning,
            "content": raw_content,
            "script": script,
            "script_path": str(script_path),
            "output": execution.output,
            "exit_code": execution.exit_code,
            "timed_out": execution.timed_out,
            "script_error": execution.error,
            "answer": answer_info.text,
            "answer_kind": answer_info.kind,
            "input_tokens": reply.input_tokens,
            "output_tokens": reply.output_tokens,
            "reasoning_tokens": reply.reasoning_tokens,
            "finish_reason": reply.finish_reason,
            "model_error": reply.error,
            "features": features,
        }
        state.turns.append(turn)
        self._save_state(state, task)
        self._log_turn(task, state, turn)
        return turn

    def record_failure(
        self,
        task: Task,
        state: TaskState,
        wave: int,
        error: str,
    ) -> None:
        """Mark a turn as done after an unexpected harness-side exception."""
        state.last_error = error[:500]
        state.turns.append(
            {
                "model": (self.settings.wave2_model or self.settings.model
                          if wave == 2 else self.settings.model),
                "wave": wave,
                "turn": len(state.turns) + 1,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": 0.0,
                "model_duration_seconds": 0.0,
                "reasoning": "",
                "content": "",
                "script": "",
                "script_path": "",
                "output": "",
                "exit_code": None,
                "timed_out": False,
                "script_error": error[:500],
                "answer": None,
                "answer_kind": "none",
                "input_tokens": 0,
                "output_tokens": 0,
                "reasoning_tokens": 0,
                "finish_reason": "",
                "model_error": error[:500],
                "features": {
                    "answer_kind": "none",
                    "script_error": error[:500],
                    "input_tokens": 0,
                    "output_tokens": 0,
                },
            }
        )
        if wave == 1:
            state.wave1_done = True
        else:
            state.wave2_done = True
        self._save_state(state, task)

    def _prepare_wave2(self, task: Task, state: TaskState) -> None:
        if state.wave2_done:
            return
        state.selected_wave2 = True
        self._delete_answers(task)
        warning = self._wave2_warning(state)
        state.messages.append({"role": "user", "content": warning})
        self._save_state(state, task)

    @staticmethod
    def _wave2_warning(state: TaskState) -> str:
        lines = ["The previous attempt did not produce a usable final answer."]
        last = state.turns[-1] if state.turns else {}
        features = last.get("features") or {}
        if last.get("model_error"):
            lines.append("The previous model call failed before producing a script.")
        if state.answer_kind == "impossible":
            lines.append(
                "Your previous answer declared this task IMPOSSIBLE. Re-check that "
                "conclusion; if a reasonable approach exists, try it. If it is "
                "still impossible, write IMPOSSIBLE again."
            )
        elif features.get("script_mentions_impossible") or features.get(
            "reasoning_keyword_impossible"
        ):
            lines.append(
                "Your previous reply suggested that the task might be impossible. "
                "Either solve it or write IMPOSSIBLE to answer.txt."
            )
        if features.get("hit_token_limit"):
            lines.append("The previous reply was cut off before it was complete.")
        if last.get("script_timed_out"):
            lines.append("The previous script timed out.")
        elif last.get("script_error"):
            lines.append("The previous script could not be started.")
        elif last.get("exit_code") not in (0, None):
            lines.append(
                f"The previous script exited with code {last.get('exit_code')}."
            )
        if not last.get("answer"):
            lines.append(
                "The previous script did not create a non-empty answer.txt."
            )
        lines.append(
            "Continue from the current workspace state. Reply with one bash "
            "script and nothing else."
        )
        return "\n".join(lines)

    def _run_script(
        self,
        task: Task,
        script_path: Path,
        turn_index: int,
    ) -> ProcessResult:
        """Run the script from the task workspace.

        A copy lives in the workspace so ``dirname "$0"`` points at the task
        files, not at ``/tmp/agent-workspaces``.  The copy is hidden and
        removed afterwards; the archive copy stays in the agent directory.
        """
        bash = shutil.which("bash") or "/bin/sh"
        workspace_script = task.workspace / f".harness_step_{turn_index:02d}.sh"
        run_path = script_path
        try:
            workspace_script.write_text(script_path.read_text(encoding="utf-8"), encoding="utf-8")
            run_path = workspace_script
        except OSError:
            log.debug("cannot place script in workspace for %s", task.task_id, exc_info=True)
        try:
            return run_process(
                [bash, str(run_path)],
                cwd=task.workspace,
                timeout=self.settings.turn_timeout,
                max_output_chars=self.settings.script_output_max_chars,
            )
        except Exception as exc:  # noqa: BLE001 - an execution bug is not fatal
            log.warning("script execution failed for %s", task.task_id, exc_info=True)
            return ProcessResult(
                command=[bash, str(run_path)],
                exit_code=None,
                output="",
                error=f"{type(exc).__name__}: {exc}",
                script_path=str(run_path),
            )
        finally:
            if run_path != script_path:
                try:
                    run_path.unlink(missing_ok=True)
                except OSError:
                    log.debug("cannot remove workspace script", exc_info=True)

    def _read_answer(self, task: Task) -> AnswerInfo:
        for path in task.answer_paths:
            try:
                with path.open("r", encoding="utf-8", errors="replace") as stream:
                    text = stream.read(MAX_ANSWER_CHARS + 1)
            except OSError:
                continue
            if len(text) > MAX_ANSWER_CHARS:
                text = text[:MAX_ANSWER_CHARS] + "\n...[answer truncated]"
            if text.strip():
                return classify_answer(text)
        return classify_answer(None)

    async def _call_model(
        self,
        messages: list[dict[str, Any]],
        *,
        max_tokens: int,
        model: Any | None = None,
    ) -> ModelReply:
        active = model if model is not None else self._model
        if active is None:
            return ModelReply(error="model is not initialized")
        model_name = (self.settings.wave2_model or self.settings.model
                      if self._wave2_model is active else self.settings.model)
        started = time.monotonic()
        try:
            response = await active.invoke(
                messages,
                max_tokens=max_tokens,
                temperature=0.0,
                timeout=self.settings.model_timeout,
            )
        except Exception as exc:  # noqa: BLE001 - record and continue
            self._model_failures += 1
            if self._model_failures >= 3:
                self._abort_requested = True
            log.warning("model call failed (%d in a row): %s", self._model_failures, exc)
            return ModelReply(
                error=f"{type(exc).__name__}: {exc}",
                duration_seconds=time.monotonic() - started,
            )

        self._model_failures = 0
        content = _message_text(getattr(response, "content", ""))
        reasoning = _message_text(getattr(response, "reasoning_content", ""))
        usage = getattr(response, "usage_metadata", None)
        input_tokens = _usage_int(usage, "input_tokens")
        output_tokens = _usage_int(usage, "output_tokens")
        reasoning_tokens = _usage_int(usage, "reasoning_tokens")
        if input_tokens == 0 and output_tokens == 0:
            input_tokens = max(1, len(json.dumps(messages, ensure_ascii=False)) // 4)
            output_tokens = max(
                1, (len(content) + len(reasoning)) // 4
            )
        return ModelReply(
            model=model_name,
            content=content,
            reasoning=reasoning,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            reasoning_tokens=reasoning_tokens,
            finish_reason=str(getattr(response, "finish_reason", "") or ""),
            duration_seconds=time.monotonic() - started,
        )

    def _log_turn(
        self,
        task: Task,
        state: TaskState,
        turn: dict[str, Any],
    ) -> None:
        self._logger.log(
            {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "task_root": str(task.root),
                "task_path": _task_path(task),
                "model": turn.get("model", self.settings.model),
                "wave": turn.get("wave"),
                "turn": turn.get("turn"),
                "started_at": turn.get("started_at"),
                "duration_seconds": turn.get("duration_seconds"),
                "overview": state.overview,
                "reasoning": turn.get("reasoning", ""),
                "content": turn.get("content", ""),
                "script": turn.get("script", ""),
                "output": turn.get("output", ""),
                "exit_code": turn.get("exit_code"),
                "timed_out": turn.get("timed_out", False),
                "script_error": turn.get("script_error", ""),
                "answer": turn.get("answer"),
                "answer_kind": turn.get("answer_kind"),
                "input_tokens": turn.get("input_tokens", 0),
                "output_tokens": turn.get("output_tokens", 0),
                "reasoning_tokens": turn.get("reasoning_tokens", 0),
                "finish_reason": turn.get("finish_reason", ""),
                "model_error": turn.get("model_error", ""),
                "features": turn.get("features", {}),
                "state_cost": state.cost,
            }
        )

    # ------------------------------------------------------------------
    # Wave selection and result
    # ------------------------------------------------------------------
    def select_wave2(
        self,
        tasks: list[Task],
        states: dict[str, TaskState],
    ) -> list[tuple[Task, TaskState]]:
        candidates: list[tuple[float, Task, TaskState]] = []
        for task in tasks:
            state = states.get(task.task_id)
            if state is None or state.wave2_done:
                continue
            if state.answer_kind in {"done", "value"}:
                continue
            last_features = (state.turns[-1].get("features") if state.turns else {}) or {}
            promise = promise_score(
                reward=task.reward,
                features=last_features,
                spent_cost=state.cost,
                wave2_max_tokens=self.settings.wave2_max_tokens,
            )
            state.promise = round(promise, 8)
            if promise <= 0:
                continue
            remaining = self.ledger.remaining
            if remaining is not None:
                estimated = estimate_retry_cost(
                    state.cost, self.settings.wave2_max_tokens
                )
                if estimated > remaining:
                    continue
            candidates.append((promise, task, state))

        candidates.sort(key=lambda item: (-item[0], -item[1].reward, item[1].task_id))
        if self.settings.wave2_max_tasks > 0:
            candidates = candidates[: self.settings.wave2_max_tasks]
        return [(task, state) for _, task, state in candidates]

    def result_for(self, task: Task, state: TaskState) -> SolveResult:
        usable = state.answer is not None and state.answer_kind in {"done", "value"}
        note_parts = [
            f"answer_kind={state.answer_kind or 'none'}",
            f"attempts={len(state.turns)}",
        ]
        if state.wave2_done:
            note_parts.append("wave2=yes")
        if state.impossible_declared:
            note_parts.append("impossible_declared")
        if state.promise:
            note_parts.append(f"promise={state.promise:.6f}")
        if state.last_error:
            note_parts.append(f"error={state.last_error[:200]}")
        return SolveResult(
            answer=state.answer,
            solved=usable,
            input_tokens=state.input_tokens,
            output_tokens=state.output_tokens,
            cost=state.cost,
            note="; ".join(note_parts),
            answer_kind=state.answer_kind,
            attempts=len(state.turns),
            promise=state.promise,
        )

    async def solve(self, task: Task) -> SolveResult:
        state = await self.prepare(task)
        await self.run_turn(task, state, 1)
        if state.answer_kind not in {"done", "value"}:
            candidates = self.select_wave2([task], {task.task_id: state})
            if candidates:
                await self.run_turn(task, state, 2)
        return self.result_for(task, state)


def _usage_int(usage: Any, name: str) -> int:
    if usage is None:
        return 0
    try:
        return int(getattr(usage, name, 0) or 0)
    except (TypeError, ValueError):
        return 0


def _message_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                if part.get("type") in {"text", "reasoning"}:
                    value = part.get("content")
                    if value:
                        parts.append(str(value))
                elif "content" in part:
                    parts.append(str(part["content"]))
        return "\n".join(parts)
    return str(content)


def extract_script(content: str) -> str:
    """Return the intended bash script.

    The system prompt asks for exactly one fenced bash block.  As a defensive
    fallback, providers sometimes put reasoning into ``content`` together with
    several Markdown blocks: the whole reply is executed as-is only when there
    is no fenced block, otherwise the last block is used.  A single wrapping
    fence is therefore handled automatically.
    """
    text = (content or "").strip()
    if not text:
        return ""
    blocks = re.findall(
        r"```(?:bash|sh|shell|zsh)?[ \t]*\r?\n(.*?)```",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if blocks:
        return blocks[-1].strip()
    lines = text.splitlines()
    if len(lines) >= 2 and lines[0].strip().startswith("```"):
        if lines[-1].strip() == "```":
            text = "\n".join(lines[1:-1]).strip()
    return text


def execution_message(script_name: str, result: ProcessResult) -> str:
    if result.timed_out:
        code = "timeout"
    elif result.exit_code is None:
        code = "unknown"
    else:
        code = result.exit_code
    lines = [f"$ bash {script_name}"]
    if result.output:
        lines.append(result.output.rstrip())
    if result.error:
        lines.append(f"[error: {result.error}]")
    lines.append(f"[exit code {code}]")
    return "\n".join(lines)


def _safe_name(value: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value or "unknown")).strip("._-")
    return stem or "unknown"


def _task_path(task: Task) -> str:
    """Best-effort dataset path such as ``math/solvable/0001``."""
    try:
        parts = task.root.parts
        if "task" in parts:
            index = len(parts) - 1 - parts[::-1].index("task")
            return "/".join(parts[index + 1 :])
    except (ValueError, AttributeError):
        pass
    return task.task_id


def build_solver(settings: Settings) -> Solver:
    return BashAgentSolver(settings)
