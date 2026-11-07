"""Verdicts for the three check kinds used by the challenge.

* ``unittest``  - run ``test*.py`` in the task workspace and require exit code 0;
* ``exact_int`` - compare the submitted answer with ``expected`` as integers;
* ``exact_str`` - compare the submitted answer with ``expected`` as a string.

The evaluator does not trust the harness's ``solved`` field: in
``solutions.json`` it only means "an answer was submitted".
"""

from __future__ import annotations

import re
import subprocess
import sys
import unicodedata
from dataclasses import asdict, dataclass

from evaluation.common.tasks import EvaluationTask, iter_test_files


@dataclass(frozen=True)
class Verdict:
    task_id: str
    check: str
    solved: bool
    expected: str | None
    actual: str | None
    detail: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def evaluate_task(
    task: EvaluationTask,
    *,
    answer: str | None = None,
    python: str | None = None,
    timeout: float = 120.0,
    strict: bool = False,
) -> Verdict:
    """Evaluate one task.

    ``answer`` overrides ``answer.txt`` (used by the CLI's ``--answer`` flag).
    ``strict`` disables the lenient integer extraction and case-insensitive
    string comparison.  Every check requires a submitted answer, because the
    regulation asks for ``answer.txt`` in each task directory.
    """
    check = (task.check or "").strip().lower()
    actual = answer if answer is not None else task.read_answer()

    if not task.solvable:
        return Verdict(
            task_id=task.task_id,
            check=task.check or "",
            solved=False,
            expected=task.expected,
            actual=actual,
            detail="task is marked unsolvable; no points are awarded",
        )

    if check == "unittest":
        return _evaluate_unittest(
            task,
            actual=actual,
            python=python or sys.executable,
            timeout=timeout,
        )

    if check == "exact_int":
        return _evaluate_exact_int(task, actual, strict=strict)
    if check in {"exact_str", "exact_string", "exact_text"}:
        return _evaluate_exact_str(task, actual, strict=strict)
    if check in {"none", "unsolvable", "impossible"}:
        return Verdict(
            task_id=task.task_id,
            check=task.check or "",
            solved=False,
            expected=task.expected,
            actual=actual,
            detail="unsolvable tasks are not awarded points",
        )

    return Verdict(
        task_id=task.task_id,
        check=task.check or "",
        solved=False,
        expected=task.expected,
        actual=actual,
        detail=f"unsupported check type: {task.check!r}",
    )


def _evaluate_exact_int(
    task: EvaluationTask,
    actual: str | None,
    *,
    strict: bool,
) -> Verdict:
    expected = _parse_int(task.expected, strict=True)
    if expected is None:
        return Verdict(
            task_id=task.task_id,
            check=task.check or "",
            solved=False,
            expected=task.expected,
            actual=actual,
            detail="task has no valid integer in 'expected'",
        )
    if actual is None or not actual.strip():
        return Verdict(
            task_id=task.task_id,
            check=task.check or "",
            solved=False,
            expected=task.expected,
            actual=actual,
            detail="no answer was submitted",
        )

    parsed = _parse_int(actual, strict=strict)
    if parsed is None:
        return Verdict(
            task_id=task.task_id,
            check=task.check or "",
            solved=False,
            expected=task.expected,
            actual=actual,
            detail="answer is not an integer",
        )

    solved = parsed == expected
    return Verdict(
        task_id=task.task_id,
        check=task.check or "",
        solved=solved,
        expected=task.expected,
        actual=actual,
        detail=(
            f"expected {expected}, got {parsed}"
            if not solved
            else f"matched integer {expected}"
        ),
    )


