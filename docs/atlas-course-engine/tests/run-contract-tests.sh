#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"
if command -v pytest >/dev/null 2>&1; then
  pytest -q docs/atlas-course-engine/tests/test_atlas_course_contract.py
else
  echo "pytest is required to execute the contract tests" >&2
  exit 2
fi
