# Pica: Persistent key-value storage

![alt text](https://github.com/user-attachments/assets/125b4dc3-a3a7-4397-aa36-917e64f34951? "Pica header")

## Overview

_Pica pica_: The Eurasian magpie. Known for collecting shiny things 

The `pica` package is very similar to `shelve` (see docs [here](https://docs.python.org/3/library/shelve.html)). Both enable key-value pairs to be stored on file without loading/saving entire dictionaries, which is super useful!
 
However, `pica` uses SQLite behind the scenes instead of DBM. This avoids some issues that `shelve` and `dbm` have with editing existing values causing runaway file bloat. See below for more info!  

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

This saves data key-value pairs to the file `data.sqlite`.

To optimise the storage and reduce file size (e.g. after deleting or editing values), you can use `vacuum`:

```python
with pica.open("data.sqlite") as db:
  db.vacuum()
```

## Comparison with `shelve`

The main advantage of `pica` over `shelve` is how it copes with value rewrites for existing keys.

With `shelve`, repeatedly updating key-value pairs can cause file sizes to keep increasing much more than one might expect, potentially leading to huge but mostly empty files.

For example, if we run this script:

```python
import os, shelve, pica

def kb(path): return os.path.getsize(path)//1024

print("=== shelve ===")
for i in range(100):
    with shelve.open("shelve") as db:
        db["data"] = list(range(i*100))  # keep changing size
print("shelve.db:", kb("shelve.db"), "KB")

print("\n=== pica ===")
for i in range(100):
    with pica.open("pica.sqlite") as db:
        db["data"] = list(range(i*100))
print("pica.sqlite:", kb("pica.sqlite"), "KB")
```

We get:
```bash
=== shelve ===
shelve.db: 508 KB

=== pica ===
pica.sqlite: 68 KB
```

Even though the contents of the files are the same: (a single list keyed by `"data"`), the file sizes are drastically different.

In fact, if we run the same script again, the shelve files _keep_ growing:

```bash
=== shelve ===
shelve.db: 1388 KB

=== pica ===
pica.sqlite: 68 KB
```

This behaviour with `shelve` can become very inconvenient very quickly, often without anyone noticing. This is where our magpie `pica` shines.