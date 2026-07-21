import os
import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock, patch

import mini_claude_code.subagent as subagent_module
from mini_claude_code.hooks import HOOKS
from mini_claude_code.loop import agent_loop
from mini_claude_code.subagent import SUB_TOOLS, extract_text, spawn_subagent
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


class SubagentHookTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._original_hooks = {event: list(hooks) for event, hooks in HOOKS.items()}
        self._original_sub_handlers = dict(subagent_module.SUB_HANDLERS)

    def tearDown(self) -> None:
        for event, hooks in self._original_hooks.items():
            HOOKS[event] = hooks
        subagent_module.SUB_HANDLERS.clear()
        subagent_module.SUB_HANDLERS.update(self._original_sub_handlers)


class SubagentRegistrationTest(unittest.TestCase):
    def test_task_tool_is_registered_for_parent_only(self) -> None:
        self.assertIn("task", [tool["name"] for tool in TOOLS])
        self.assertIs(TOOL_HANDLERS["task"], spawn_subagent)
        self.assertEqual(
            [tool["name"] for tool in SUB_TOOLS],
            ["bash", "read_file", "write_file", "edit_file", "glob"],
        )


class SubagentLoopTest(SubagentHookTestCase):
    def test_spawn_subagent_uses_fresh_messages_and_returns_text_summary(self) -> None:
        final_block = SimpleNamespace(type="text", text="summary only")
        client = FakeClient([SimpleNamespace(stop_reason="end_turn", content=[final_block])])

        result = spawn_subagent("inspect the project", client=client, model="test-model")

        self.assertEqual(result, "summary only")
        self.assertEqual(
            client.messages.calls[0]["messages"],
            [{"role": "user", "content": "inspect the project"}],
        )

    def test_subagent_dispatches_basic_tools_and_continues_until_summary(self) -> None:
        tool_block = SimpleNamespace(
            type="tool_use",
            id="toolu_sub",
            name="bash",
            input={"command": "pwd"},
        )
        final_block = SimpleNamespace(type="text", text="pwd checked")
        client = FakeClient([
            SimpleNamespace(stop_reason="tool_use", content=[tool_block]),
            SimpleNamespace(stop_reason="end_turn", content=[final_block]),
        ])
        post_hook = Mock(return_value=None)
        HOOKS["PreToolUse"] = []
        HOOKS["PostToolUse"] = [post_hook]

        with patch.dict(subagent_module.SUB_HANDLERS, {"bash": lambda command: f"ran {command}"}, clear=True):
            result = spawn_subagent("run pwd", client=client, model="test-model")

        self.assertEqual(result, "pwd checked")
        self.assertEqual(
            client.messages.calls[1]["messages"][-1],
            {
                "role": "user",
                "content": [{"type": "tool_result", "tool_use_id": "toolu_sub", "content": "ran pwd"}],
            },
        )
        post_hook.assert_called_once_with(tool_block, "ran pwd")

    def test_subagent_pre_tool_hook_can_block_without_running_handler(self) -> None:
        tool_block = SimpleNamespace(
            type="tool_use",
            id="toolu_blocked",
            name="bash",
            input={"command": "rm -rf /"},
        )
        final_block = SimpleNamespace(type="text", text="blocked summary")
        client = FakeClient([
            SimpleNamespace(stop_reason="tool_use", content=[tool_block]),
            SimpleNamespace(stop_reason="end_turn", content=[final_block]),
        ])
        handler = Mock(return_value="should not run")
        HOOKS["PreToolUse"] = [lambda block: "Permission denied"]

        with patch.dict(subagent_module.SUB_HANDLERS, {"bash": handler}, clear=True):
            result = spawn_subagent("try dangerous command", client=client, model="test-model")

        self.assertEqual(result, "blocked summary")
        handler.assert_not_called()
        self.assertEqual(
            client.messages.calls[1]["messages"][-1]["content"],
            [{"type": "tool_result", "tool_use_id": "toolu_blocked", "content": "Permission denied"}],
        )

    def test_subagent_has_bounded_turns_and_fallback_summary(self) -> None:
        tool_block = SimpleNamespace(
            type="tool_use",
            id="toolu_loop",
            name="bash",
            input={"command": "pwd"},
        )
        client = FakeClient([
            SimpleNamespace(stop_reason="tool_use", content=[tool_block]),
            SimpleNamespace(stop_reason="tool_use", content=[tool_block]),
        ])
        HOOKS["PreToolUse"] = []
        HOOKS["PostToolUse"] = []

        with patch.dict(subagent_module.SUB_HANDLERS, {"bash": lambda command: "ran"}, clear=True):
            result = spawn_subagent("loop forever", client=client, model="test-model", max_turns=2)

        self.assertEqual(result, "Subagent stopped after 30 turns without final answer.")
        self.assertEqual(len(client.messages.calls), 2)

    def test_extract_text_ignores_non_text_blocks(self) -> None:
        self.assertEqual(
            extract_text([
                SimpleNamespace(type="text", text="alpha"),
                SimpleNamespace(type="tool_use", text="ignored"),
                SimpleNamespace(type="text", text="beta"),
            ]),
            "alpha\nbeta",
        )


class ParentLoopTaskTest(unittest.TestCase):
    def test_parent_receives_task_summary_as_single_tool_result(self) -> None:
        task_block = SimpleNamespace(
            type="tool_use",
            id="toolu_task",
            name="task",
            input={"description": "summarize files"},
        )
        final_block = SimpleNamespace(type="text", text="done")
        client = FakeClient([
            SimpleNamespace(stop_reason="tool_use", content=[task_block]),
            SimpleNamespace(stop_reason="end_turn", content=[final_block]),
        ])
        messages = [{"role": "user", "content": "delegate this"}]

        with patch.dict(TOOL_HANDLERS, {"task": lambda description: "subagent summary"}, clear=True):
            with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
                agent_loop(messages, client=client)

        self.assertEqual(
            messages[2],
            {
                "role": "user",
                "content": [{"type": "tool_result", "tool_use_id": "toolu_task", "content": "subagent summary"}],
            },
        )


if __name__ == "__main__":
    unittest.main()
