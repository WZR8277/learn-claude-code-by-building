import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import mini_claude_code.tool as tool_module
from mini_claude_code.loop import agent_loop
from mini_claude_code.tool import TOOLS, TOOL_HANDLERS, run_edit, run_glob, run_read, run_write


class FakeMessages:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self._responses.pop(0)


class FakeClient:
    def __init__(self, responses):
        self.messages = FakeMessages(responses)


class ToolUseTest(unittest.TestCase):
    def test_s02_tools_have_matching_handlers(self) -> None:
        names = [
            "bash", "read_file", "write_file", "edit_file", "glob",
            "todo_write", "task", "load_skill", "compact",
            "create_task", "list_tasks", "get_task", "claim_task", "complete_task",
        ]
        handler_names = [
            "bash", "read_file", "write_file", "edit_file", "glob",
            "todo_write", "task", "load_skill",
            "create_task", "list_tasks", "get_task", "claim_task", "complete_task",
        ]

        self.assertEqual([tool["name"] for tool in TOOLS], names)
        self.assertEqual(list(TOOL_HANDLERS), handler_names)

    def test_file_tools_follow_the_tutorial_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as workspace:
            with patch.object(tool_module, "WORKDIR", Path(workspace).resolve()):
                self.assertEqual(
                    run_write("notes/lesson.txt", "alpha\nbeta\nbeta\n"),
                    "Wrote 16 bytes to notes/lesson.txt",
                )
                self.assertEqual(
                    run_edit("notes/lesson.txt", "beta", "gamma"),
                    "Edited notes/lesson.txt",
                )
                self.assertEqual(
                    run_read("notes/lesson.txt", limit=2),
                    "alpha\ngamma\n... (1 more lines)",
                )
                self.assertEqual(run_glob("*/*.txt"), "notes/lesson.txt")

    def test_safe_path_rejects_traversal_and_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            workspace = (base / "workspace").resolve()
            outside = (base / "outside").resolve()
            workspace.mkdir()
            outside.mkdir()
            (outside / "secret.txt").write_text("secret")

            with patch.object(tool_module, "WORKDIR", workspace):
                traversal = run_read("../outside/secret.txt")
                self.assertIn("Path escapes workspace", traversal)

                try:
                    (workspace / "link").symlink_to(outside, target_is_directory=True)
                except OSError as exc:
                    self.skipTest(f"symlinks unavailable: {exc}")

                symlink_write = run_write("link/new.txt", "blocked")
                self.assertIn("Path escapes workspace", symlink_write)
                self.assertFalse((outside / "new.txt").exists())


class AgentLoopDispatchTest(unittest.TestCase):
    def test_multiple_tool_calls_use_handler_map_in_original_order(self) -> None:
        calls = []
        handlers = {
            "first": lambda value: calls.append(("first", value)) or f"first:{value}",
            "second": lambda value: calls.append(("second", value)) or f"second:{value}",
        }
        tool_blocks = [
            SimpleNamespace(type="tool_use", id="toolu_1", name="first", input={"value": 1}),
            SimpleNamespace(type="tool_use", id="toolu_2", name="second", input={"value": 2}),
        ]
        final_block = SimpleNamespace(type="text", text="done")
        client = FakeClient([
            SimpleNamespace(stop_reason="tool_use", content=tool_blocks),
            SimpleNamespace(stop_reason="end_turn", content=[final_block]),
        ])
        messages = [{"role": "user", "content": "run both"}]

        with patch.dict(TOOL_HANDLERS, handlers, clear=True):
            with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
                agent_loop(messages, client=client)

        self.assertEqual(calls, [("first", 1), ("second", 2)])
        self.assertEqual(
            messages[2],
            {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": "toolu_1", "content": "first:1"},
                    {"type": "tool_result", "tool_use_id": "toolu_2", "content": "second:2"},
                ],
            },
        )

    def test_unknown_tool_is_returned_to_the_model(self) -> None:
        tool_block = SimpleNamespace(
            type="tool_use",
            id="toolu_unknown",
            name="missing",
            input={},
        )
        final_block = SimpleNamespace(type="text", text="done")
        client = FakeClient([
            SimpleNamespace(stop_reason="tool_use", content=[tool_block]),
            SimpleNamespace(stop_reason="end_turn", content=[final_block]),
        ])
        messages = [{"role": "user", "content": "use a missing tool"}]

        with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
            agent_loop(messages, client=client)

        self.assertEqual(
            messages[2]["content"],
            [{"type": "tool_result", "tool_use_id": "toolu_unknown", "content": "Unknown: missing"}],
        )


if __name__ == "__main__":
    unittest.main()
