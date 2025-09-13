# Pica: Persistent key-value storage

![alt text](https://github.com/user-attachments/assets/125b4dc3-a3a7-4397-aa36-917e64f34951? "Pica header")

## Overview

_Pica pica_: The Eurasian magpie. Known for collecting shiny things 

The `pica` package is very similar to `shelve` (see docs [here](https://docs.python.org/3/library/shelve.html)). Both enable key-value pairs to be stored on file without loading/saving entire dictionaries.
 
However, `pica` uses SQLite behind the scenes instead of DBM. This means that values for existing keys can be edited as much as you like without file sizes increasing, eliminating bloat.

## Usage

Installation: `pip install picapica`

Basic usage:

```python
import pica

with pica.open("data.sqlite") as db:
    db["x"] = 1
    db["y"] = {"a": 42}

    print(db["x"])
    print("y" in db)
    print(len(db))

```

This saves data key-value paris to the file `data.sqlite`.

Unlike `shelve`, repeatedly updating key-value pairs does not necessarily increase the file size. However, the storage can still be optimised now and again! For this, use `db.vacuum`:

```python
with pica.open("data.sqlite") as db:
  db.vacuum()
```