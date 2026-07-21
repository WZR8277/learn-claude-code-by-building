"""Session-local TodoWrite tool introduced by s05."""

import ast
import json
from typing import Any


CURRENT_TODOS: list[dict[str, str]] = []
TODO_STATUSES = ("pending", "in_progress", "completed")


def normalize_todos(todos: Any) -> tuple[list[dict[str, str]] | None, str | None]:
    if isinstance(todos, str):
        try:
            todos = json.loads(todos)
        except json.JSONDecodeError:
            try:
                todos = ast.literal_eval(todos)
            except (SyntaxError, ValueError):
                return None, "Error: todos must be a list or JSON array string"

    if not isinstance(todos, list):
        return None, "Error: todos must be a list"

    for index, todo in enumerate(todos):
        if not isinstance(todo, dict):
            return None, f"Error: todos[{index}] must be an object"
        if "content" not in todo or "status" not in todo:
            return None, f"Error: todos[{index}] missing 'content' or 'status'"
        if todo["status"] not in TODO_STATUSES:
            return None, f"Error: todos[{index}] has invalid status '{todo['status']}'"

    return todos, None


def run_todo_write(todos: Any) -> str:
    """更新当前会话 TODO；它只组织注意力，不执行任务也不持久化。"""
    global CURRENT_TODOS
    normalized, error = normalize_todos(todos)
    if error:
        return error

    CURRENT_TODOS = normalized or []
    lines = ["\n\033[33m## Current Tasks\033[0m"]
    icons = {
        "pending": " ",
        "in_progress": "\033[36m>\033[0m",
        "completed": "\033[32m✓\033[0m",
    }
    for todo in CURRENT_TODOS:
        lines.append(f"  [{icons[todo['status']]}] {todo['content']}")
    print("\n".join(lines))
    return f"Updated {len(CURRENT_TODOS)} tasks"
