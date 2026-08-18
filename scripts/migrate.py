#!/usr/bin/env python3
"""Create/upgrade Atlas schema via SQLAlchemy metadata (SQLite + Postgres)."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.db.base import Base
from app.db.session import engine
from app import models  # noqa: F401 — register models


def main() -> None:
    Path(ROOT / "data").mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    print("OK: schema applied to", engine.url)
    print("tables:", sorted(Base.metadata.tables.keys()))


if __name__ == "__main__":
    main()
