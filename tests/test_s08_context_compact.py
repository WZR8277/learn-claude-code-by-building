import os
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import mini_claude_code.compact as compact_module
from mini_claude_code.compact import (
    compact_history,
    micro_compact,
    reactive_compact,
    snip_compact,
    tool_result_budget,
)
from mini_claude_code.loop import agent_loop


class FakeMessages:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(deepcopy(kwargs))
        response = self._responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class FakeClient:
    def __init__(self, responses):
        self.messages = FakeMessages(responses)


def text_block(text: str):
    return SimpleNamespace(type="text", text=text)


def tool_block(block_id: str, name: str = "bash", **input_args):
    return SimpleNamespace(type="tool_use", id=block_id, name=name, input=input_args)


class ContextCompactTest(unittest.TestCase):
    def test_snip_compact_keeps_edges_and_does_not_split_tool_pair(self) -> None:
        messages = [
            {"role": "user", "content": "start"},
            {"role": "assistant", "content": [text_block("a")]},
            {"role": "assistant", "content": [tool_block("toolu_1")]},
            {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_1", "content": "ok"}]},
            {"role": "assistant", "content": [text_block("middle")]},
            {"role": "user", "content": "later"},
            {"role": "assistant", "content": [tool_block("toolu_2")]},
            {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_2", "content": "ok"}]},
        ]

        compacted = snip_compact(messages, max_messages=6)

        self.assertEqual(compacted[0]["content"], "start")
        self.assertIn("[snipped", compacted[2]["content"])
        self.assertEqual(compacted[-2]["content"][0].id, "toolu_2")
        self.assertEqual(compacted[-1]["content"][0]["tool_use_id"], "toolu_2")

    def test_micro_compact_replaces_only_older_large_tool_results(self) -> None:
        messages = []
        for index in range(5):
            messages.append({"role": "assistant", "content": [tool_block(f"toolu_{index}")]})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": f"toolu_{index}",
                    "content": "x" * 150,
                }],
            })

        compacted = micro_compact(messages)

        self.assertEqual(
            compacted[1]["content"][0]["content"],
            "[Earlier tool result compacted. Re-run if needed.]",
        )
        self.assertEqual(compacted[-1]["content"][0]["content"], "x" * 150)

    def test_tool_result_budget_persists_largest_outputs_from_last_message(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            messages = [{
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": "small", "content": "ok"},
                    {"type": "tool_result", "tool_use_id": "large", "content": "x" * 100},
                ],
            }]

            with patch.object(compact_module, "TOOL_RESULTS_DIR", output_dir):
                with patch.object(compact_module, "PERSIST_THRESHOLD", 20):
                    compacted = tool_result_budget(messages, max_bytes=50)

            self.assertTrue((output_dir / "large.txt").exists())
            self.assertIn("Full output persisted", compacted[-1]["content"][1]["content"])
            self.assertEqual(compacted[-1]["content"][0]["content"], "ok")

    def test_compact_history_writes_transcript_and_returns_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            client = FakeClient([SimpleNamespace(content=[text_block("summary")])])
            messages = [{"role": "user", "content": "hello"}]

            with patch.object(compact_module, "TRANSCRIPT_DIR", Path(temp_dir)):
                compacted = compact_history(messages, client=client, model="test-model")

            self.assertEqual(compacted, [{"role": "user", "content": "[Compacted]\n\nsummary"}])
            self.assertEqual(len(list(Path(temp_dir).glob("transcript_*.jsonl"))), 1)

    def test_reactive_compact_keeps_recent_tail_and_boundary_pair(self) -> None:
        messages = [
            {"role": "user", "content": "old"},
            {"role": "assistant", "content": [text_block("old answer")]},
            {"role": "user", "content": "middle"},
            {"role": "assistant", "content": [tool_block("toolu_keep")]},
            {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_keep", "content": "kept"}]},
            {"role": "assistant", "content": [text_block("done")]},
        ]
        client = FakeClient([SimpleNamespace(content=[text_block("summary")])])

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(compact_module, "TRANSCRIPT_DIR", Path(temp_dir)):
                compacted = reactive_compact(messages, client=client, model="test-model")

        self.assertEqual(compacted[0]["content"], "[Reactive compact]\n\nsummary")
        tool_index = next(
            index for index, message in enumerate(compacted)
            if isinstance(message.get("content"), list)
            and getattr(message["content"][0], "id", None) == "toolu_keep"
        )
        self.assertEqual(compacted[tool_index + 1]["content"][0]["tool_use_id"], "toolu_keep")


class AgentLoopCompactTest(unittest.TestCase):
    def test_loop_runs_pre_call_compactors_before_model_call(self) -> None:
        final_block = text_block("done")
        client = FakeClient([SimpleNamespace(stop_reason="end_turn", content=[final_block])])
        messages = [{"role": "user", "content": str(index)} for index in range(55)]

        with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
            agent_loop(messages, client=client)

        call_messages = client.messages.calls[0]["messages"]
        self.assertTrue(any("[snipped" in message.get("content", "") for message in call_messages))

    def test_loop_auto_compacts_when_estimated_context_is_too_large(self) -> None:
        final_block = text_block("done")
        client = FakeClient([SimpleNamespace(stop_reason="end_turn", content=[final_block])])
        messages = [{"role": "user", "content": "large"}]

        with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
            with patch("mini_claude_code.loop.CONTEXT_LIMIT", 1):
                with patch("mini_claude_code.loop.compact_history", return_value=[{"role": "user", "content": "[Compacted]\n\nsummary"}]):
                    agent_loop(messages, client=client)

        self.assertEqual(client.messages.calls[0]["messages"], [{"role": "user", "content": "[Compacted]\n\nsummary"}])

    def test_loop_reacts_to_prompt_too_long_once_then_retries(self) -> None:
        final_block = text_block("done")
        client = FakeClient([
            RuntimeError("prompt_too_long"),
            SimpleNamespace(stop_reason="end_turn", content=[final_block]),
        ])
        messages = [{"role": "user", "content": "large"}]

        with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
            with patch("mini_claude_code.loop.reactive_compact", return_value=[{"role": "user", "content": "[Reactive compact]\n\nsummary"}]):
                agent_loop(messages, client=client)

        self.assertEqual(len(client.messages.calls), 2)
        self.assertEqual(client.messages.calls[1]["messages"], [{"role": "user", "content": "[Reactive compact]\n\nsummary"}])

    def test_compact_tool_returns_result_without_orphaning_protocol_pair(self) -> None:
        compact_call = tool_block("toolu_compact", "compact", focus="current task")
        final_block = text_block("done")
        client = FakeClient([
            SimpleNamespace(stop_reason="tool_use", content=[compact_call]),
            SimpleNamespace(stop_reason="end_turn", content=[final_block]),
        ])
        messages = [{"role": "user", "content": "please compact"}]

        with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
            with patch("mini_claude_code.loop.compact_history", return_value=[{"role": "user", "content": "[Compacted]\n\nsummary"}]):
                agent_loop(messages, client=client)

        second_call_messages = client.messages.calls[1]["messages"]
        self.assertEqual(second_call_messages[0]["content"], "[Compacted]\n\nsummary")
        self.assertEqual(second_call_messages[1]["role"], "assistant")
        self.assertEqual(second_call_messages[1]["content"][0].id, "toolu_compact")
        self.assertEqual(second_call_messages[2]["content"][0]["tool_use_id"], "toolu_compact")


if __name__ == "__main__":
    unittest.main()
