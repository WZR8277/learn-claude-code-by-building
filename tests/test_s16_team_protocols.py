import os
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import mini_claude_code.team as team_module
from mini_claude_code.loop import agent_loop
from mini_claude_code.team import (
    MessageBus,
    ProtocolState,
    consume_lead_inbox,
    match_response,
    pending_requests,
    reset_team_state,
    run_request_shutdown,
    run_review_plan,
    spawn_teammate_thread,
)
from mini_claude_code.tool import TOOL_HANDLERS, TOOLS


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


def text_block(text: str):
    return SimpleNamespace(type="text", text=text)


def tool_block(block_id: str, tool_name: str, **input_args):
    return SimpleNamespace(type="tool_use", id=block_id, name=tool_name, input=input_args)


class TeamProtocolTest(unittest.TestCase):
    def tearDown(self) -> None:
        reset_team_state()

    def test_message_bus_persists_protocol_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bus = MessageBus(Path(temp_dir))

            bus.send(
                "lead",
                "alice",
                "Please shut down",
                "shutdown_request",
                {"request_id": "req_1"},
            )

            messages = bus.read_inbox("alice")
            self.assertEqual(messages[0]["type"], "shutdown_request")
            self.assertEqual(messages[0]["metadata"], {"request_id": "req_1"})

    def test_match_response_updates_only_matching_protocol_type(self) -> None:
        pending_requests["req_plan"] = ProtocolState(
            request_id="req_plan",
            type="plan_approval",
            sender="alice",
            target="lead",
            status="pending",
            payload="refactor auth",
        )

        mismatch = match_response("shutdown_response", "req_plan", approve=True)
        self.assertIn("Type mismatch", mismatch)
        self.assertEqual(pending_requests["req_plan"].status, "pending")

        matched = match_response("plan_approval_response", "req_plan", approve=True)
        self.assertEqual(matched, "plan_approval approved (req_plan)")
        self.assertEqual(pending_requests["req_plan"].status, "approved")

    def test_consume_lead_inbox_routes_protocol_responses_before_returning_messages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            reset_team_state(Path(temp_dir))
            pending_requests["req_shutdown"] = ProtocolState(
                request_id="req_shutdown",
                type="shutdown",
                sender="lead",
                target="alice",
                status="pending",
                payload="",
            )
            team_module.BUS.send(
                "alice",
                "lead",
                "Shutting down gracefully.",
                "shutdown_response",
                {"request_id": "req_shutdown", "approve": True},
            )

            messages = consume_lead_inbox(route_protocol=True)

            self.assertEqual(messages[0]["type"], "shutdown_response")
            self.assertEqual(pending_requests["req_shutdown"].status, "approved")

    def test_request_shutdown_sends_protocol_message_to_teammate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            reset_team_state(Path(temp_dir))
            with patch.object(team_module.random, "randint", return_value=42):
                result = run_request_shutdown("alice")

            self.assertEqual(result, "Shutdown request sent to alice (req: req_000042)")
            self.assertEqual(pending_requests["req_000042"].type, "shutdown")
            inbox = team_module.BUS.read_inbox("alice")
            self.assertEqual(inbox[0]["type"], "shutdown_request")
            self.assertEqual(inbox[0]["metadata"]["request_id"], "req_000042")

    def test_review_plan_updates_state_and_sends_response_to_teammate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            reset_team_state(Path(temp_dir))
            pending_requests["req_plan"] = ProtocolState(
                request_id="req_plan",
                type="plan_approval",
                sender="bob",
                target="lead",
                status="pending",
                payload="refactor auth",
            )

            result = run_review_plan("req_plan", approve=False, feedback="Too broad")

            self.assertEqual(result, "Plan rejected (req_plan)")
            self.assertEqual(pending_requests["req_plan"].status, "rejected")
            inbox = team_module.BUS.read_inbox("bob")
            self.assertEqual(inbox[0]["type"], "plan_approval_response")
            self.assertEqual(inbox[0]["metadata"], {"request_id": "req_plan", "approve": False})

    def test_idle_teammate_handles_shutdown_request_and_exits(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            reset_team_state(Path(temp_dir))
            client = FakeClient([
                SimpleNamespace(stop_reason="end_turn", content=[text_block("idle now")]),
            ])

            spawn_teammate_thread(
                "alice",
                "backend developer",
                "wait for protocol",
                {
                    "bash": lambda command: "ok",
                    "read_file": lambda path: "content",
                    "write_file": lambda path, content: "written",
                },
                client=client,
                model="test-model",
                idle_poll_seconds=0.01,
                idle_timeout_seconds=1,
            )
            team_module.BUS.send(
                "lead",
                "alice",
                "Please stop",
                "shutdown_request",
                {"request_id": "req_shutdown"},
            )

            for _ in range(100):
                inbox = team_module.BUS.read_inbox("lead")
                if inbox:
                    break
                time.sleep(0.01)
            else:
                self.fail("teammate did not answer shutdown request")

            self.assertIn("shutdown_response", [message["type"] for message in inbox])


class AgentLoopProtocolToolTest(unittest.TestCase):
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

    def test_protocol_tools_are_registered(self) -> None:
        names = [tool["name"] for tool in TOOLS]
        for name in ["request_shutdown", "request_plan", "review_plan"]:
            self.assertIn(name, names)
            self.assertIn(name, TOOL_HANDLERS)

    def test_agent_loop_dispatches_request_shutdown_tool(self) -> None:
        shutdown_call = tool_block("toolu_shutdown", "request_shutdown", teammate="alice")
        client = FakeClient([
            SimpleNamespace(stop_reason="tool_use", content=[shutdown_call]),
            SimpleNamespace(stop_reason="end_turn", content=[text_block("requested")]),
        ])
        messages = [{"role": "user", "content": "ask alice to stop"}]

        with tempfile.TemporaryDirectory() as temp_dir:
            reset_team_state(Path(temp_dir))
            with patch.object(team_module.random, "randint", return_value=7):
                with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
                    agent_loop(messages, client=client)

        self.assertEqual(
            messages[2]["content"],
            [{
                "type": "tool_result",
                "tool_use_id": "toolu_shutdown",
                "content": "Shutdown request sent to alice (req: req_000007)",
            }],
        )


if __name__ == "__main__":
    unittest.main()
