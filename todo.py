#!/usr/bin/env python3
"""Basic todo app with add/list/delete functionality."""

import json
import sys
from pathlib import Path

DATA_FILE = Path(__file__).parent / "todos.json"


def load_todos():
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open() as f:
        return json.load(f)


def save_todos(todos):
    with DATA_FILE.open("w") as f:
        json.dump(todos, f, indent=2)


def next_id(todos):
    return max((t["id"] for t in todos), default=0) + 1


def cmd_add(args):
    if not args:
        print("Usage: todo add <title>", file=sys.stderr)
        sys.exit(1)
    title = " ".join(args)
    todos = load_todos()
    todo = {"id": next_id(todos), "title": title}
    todos.append(todo)
    save_todos(todos)
    print(f"Added: [{todo['id']}] {todo['title']}")


def cmd_list(_args):
    todos = load_todos()
    if not todos:
        print("No todos.")
        return
    for t in todos:
        print(f"[{t['id']}] {t['title']}")


def cmd_delete(args):
    if not args:
        print("Usage: todo delete <id>", file=sys.stderr)
        sys.exit(1)
    try:
        target_id = int(args[0])
    except ValueError:
        print(f"Error: id must be an integer, got '{args[0]}'", file=sys.stderr)
        sys.exit(1)
    todos = load_todos()
    remaining = [t for t in todos if t["id"] != target_id]
    if len(remaining) == len(todos):
        print(f"Error: no todo with id {target_id}", file=sys.stderr)
        sys.exit(1)
    save_todos(remaining)
    print(f"Deleted todo {target_id}")


COMMANDS = {
    "add": cmd_add,
    "list": cmd_list,
    "delete": cmd_delete,
}


def main():
    args = sys.argv[1:]
    if not args or args[0] not in COMMANDS:
        print("Usage: todo <add|list|delete> [args]", file=sys.stderr)
        print("  add <title>   Add a new todo item")
        print("  list          List all todo items")
        print("  delete <id>   Delete a todo item by id")
        sys.exit(1)
    COMMANDS[args[0]](args[1:])


if __name__ == "__main__":
    main()
