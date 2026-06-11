Pica
=======

Pica is a Python library for persistent key-value storage on file using SQLite. It enables key-value pairs to be stored on file without loading/saving entire dictionaries.

Installation
------------

.. code-block:: bash

   pip install picapica

Usage
-----

.. code-block:: python

    with pica.open("data.sqlite") as db:
        db["x"] = 1
        db["y"] = {"a": 42}

        print(db["x"])
        print("y" in db)
        print(len(db))
