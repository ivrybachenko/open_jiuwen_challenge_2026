"""Bash-as-action agent.

The model has no tool schema.  Its whole reply is a bash script; the harness
executes it in the task workspace and returns the output.  ``ScriptAgent`` is
an openJiuwen ``BaseAgent`` and ``invoke`` is exactly one turn; the run
orchestrator keeps the cross-task wave selection outside the agent.
"""

from __future__ import annotations

import json
import logging
import re
import shutil
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from harness.config import MODELS, Settings
from harness.domain.attempts import AnswerInfo, classify_answer
from harness.domain.budget import TokenLedger
from harness.domain.state import TaskState
from harness.domain.tasks import Task
from harness.infrastructure.attempt_log import AttemptLogger
from harness.infrastructure.logging_setup import configure_logging
from harness.infrastructure.overview import OverviewLimits, build_overview
from harness.infrastructure.shell import ProcessResult, run_process
from harness.infrastructure.state_store import StateStore

# openJiuwen installs its logger on the first import.  Configure it before the
# agent/rail imports so the read-only container root is never used for logs.
configure_logging()

from openjiuwen.core.single_agent.base import BaseAgent  # noqa: E402
from openjiuwen.core.single_agent.rail.base import (  # noqa: E402
    AgentCallbackContext,
    AgentCallbackEvent,
    AgentRail,
    InvokeInputs,
    ModelCallInputs,
)
from openjiuwen.core.single_agent.schema.agent_card import AgentCard  # noqa: E402

from harness.agents.rails import (  # noqa: E402
    AnswerRail,
    BudgetRail,
    FailureRail,
    FeatureRail,
    FollowUpRail,
)

log = logging.getLogger(__name__)

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
file content is not a submission. Writing answer.txt is the only way to submit:
even if the tests already pass when the turn starts, the script must still
write answer.txt, and it must do so after the work and verification, as the
last step. Never put reasoning or intermediate results in answer.txt.

If the reply contains more than one fenced bash block, the blocks are joined in
order and executed as one script, so the block that writes answer.txt must come
last.

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


def execution_message(script_name: str, result: ProcessResult) -> str:
    """Render one script observation for the next model turn."""
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


