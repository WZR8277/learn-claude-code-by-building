import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from mini_claude_code.loop import agent_loop
from mini_claude_code.tool import TOOL_HANDLERS


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


class AgentLoopTest(unittest.TestCase):
    def test_tool_use_result_is_returned_with_matching_id(self) -> None:
        tool_block = SimpleNamespace(
            type="tool_use",
            id="toolu_123",
            name="bash",
            input={"command": "pwd"},
        )
        final_block = SimpleNamespace(type="text", text="done")
        client = FakeClient([
            SimpleNamespace(stop_reason="tool_use", content=[tool_block]),
            SimpleNamespace(stop_reason="end_turn", content=[final_block]),
        ])
        messages = [{"role": "user", "content": "where am I?"}]

        with patch.dict(TOOL_HANDLERS, {"bash": lambda command: f"ran {command}"}):
            with patch("mini_claude_code.loop.extract_memories", return_value=0):
                with patch("mini_claude_code.loop.consolidate_memories", return_value=0):
                    with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
                        agent_loop(messages, client=client)

        self.assertEqual(len(client.messages.calls), 2)
        self.assertEqual(messages[1]["role"], "assistant")
        self.assertEqual(messages[2], {
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": "toolu_123",
                "content": "ran pwd",
            }],
        })
        self.assertEqual(messages[3]["content"], [final_block])

    def test_loop_stops_when_model_does_not_request_tool(self) -> None:
        final_block = SimpleNamespace(type="text", text="answer")
        client = FakeClient([
            SimpleNamespace(stop_reason="end_turn", content=[final_block]),
        ])
        messages = [{"role": "user", "content": "hello"}]

        with patch("mini_claude_code.loop.extract_memories", return_value=0):
            with patch("mini_claude_code.loop.consolidate_memories", return_value=0):
                with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
                    agent_loop(messages, client=client)

        self.assertEqual(len(client.messages.calls), 1)
        self.assertEqual(messages[-1], {"role": "assistant", "content": [final_block]})


if __name__ == "__main__":
    unittest.main()
