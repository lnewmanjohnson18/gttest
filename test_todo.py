#!/usr/bin/env python3
"""Tests for the todo app."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


# Import the module for unit-testing internals
import importlib.util

spec = importlib.util.spec_from_file_location("todo", Path(__file__).parent / "todo.py")
todo_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(todo_mod)


class TodoIntegrationTests(unittest.TestCase):
    """Integration tests using a temporary data file."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.data_path = Path(self.tmp.name)
        # Patch the DATA_FILE used by all functions
        self.patcher = patch.object(todo_mod, "DATA_FILE", self.data_path)
        self.patcher.start()
        # Remove the file so load_todos sees an absent file
        self.data_path.unlink()

    def tearDown(self):
        self.patcher.stop()
        self.data_path.unlink(missing_ok=True)

    def test_list_empty(self):
        with patch("builtins.print") as mock_print:
            todo_mod.cmd_list([])
        mock_print.assert_called_once_with("No todos.")

    def test_add_and_list(self):
        todo_mod.cmd_add(["Buy", "milk"])
        todo_mod.cmd_add(["Walk", "the", "dog"])
        todos = todo_mod.load_todos()
        self.assertEqual(len(todos), 2)
        self.assertEqual(todos[0]["title"], "Buy milk")
        self.assertEqual(todos[1]["title"], "Walk the dog")
        self.assertEqual(todos[0]["id"], 1)
        self.assertEqual(todos[1]["id"], 2)

    def test_delete(self):
        todo_mod.cmd_add(["First"])
        todo_mod.cmd_add(["Second"])
        todo_mod.cmd_delete(["1"])
        todos = todo_mod.load_todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]["title"], "Second")

    def test_delete_nonexistent(self):
        todo_mod.cmd_add(["Only"])
        with self.assertRaises(SystemExit):
            todo_mod.cmd_delete(["99"])

    def test_add_no_title(self):
        with self.assertRaises(SystemExit):
            todo_mod.cmd_add([])

    def test_delete_invalid_id(self):
        with self.assertRaises(SystemExit):
            todo_mod.cmd_delete(["abc"])

    def test_ids_increment_after_delete(self):
        todo_mod.cmd_add(["First"])
        todo_mod.cmd_add(["Second"])
        todo_mod.cmd_delete(["1"])
        todo_mod.cmd_add(["Third"])
        todos = todo_mod.load_todos()
        ids = [t["id"] for t in todos]
        # ids should be unique and increasing
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, sorted(ids))

    def test_unknown_command_exits(self):
        with patch.object(sys, "argv", ["todo", "unknown"]):
            with self.assertRaises(SystemExit):
                todo_mod.main()

    def test_special_characters_in_title(self):
        special_titles = [
            "Buy milk & eggs",
            "Fix bug: null pointer (urgent!)",
            'Say "hello world"',
            "Path: C:\\Users\\test",
            "Emoji 🎉 party",
            "Tab\there",
            "Newline\nin title",
            "<script>alert('xss')</script>",
            "100% done",
            "Price: $9.99 / item",
        ]
        for title in special_titles:
            todo_mod.cmd_add(title.split(" ") if " " in title else [title])

        todos = todo_mod.load_todos()
        self.assertEqual(len(todos), len(special_titles))
        for i, expected in enumerate(special_titles):
            stored = todos[i]["title"]
            # titles passed as word-split args are rejoined with spaces
            self.assertEqual(stored, " ".join(expected.split(" ")))

    def test_add_ten_and_delete_all(self):
        for i in range(1, 11):
            todo_mod.cmd_add([f"Todo number {i}"])

        todos = todo_mod.load_todos()
        self.assertEqual(len(todos), 10)

        ids = [t["id"] for t in todos]
        for tid in ids:
            todo_mod.cmd_delete([str(tid)])

        todos = todo_mod.load_todos()
        self.assertEqual(todos, [])


if __name__ == "__main__":
    unittest.main()
