"""DeepAgent-based solver.

The openJiuwen SDK is imported lazily: its logger must be reconfigured before
the first SDK import (the container runs with a read-only root filesystem).
"""

from __future__ import annotations

import logging
import shutil
import uuid
from abc import ABC, abstractmethod
from contextlib import nullcontext
from dataclasses import dataclass

from harness.application.config import Settings
from harness.application.llm import MODELS, TokenLedger
from harness.application.ojw import configure_logging
from harness.application.tasks import Task
from harness.application.trajectory import TrajectoryRecorder

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a coding agent solving one benchmark task.

Rules:
- Work only inside the current working directory.
- Use the bash and file tools to inspect files, run code and compute the answer.
- For coding tasks, fix the code and make the tests pass; do not edit tests.
- When the task is complete, call the `write_answer` tool exactly once with the
  final answer. For coding tasks the answer is the word DONE.
- Do not ask questions, do not explain your reasoning, do not create answer.txt
  manually.
"""


@dataclass
class SolveResult:
    answer: str | None = None
    solved: bool = False
    input_tokens: int = 0
    output_tokens: int = 0
    note: str = ""


class Solver(ABC):
    name = "base"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.ledger = TokenLedger(settings.budget)

    @property
    def spent(self) -> int:
        return self.ledger.spent

    async def start(self) -> None:
        """One-time runtime setup (may be a no-op)."""

    async def close(self) -> None:
        """One-time runtime teardown."""

    @abstractmethod
    async def solve(self, task: Task) -> SolveResult:
        """Solve one task. Must not write the solutions file itself."""


def _make_finish_rail():
    """Stop the ReAct loop right after ``write_answer`` to save one LLM call."""
    from openjiuwen.harness.rails.base import DeepAgentRail

    class FinishAfterAnswerRail(DeepAgentRail):
        priority = 10

        def __init__(self) -> None:
            super().__init__()
            self.done = False

        async def after_tool_call(self, ctx) -> None:
            if self.done:
                return
            name = getattr(ctx.inputs, "tool_name", "") or getattr(
                getattr(ctx.inputs, "tool_call", None), "name", ""
            )
            if name != "write_answer":
                return
            self.done = True
            ctx.request_force_finish(
                {"output": "answer submitted", "result_type": "answer"}
            )

    return FinishAfterAnswerRail()


class DeepAgentSolver(Solver):
    name = "deepagent"

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)
        self._runner_started = False
        self._sys_operation = None
        self._trajectory = (
            TrajectoryRecorder(settings.trajectories_dir, settings.run_id)
            if settings.trajectories_dir is not None
            else None
        )

    async def start(self) -> None:
        configure_logging()
        if not self.settings.llm_base_url or not self.settings.llm_api_key:
            raise RuntimeError("LLM_BASE_URL and LLM_API_KEY must be set")
        if self.settings.model not in MODELS:
            raise ValueError(
                f"unsupported model {self.settings.model!r}; allowed: {', '.join(MODELS)}"
            )

        from openjiuwen.core.runner import Runner
        from openjiuwen.core.sys_operation import (
            LocalWorkConfig,
            OperationMode,
            SysOperation,
            SysOperationCard,
        )

        await Runner.start()
        self._runner_started = True
        if self._trajectory is not None:
            self._trajectory.start()
        # One operation for the whole run: cwd/sandbox are per-agent ContextVars,
        # so sharing it avoids creating 100 thread pools and lock managers.
        self._sys_operation = SysOperation(
            SysOperationCard(
                id="harness-sysop",
                mode=OperationMode.LOCAL,
                work_config=LocalWorkConfig(
                    shell_allowlist=None,
                    restrict_to_sandbox=True,
                ),
            )
        )

    async def close(self) -> None:
        try:
            if self._runner_started:
                from openjiuwen.core.runner import Runner

                try:
                    await Runner.stop()
                except Exception:  # noqa: BLE001 - never mask the saved results
                    log.exception("failed to stop openJiuwen Runner")
                finally:
                    self._runner_started = False
        finally:
            if self._trajectory is not None:
                self._trajectory.close()

    def _trajectory_span(self, task_id: str):
        """Root span openJiuwen needs before it emits LLM/tool spans."""
        if self._trajectory is None or not self._trajectory.enabled:
            return nullcontext()
        return self._trajectory.task_span(task_id)

    async def _solve_one(self, task: Task) -> SolveResult:
        from openjiuwen.core.foundation.llm import init_model
        from openjiuwen.core.foundation.tool import tool
        from openjiuwen.core.runner import Runner
        from openjiuwen.core.single_agent.schema.agent_card import AgentCard
        from openjiuwen.harness import create_deep_agent
        from openjiuwen.harness.cli.rails.token_tracker import TokenTrackingRail
        from openjiuwen.harness.rails.sys_operation_rail import SysOperationRail

        captured: list[str] = []

        @tool(
            name="write_answer",
            description=(
                "Submit the final answer for this task. Writes answer.txt in the "
                "working directory. Call it exactly once when the task is done."
            ),
            input_params={
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "Final answer, e.g. 42, a year, or DONE for coding tasks.",
                    }
                },
                "required": ["answer"],
            },
        )
        def write_answer(answer: str) -> str:
            text = str(answer).strip()
            if not text:
                return "error: answer is empty"
            try:
                task.write_answer(text)
            except OSError:
                log.exception("cannot write answer.txt for %s", task.task_id)
                return "error: cannot write answer.txt"
            captured.append(text)
            return "answer recorded"

        model = init_model(
            provider="OpenAI",
            model_name=self.settings.model,
            api_key=self.settings.llm_api_key or "",
            api_base=self.settings.llm_base_url or "",
            timeout=180.0,
            verify_ssl=True,
            max_tokens=8192,
        )

        workspace = self.settings.agent_workspace / task.task_id
        shutil.rmtree(workspace, ignore_errors=True)
        workspace.mkdir(parents=True, exist_ok=True)

        # A stale answer from a previous local run must not be counted.
        for path in task.answer_paths:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                log.debug("cannot remove stale %s", path, exc_info=True)

        tracker = TokenTrackingRail()
        rails = [SysOperationRail(), tracker, _make_finish_rail()]
        if self._trajectory is not None and self._trajectory.enabled:
            trajectory_rail = self._trajectory.rail()
            if trajectory_rail is not None:
                rails.append(trajectory_rail)
        agent = create_deep_agent(
            model=model,
            card=AgentCard(
                id=f"harness-{uuid.uuid4().hex[:8]}",
                name="harness",
                description="Budget-aware coding agent",
            ),
            system_prompt=SYSTEM_PROMPT,
            tools=[write_answer],
            rails=rails,
            workspace=str(workspace),
            cwd=str(task.workspace),
            project_root=str(task.workspace),
            sys_operation=self._sys_operation,
            max_iterations=self.settings.max_iterations,
            enable_task_loop=False,
            enable_task_planning=False,
            enable_read_image_multimodal=False,
            enable_security_rail=False,
            restrict_to_work_dir=True,
            language="en",
        )

        answer: str | None = None
        result_type = "unknown"
        error_note = ""
        try:
            with self._trajectory_span(task.task_id):
                result = await Runner.run_agent(
                    agent,
                    {
                        "query": (
                            f"{task.instruction}\n\n"
                            f"Current working directory: {task.workspace}\n"
                            "Call write_answer with the final answer when done."
                        ),
                        "conversation_id": task.task_id,
                    },
                )
            if isinstance(result, dict):
                result_type = str(result.get("result_type", "unknown"))
        except Exception as exc:  # noqa: BLE001 - record the task, keep going
            log.exception("task %s failed", task.task_id)
            error_note = f"; error={type(exc).__name__}: {exc}"
        finally:
            _cleanup_agent(agent)
            try:
                await Runner.release(task.task_id)
            except Exception:  # noqa: BLE001 - release is best-effort
                log.debug("failed to release session %s", task.task_id, exc_info=True)

        answer = captured[-1] if captured else _read_answer_file(task)

        note = f"result_type={result_type}{error_note}"
        if captured:
            note += "; answer via write_answer"
        elif answer is not None:
            note += "; answer read from answer.txt"
        else:
            note += "; no answer produced"

        return SolveResult(
            answer=answer,
            solved=answer is not None,
            input_tokens=tracker.total_input_tokens,
            output_tokens=tracker.total_output_tokens,
            note=note,
        )

    async def solve(self, task: Task) -> SolveResult:
        return await self._solve_one(task)


def _read_answer_file(task: Task) -> str | None:
    for path in task.answer_paths:
        try:
            text = path.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeDecodeError):
            continue
        if text:
            return text
    return None


def _cleanup_agent(agent) -> None:
    """Drop per-task tools from the global resource manager."""
    try:
        for ability in list(agent.ability_manager.list()):
            try:
                agent.ability_manager.remove_ability(ability.name)
            except Exception:  # noqa: BLE001 - best-effort cleanup
                log.debug("failed to remove ability %s", ability.name, exc_info=True)
    except Exception:  # noqa: BLE001
        log.debug("failed to list abilities", exc_info=True)


def build_solver(settings: Settings) -> Solver:
    return DeepAgentSolver(settings)
