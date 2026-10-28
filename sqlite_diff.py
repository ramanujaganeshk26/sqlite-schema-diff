#!/usr/bin/env python3
"""SQLite Schema and Stats Diff Tool."""

import argparse
import sqlite3
import sys
from typing import Dict, Any, List


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


def diff_databases(db1_data: Dict[str, Any], db2_data: Dict[str, Any]) -> Dict[str, Any]:
    """Compute diff between two inspected databases."""
    t1 = db1_data.get("tables", {})
    t2 = db2_data.get("tables", {})

    all_tables = sorted(set(t1.keys()) | set(t2.keys()))

    added = []
    removed = []
    modified = []
    unchanged = []

    for t in all_tables:
        if t not in t1:
            added.append({"table": t, "row_count": t2[t]["row_count"]})
        elif t not in t2:
            removed.append({"table": t, "row_count": t1[t]["row_count"]})
        else:
            s1, s2 = t1[t]["sql"], t2[t]["sql"]
            c1, c2 = t1[t]["row_count"], t2[t]["row_count"]
            if s1 != s2 or c1 != c2:
                modified.append({
                    "table": t,
                    "schema_changed": s1 != s2,
                    "sql_a": s1,
                    "sql_b": s2,
                    "row_count_a": c1,
                    "row_count_b": c2,
                    "row_count_delta": c2 - c1,
                })
            else:
                unchanged.append(t)

    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged,
    }


def main():
    parser = argparse.ArgumentParser(description="Compare two SQLite databases.")
    parser.add_argument("db1", help="Path to first SQLite database")
    parser.add_argument("db2", help="Path to second SQLite database")
    args = parser.parse_args()

    db1_data = inspect_db(args.db1)
    db2_data = inspect_db(args.db2)
    diff = diff_databases(db1_data, db2_data)
    print(diff)


if __name__ == "__main__":
    main()
