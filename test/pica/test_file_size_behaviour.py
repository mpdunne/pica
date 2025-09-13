import os
import pica

from pathlib import Path

PAGE_TOLERANCE = 8192  # allow up to 2 pages wiggle room


def test_overwrite_same_key_no_growth(db_nowal, db_path: Path):
    import os
    def size(): return db_path.stat().st_size

    payload = os.urandom(1024)  # 1 KiB
    db_nowal["blob"] = payload
    base = size()

    # Overwrite with same-sized payload many times; size should not ratchet
    for _ in range(1000):
        db_nowal["blob"] = os.urandom(len(payload))

    after = size()
    assert after <= base + PAGE_TOLERANCE


def test_overwrite_with_growth_reuses_space(db_nowal, db_path: Path):
    def size(): return db_path.stat().st_size

    db_nowal["k"] = os.urandom(2048)
    base = size()

    # Grow value moderately
    db_nowal["k"] = os.urandom(32768)  # 32 KiB
    grown = size()
    assert grown >= base  # likely grows to accommodate

    # Now overwrite with slightly smaller data, expect no further ratcheting
    for _ in range(200):
        db_nowal["k"] = os.urandom(32768)
    after = size()
    assert after <= grown + PAGE_TOLERANCE


def test_delete_then_vacuum_shrinks(db_path: Path):
    # Use wal=False for deterministic single file size checks
    with pica.open(db_path, wal=False) as db:
        for i in range(300):
            db[f"k{i}"] = os.urandom(4096)  # ~1 page each

    grown = db_path.stat().st_size

    with pica.open(db_path, wal=False) as db:
        for i in range(300):
            del db[f"k{i}"]
        # still large prior to VACUUM
        pre = db_path.stat().st_size
        assert pre >= grown

        db.vacuum()

    post = db_path.stat().st_size
    assert post < pre
    assert post < grown / 2
