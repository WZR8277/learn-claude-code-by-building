import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import mini_claude_code.permission as permission_module
from mini_claude_code.loop import agent_loop
from mini_claude_code.permission import ask_user, check_deny_list, check_rules
from mini_claude_code.tool import TOOL_HANDLERS


class FakeMessages:
    def __init__(self, responses):
        self._responses = list(responses)

    def create(self, **kwargs):
        return self._responses.pop(0)


class FakeClient:
    def __init__(self, responses):
        self.messages = FakeMessages(responses)


def run_tool_blocks(blocks):
    final_block = SimpleNamespace(type="text", text="done")
    client = FakeClient([
        SimpleNamespace(stop_reason="tool_use", content=blocks),
        SimpleNamespace(stop_reason="end_turn", content=[final_block]),
    ])
    messages = [{"role": "user", "content": "run tools"}]
    with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
        agent_loop(messages, client=client)
    return messages


class PermissionRuleTest(unittest.TestCase):
    def test_hard_deny_and_rule_matching_follow_tutorial_order(self) -> None:
        self.assertIn("rm -rf /", check_deny_list("rm -rf /"))
        self.assertEqual(
            check_rules("bash", {"command": "rm build.log"}),
            "Potentially destructive command",
        )
        self.assertIsNone(check_rules("read_file", {"path": "notes.txt"}))

    def test_user_approval_only_accepts_explicit_yes(self) -> None:
        with patch("builtins.input", side_effect=["yes", "no"]):
            self.assertEqual(ask_user("bash", {"command": "rm a"}, "reason"), "allow")
            self.assertEqual(ask_user("bash", {"command": "rm b"}, "reason"), "deny")


class AgentLoopPermissionTest(unittest.TestCase):
    def test_hard_deny_neither_asks_nor_executes(self) -> None:
        block = SimpleNamespace(
            type="tool_use",
            id="toolu_deny",
            name="bash",
            input={"command": "sudo reboot"},
        )

        with patch.object(permission_module, "ask_user") as ask_mock:
            with patch.dict(TOOL_HANDLERS, {"bash": Mock()}, clear=True):
                handler = TOOL_HANDLERS["bash"]
                messages = run_tool_blocks([block])

        ask_mock.assert_not_called()
        handler.assert_not_called()
        self.assertEqual(
            messages[2]["content"],
            [{
                "type": "tool_result",
                "tool_use_id": "toolu_deny",
                "content": "Permission denied.",
            }],
        )

    def test_each_ask_decision_controls_only_its_current_call(self) -> None:
        blocks = [
            SimpleNamespace(
                type="tool_use",
                id="toolu_allow",
                name="bash",
                input={"command": "rm first.txt"},
            ),
            SimpleNamespace(
                type="tool_use",
                id="toolu_reject",
                name="bash",
                input={"command": "rm second.txt"},
            ),
        ]
        handler = Mock(side_effect=lambda command: f"ran {command}")

        with patch.object(permission_module, "ask_user", side_effect=["allow", "deny"]):
            with patch.dict(TOOL_HANDLERS, {"bash": handler}, clear=True):
                messages = run_tool_blocks(blocks)

        handler.assert_called_once_with(command="rm first.txt")
        self.assertEqual(
            messages[2]["content"],
            [
                {
                    "type": "tool_result",
                    "tool_use_id": "toolu_allow",
                    "content": "ran rm first.txt",
                },
                {
                    "type": "tool_result",
                    "tool_use_id": "toolu_reject",
                    "content": "Permission denied.",
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
