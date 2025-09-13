import pica
import pytest

from pathlib import Path


def test_open_context_manager(db_path: Path):
    with pica.open(db_path) as db:
        db["x"] = 1
        assert db["x"] == 1
        assert "x" in db
        assert len(db) == 1

    # Re-open to ensure persistence
    with pica.open(db_path) as db:
        assert db["x"] == 1


def test_keys_items_values_and_delete(db):
    for i in range(5):
        db[f"k{i}"] = i

    assert set(db.keys()) == {f"k{i}" for i in range(5)}
    assert dict(db.items()) == {f"k{i}": i for i in range(5)}
    assert set(db.values()) == {0, 1, 2, 3, 4}

    del db["k3"]
    assert "k3" not in db
    assert len(db) == 4

    with pytest.raises(KeyError):
        _ = db["missing"]
    with pytest.raises(KeyError):
        del db["missing"]


def test_set_many_get_many(db):
    pairs = [(f"key{i}", {"i": i}) for i in range(100)]
    db.set_many(pairs)

    result = db.get_many([f"key{i}" for i in range(100)])
    # get_many returns only found keys in request order
    assert len(result) == 100
    assert result[0] == {"i": 0}
    assert result[-1] == {"i": 99}


def test_read_only_blocks_writes(db_path: Path):
    with pica.open(db_path) as rw:
        rw["x"] = 1

    with pica.open(db_path, read_only=True) as ro:
        assert ro["x"] == 1
        with pytest.raises(Exception):
            ro["y"] = 2
        with pytest.raises(Exception):
            del ro["x"]
