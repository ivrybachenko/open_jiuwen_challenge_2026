#!/bin/bash
cd /Users/zbr174/dev/open_jiuwen_challenge_2026/research/experiments/0004-solve-or-collect-next-turn-data/results/goal-nn/run-03/work/tasks/006_coding_0124/workspace

# First, let's see the full test file
echo "=== FULL TEST FILE ==="
cat test_dial.py
echo "=== FULL DIAL.PY ==="
cat dial.py
echo "=== RUNNING TESTS ==="
python3 test_dial.py 2>&1