"""Contract tests for the Atlas course-engine package.

These tests are intentionally dependency-light. Goose should adapt paths/imports to the
actual implementation rather than deleting the assertions. The tests may begin as
contract/fixture tests and should become executable against the real engine.
"""
from pathlib import Path
import csv
import json
import os

ROOT = Path(__file__).resolve().parents[3]


def _find_csv():
    candidates = list(ROOT.rglob("*.csv"))
    preferred = [p for p in candidates if "course" in p.name.lower() or "atlas" in p.name.lower()]
    return preferred[0] if preferred else None


def test_contract_files_exist():
    required = [
        ROOT / "docs/atlas-course-engine/00-MASTER-SCOPE.md",
        ROOT / "docs/atlas-course-engine/01-REQUIREMENTS.md",
        ROOT / "docs/atlas-course-engine/02-DATA-AND-SCHEMA-CONTRACT.md",
        ROOT / "docs/atlas-course-engine/03-IMPLEMENTATION-MATRIX.csv",
        ROOT / "docs/atlas-course-engine/04-TEST-EXPECTATIONS.md",
        ROOT / "docs/atlas-course-engine/06-GOOSE-RUN.md",
        ROOT / "docs/atlas-course-engine/07-DEFINITION-OF-DONE.md",
    ]
    missing = [str(p) for p in required if not p.exists()]
    assert not missing, f"Missing contract files: {missing}"


def test_no_fake_done_language_in_matrix():
    p = ROOT / "docs/atlas-course-engine/03-IMPLEMENTATION-MATRIX.csv"
    with p.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows
    for row in rows:
        assert row["implementation_state"] != "DONE"


def test_canonical_csv_is_structurally_readable_if_present():
    p = _find_csv()
    if p is None:
        return
    with p.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert rows, f"CSV exists but has no records: {p}"
    headers = {h.strip() for h in rows[0].keys() if h}
    assert headers, f"CSV has no headers: {p}"


def test_no_obvious_secrets_in_contract_tree():
    bad = []
    for p in (ROOT / "docs/atlas-course-engine").rglob("*"):
        if not p.is_file() or p.suffix in {".pyc"}:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore").lower()
        for marker in ("aws_secret_access_key=", "service_role_key=", "authorization: bearer "):
            if marker in text:
                bad.append(f"{p}: {marker}")
    assert not bad, bad
