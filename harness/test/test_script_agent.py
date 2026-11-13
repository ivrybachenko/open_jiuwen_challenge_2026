"""Tests for the BaseAgent-based ScriptAgent and its lifecycle rails."""

from __future__ import annotations

import asyncio
import json
import tempfile
import unittest
from pathlib import Path

from harness.solving.agents.rails import (
    AnswerRail,
    BudgetRail,
    FailureRail,
    FeatureRail,
    FollowUpRail,
)
from harness.solving.agents.script_agent import (
    SYSTEM_PROMPT,
    ModelReply,
    ScriptAgent,
)
from harness.tasks import classify_answer
from harness.accounting import TokenLedger
from harness.config import DEFAULT_MODEL, Settings
from harness.tasks import TaskState
from harness.tasks import Task
from harness.solving.workspace import ProcessResult

# Imported after the harness modules: importing them configures the openJiuwen
# logger before the SDK modules are touched, matching the production order.
from openjiuwen.core.single_agent.base import BaseAgent
from openjiuwen.core.single_agent.rail.base import (
    AgentCallbackContext,
    InvokeInputs,
    ModelCallInputs,
)


def make_settings(tmp: Path) -> Settings:
    return Settings(
        tasks_dir=tmp / "tasks",
        out=tmp / "solutions.json",
        llm_base_url="http://example.invalid/v1",
        llm_api_key="test-key",
        model=DEFAULT_MODEL,
        budget=None,
        max_iterations=12,
        agent_workspace=tmp / "agent",
        trajectories_dir=tmp / "traces",
        run_id="run-1",
    )


def make_task(tmp: Path, task_id: str = "math_0000") -> Task:
    root = tmp / "tasks" / task_id
    workspace = root / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "data.txt").write_text("1 2 3\n", encoding="utf-8")
    payload = {
        "task_id": task_id,
        "task_type": "math",
        "instruction": "Add the numbers in data.txt.",
        "reward": 5,
        "check": "exact_int",
    }
    (root / "task.json").write_text(json.dumps(payload), encoding="utf-8")
    return Task(
        task_id=task_id,
        task_type="math",
        instruction=str(payload["instruction"]),
        reward=5,
        expected=None,
        check="exact_int",
        root=root,
    )


def make_state(task: Task, **overrides) -> TaskState:
    state = TaskState(
        task_id=task.task_id,
        task_root=str(task.root),
        model=DEFAULT_MODEL,
        overview="$ cat task.txt\ndo it",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "$ cat task.txt\ndo it"},
        ],
    )
    for key, value in overrides.items():
        setattr(state, key, value)
    return state


def make_ctx(agent: ScriptAgent, **extra) -> AgentCallbackContext:
    ctx = AgentCallbackContext(
        agent=agent,
        inputs=InvokeInputs(query="task", conversation_id="math_0000"),
    )
    ctx.extra.update(extra)
    return ctx


class AgentContractTest(unittest.TestCase):
    def test_script_agent_is_a_tool_free_base_agent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agent = ScriptAgent(make_settings(Path(tmp)))
            self.assertIsInstance(agent, BaseAgent)
            self.assertEqual(agent.name, "script")
            self.assertEqual(agent.ability_manager.list(), [])
            asyncio.run(agent._ensure_rails())
            self.assertEqual(agent.ability_manager.list(), [])
            self.assertEqual(agent.card.name, "script-agent")


