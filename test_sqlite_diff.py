import os
import sqlite3
import tempfile
import unittest
from sqlite_diff import inspect_db, diff_databases, format_text_diff


class TestSqliteDiff(unittest.TestCase):
    def setUp(self):
        self.db1_fd, self.db1_path = tempfile.mkstemp(suffix=".db")
        self.db2_fd, self.db2_path = tempfile.mkstemp(suffix=".db")

        # Populate DB 1
        conn1 = sqlite3.connect(self.db1_path)
        conn1.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        conn1.execute("INSERT INTO users VALUES (1, 'Alice')")
        conn1.execute("CREATE TABLE legacy (id INTEGER)")
        conn1.commit()
        conn1.close()

        # Populate DB 2
        conn2 = sqlite3.connect(self.db2_path)
        conn2.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
        conn2.execute("INSERT INTO users VALUES (1, 'Alice', 'a@example.com'), (2, 'Bob', 'b@example.com')")
        conn2.execute("CREATE TABLE new_table (id INTEGER)")
        conn2.commit()
        conn2.close()

    def tearDown(self):
        os.close(self.db1_fd)
        os.close(self.db2_fd)
        os.unlink(self.db1_path)
        os.unlink(self.db2_path)

    def test_inspect_db(self):
        d1 = inspect_db(self.db1_path)
        self.assertIn("users", d1["tables"])
        self.assertEqual(d1["tables"]["users"]["row_count"], 1)

    def test_diff_databases(self):
        d1 = inspect_db(self.db1_path)
        d2 = inspect_db(self.db2_path)
        diff = diff_databases(d1, d2)

        added_names = [x["table"] for x in diff["added"]]
        removed_names = [x["table"] for x in diff["removed"]]
        modified_names = [x["table"] for x in diff["modified"]]

        self.assertIn("new_table", added_names)
        self.assertIn("legacy", removed_names)
        self.assertIn("users", modified_names)

    def test_format_text_diff(self):
        d1 = inspect_db(self.db1_path)
        d2 = inspect_db(self.db2_path)
        diff = diff_databases(d1, d2)
        formatted = format_text_diff(diff)
        self.assertIn("=== Added Tables ===", formatted)
        self.assertIn("=== Removed Tables ===", formatted)
        self.assertIn("=== Modified Tables ===", formatted)


if __name__ == "__main__":
    unittest.main()
