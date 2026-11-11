"""Unit tests for the canonical JSONL archive and its readable YAML view."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from harness.application.trajectory import ReadableTrajectoryStore


def _attr(key: str, value) -> dict:
    if isinstance(value, bool):
        encoded = {"boolValue": value}
    elif isinstance(value, int):
        encoded = {"intValue": str(value)}
    else:
        encoded = {"stringValue": str(value)}
    return {"key": key, "value": encoded}


def _span(name: str, attributes: list[dict], start: int, end: int) -> dict:
    return {
        "traceId": "a" * 32,
        "spanId": f"{start:016x}"[-16:],
        "name": name,
        "kind": "SPAN_KIND_INTERNAL",
        "attributes": attributes,
        "startTimeUnixNano": str(start),
        "endTimeUnixNano": str(end),
    }


def _trajectory() -> Trajectory:
    from openjiuwen.agent_evolving.trajectory.model import Trajectory

    prompts = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "How many boxes?"},
    ]
    completions = [
        {
            "role": "assistant",
            "reasoning_content": "Let me compute it.",
            "content": "",
            "tool_calls": [
                {
                    "id": "call-1",
                    "name": "bash",
                    "arguments": {"command": "echo 42"},
                }
            ],
        }
    ]
    llm = _span(
        "chat test-model",
        [
            _attr("gen_ai.operation.name", "chat"),
            _attr("gen_ai.request.model", "test-model"),
            _attr("gen_ai.input.messages", json.dumps(prompts)),
            _attr("gen_ai.output.messages", json.dumps(completions)),
            _attr("gen_ai.usage.input_tokens", 12),
            _attr("gen_ai.usage.output_tokens", 7),
        ],
        1_700_000_000_000_000_000,
        1_700_000_001_500_000_000,
    )
    tool = _span(
        "execute_tool bash",
        [
            _attr("gen_ai.operation.name", "execute_tool"),
            _attr("gen_ai.tool.name", "bash"),
            _attr("gen_ai.tool.call.arguments", json.dumps({"command": "echo 42"})),
            _attr("gen_ai.tool.call.result", "42"),
        ],
        1_700_000_001_500_000_000,
        1_700_000_002_000_000_000,
    )
    return Trajectory.from_otlp(
        {
            "resourceSpans": [
                {
                    "resource": {
                        "attributes": [
                            _attr("openjiuwen.trajectory_id", "traj-1"),
                            _attr("gen_ai.conversation.id", "task_1"),
                        ]
                    },
                    "scopeSpans": [{"spans": [llm, tool]}],
                }
            ]
        }
    )


class ReadableTrajectoryStoreTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Configure the SDK logger before its first import, as the harness does.
        from harness.application.ojw import configure_logging

        configure_logging()

    def test_writes_jsonl_and_readable_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            store = ReadableTrajectoryStore(base)
            store.save(_trajectory())

            archive = base / "trajectories_default.jsonl"
            self.assertTrue(archive.is_file())
            self.assertIn("reasoning_content", archive.read_text(encoding="utf-8"))

            readable = base / "readable" / "task_1__traj-1.yaml"
            self.assertTrue(readable.is_file())
            payload = yaml.safe_load(readable.read_text(encoding="utf-8"))

            self.assertEqual(payload["task_id"], "task_1")
            self.assertEqual(payload["trajectory_id"], "traj-1")
            self.assertNotIn("run_id", payload)
            self.assertEqual(payload["model"], "test-model")
            self.assertEqual(payload["task"], "How many boxes?")
            self.assertEqual([step["kind"] for step in payload["steps"]], ["llm", "tool"])

            llm_step, tool_step = payload["steps"]
            self.assertEqual(llm_step["reasoning"], "Let me compute it.")
            self.assertEqual(llm_step["tool_calls"][0]["name"], "bash")
            self.assertEqual(llm_step["usage"]["prompt_tokens"], 12)
            self.assertEqual(tool_step["tool"], "bash")
            self.assertEqual(tool_step["arguments"], {"command": "echo 42"})
            self.assertEqual(tool_step["result"], "42")

    def test_run_id_is_written_to_jsonl_and_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            store = ReadableTrajectoryStore(base, run_id="run-123")
            store.save(_trajectory())

            record = json.loads(
                (base / "trajectories_default.jsonl").read_text(encoding="utf-8")
            )
            attributes = {
                item["key"]: item["value"]
                for item in record["resourceSpans"][0]["resource"]["attributes"]
            }
            self.assertEqual(
                attributes["harness.run_id"], {"stringValue": "run-123"}
            )

            readable = base / "readable" / "task_1__traj-1.yaml"
            payload = yaml.safe_load(readable.read_text(encoding="utf-8"))
            self.assertEqual(payload["run_id"], "run-123")

    def test_yaml_failure_keeps_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            store = ReadableTrajectoryStore(base)
            with patch(
                "harness.application.trajectory._readable_payload",
                side_effect=RuntimeError("boom"),
            ):
                store.save(_trajectory())

            self.assertTrue((base / "trajectories_default.jsonl").is_file())
            self.assertFalse((base / "readable").exists())


if __name__ == "__main__":
    unittest.main()
