"""Model-facing prompts and observations for the bash-script agent."""

from __future__ import annotations

from harness.application.shell import ProcessResult
from harness.application.state import TaskState

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


def followup_warning(state: TaskState, *, final: bool) -> str:
    """Build the user message that starts a follow-up wave."""
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
            "Even if the tests already pass, this turn must end by writing "
            "answer.txt (DONE for coding tasks)."
        )
    lines.append(
        "Continue from the current workspace state. Reply with one bash "
        "script and nothing else."
    )
    if final:
        lines.append(
            "This is the final attempt: combine every remaining command into "
            "one script and write answer.txt at the end. Do not spend it on a "
            "single grep, ls or cat."
        )
    return "\n".join(lines)
