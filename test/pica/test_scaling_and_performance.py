import os
import pica
import pytest

from pathlib import Path


@pytest.mark.slow
def test_many_keys_scale(tmp_path: Path):
    db_path = tmp_path / "data.sqlite"
    N = 10_000
    with pica.open(db_path) as db:
        for i in range(N):
            db[f"k{i}"] = i
        assert len(db) == N

    with pica.open(db_path) as db:
        # spot-check a few
        for i in (0, N//2, N-1):
            assert db[f"k{i}"] == i


@pytest.mark.slow
def test_large_values(tmp_path: Path):
    db_path = tmp_path / "data.sqlite"
    big = os.urandom(2_000_000)  # ~2 MB
    with pica.open(db_path) as db:
        db["big"] = big
        assert db["big"] == big
