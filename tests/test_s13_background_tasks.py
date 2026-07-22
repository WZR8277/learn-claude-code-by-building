import os
import threading
import time
import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

import mini_claude_code.background as background_module
from mini_claude_code.background import (
    collect_background_results,
    reset_background_tasks,
    should_run_background,
    start_background_task,
)
from mini_claude_code.loop import agent_loop
from mini_claude_code.tool import TOOL_HANDLERS, TOOLS, run_bash


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


def text_block(text: str):
    return SimpleNamespace(type="text", text=text)


def tool_block(block_id: str, name: str, **input_args):
    return SimpleNamespace(type="tool_use", id=block_id, name=name, input=input_args)


class BackgroundTaskUnitTest(unittest.TestCase):
    def tearDown(self) -> None:
        reset_background_tasks()

    def test_bash_schema_allows_background_hint(self) -> None:
        bash_tool = next(tool for tool in TOOLS if tool["name"] == "bash")

        self.assertIn("run_in_background", bash_tool["input_schema"]["properties"])
        self.assertEqual(run_bash("printf ok", run_in_background=True), "ok")

    def test_background_decision_uses_explicit_hint_then_slow_heuristic(self) -> None:
        self.assertTrue(should_run_background("bash", {"command": "echo ok", "run_in_background": True}))
        self.assertTrue(should_run_background("bash", {"command": "npm install"}))
        self.assertTrue(should_run_background("bash", {"command": "pytest tests"}))
        self.assertFalse(should_run_background("read_file", {"path": "README.md"}))
        self.assertFalse(should_run_background("bash", {"command": "git status"}))

    def test_completed_background_result_is_collected_once_as_notification(self) -> None:
        block = tool_block("toolu_bg", "bash", command="build project", run_in_background=True)

        bg_id = start_background_task(block, {"bash": lambda **_: "build completed"})

        for _ in range(20):
            notifications = collect_background_results()
            if notifications:
                break
            time.sleep(0.01)
        else:
            self.fail("background task did not complete")

        self.assertEqual(bg_id, "bg_0001")
        self.assertEqual(collect_background_results(), [])
        self.assertIn("<task_notification>", notifications[0])
        self.assertIn("<task_id>bg_0001</task_id>", notifications[0])
        self.assertIn("<command>build project</command>", notifications[0])
        self.assertIn("<summary>build completed</summary>", notifications[0])


class AgentLoopBackgroundTest(unittest.TestCase):
    def tearDown(self) -> None:
        reset_background_tasks()

    def test_agent_loop_returns_placeholder_without_waiting_for_background_output(self) -> None:
        started = threading.Event()
        release = threading.Event()

        def slow_handler(command: str, run_in_background: bool = False) -> str:
            started.set()
            release.wait(1)
            return f"finished {command}"

        background_call = tool_block(
            "toolu_bg",
            "bash",
            command="npm install",
            run_in_background=True,
        )
        client = FakeClient([
            SimpleNamespace(stop_reason="tool_use", content=[background_call]),
            SimpleNamespace(stop_reason="end_turn", content=[text_block("continuing")]),
        ])
        messages = [{"role": "user", "content": "run install in background"}]

        with patch.dict(TOOL_HANDLERS, {"bash": slow_handler}, clear=True):
            with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
                with patch("mini_claude_code.loop.extract_memories", return_value=0):
                    with patch("mini_claude_code.loop.consolidate_memories", return_value=0):
                        agent_loop(messages, client=client)

        release.set()

        self.assertTrue(started.is_set())
        self.assertEqual(
            messages[2]["content"],
            [{
                "type": "tool_result",
                "tool_use_id": "toolu_bg",
                "content": (
                    "[Background task bg_0001 started] "
                    "Result will be available when complete."
                ),
            }],
        )

    def test_agent_loop_injects_ready_background_notification_with_tool_results(self) -> None:
        with background_module.background_lock:
            background_module.background_tasks["bg_0042"] = {
                "tool_use_id": "toolu_old",
                "command": "pytest",
                "status": "completed",
            }
            background_module.background_results["bg_0042"] = "tests passed"

        read_call = tool_block("toolu_read", "read_file", path="README.md")
        client = FakeClient([
            SimpleNamespace(stop_reason="tool_use", content=[read_call]),
            SimpleNamespace(stop_reason="end_turn", content=[text_block("done")]),
        ])
        messages = [{"role": "user", "content": "read while collecting notifications"}]

        with patch.dict(TOOL_HANDLERS, {"read_file": lambda path: "file content"}, clear=True):
            with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
                with patch("mini_claude_code.loop.extract_memories", return_value=0):
                    with patch("mini_claude_code.loop.consolidate_memories", return_value=0):
                        agent_loop(messages, client=client)

        user_content = messages[2]["content"]
        self.assertEqual(user_content[0]["type"], "text")
        self.assertIn("<task_id>bg_0042</task_id>", user_content[0]["text"])
        self.assertIn("<summary>tests passed</summary>", user_content[0]["text"])
        self.assertEqual(
            user_content[1],
            {"type": "tool_result", "tool_use_id": "toolu_read", "content": "file content"},
        )


if __name__ == "__main__":
    unittest.main()
