# sqlite-schema-diff

A lightweight, zero-dependency Python CLI tool to inspect and diff schemas and row counts between two SQLite database files.

## Features
- Compares tables, schema definition SQL, and table row counts.
- Highlights added, removed, and modified tables.
- Outputs human-readable plain text or structured JSON.
- Built purely using Python standard library (`sqlite3`, `argparse`, `json`).

## Usage

Run directly with Python 3:

```bash
python3 sqlite_diff.py path/to/db1.sqlite path/to/db2.sqlite
```

To output JSON structured format:

```bash
python3 sqlite_diff.py path/to/db1.sqlite path/to/db2.sqlite --json
```

## Running Tests

Run unit tests using python's built-in `unittest` module:

```bash
python3 -m unittest test_sqlite_diff.py
```

---
_This project was scaffolded with the help of an AI agent._
