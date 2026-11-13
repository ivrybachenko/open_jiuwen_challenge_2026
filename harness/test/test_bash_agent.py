"""Unit tests for the bash solver prompt, state and wave selection."""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
import unittest
from pathlib import Path

from harness.solving.agents.rails.followup import followup_warning
from harness.solving.agents.script_agent import (
    SYSTEM_PROMPT,
    ScriptAgent,
    execution_message,
    extract_script,
)
from harness.config import DEFAULT_MODEL, Settings
from harness.tasks import TaskState
from harness.tasks import Task
from harness.solving.workspace import ProcessResult
from harness.solving.scheduler import WaveScheduler


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

    def test_prompt_requires_answer_even_when_tests_pass(self) -> None:
        lowered = SYSTEM_PROMPT.lower()
        self.assertIn("even if the tests already pass", lowered)
        self.assertIn("joined in", lowered)
        self.assertIn("executed as one script", lowered)
        self.assertIn("must come\nlast", lowered)

    def test_extract_script_joins_all_fenced_blocks_in_order(self) -> None:
        self.assertEqual(
            extract_script("```bash\necho 42\n```"),
            "echo 42",
        )
        self.assertEqual(extract_script("echo 42"), "echo 42")
        content = (
            "I will inspect first.\n"
            "```bash\ncat data.txt\n```\n"
            "Then I will fix and submit.\n"
            "```bash\necho 42 > answer.txt\n```\n"
        )
        self.assertEqual(
            extract_script(content),
            "cat data.txt\necho 42 > answer.txt",
        )

    def test_extract_script_keeps_the_submission_last(self) -> None:
        content = (
            "```bash\nsed -i 's/a/b/' mylib.py\n```\n"
            "```bash\npython3 test_mylib.py\n```\n"
            "```bash\necho DONE > answer.txt\n```\n"
        )
        script = extract_script(content)
        self.assertTrue(script.endswith("echo DONE > answer.txt"))
        self.assertIn("sed -i", script)

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
            solver = ScriptAgent(settings)
            state = asyncio.run(solver.prepare(task))
            self.assertIn("$ cat task.txt", state.overview)
            self.assertEqual(state.messages[0]["content"], SYSTEM_PROMPT)
            self.assertTrue((tmp_path / "agent" / task.task_id / "state.json").is_file())

            state.wave1_done = True
            solver._state.save(task, state)

            restored = asyncio.run(ScriptAgent(settings).prepare(task))
            self.assertTrue(restored.wave1_done)

    def test_no_resume_starts_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            task = make_task(tmp_path)
            settings = make_settings(tmp_path)
            solver = ScriptAgent(settings)
            state = asyncio.run(solver.prepare(task))
            state.wave1_done = True
            solver._state.save(task, state)

            fresh = asyncio.run(
                ScriptAgent(make_settings(tmp_path, resume=False)).prepare(task)
            )
            self.assertFalse(fresh.wave1_done)

    def test_record_failure_marks_wave_done(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            task = make_task(tmp_path)
            solver = ScriptAgent(make_settings(tmp_path))
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
            solver = ScriptAgent(settings)
            task = make_task(tmp_path)
            done = make_state(task, answer="42", answer_kind="value", wave1_done=True)
            selected = WaveScheduler(settings).select_candidates(
                [task], {task.task_id: done}, 2, remaining=None
            )
            self.assertEqual(selected, [])

    def test_impossible_can_be_selected_and_warned(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            solver = ScriptAgent(make_settings(tmp_path))
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
            selected = WaveScheduler(solver.settings).select_candidates(
                [task], {task.task_id: state}, 2, remaining=None
            )
            self.assertEqual(len(selected), 1)
            warning = followup_warning(state, final=False).lower()
            self.assertIn("impossible", warning)
            self.assertIn("cut off", warning)
            self.assertNotIn("budget", warning)

    def test_budget_filters_expensive_retries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            settings = make_settings(tmp_path)
            solver = ScriptAgent(settings)
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
            selected = WaveScheduler(settings).select_candidates(
                [task], {task.task_id: state}, 2, remaining=100
            )
            self.assertEqual(selected, [])

    def test_higher_reward_wins_when_probability_is_equal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            solver = ScriptAgent(make_settings(tmp_path))
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
            selected = WaveScheduler(solver.settings).select_candidates(
                [task_a, task_b], {"a": state_a, "b": state_b}, 2, remaining=None
            )
            self.assertEqual([task.task_id for task, _ in selected], ["b", "a"])

    def test_result_does_not_count_impossible_as_solved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            solver = ScriptAgent(make_settings(tmp_path))
            task = make_task(tmp_path)
            impossible = make_state(
                task, answer="IMPOSSIBLE\nno data", answer_kind="impossible"
            )
            value = make_state(task, answer="42", answer_kind="value")
            self.assertFalse(solver.result_for(task, impossible).solved)
            self.assertTrue(solver.result_for(task, value).solved)

    def test_wave2_warning_requires_submission(self) -> None:
        state = TaskState(
            task_id="coding_0003",
            task_root="/data/tasks/coding_0003",
            model=DEFAULT_MODEL,
            turns=[{"wave": 1, "answer": None, "exit_code": 0, "features": {}}],
        )
        warning = followup_warning(state, final=False).lower()
        self.assertIn("did not create a non-empty answer.txt", warning)
        self.assertIn("even if the tests already pass", warning)
        self.assertNotIn("final attempt", warning)

    def test_final_wave_warning_requires_chaining(self) -> None:
        state = TaskState(
            task_id="search_0005",
            task_root="/data/tasks/search_0005",
            model=DEFAULT_MODEL,
            turns=[{"wave": 2, "answer": None, "exit_code": 0, "features": {}}],
        )
        warning = followup_warning(state, final=True).lower()
        self.assertIn("final attempt", warning)
        self.assertIn("single grep", warning)
        self.assertIn("write answer.txt", warning)

    def test_wave_done_uses_turns_and_flags(self) -> None:
        state = TaskState(
            task_id="search_0001",
            task_root="/data/tasks/search_0001",
            model=DEFAULT_MODEL,
            turns=[{"wave": 1}, {"wave": 2}, {"wave": 3}],
        )
        self.assertTrue(state.wave_done(1))
        self.assertTrue(state.wave_done(2))
        self.assertTrue(state.wave_done(3))
        self.assertFalse(state.wave_done(4))

    def test_third_wave_is_selected_after_the_second(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            solver = ScriptAgent(make_settings(tmp_path))
            task = make_task(tmp_path, reward=10)
            features = {
                "answer_kind": "none",
                "hit_token_limit": False,
                "script_error": "",
                "script_timed_out": False,
                "exit_code": 0,
                "reasoning_keyword_impossible": 0,
                "reasoning_keyword_give_up": 0,
                "reasoning_words": 100,
                "script_has_write_answer": False,
                "script_has_python": True,
                "output_chars": 10,
                "tests_in_overview": False,
            }
            state = make_state(
                task,
                wave1_done=True,
                wave2_done=True,
                cost=100,
                turns=[
                    {"wave": 1, "features": features},
                    {"wave": 2, "features": features},
                ],
            )
            selector = WaveScheduler(solver.settings)
            self.assertEqual(
                len(selector.select_candidates([task], {task.task_id: state}, 3)),
                1,
            )

            state.turns.append({"wave": 3, "features": features})
            self.assertEqual(
                selector.select_candidates([task], {task.task_id: state}, 3),
                [],
            )

    def test_run_turn_skips_a_completed_wave(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            solver = ScriptAgent(make_settings(tmp_path))
            task = make_task(tmp_path)
            state = make_state(task, turns=[{"wave": 1}])
            self.assertIsNone(asyncio.run(solver.run_turn(task, state, 1)))


class ScriptExecutionTest(unittest.TestCase):
    def test_relative_script_and_task_paths_still_execute(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.getcwd()
            os.chdir(tmp)
            try:
                root = Path("tasks") / "math_0000"
                workspace = root / "workspace"
                workspace.mkdir(parents=True)
                task = Task(
                    task_id="math_0000",
                    task_type="math",
                    instruction="write 42",
                    reward=1.0,
                    expected="42",
                    check="exact_int",
                    root=root,
                )
                agent_dir = Path("agent")
                agent_dir.mkdir()
                script = agent_dir / "turn_01.sh"
                script.write_text("echo hello; echo 42 > answer.txt\n", encoding="utf-8")

                solver = ScriptAgent(make_settings(Path(tmp)))
                result = solver._run_script(task, script, 1)

                self.assertEqual(result.exit_code, 0)
                self.assertIn("hello", result.output)
                self.assertEqual(
                    (workspace / "answer.txt").read_text(encoding="utf-8").strip(),
                    "42",
                )
                self.assertFalse((workspace / ".harness_step_01.sh").exists())
            finally:
                os.chdir(previous)


if __name__ == "__main__":
    unittest.main()
