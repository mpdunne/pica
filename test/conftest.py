import os
from pathlib import Path
import pytest

import pica

@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "data.sqlite"

@pytest.fixture
def db(db_path: Path):
    # WAL on by default; good for concurrency tests
    with pica.open(db_path, wal=True) as handle:
        yield handle

@pytest.fixture
def db_nowal(db_path: Path):
    # For file-size assertions (avoid -wal file interference)
    with pica.open(db_path, wal=False) as handle:
        yield handle

def file_size(path: Path) -> int:
    return path.stat().st_size if path.exists() else 0
