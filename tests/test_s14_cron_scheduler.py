import os
import tempfile
import unittest
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import mini_claude_code.cron_scheduler as cron_module
from mini_claude_code.cron_scheduler import (
    cancel_job,
    consume_cron_queue,
    cron_matches,
    fire_due_jobs,
    reset_cron_state,
    run_cancel_cron,
    run_list_crons,
    run_schedule_cron,
    schedule_job,
    validate_cron,
)
from mini_claude_code.loop import agent_loop
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


class CronSchedulerTest(unittest.TestCase):
    def setUp(self) -> None:
        reset_background_patch = patch("mini_claude_code.loop.extract_memories", return_value=0)
        consolidate_patch = patch("mini_claude_code.loop.consolidate_memories", return_value=0)
        self.patches = [reset_background_patch, consolidate_patch]
        for item in self.patches:
            item.start()

    def tearDown(self) -> None:
        for item in reversed(self.patches):
            item.stop()
        reset_cron_state()

    def test_cron_matches_basic_steps_ranges_lists_and_dom_dow_or(self) -> None:
        monday = datetime(2026, 7, 20, 9, 10)

        self.assertTrue(cron_matches("*/5 9 * * *", monday))
        self.assertTrue(cron_matches("10 8-10 * * *", monday))
        self.assertTrue(cron_matches("10 1,9,17 * * *", monday))
        self.assertFalse(cron_matches("*/15 9 * * *", monday))

        # day-of-month=21 不匹配，但 day-of-week=1(周一) 匹配，所以按 cron OR 语义触发。
        self.assertTrue(cron_matches("10 9 21 * 1", monday))

    def test_validate_cron_reports_invalid_fields(self) -> None:
        self.assertIsNone(validate_cron("0 9 * * 1-5"))
        self.assertEqual(validate_cron("* * *"), "Expected 5 fields, got 3")
        self.assertIn("minute", validate_cron("60 * * * *"))
        self.assertIn("Step must be > 0", validate_cron("*/0 * * * *"))

    def test_schedule_list_cancel_and_durable_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / ".scheduled_tasks.json"
            with patch.object(cron_module, "DURABLE_PATH", path):
                with patch.object(cron_module.random, "randint", return_value=42):
                    job = schedule_job("0 9 * * *", "run tests", durable=True)

                self.assertEqual(job.id, "cron_000042")
                self.assertIn("cron_000042", run_list_crons())
                self.assertTrue(path.exists())
                self.assertIn("run tests", path.read_text())
                self.assertEqual(cancel_job("cron_000042"), "Cancelled cron_000042")
                self.assertEqual(run_list_crons(), "No cron jobs. Use schedule_cron to add one.")

    def test_fire_due_jobs_enqueues_once_per_minute_and_removes_one_shot(self) -> None:
        with patch.object(cron_module.random, "randint", return_value=7):
            job = schedule_job("* * * * *", "one shot", recurring=False, durable=False)

        now = datetime(2026, 7, 20, 9, 10)

        self.assertEqual(fire_due_jobs(now), [job])
        self.assertEqual(fire_due_jobs(now), [])
        self.assertEqual(consume_cron_queue(), [job])
        self.assertNotIn(job.id, cron_module.scheduled_jobs)

    def test_recurring_job_can_fire_again_on_the_next_day_same_minute(self) -> None:
        with patch.object(cron_module.random, "randint", return_value=11):
            job = schedule_job("10 9 * * *", "daily check", recurring=True, durable=False)

        first_day = datetime(2026, 7, 20, 9, 10)
        second_day = datetime(2026, 7, 21, 9, 10)

        self.assertEqual(fire_due_jobs(first_day), [job])
        self.assertEqual(fire_due_jobs(first_day), [])
        self.assertEqual(fire_due_jobs(second_day), [job])
        self.assertEqual(consume_cron_queue(), [job, job])

    def test_queue_processor_skips_delivery_when_agent_is_busy(self) -> None:
        with patch.object(cron_module.random, "randint", return_value=13):
            schedule_job("* * * * *", "busy check", recurring=True, durable=False)
        fire_due_jobs(datetime(2026, 7, 20, 9, 10))

        self.assertTrue(cron_module.agent_lock.acquire(blocking=False))
        try:
            self.assertFalse(cron_module._try_acquire_agent_for_cron())
        finally:
            cron_module.agent_lock.release()

        delivered = []
        self.assertTrue(cron_module._try_acquire_agent_for_cron())
        try:
            cron_module._deliver_cron_if_still_needed(lambda: delivered.append("ran"))
        finally:
            cron_module.agent_lock.release()

        self.assertEqual(delivered, ["ran"])

    def test_cron_tools_are_registered_and_dispatchable(self) -> None:
        names = [tool["name"] for tool in TOOLS]

        for name in ["schedule_cron", "list_crons", "cancel_cron"]:
            self.assertIn(name, names)

        self.assertIs(TOOL_HANDLERS["schedule_cron"], run_schedule_cron)
        self.assertIs(TOOL_HANDLERS["list_crons"], run_list_crons)
        self.assertIs(TOOL_HANDLERS["cancel_cron"], run_cancel_cron)

        with patch.object(cron_module.random, "randint", return_value=8):
            scheduled = run_schedule_cron("0 9 * * *", "daily check", durable=False)
        self.assertIn("Scheduled cron_000008", scheduled)
        self.assertIn("daily check", run_list_crons())
        self.assertEqual(run_cancel_cron("cron_000008"), "Cancelled cron_000008")

    def test_agent_loop_consumes_scheduled_jobs_before_model_call(self) -> None:
        with patch.object(cron_module.random, "randint", return_value=99):
            job = schedule_job("* * * * *", "check build", recurring=True, durable=False)
        fire_due_jobs(datetime(2026, 7, 20, 9, 10))

        client = FakeClient([
            SimpleNamespace(stop_reason="end_turn", content=[text_block("scheduled handled")]),
        ])
        messages = []

        with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
            agent_loop(messages, client=client)

        self.assertEqual(messages[0], {"role": "user", "content": "[Scheduled] check build"})
        self.assertEqual(client.messages.calls[0]["messages"][0]["content"], "[Scheduled] check build")
        self.assertEqual(consume_cron_queue(), [])

    def test_agent_loop_dispatches_schedule_cron_tool(self) -> None:
        schedule_call = tool_block(
            "toolu_cron",
            "schedule_cron",
            cron="0 9 * * *",
            prompt="daily check",
            durable=False,
        )
        client = FakeClient([
            SimpleNamespace(stop_reason="tool_use", content=[schedule_call]),
            SimpleNamespace(stop_reason="end_turn", content=[text_block("done")]),
        ])
        messages = [{"role": "user", "content": "schedule a daily check"}]

        with patch.object(cron_module.random, "randint", return_value=12):
            with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
                agent_loop(messages, client=client)

        self.assertEqual(
            messages[2]["content"],
            [{
                "type": "tool_result",
                "tool_use_id": "toolu_cron",
                "content": "Scheduled cron_000012: '0 9 * * *' -> daily check",
            }],
        )


if __name__ == "__main__":
    unittest.main()
