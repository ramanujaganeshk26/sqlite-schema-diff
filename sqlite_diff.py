#!/usr/bin/env python3
"""SQLite Schema and Stats Diff Tool."""

import argparse
import json
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


def format_text_diff(diff: Dict[str, Any]) -> str:
    """Format database diff as clean human-readable text."""
    lines = []
    if diff["added"]:
        lines.append("=== Added Tables ===")
        for item in diff["added"]:
            lines.append(f"  + {item['table']} ({item['row_count']} rows)")
        lines.append("")

    if diff["removed"]:
        lines.append("=== Removed Tables ===")
        for item in diff["removed"]:
            lines.append(f"  - {item['table']} ({item['row_count']} rows)")
        lines.append("")

    if diff["modified"]:
        lines.append("=== Modified Tables ===")
        for item in diff["modified"]:
            lines.append(f"  * Table: {item['table']}")
            if item["schema_changed"]:
                lines.append("    Schema changed!")
                lines.append(f"    Old: {item['sql_a']}")
                lines.append(f"    New: {item['sql_b']}")
            if item["row_count_delta"] != 0:
                sign = "+" if item["row_count_delta"] > 0 else ""
                lines.append(
                    f"    Rows: {item['row_count_a']} -> {item['row_count_b']} ({sign}{item['row_count_delta']})"
                )
            lines.append("")

    if not (diff["added"] or diff["removed"] or diff["modified"]):
        lines.append("Databases are identical.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Compare schemas and row counts of two SQLite databases.")
    parser.add_argument("db1", help="Path to first SQLite database")
    parser.add_argument("db2", help="Path to second SQLite database")
    parser.add_argument("--json", action="store_true", help="Output diff as JSON")

    args = parser.parse_args()

    try:
        db1_data = inspect_db(args.db1)
        db2_data = inspect_db(args.db2)
    except sqlite3.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        sys.exit(1)

    diff = diff_databases(db1_data, db2_data)

    if args.json:
        print(json.dumps(diff, indent=2))
    else:
        print(format_text_diff(diff))


if __name__ == "__main__":
    main()
