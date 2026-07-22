import os
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import mini_claude_code.task_system as task_module
from mini_claude_code.loop import agent_loop
from mini_claude_code.task_system import (
    can_start,
    claim_task,
    complete_task,
    create_task,
    get_task,
    list_tasks,
    run_claim_task,
    run_complete_task,
    run_create_task,
    run_get_task,
    run_list_tasks,
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


def tool_block(block_id: str, name: str, **input_args):
    return SimpleNamespace(type="tool_use", id=block_id, name=name, input=input_args)


class TaskSystemTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tasks_dir = Path(self.temp_dir.name)
        self.patches = [
            patch.object(task_module, "TASKS_DIR", self.tasks_dir),
            patch.object(task_module.time, "time", return_value=1234),
            patch.object(task_module.random, "randint", side_effect=range(42, 10_000)),
        ]
        for patcher in self.patches:
            patcher.start()

    def tearDown(self) -> None:
        for patcher in reversed(self.patches):
            patcher.stop()
        self.temp_dir.cleanup()


class TaskPersistenceTest(TaskSystemTestCase):
    def test_create_task_persists_json_file(self) -> None:
        task = create_task("setup schema", "Create database tables")

        self.assertEqual(task.id, "task_1234_0042")
        self.assertTrue((self.tasks_dir / "task_1234_0042.json").exists())
        self.assertIn("Create database tables", get_task(task.id))

    def test_list_tasks_reads_sorted_persistent_files(self) -> None:
        first = create_task("first")
        with patch.object(task_module.random, "randint", return_value=43):
            second = create_task("second")

        self.assertEqual([task.id for task in list_tasks()], [first.id, second.id])

    def test_claim_requires_completed_dependencies(self) -> None:
        schema = create_task("schema")
        api = create_task("api", blockedBy=[schema.id])

        self.assertFalse(can_start(api.id))
        self.assertEqual(claim_task(api.id), f"Blocked by: ['{schema.id}']")

        self.assertIn("Claimed", claim_task(schema.id))
        self.assertIn("Unblocked: api", complete_task(schema.id))
        self.assertTrue(can_start(api.id))
        self.assertIn("Claimed", claim_task(api.id))

    def test_missing_dependency_is_blocked_not_ignored(self) -> None:
        task = create_task("orphan", blockedBy=["missing"])

        self.assertFalse(can_start(task.id))
        self.assertEqual(claim_task(task.id), "Blocked by: ['missing']")

    def test_complete_requires_in_progress_status(self) -> None:
        task = create_task("schema")

        self.assertEqual(complete_task(task.id), f"Task {task.id} is pending, cannot complete")


class TaskToolTest(TaskSystemTestCase):
    def test_task_tools_are_registered(self) -> None:
        names = [tool["name"] for tool in TOOLS]

        for name in ["create_task", "list_tasks", "get_task", "claim_task", "complete_task"]:
            self.assertIn(name, names)

        self.assertIs(TOOL_HANDLERS["create_task"], run_create_task)
        self.assertIs(TOOL_HANDLERS["list_tasks"], run_list_tasks)
        self.assertIs(TOOL_HANDLERS["get_task"], run_get_task)
        self.assertIs(TOOL_HANDLERS["claim_task"], run_claim_task)
        self.assertIs(TOOL_HANDLERS["complete_task"], run_complete_task)

    def test_tool_wrappers_return_tutorial_strings(self) -> None:
        created = run_create_task("schema")
        task_id = created.split(":", 1)[0].removeprefix("Created ")

        self.assertIn("schema", run_list_tasks())
        self.assertIn('"subject": "schema"', run_get_task(task_id))
        self.assertIn("Claimed", run_claim_task(task_id))
        self.assertIn("Completed", run_complete_task(task_id))
        self.assertEqual(run_get_task("missing"), "Error: Task missing not found")


class AgentLoopTaskToolTest(TaskSystemTestCase):
    def test_agent_loop_dispatches_task_tools(self) -> None:
        create_call = tool_block("toolu_create", "create_task", subject="schema")
        final_block = text_block("done")
        client = FakeClient([
            SimpleNamespace(stop_reason="tool_use", content=[create_call]),
            SimpleNamespace(stop_reason="end_turn", content=[final_block]),
        ])
        messages = [{"role": "user", "content": "create a task"}]

        with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
            with patch("mini_claude_code.loop.extract_memories", return_value=0):
                with patch("mini_claude_code.loop.consolidate_memories", return_value=0):
                    agent_loop(messages, client=client)

        self.assertIn("Created task_1234_0042: schema", messages[2]["content"][0]["content"])
        self.assertEqual(messages[-1]["content"], [final_block])


if __name__ == "__main__":
    unittest.main()
