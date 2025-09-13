import io
import pytest


class Thing:
    """
    A thing.
    """
    def __init__(self, x): self.x = x
    def __eq__(self, other): return isinstance(other, Thing) and other.x == self.x


def test_pickle_roundtrip_custom_class(db):
    obj = Thing({"a": 1})
    db["obj"] = obj
    assert db["obj"] == obj


def test_unpicklable_raises(db):
    # Open file handles aren't picklable: ensure we surface an error on set
    f = io.BytesIO(b"data")
    f.close()  # closed BytesIO is picklable; use a real file-like?
    # Use a real open file which isn't picklable on many platforms
    import tempfile
    with tempfile.TemporaryFile() as tf:
        with pytest.raises(Exception):
            db["bad"] = tf  # PicklingError / AttributeError etc.


def test_bytes_and_text(db):
    db["b"] = b"\x00\x01\x02"
    db["t"] = "hello"
    assert db["b"] == b"\x00\x01\x02"
    assert db["t"] == "hello"
