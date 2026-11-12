"""Unit tests for the bash solver prompt, state and wave selection."""

from __future__ import annotations

import asyncio
import json
import tempfile
import unittest
from pathlib import Path

from harness.application.config import Settings
from harness.application.llm import DEFAULT_MODEL
from harness.application.solver import (
    SYSTEM_PROMPT,
    BashAgentSolver,
    TaskState,
    execution_message,
    extract_script,
)
from harness.application.shell import ProcessResult
from harness.application.tasks import Task


def make_settings(tmp: Path, *, resume: bool = True) -> Settings:
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
        resume=resume,
    )


def make_task(
    tmp: Path,
    task_id: str = "math_0000",
    reward: float = 5,
) -> Task:
    root = tmp / "tasks" / task_id
    workspace = root / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "data.txt").write_text("1 2 3\n", encoding="utf-8")
    payload = {
        "task_id": task_id,
        "task_type": "math",
        "instruction": "Add the numbers in data.txt.",
        "reward": reward,
        "check": "exact_int",
    }
    (root / "task.json").write_text(json.dumps(payload), encoding="utf-8")
    return Task(
        task_id=task_id,
        task_type="math",
        instruction=str(payload["instruction"]),
        reward=reward,
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


class PromptTest(unittest.TestCase):
    def test_prompt_has_no_tool_list_or_budget(self) -> None:
        lowered = SYSTEM_PROMPT.lower()
        self.assertNotIn("budget", lowered)
        self.assertNotIn("tokens left", lowered)
        self.assertIn("bash script", lowered)
        self.assertIn("answer.txt", lowered)
        self.assertIn("impossible", lowered)

    def test_prompt_requires_one_fenced_block_without_prose(self) -> None:
        lowered = SYSTEM_PROMPT.lower()
        self.assertIn("exactly one fenced", lowered)
        self.assertIn("do not write any text before or after", lowered)
        self.assertNotIn("without markdown fences", lowered)

    def test_extract_script_takes_the_last_fenced_block(self) -> None:
        self.assertEqual(
            extract_script("```bash\necho 42\n```"),
            "echo 42",
        )
        self.assertEqual(extract_script("echo 42"), "echo 42")
        content = (
            "I will inspect first.\n"
            "```bash\ncat data.txt\n```\n"
            "Then I will submit.\n"
            "```bash\necho 42 > answer.txt\n```\n"
        )
        self.assertEqual(extract_script(content), "echo 42 > answer.txt")

    def test_execution_message_has_exit_code(self) -> None:
        message = execution_message(
            "turn_01.sh",
            ProcessResult(exit_code=1, output="boom"),
        )
        self.assertIn("$ bash turn_01.sh", message)
        self.assertIn("boom", message)
        self.assertIn("[exit code 1]", message)


class StateTest(unittest.TestCase):
    def test_prepare_builds_overview_and_restores_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            settings = make_settings(tmp_path)
            task = make_task(tmp_path)
            solver = BashAgentSolver(settings)
            state = asyncio.run(solver.prepare(task))
            self.assertIn("$ cat task.txt", state.overview)
            self.assertEqual(state.messages[0]["content"], SYSTEM_PROMPT)
            self.assertTrue((tmp_path / "agent" / task.task_id / "state.json").is_file())

            state.wave1_done = True
            solver._save_state(state, task)

            restored = asyncio.run(BashAgentSolver(settings).prepare(task))
            self.assertTrue(restored.wave1_done)

    def test_no_resume_starts_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            task = make_task(tmp_path)
            settings = make_settings(tmp_path)
            solver = BashAgentSolver(settings)
            state = asyncio.run(solver.prepare(task))
            state.wave1_done = True
            solver._save_state(state, task)

            fresh = asyncio.run(
                BashAgentSolver(make_settings(tmp_path, resume=False)).prepare(task)
            )
            self.assertFalse(fresh.wave1_done)

    def test_record_failure_marks_wave_done(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            task = make_task(tmp_path)
            solver = BashAgentSolver(make_settings(tmp_path))
            state = asyncio.run(solver.prepare(task))
            solver.record_failure(task, state, 1, "RuntimeError: boom")
            self.assertTrue(state.wave1_done)
            self.assertIn("boom", state.last_error)
            self.assertEqual(state.turns[-1]["model_error"], "RuntimeError: boom")


class WaveSelectionTest(unittest.TestCase):
    def test_final_answers_are_not_selected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            settings = make_settings(tmp_path)
            solver = BashAgentSolver(settings)
            task = make_task(tmp_path)
            done = make_state(task, answer="42", answer_kind="value", wave1_done=True)
            self.assertEqual(solver.select_wave2([task], {task.task_id: done}), [])

    def test_impossible_can_be_selected_and_warned(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            solver = BashAgentSolver(make_settings(tmp_path))
            task = make_task(tmp_path, reward=10)
            state = make_state(
                task,
                answer="IMPOSSIBLE",
                answer_kind="impossible",
                wave1_done=True,
                turns=[
                    {
                        "wave": 1,
                        "answer": "IMPOSSIBLE",
                        "answer_kind": "impossible",
                        "features": {
                            "answer_kind": "impossible",
                            "hit_token_limit": True,
                            "script_error": "",
                            "script_timed_out": False,
                            "exit_code": 0,
                            "reasoning_keyword_impossible": 1,
                            "reasoning_keyword_give_up": 0,
                            "reasoning_words": 100,
                            "script_has_write_answer": True,
                            "script_has_python": True,
                            "output_chars": 0,
                            "tests_in_overview": False,
                        },
                    }
                ],
            )
            selected = solver.select_wave2([task], {task.task_id: state})
            self.assertEqual(len(selected), 1)
            warning = solver._wave2_warning(state).lower()
            self.assertIn("impossible", warning)
            self.assertIn("cut off", warning)
            self.assertNotIn("budget", warning)

    def test_budget_filters_expensive_retries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            settings = make_settings(tmp_path)
            solver = BashAgentSolver(settings)
            solver.ledger.limit = 100
            task = make_task(tmp_path, reward=10)
            state = make_state(
                task,
                wave1_done=True,
                cost=900,
                turns=[
                    {
                        "features": {
                            "answer_kind": "none",
                            "hit_token_limit": False,
                            "script_error": "",
                            "script_timed_out": False,
                            "exit_code": 0,
                            "reasoning_keyword_impossible": 0,
                            "reasoning_keyword_give_up": 0,
                            "reasoning_words": 100,
                            "script_has_write_answer": True,
                            "script_has_python": True,
                            "output_chars": 10,
                            "tests_in_overview": False,
                        }
                    }
                ],
            )
            self.assertEqual(solver.select_wave2([task], {task.task_id: state}), [])

    def test_higher_reward_wins_when_probability_is_equal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            solver = BashAgentSolver(make_settings(tmp_path))
            task_a = make_task(tmp_path, task_id="a", reward=1)
            task_b = make_task(tmp_path, task_id="b", reward=10)
            features = {
                "answer_kind": "none",
                "hit_token_limit": False,
                "script_error": "",
                "script_timed_out": False,
                "exit_code": 0,
                "reasoning_keyword_impossible": 0,
                "reasoning_keyword_give_up": 0,
                "reasoning_words": 100,
                "script_has_write_answer": True,
                "script_has_python": True,
                "output_chars": 10,
                "tests_in_overview": False,
            }
            state_a = make_state(
                task_a, wave1_done=True, cost=100, turns=[{"features": features}]
            )
            state_b = make_state(
                task_b, wave1_done=True, cost=100, turns=[{"features": features}]
            )
            selected = solver.select_wave2(
                [task_a, task_b], {"a": state_a, "b": state_b}
            )
            self.assertEqual([task.task_id for task, _ in selected], ["b", "a"])

    def test_result_does_not_count_impossible_as_solved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            solver = BashAgentSolver(make_settings(tmp_path))
            task = make_task(tmp_path)
            impossible = make_state(
                task, answer="IMPOSSIBLE\nno data", answer_kind="impossible"
            )
            value = make_state(task, answer="42", answer_kind="value")
            self.assertFalse(solver.result_for(task, impossible).solved)
            self.assertTrue(solver.result_for(task, value).solved)


if __name__ == "__main__":
    unittest.main()
