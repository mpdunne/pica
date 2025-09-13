import threading
import time
import pica

from pathlib import Path


def test_wal_allows_readers_during_writes(tmp_path):
    db_path = tmp_path / "data.sqlite"

    # Prime the DB and turn on WAL with a writeable handle first
    with pica.open(db_path, wal=True) as db:
        db["counter"] = 0  # also ensures table exists and -wal/-shm get created

    stop = False
    read_errors, write_errors = [], []

    def writer():
        try:
            with pica.open(db_path, wal=True) as db:
                for i in range(1000):
                    if stop: break
                    db["counter"] = i
        except Exception as e:
            write_errors.append(e)

    def reader():
        try:
            with pica.open(db_path, wal=True, read_only=True) as ro:
                while not stop:
                    _ = ro["counter"]
        except Exception as e:
            read_errors.append(e)

    t_w = threading.Thread(target=writer)
    t_r1 = threading.Thread(target=reader); t_r2 = threading.Thread(target=reader)
    t_w.start(); t_r1.start(); t_r2.start()
    time.sleep(0.5); stop = True
    t_w.join(); t_r1.join(); t_r2.join()

    assert not write_errors
    assert not read_errors


def test_read_only_guard(tmp_path: Path):
    db_path = tmp_path / "data.sqlite"
    with pica.open(db_path) as db:
        db["x"] = 1

    # Trying to write via read_only handle should error
    with pica.open(db_path, wal=True, read_only=True) as ro:
        ok = ro["x"]
        assert ok == 1
        threw = False
        try:
            ro["y"] = 2
        except Exception:
            threw = True
        assert threw