def _evaluate_exact_str(
    task: EvaluationTask,
    actual: str | None,
    *,
    strict: bool,
) -> Verdict:
    if task.expected is None:
        return Verdict(
            task_id=task.task_id,
            check=task.check or "",
            solved=False,
            expected=task.expected,
            actual=actual,
            detail="task has no 'expected' value",
        )
    if actual is None or not actual.strip():
        return Verdict(
            task_id=task.task_id,
            check=task.check or "",
            solved=False,
            expected=task.expected,
            actual=actual,
            detail="no answer was submitted",
        )

    expected_norm = _normalize_str(task.expected, strict=strict)
    actual_norm = _normalize_str(actual, strict=strict)
    solved = bool(actual_norm) and actual_norm == expected_norm
    return Verdict(
        task_id=task.task_id,
        check=task.check or "",
        solved=solved,
        expected=task.expected,
        actual=actual,
        detail=(
            f"expected {expected_norm!r}, got {actual_norm!r}"
            if not solved
            else f"matched {expected_norm!r}"
        ),
    )


def _evaluate_unittest(
    task: EvaluationTask,
    *,
    actual: str | None,
    python: str,
    timeout: float,
) -> Verdict:
    workspace = task.workspace
    test_files = iter_test_files(workspace)
    if not test_files:
        return Verdict(
            task_id=task.task_id,
            check=task.check or "",
            solved=False,
            expected=task.expected,
            actual=actual,
            detail=f"no test*.py files found in {workspace}",
        )

    failures: list[str] = []
    for test_file in test_files:
        try:
            completed = subprocess.run(
                [python, str(test_file)],
                cwd=str(workspace),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            failures.append(f"{test_file.name}: timeout after {timeout}s")
            continue
        except OSError as exc:
            failures.append(f"{test_file.name}: cannot run: {exc}")
            continue

        if completed.returncode != 0:
            output = ((completed.stdout or "") + (completed.stderr or "")).strip()
            failures.append(
                f"{test_file.name}: exit {completed.returncode}"
                + (f"\n{_tail(output, 2000)}" if output else "")
            )

    if failures:
        return Verdict(
            task_id=task.task_id,
            check=task.check or "",
            solved=False,
            expected=task.expected,
            actual=actual,
            detail="\n\n".join(failures),
        )

    # The regulation requires answer.txt in every task directory.  Tests
    # passing without a submitted answer is not enough.
    if actual is None or not actual.strip():
        return Verdict(
            task_id=task.task_id,
            check=task.check or "",
            solved=False,
            expected=task.expected,
            actual=actual,
            detail="tests passed, but no answer was submitted",
        )

    return Verdict(
        task_id=task.task_id,
        check=task.check or "",
        solved=True,
        expected=task.expected,
        actual=actual,
        detail=f"{len(test_files)} test file(s) passed",
    )


def _parse_int(text: str | None, *, strict: bool) -> int | None:
    if text is None:
        return None
    cleaned = _clean_text(text)
    candidate = (
        cleaned.replace(",", "")
        .replace("_", "")
        .replace(" ", "")
        .rstrip(".")
    )
    if re.fullmatch(r"[+-]?\d+", candidate):
        return int(candidate)

    if strict:
        return None

    # Lenient mode: accept "The answer is 42" but only when the text contains
    # exactly one integer, so ambiguous submissions still fail.
    numbers = re.findall(r"(?<![\w.])[+-]?\d+(?!\w)(?!\.\d)", cleaned)
    if len(numbers) == 1:
        return int(numbers[0].replace(",", ""))
    return None


def _normalize_str(text: str, *, strict: bool) -> str:
    value = unicodedata.normalize("NFKC", _clean_text(text))
    value = " ".join(value.split())
    value = value.strip(".,;:!?")
    return value if strict else value.casefold()


def _clean_text(text: str) -> str:
    value = text.strip()
    if value.startswith("```") and value.endswith("```"):
        value = value.strip("`").strip()
        lines = value.splitlines()
        if (
            len(lines) >= 2
            and re.fullmatch(r"[A-Za-z0-9_+-]+", lines[0].strip())
        ):
            value = "\n".join(lines[1:]).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"', "`"}:
        value = value[1:-1]
    return value


def _tail(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return "..." + text[-limit:]
