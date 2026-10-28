#!/usr/bin/env python3
"""SQLite Schema and Stats Diff Tool."""

import argparse
import sqlite3
import sys
from typing import Dict, Any


def inspect_db(db_path: str) -> Dict[str, Any]:
    """Inspect SQLite database schema and row counts."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT type, name, sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name")
    schema_items = cursor.fetchall()

    tables = {}
    for item_type, name, sql in schema_items:
        if item_type == "table" and not name.startswith("sqlite_"):
            cursor.execute(f'SELECT COUNT(*) FROM "{name}"')
            row_count = cursor.fetchone()[0]
            tables[name] = {"sql": sql.strip(), "row_count": row_count}

    conn.close()
    return {"tables": tables}


def main():
    parser = argparse.ArgumentParser(description="Compare two SQLite databases.")
    parser.add_argument("db1", help="Path to first SQLite database")
    parser.add_argument("db2", help="Path to second SQLite database")
    args = parser.parse_args()

    db1_data = inspect_db(args.db1)
    db2_data = inspect_db(args.db2)
    print(f"Database 1 tables: {len(db1_data['tables'])}")
    print(f"Database 2 tables: {len(db2_data['tables'])}")


if __name__ == "__main__":
    main()
