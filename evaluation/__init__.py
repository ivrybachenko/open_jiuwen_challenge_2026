"""Evaluation tools for the OpenJiuwen Challenge 2026 harness.

The package is intentionally dependency-free (stdlib only) so it can be run
with the same interpreter as the harness or with the system Python:

    python -m evaluation.harness_task_checker --task coding/easy/0001
    python -m evaluation.harness_task_set_checker --task-set data/task_set/example.yaml
    python -m evaluation.dockerfile_checker
    python -m evaluation.answer_evaluator --task data/task/coding/easy/0001
    python -m evaluation.commit_harness_version --harness-version 0001
"""
