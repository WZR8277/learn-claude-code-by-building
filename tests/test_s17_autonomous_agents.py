import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import mini_claude_code.task_system as task_module
import mini_claude_code.team as team_module
from mini_claude_code.task_system import claim_task, create_task, load_task, scan_unclaimed_tasks
from mini_claude_code.team import reset_team_state, spawn_teammate_thread
from mini_claude_code.tool import TOOL_HANDLERS, TOOLS


class FakeMessages:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if not self._responses:
            raise RuntimeError("no more fake responses")
        return self._responses.pop(0)


class FakeClient:
    def __init__(self, responses):
        self.messages = FakeMessages(responses)


def text_block(text: str):
    return SimpleNamespace(type="text", text=text)


def tool_block(block_id: str, name: str, **input_args):
    return SimpleNamespace(type="tool_use", id=block_id, name=name, input=input_args)


class AutonomousAgentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tasks_dir = Path(self.temp_dir.name) / "tasks"
        self.mailbox_dir = Path(self.temp_dir.name) / "mailboxes"
        self.patches = [
            patch.object(task_module, "TASKS_DIR", self.tasks_dir),
            patch.object(task_module.time, "time", return_value=1234),
            patch.object(task_module.random, "randint", side_effect=range(42, 10_000)),
        ]
        for patcher in self.patches:
            patcher.start()
        reset_team_state(self.mailbox_dir)

    def tearDown(self) -> None:
        reset_team_state()
        for patcher in reversed(self.patches):
            patcher.stop()
        self.temp_dir.cleanup()

    def test_scan_unclaimed_tasks_ignores_owned_and_blocked_tasks(self) -> None:
        ready = create_task("ready")
        claimed = create_task("claimed")
        blocked_root = create_task("root")
        blocked = create_task("blocked", blockedBy=[blocked_root.id])
        claim_task(claimed.id, owner="alice")

        self.assertEqual([task.id for task in scan_unclaimed_tasks()], [ready.id, blocked_root.id])
        self.assertNotIn(blocked.id, [task.id for task in scan_unclaimed_tasks()])

    def test_teammate_auto_claims_task_during_idle_and_completes_it(self) -> None:
        task = create_task("write tests")
        client = FakeClient([
            SimpleNamespace(stop_reason="end_turn", content=[text_block("idle")]),
            SimpleNamespace(
                stop_reason="tool_use",
                content=[tool_block("toolu_complete", "complete_task", task_id=task.id)],
            ),
        ])

        result = spawn_teammate_thread(
            "alice",
            "backend developer",
            "look for work",
            {
                "bash": lambda command: "ok",
                "read_file": lambda path: "content",
                "write_file": lambda path, content: "written",
            },
            client=client,
            model="test-model",
            idle_poll_seconds=0.01,
            idle_timeout_seconds=0.05,
        )

        self.assertIn("(autonomous)", result)
        for _ in range(100):
            if load_task(task.id).status == "completed":
                break
            time.sleep(0.01)
        else:
            self.fail("autonomous teammate did not complete claimed task")

        completed = load_task(task.id)
        self.assertEqual(completed.owner, "alice")
        self.assertEqual(completed.status, "completed")
        tool_names = [tool["name"] for tool in client.messages.calls[1]["tools"]]
        self.assertIn("claim_task", tool_names)
        self.assertIn("complete_task", tool_names)

    def test_protocol_shutdown_still_works_during_idle(self) -> None:
        client = FakeClient([
            SimpleNamespace(stop_reason="end_turn", content=[text_block("idle")]),
        ])

        spawn_teammate_thread(
            "bob",
            "reviewer",
            "wait",
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
            "bob",
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
            self.fail("idle teammate did not respond to shutdown")

        self.assertIn("shutdown_response", [message["type"] for message in inbox])


class AutonomousToolRegistrationTest(unittest.TestCase):
    def test_lead_tool_count_stays_stable_and_teammate_autonomy_uses_existing_task_tools(self) -> None:
        names = [tool["name"] for tool in TOOLS]

        for name in ["list_tasks", "claim_task", "complete_task", "spawn_teammate"]:
            self.assertIn(name, names)
            self.assertIn(name, TOOL_HANDLERS)


if __name__ == "__main__":
    unittest.main()