class ScriptAgent(BaseAgent):
    """Bash-as-action agent built on the openJiuwen ``BaseAgent`` contract.

    The agent has no tool schemas.  Each ``invoke`` is one model turn: the reply
    is parsed as a bash script, executed in the task workspace, and the
    observation is appended to the conversation.  Waves stay outside the agent
    because they are selected across all tasks.
    """

    name = "script"

    def __init__(self, settings: Settings) -> None:
        super().__init__(
            AgentCard(
                id="openjiuwen-harness-script-agent",
                name="script-agent",
                description=(
                    "Budget-aware bash-script agent for the "
                    "OpenJiuwen challenge"
                ),
            )
        )
        self.settings = settings
        self.ledger = TokenLedger(settings.budget)
        self._state = StateStore(settings)
        self._budget_rail = BudgetRail(self.ledger)
        self._failure_rail = FailureRail()
        self._rails: list[AgentRail] = [
            self._failure_rail,
            self._budget_rail,
            FollowUpRail(),
            AnswerRail(),
            FeatureRail(),
        ]
        self._rails_registered = False
        self._runner_started = False
        self._model = None
        self._wave2_model = None
        self._logger = AttemptLogger(settings.trajectories_dir, settings.run_id)

    def configure(self, config: Any) -> "ScriptAgent":
        """Accept an optional openJiuwen config for the BaseAgent contract.

        The harness config lives in :class:`Settings`; this method exists so
        the class is a concrete ``BaseAgent`` and can be passed to SDK helpers.
        """
        self._config = config
        return self

    @property
    def spent(self) -> int:
        return self.ledger.spent

    @property
    def budget_exceeded(self) -> bool:
        return self._budget_rail.budget_exceeded

    @property
    def abort_requested(self) -> bool:
        return self._failure_rail.abort_requested

    @property
    def state_store(self) -> StateStore:
        """Expose persistence so a rail can own its state transition."""
        return self._state

    def restore_budget(self, input_tokens: int, output_tokens: int, spent: int) -> None:
        """Continue a previous process without losing the budget state."""
        self.ledger.input_tokens = max(0, int(input_tokens))
        self.ledger.output_tokens = max(0, int(output_tokens))
        self.ledger.spent = max(0, int(spent))

    async def _ensure_rails(self) -> None:
        """Register the lifecycle rails once, before the first turn."""
        if self._rails_registered:
            return
        for rail in self._rails:
            await self.register_rail(rail)
        self._rails_registered = True

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
        await self._ensure_rails()

    async def close(self) -> None:
        if self._rails_registered:
            for rail in self._rails:
                try:
                    await self.unregister_rail(rail)
                except Exception:  # noqa: BLE001 - teardown is best-effort
                    log.debug("failed to unregister rail", exc_info=True)
            self._rails_registered = False
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
    async def prepare(self, task: Task) -> TaskState:
        state = self._state.load(task)
        if state is None:
            self._state.reset(task)
            state = TaskState(
                task_id=task.task_id,
                task_root=str(task.root),
                model=self.settings.model,
                wave2_model=(self.settings.wave2_model
                             or self.settings.model),
            )
            self._state.clear_answers(task)
        else:
            self._state.ensure_dir(task)

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
        self._state.save(task, state)
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

    # ------------------------------------------------------------------
    # Turns
    # ------------------------------------------------------------------
    async def invoke(self, inputs: Any, session: Any = None) -> Any:
        """Run one turn through the openJiuwen ``BaseAgent`` entry point.

        ``inputs`` is either a :class:`Task` (wave 1) or a dict with ``task``,
        optional ``state`` and ``wave``.  The per-task state still lives in
        ``state.json``; the session argument is accepted for contract
        compatibility and is not used for persistence.
        """
        del session
        if isinstance(inputs, Task):
            task = inputs
            state = await self.prepare(task)
            wave = 1
        elif isinstance(inputs, dict):
            task = inputs.get("task")
            if not isinstance(task, Task):
                raise TypeError(
                    "ScriptAgent.invoke expects a Task or a dict with 'task'"
                )
            state = inputs.get("state")
            if state is None:
                state = await self.prepare(task)
            if not isinstance(state, TaskState):
                raise TypeError("ScriptAgent.invoke expects a TaskState")
            wave = int(inputs.get("wave", 1) or 1)
        else:
            raise TypeError("ScriptAgent.invoke expects a Task or a dict")
        return await self.run_turn(task, state, wave)

    async def stream(
        self,
        inputs: Any,
        session: Any = None,
        stream_modes: Any = None,
    ) -> Any:
        """Yield the single turn result; the evaluator uses ``invoke``."""
        del stream_modes
        yield await self.invoke(inputs, session=session)

    async def run_turn(
        self,
        task: Task,
        state: TaskState,
        wave: int,
    ) -> dict[str, Any] | None:
        if state.wave_done(wave):
            return None
        await self._ensure_rails()

        max_tokens = (
            self.settings.wave1_max_tokens
            if wave == 1
            else self.settings.wave2_max_tokens
        )
        model_name = (self.settings.wave2_model or self.settings.model
                      if wave > 1 else self.settings.model)
        model = self._wave2_model if wave > 1 else self._model

        invoke_inputs = InvokeInputs(
            query=task.instruction,
            conversation_id=task.task_id,
        )
        ctx = AgentCallbackContext(agent=self, inputs=invoke_inputs)
        ctx.extra.update(
            task=task,
            state=state,
            wave=wave,
            max_tokens=max_tokens,
        )

        async with ctx.lifecycle(
            AgentCallbackEvent.BEFORE_INVOKE,
            AgentCallbackEvent.AFTER_INVOKE,
        ):
            turn_index = len(state.turns) + 1
            started_at = datetime.now(timezone.utc).isoformat()
            started = time.monotonic()

            reply = await self._call_model(
                state.messages, max_tokens=max_tokens, model=model
            )
            ctx.extra["reply"] = reply
            ctx.inputs = ModelCallInputs(
                messages=state.messages,
                response=reply,
            )
            await ctx.fire(AgentCallbackEvent.AFTER_MODEL_CALL)

            raw_content = reply.content
            script = extract_script(raw_content)

            script_path = self._state.agent_dir(task) / f"turn_{turn_index:02d}.sh"
            write_error = ""
            try:
                script_path.write_text(script, encoding="utf-8")
            except OSError as exc:
                write_error = f"{type(exc).__name__}: {exc}"
                log.warning(
                    "cannot write script for %s", task.task_id, exc_info=True
                )

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

            state.last_error = reply.error if reply.error else ""

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
            elif wave == 2:
                state.wave2_done = True

            turn = {
                "model": model_name,
                "wave": wave,
                "turn": turn_index,
                "started_at": started_at,
                "duration_seconds": 0.0,
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
                "features": {},
            }
            ctx.extra.update(
                script=script,
                execution=execution,
                answer_info=answer_info,
                turn=turn,
            )
            invoke_inputs.result = {
                "turn": turn,
                "answer": answer_info.text,
            }

        # AFTER_INVOKE rails have now recorded the answer and features.
        turn["duration_seconds"] = round(time.monotonic() - started, 3)
        state.turns.append(turn)
        self._state.save(task, state)
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
        elif wave == 2:
            state.wave2_done = True
        self._state.save(task, state)

    # ------------------------------------------------------------------
    # Script execution
    # ------------------------------------------------------------------
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
        workspace = task.workspace.resolve()
        # ``script_path`` may be relative (relative --tasks-dir or
        # --agent-workspace) while ``cwd`` is the task workspace, so bash would
        # look for it in the wrong directory.  Always execute an absolute path.
        run_path = script_path.resolve()
        workspace_script = workspace / f".harness_step_{turn_index:02d}.sh"
        placed = False
        try:
            workspace_script.write_text(
                run_path.read_text(encoding="utf-8"), encoding="utf-8"
            )
            placed = True
        except OSError:
            log.debug("cannot place script in workspace for %s", task.task_id, exc_info=True)
        try:
            return run_process(
                [bash, str(workspace_script if placed else run_path)],
                cwd=workspace,
                timeout=self.settings.turn_timeout,
                max_output_chars=self.settings.script_output_max_chars,
            )
        except Exception as exc:  # noqa: BLE001 - an execution bug is not fatal
            log.warning("script execution failed for %s", task.task_id, exc_info=True)
            return ProcessResult(
                command=[bash, str(workspace_script if placed else run_path)],
                exit_code=None,
                output="",
                error=f"{type(exc).__name__}: {exc}",
                script_path=str(workspace_script if placed else run_path),
            )
        finally:
            if placed:
                try:
                    workspace_script.unlink(missing_ok=True)
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
            # FailureRail counts consecutive errors and requests the abort.
            return ModelReply(
                error=f"{type(exc).__name__}: {exc}",
                duration_seconds=time.monotonic() - started,
            )

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

    def result_for(self, task: Task, state: TaskState) -> SolveResult:
        usable = state.answer is not None and state.answer_kind in {"done", "value"}
        note_parts = [
            f"answer_kind={state.answer_kind or 'none'}",
            f"attempts={len(state.turns)}",
        ]
        if state.wave2_done:
            waves = max(
                (int(turn.get("wave", 0) or 0) for turn in state.turns),
                default=2,
            )
            note_parts.append(f"waves={max(2, waves)}")
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

    The system prompt asks for exactly one fenced bash block.  Providers and
    models still sometimes return several blocks (``cat``, then an edit, then
    the tests, then the submission).  Running only the last block loses the
    work, so every bash block is joined in order into one script; the fallback
    is the whole reply when there is no fenced block at all.
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
        return "\n".join(block.strip() for block in blocks if block.strip())
    lines = text.splitlines()
    if len(lines) >= 2 and lines[0].strip().startswith("```"):
        if lines[-1].strip() == "```":
            text = "\n".join(lines[1:-1]).strip()
    return text


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