class RailTest(unittest.TestCase):
    def test_budget_rail_charges_state_and_ledger_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(Path(tmp))
            state = make_state(task)
            ledger = TokenLedger(limit=1000)
            rail = BudgetRail(ledger)
            ctx = make_ctx(
                ScriptAgent(make_settings(Path(tmp))),
                state=state,
            )
            ctx.inputs = ModelCallInputs(
                response=ModelReply(input_tokens=10, output_tokens=5)
            )
            asyncio.run(rail.after_model_call(ctx))
            self.assertEqual(state.input_tokens, 10)
            self.assertEqual(state.output_tokens, 5)
            self.assertEqual(state.cost, 6)
            self.assertEqual(ledger.spent, 6)
            self.assertFalse(rail.budget_exceeded)

    def test_budget_rail_marks_the_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(Path(tmp))
            state = make_state(task)
            rail = BudgetRail(TokenLedger(limit=1))
            ctx = make_ctx(
                ScriptAgent(make_settings(Path(tmp))),
                state=state,
            )
            ctx.inputs = ModelCallInputs(
                response=ModelReply(input_tokens=10, output_tokens=5)
            )
            asyncio.run(rail.after_model_call(ctx))
            self.assertTrue(rail.budget_exceeded)

    def test_failure_rail_aborts_after_three_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agent = ScriptAgent(make_settings(Path(tmp)))
            agent._model = object()  # simulate a started harness
            rail = FailureRail()
            for _ in range(3):
                ctx = make_ctx(agent)
                ctx.inputs = ModelCallInputs(
                    response=ModelReply(error="RuntimeError: boom")
                )
                asyncio.run(rail.after_model_call(ctx))
            self.assertTrue(rail.abort_requested)

            ctx = make_ctx(agent)
            ctx.inputs = ModelCallInputs(
                response=ModelReply(content="ok", output_tokens=1)
            )
            asyncio.run(rail.after_model_call(ctx))
            # A run-level abort stays latched once requested, as before.
            self.assertTrue(rail.abort_requested)
            self.assertEqual(rail.failures, 0)

    def test_answer_rail_restores_the_previous_answer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(Path(tmp))
            state = make_state(
                task,
                answer="42",
                answer_kind="value",
                wave1_done=True,
            )
            rail = AnswerRail()
            ctx = make_ctx(
                ScriptAgent(make_settings(Path(tmp))),
                task=task,
                state=state,
                wave=2,
                answer_info=classify_answer(None),
            )
            asyncio.run(rail.after_invoke(ctx))
            self.assertEqual(
                task.workspace.joinpath("answer.txt").read_text(
                    encoding="utf-8"
                ).strip(),
                "42",
            )

    def test_followup_rail_adds_the_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(Path(tmp))
            state = make_state(task, wave1_done=True)
            rail = FollowUpRail()
            ctx = make_ctx(
                ScriptAgent(make_settings(Path(tmp))),
                task=task,
                state=state,
                wave=2,
            )
            asyncio.run(rail.before_invoke(ctx))
            self.assertTrue(state.selected_wave2)
            self.assertIn(
                "previous attempt", state.messages[-1]["content"].lower()
            )

    def test_feature_rail_fills_turn_features(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = make_task(Path(tmp))
            state = make_state(task)
            reply = ModelReply(
                content="echo 42",
                input_tokens=10,
                output_tokens=5,
            )
            execution = ProcessResult(
                exit_code=0,
                output="42\n",
                duration_seconds=0.1,
            )
            turn = {"turn": 1}
            rail = FeatureRail()
            ctx = make_ctx(
                ScriptAgent(make_settings(Path(tmp))),
                task=task,
                state=state,
                wave=1,
                reply=reply,
                execution=execution,
                answer_info=classify_answer("42"),
                script="echo 42",
                max_tokens=1000,
                turn=turn,
            )
            asyncio.run(rail.after_invoke(ctx))
            self.assertEqual(turn["features"]["answer_kind"], "value")
            self.assertEqual(turn["features"]["output_chars"], 3)
            self.assertEqual(turn["features"]["wave"], 1)


class RunTurnTest(unittest.TestCase):
    def test_run_turn_uses_the_rails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            agent = ScriptAgent(make_settings(tmp_path))
            task = make_task(tmp_path)
            state = asyncio.run(agent.prepare(task))

            calls: list[dict] = []

            async def fake_call(messages, *, max_tokens, model=None):
                calls.append({"messages": list(messages), "max_tokens": max_tokens})
                return ModelReply(
                    content="```bash\necho 42 > answer.txt\n```",
                    input_tokens=10,
                    output_tokens=5,
                )

            agent._call_model = fake_call  # type: ignore[method-assign]
            turn = asyncio.run(agent.run_turn(task, state, 1))

            self.assertIsNotNone(turn)
            assert turn is not None
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["max_tokens"], 1000)
            self.assertEqual(turn["answer"], "42")
            self.assertEqual(turn["answer_kind"], "value")
            self.assertEqual(turn["features"]["answer_kind"], "value")
            self.assertEqual(state.answer, "42")
            self.assertEqual(state.cost, 6)
            self.assertEqual(agent.spent, 6)
            self.assertEqual(len(state.turns), 1)
            self.assertEqual(
                task.workspace.joinpath("answer.txt").read_text(
                    encoding="utf-8"
                ).strip(),
                "42",
            )

    def test_invoke_accepts_a_task_and_a_wave(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            agent = ScriptAgent(make_settings(tmp_path))
            task = make_task(tmp_path)

            async def fake_call(messages, *, max_tokens, model=None):
                return ModelReply(
                    content="```bash\necho 42 > answer.txt\n```",
                    input_tokens=1,
                    output_tokens=1,
                )

            agent._call_model = fake_call  # type: ignore[method-assign]
            turn = asyncio.run(agent.invoke(task))
            self.assertIsNotNone(turn)
            self.assertEqual(turn["wave"], 1)


if __name__ == "__main__":
    unittest.main()
