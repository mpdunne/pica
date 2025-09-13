from __future__ import annotations

import sqlite3, pickle, pathlib

from typing import Any, Iterable, Iterator, Tuple, List


class Stash:
    """
    A pica Stash. Simple persistent key/value store on a single SQLite file, with no bloat.
    """
    def __init__(
        self,
        path: str | pathlib.Path,
        *,
        wal: bool = True,
        read_only: bool = False,
    ):
        """
        Constructor for the pica Stash class.

        :param path: The path to which to save the data.
        :param wal: Write-ahead logging. Slighlty larger file, but better for concurrent or frequent writes.
        :param read_only: Opens the database in read-only mode.
        """
        self.path = str(path)
        self._dumps, self._loads = pickle.dumps, pickle.loads
        uri = f"file:{self.path}?mode={'ro' if read_only else 'rwc'}"
        self._con = sqlite3.connect(uri, uri=True, isolation_level=None, detect_types=0)
        self._con.execute("PRAGMA foreign_keys=ON")
        if wal and not read_only:
            self._con.execute("PRAGMA journal_mode=WAL")
            self._con.execute("PRAGMA synchronous=NORMAL")
        self._con.execute(
            "CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v BLOB NOT NULL)"
        )

    ############
    # Context! #
    ############

    def __enter__(self) -> Stash: return self
    def __exit__(self, exc_type, exc, tb) -> None: self.close()

    #################################
    # Standard key-value operations #
    #################################

    def __setitem__(self, key: str, value: Any) -> None:
        self._con.execute("BEGIN IMMEDIATE")
        self._con.execute(
            "INSERT INTO kv(k,v) VALUES(?,?) "
            "ON CONFLICT(k) DO UPDATE SET v=excluded.v",
            (key, self._dumps(value))
        )
        self._con.execute("COMMIT")

    def __getitem__(self, key: str) -> Any:
        row = self._con.execute("SELECT v FROM kv WHERE k=?", (key,)).fetchone()
        if row is None: raise KeyError(key)
        return self._loads(row[0])

    def __delitem__(self, key: str) -> None:
        cur = self._con.execute("DELETE FROM kv WHERE k=?", (key,))
        if cur.rowcount == 0: raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return self._con.execute("SELECT 1 FROM kv WHERE k=? LIMIT 1", (key,)).fetchone() is not None

    def __len__(self) -> int:
        return self._con.execute("SELECT COUNT(*) FROM kv").fetchone()[0]

    #################################
    # Standard key-value attributes #
    #################################

    def keys(self) -> Iterator[str]:
        for (k,) in self._con.execute("SELECT k FROM kv"):
            yield k

    def items(self) -> Iterator[Tuple[str, Any]]:
        for k, v in self._con.execute("SELECT k,v FROM kv"):
            yield k, self._loads(v)

    def values(self) -> Iterator[Any]:
        for _, v in self.items():
            yield v

    ####################
    # Batch operations #
    ####################

    def set_many(self, pairs: Iterable[Tuple[str, Any]]) -> None:
        """
        Set many pairs!

        :param pairs: A list of key-value pairs.
        """
        self._con.execute("BEGIN IMMEDIATE")
        self._con.executemany(
            "INSERT INTO kv(k,v) VALUES(?,?) "
            "ON CONFLICT(k) DO UPDATE SET v=excluded.v",
            ((k, self._dumps(v)) for k, v in pairs),
        )
        self._con.execute("COMMIT")

    def get_many(self, keys: Iterable[str]) -> List[Any]:
        """
        Get many values!

        :param keys: A list of keys to get.
        """
        ks = list(keys)
        if not ks: return []
        q = ",".join("?" for _ in ks)
        rows = self._con.execute(f"SELECT k,v FROM kv WHERE k IN ({q})", ks).fetchall()
        m = {k: self._loads(v) for k, v in rows}
        return [m[k] for k in ks if k in m]

    ###############
    # Maintenance #
    ###############

    def vacuum(self) -> None:
        """
        Reorganise things to optimise space.
        """
        self._con.execute("VACUUM")

    def close(self) -> None:
        """
        Close the stash.
        """
        if getattr(self, "_con", None):
            self._con.close()
            self._con = None
