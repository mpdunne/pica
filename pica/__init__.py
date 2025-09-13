from ._stash import Stash as _Stash

__all__ = ["open", "Stash", "__version__"]
__version__ = "0.1.0"


def open(path, *, wal: bool = True, read_only: bool = False) -> _Stash:
    """
    Open a pica stash! 🐦‍⬛
    """
    return _Stash(path, wal=wal, read_only=read_only)


Stash = _Stash
