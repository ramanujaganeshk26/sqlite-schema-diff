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

## Examples & Output

### Text Diff Example
When comparing an older database against a newer version with schema and row updates:

```bash
python3 sqlite_diff.py v1.db v2.db
```

Output:
```text
=== Added Tables ===
  + new_table (5 rows)

=== Removed Tables ===
  - legacy_table (12 rows)

=== Modified Tables ===
  * Table: users
    Schema changed!
    Old: CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)
    New: CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)
    Rows: 100 -> 145 (+45)
```

### JSON Output Example

```bash
python3 sqlite_diff.py v1.db v2.db --json
```

Output:
```json
{
  "added": [
    {"table": "new_table", "row_count": 5}
  ],
  "removed": [
    {"table": "legacy_table", "row_count": 12}
  ],
  "modified": [
    {
      "table": "users",
      "schema_changed": true,
      "sql_a": "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)",
      "sql_b": "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)",
      "row_count_a": 100,
      "row_count_b": 145,
      "row_count_delta": 45
    }
  ],
  "unchanged": ["config"]
}
```

## Python API Usage

You can also import and use `sqlite_diff` inside your own Python scripts:

```python
from sqlite_diff import inspect_db, diff_databases, format_text_diff

db1_info = inspect_db("v1.db")
db2_info = inspect_db("v2.db")

diff_result = diff_databases(db1_info, db2_info)
print(format_text_diff(diff_result))
```

## Running Tests

Run unit tests using python's built-in `unittest` module:

```bash
python3 -m unittest test_sqlite_diff.py
```
