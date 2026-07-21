import os
import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

import mini_claude_code.todo as todo_module
from mini_claude_code.loop import agent_loop
from mini_claude_code.todo import normalize_todos, run_todo_write
from mini_claude_code.tool import TOOL_HANDLERS, TOOLS


class FakeMessages:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(deepcopy(kwargs))
        return self._responses.pop(0)


class FakeClient:
    def __init__(self, responses):
        self.messages = FakeMessages(responses)


class TodoWriteToolTest(unittest.TestCase):
    def setUp(self) -> None:
        todo_module.CURRENT_TODOS = []

    def test_todo_write_is_registered_as_s05_tool(self) -> None:
        self.assertIn("todo_write", [tool["name"] for tool in TOOLS])
        self.assertIs(TOOL_HANDLERS["todo_write"], run_todo_write)

    def test_todo_write_updates_session_local_tasks(self) -> None:
        output = run_todo_write([
            {"content": "读 s05", "status": "completed"},
            {"content": "实现 TodoWrite", "status": "in_progress"},
        ])

        self.assertEqual(output, "Updated 2 tasks")
        self.assertEqual(
            todo_module.CURRENT_TODOS,
            [
                {"content": "读 s05", "status": "completed"},
                {"content": "实现 TodoWrite", "status": "in_progress"},
            ],
        )

    def test_todo_write_accepts_json_array_string(self) -> None:
        output = run_todo_write('[{"content": "plan", "status": "pending"}]')

        self.assertEqual(output, "Updated 1 tasks")
        self.assertEqual(todo_module.CURRENT_TODOS[0]["content"], "plan")

    def test_todo_validation_matches_tutorial_errors(self) -> None:
        self.assertEqual(
            normalize_todos("not json"),
            (None, "Error: todos must be a list or JSON array string"),
        )
        self.assertEqual(normalize_todos({"content": "x"}), (None, "Error: todos must be a list"))
        self.assertEqual(
            normalize_todos([{"content": "x", "status": "blocked"}]),
            (None, "Error: todos[0] has invalid status 'blocked'"),
        )


class AgentLoopTodoWriteTest(unittest.TestCase):
    def test_todo_write_resets_reminder_counter_and_returns_tool_result(self) -> None:
        todo_block = SimpleNamespace(
            type="tool_use",
            id="toolu_todo",
            name="todo_write",
            input={"todos": [{"content": "plan", "status": "in_progress"}]},
        )
        final_block = SimpleNamespace(type="text", text="done")
        client = FakeClient([
            SimpleNamespace(stop_reason="tool_use", content=[todo_block]),
            SimpleNamespace(stop_reason="end_turn", content=[final_block]),
        ])
        messages = [{"role": "user", "content": "start"}]

        with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
            agent_loop(messages, client=client)

        self.assertEqual(
            messages[2]["content"],
            [{"type": "tool_result", "tool_use_id": "toolu_todo", "content": "Updated 1 tasks"}],
        )

    def test_reminder_is_injected_after_three_tool_rounds_without_todo_update(self) -> None:
        tool_rounds = []
        for index in range(4):
            tool_rounds.extend([
                SimpleNamespace(
                    stop_reason="tool_use",
                    content=[
                        SimpleNamespace(
                            type="tool_use",
                            id=f"toolu_{index}",
                            name="bash",
                            input={"command": "pwd"},
                        )
                    ],
                ),
            ])
        tool_rounds.append(SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text="done")]))

        client = FakeClient(tool_rounds)
        messages = [{"role": "user", "content": "work without todo"}]

        with patch.dict(TOOL_HANDLERS, {"bash": lambda command: "ran"}, clear=True):
            with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
                agent_loop(messages, client=client)

        call_messages = client.messages.calls[3]["messages"]
        self.assertEqual(call_messages[-1], {"role": "user", "content": "<reminder>Update your todos.</reminder>"})


if __name__ == "__main__":
    unittest.main()
