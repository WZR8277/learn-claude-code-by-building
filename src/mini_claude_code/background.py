"""Background task execution for slow tool calls."""

from __future__ import annotations

import threading
from typing import Any, Callable


ToolHandler = Callable[..., str]

_background_counter = 0
background_tasks: dict[str, dict[str, str]] = {}
background_results: dict[str, str] = {}
background_lock = threading.Lock()


def is_slow_operation(tool_name: str, tool_input: dict[str, Any]) -> bool:
    """Return whether a tool call looks slow enough to run in the background."""
    if tool_name != "bash":
        return False

    command = str(tool_input.get("command", "")).lower()
    slow_keywords = [
        "install",
        "build",
        "test",
        "deploy",
        "compile",
        "docker build",
        "pip install",
        "npm install",
        "cargo build",
        "pytest",
        "make",
    ]
    return any(keyword in command for keyword in slow_keywords)


def should_run_background(tool_name: str, tool_input: dict[str, Any]) -> bool:
    """Use the model's explicit request first, then fall back to a simple heuristic."""
    if tool_input.get("run_in_background"):
        return True
    return is_slow_operation(tool_name, tool_input)


def execute_tool(block: Any, handlers: dict[str, ToolHandler]) -> str:
    """Dispatch one tool block through the handler map used by the main loop."""
    handler = handlers.get(block.name)
    if not handler:
        return f"Unknown: {block.name}"
    return handler(**block.input)


def start_background_task(block: Any, handlers: dict[str, ToolHandler]) -> str:
    """Start a daemon thread for a tool call and return its background task id."""
    global _background_counter

    with background_lock:
        _background_counter += 1
        bg_id = f"bg_{_background_counter:04d}"
        # 原始 tool_use 只会收到一次占位 tool_result；后台完成后另发 task_notification。
        background_tasks[bg_id] = {
            "tool_use_id": block.id,
            "command": str(block.input.get("command", "")),
            "status": "running",
        }

    def worker() -> None:
        try:
            output = execute_tool(block, handlers)
        except Exception as exc:
            output = f"Error: {exc}"

        with background_lock:
            task = background_tasks.get(bg_id)
            if task is None:
                return
            task["status"] = "completed"
            background_results[bg_id] = output

    threading.Thread(target=worker, daemon=True).start()
    return bg_id


def collect_background_results() -> list[str]:
    """Collect completed background outputs as task_notification text blocks."""
    with background_lock:
        ready_ids = [
            bg_id
            for bg_id, task in background_tasks.items()
            if task["status"] == "completed"
        ]

    notifications = []
    for bg_id in ready_ids:
        with background_lock:
            task = background_tasks.pop(bg_id)
            output = background_results.pop(bg_id, "")

        # 这里不复用 tool_use_id，因为 Messages API 要求每个 tool_use 只配一个 tool_result。
        notifications.append(
            "<task_notification>\n"
            f"  <task_id>{bg_id}</task_id>\n"
            "  <status>completed</status>\n"
            f"  <command>{task['command']}</command>\n"
            f"  <summary>{output[:200]}</summary>\n"
            "</task_notification>"
        )

    return notifications


def reset_background_tasks() -> None:
    """Reset module state for isolated tests."""
    global _background_counter
    with background_lock:
        _background_counter = 0
        background_tasks.clear()
        background_results.clear()
