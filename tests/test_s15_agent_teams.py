import os
import tempfile
import time
import unittest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import mini_claude_code.team as team_module
from mini_claude_code.loop import agent_loop
from mini_claude_code.team import (
    MessageBus,
    active_teammates,
    format_lead_inbox_messages,
    reset_team_state,
    spawn_teammate_thread,
)
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


def text_block(text: str):
    return SimpleNamespace(type="text", text=text)


def tool_block(block_id: str, tool_name: str, **input_args):
    return SimpleNamespace(type="tool_use", id=block_id, name=tool_name, input=input_args)


class MessageBusTest(unittest.TestCase):
    def test_send_appends_jsonl_and_read_consumes_inbox(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bus = MessageBus(Path(temp_dir))

            bus.send("alice", "lead", "schema ready", "result")
            bus.send("bob", "lead", "tests ready")

            messages = bus.read_inbox("lead")

            self.assertEqual([item["from"] for item in messages], ["alice", "bob"])
            self.assertEqual(messages[0]["to"], "lead")
            self.assertEqual(messages[0]["type"], "result")
            self.assertEqual(bus.read_inbox("lead"), [])

    def test_format_lead_inbox_messages_creates_injectable_user_text(self) -> None:
        text = format_lead_inbox_messages([
            {"from": "alice", "content": "schema ready"},
            {"from": "bob", "content": "client ready"},
        ])

        self.assertIn("[Inbox]", text)
        self.assertIn("From alice: schema ready", text)
        self.assertIn("From bob: client ready", text)


class TeammateThreadTest(unittest.TestCase):
    def tearDown(self) -> None:
        reset_team_state()

    def test_teammate_runs_own_loop_and_sends_final_result_to_lead(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            reset_team_state(Path(temp_dir))
            client = FakeClient([
                SimpleNamespace(
                    stop_reason="end_turn",
                    content=[text_block("schema.sql has been created")],
                ),
            ])

            result = spawn_teammate_thread(
                "alice",
                "backend developer",
                "create schema",
                {
                    "bash": lambda command: "ok",
                    "read_file": lambda path: "content",
                    "write_file": lambda path, content: "written",
                },
                client=client,
                model="test-model",
            )

            self.assertEqual(result, "Teammate 'alice' spawned as backend developer")
            for _ in range(100):
                inbox = team_module.BUS.read_inbox("lead")
                if inbox:
                    break
                time.sleep(0.01)
            else:
                self.fail("teammate did not send a lead result")

            self.assertEqual(inbox[0]["from"], "alice")
            self.assertEqual(inbox[0]["type"], "result")
            self.assertIn("schema.sql", inbox[0]["content"])
            self.assertNotIn("alice", active_teammates)
            self.assertEqual(client.messages.calls[0]["tools"][-1]["name"], "send_message")


class AgentTeamToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.patches = [
            patch("mini_claude_code.loop.extract_memories", return_value=0),
            patch("mini_claude_code.loop.consolidate_memories", return_value=0),
        ]
        for item in self.patches:
            item.start()

    def tearDown(self) -> None:
        for item in reversed(self.patches):
            item.stop()
        reset_team_state()

    def test_team_tools_are_registered(self) -> None:
        names = [tool["name"] for tool in TOOLS]

        for name in ["spawn_teammate", "send_message", "check_inbox"]:
            self.assertIn(name, names)
            self.assertIn(name, TOOL_HANDLERS)

    def test_agent_loop_dispatches_spawn_teammate_tool(self) -> None:
        spawn_call = tool_block(
            "toolu_spawn",
            "spawn_teammate",
            name="alice",
            role="backend developer",
            prompt="create schema",
        )
        client = FakeClient([
            SimpleNamespace(stop_reason="tool_use", content=[spawn_call]),
            SimpleNamespace(stop_reason="end_turn", content=[text_block("delegated")]),
        ])
        messages = [{"role": "user", "content": "ask alice to help"}]

        with patch("mini_claude_code.tool.spawn_teammate_thread", return_value="spawned"):
            with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
                agent_loop(messages, client=client)

        self.assertEqual(
            messages[2]["content"],
            [{"type": "tool_result", "tool_use_id": "toolu_spawn", "content": "spawned"}],
        )


if __name__ == "__main__":
    unittest.main()
