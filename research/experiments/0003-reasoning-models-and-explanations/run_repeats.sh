#!/usr/bin/env bash
# Run three independent repeats of the key experiment 0003 configurations.
#
# The NeuralDeep key allows only one concurrent harness stream: running three
# passes in parallel returns HTTP 429 and the harness aborts after three
# consecutive model errors.  This script therefore runs the passes strictly
# one after another.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
cd "${REPO_ROOT}"

CONFIGS="${CONFIGS:-rr-plain,nr-plain,nn-plain,nn-single}"

for pass in 1 2 3; do
  out_dir="${SCRIPT_DIR}/results/repeats-${pass}"
  echo "=== repeat ${pass}: ${out_dir} ==="
  python3 "${SCRIPT_DIR}/run_experiment.py" \
    --configs "${CONFIGS}" \
    --out-dir "${out_dir}" \
    --timeout 7200

  python3 - "${out_dir}" <<'PY'
import json
import sys
from pathlib import Path

out_dir = Path(sys.argv[1])
broken = []
for path in sorted(out_dir.glob("*/summary.json")):
    payload = json.loads(path.read_text(encoding="utf-8"))
    summary = payload["summary"]
    if summary["cost"] < 1000 or summary["solved_tasks"] < 1:
        broken.append((path.parent.name, summary))
if broken:
    for name, summary in broken:
        print(f"error: {name}: suspicious summary {summary}", file=sys.stderr)
    raise SystemExit(1)
print(f"checked {out_dir}: all configs look valid")
PY
done
