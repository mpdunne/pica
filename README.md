# Pica: Persistent key-value storage

<img width="2176" height="544" alt="image" src="https://github.com/user-attachments/assets/125b4dc3-a3a7-4397-aa36-917e64f34951" />

## Overview

_Pica pica_: The Eurasian magpie. Known for collecting shiny things

Like `shelve`, but allows key-value pairs to be edited without causing file bloat. Works with any picklable objects!

Installation: `pip install picapica`

## Usage

Basic usage:

```
import pica

with pica.open("data.sqlite") as db:
    db["x"] = 1
    db["y"] = {"a": 42}

    print(db["x"])
    print("y" in db)
    print(len(db))

```

Unlike `shelve`, repeatedly updating key-value pairs does not necessarily increase the file size. However, the storage can still be optimised now and again! For this, use `db.vacuum`:

```
with pica.open("data.sqlite") as db:
  db.vacuum()
```
