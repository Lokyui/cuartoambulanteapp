from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
DB_SRC = ROOT / "src"

if str(DB_SRC) not in sys.path:
    sys.path.insert(0, str(DB_SRC))


from db.dal import DAL  # noqa: E402


@pytest.fixture
def dal(tmp_path: Path) -> DAL:
    instancia = DAL(db_path=tmp_path / "test.db")
    instancia.inicializar()
    return instancia
