import os
import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

import mini_claude_code.error_recovery as recovery_module
from mini_claude_code.error_recovery import (
    ESCALATED_MAX_TOKENS,
    MAX_CONSECUTIVE_529,
    RecoveryState,
    is_prompt_too_long_error,
    retry_delay,
    with_retry,
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


class ErrorRecoveryHelperTest(unittest.TestCase):
    def test_retry_delay_uses_retry_after_or_exponential_jitter(self) -> None:
        self.assertEqual(retry_delay(3, retry_after=7), 7)

        with patch.object(recovery_module.random, "uniform", return_value=0.25):
            self.assertEqual(retry_delay(1), 1.25)

    def test_prompt_too_long_detection_accepts_common_messages(self) -> None:
        self.assertTrue(is_prompt_too_long_error(RuntimeError("prompt_is_too_long")))
        self.assertTrue(is_prompt_too_long_error(RuntimeError("context_length_exceeded")))
        self.assertFalse(is_prompt_too_long_error(RuntimeError("permission denied")))

    def test_with_retry_backs_off_for_429_and_returns_result(self) -> None:
        attempts = [RuntimeError("429 rate limited"), "ok"]
        sleeps = []
        state = RecoveryState(current_model="primary")

        def flaky():
            value = attempts.pop(0)
            if isinstance(value, Exception):
                raise value
            return value

        with patch.object(recovery_module.random, "uniform", return_value=0):
            result = with_retry(flaky, state, sleep=sleeps.append)

        self.assertEqual(result, "ok")
        self.assertEqual(sleeps, [0.5])

    def test_with_retry_switches_to_fallback_after_consecutive_529(self) -> None:
        attempts = [RuntimeError("529 overloaded") for _ in range(MAX_CONSECUTIVE_529)]
        attempts.append("ok")
        state = RecoveryState(current_model="primary")

        def flaky():
            value = attempts.pop(0)
            if isinstance(value, Exception):
                raise value
            return value

        with patch.dict(os.environ, {"FALLBACK_MODEL_ID": "fallback"}):
            with patch.object(recovery_module.random, "uniform", return_value=0):
                result = with_retry(flaky, state, sleep=lambda _delay: None)

        self.assertEqual(result, "ok")
        self.assertEqual(state.current_model, "fallback")


class AgentLoopRecoveryTest(unittest.TestCase):
    def test_loop_escalates_output_tokens_before_appending_truncated_response(self) -> None:
        truncated = SimpleNamespace(stop_reason="max_tokens", content=[text_block("partial")])
        final = SimpleNamespace(stop_reason="end_turn", content=[text_block("done")])
        client = FakeClient([truncated, final])
        messages = [{"role": "user", "content": "write a long answer"}]

        with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
            with patch("mini_claude_code.loop.extract_memories", return_value=0):
                with patch("mini_claude_code.loop.consolidate_memories", return_value=0):
                    agent_loop(messages, client=client)

        self.assertEqual(len(client.messages.calls), 2)
        self.assertEqual(client.messages.calls[1]["max_tokens"], ESCALATED_MAX_TOKENS)
        self.assertNotIn("partial", str(messages))
        self.assertEqual(messages[-1]["content"], [text_block("done")])

    def test_loop_continues_after_second_max_tokens_until_limit(self) -> None:
        responses = [
            SimpleNamespace(stop_reason="max_tokens", content=[text_block("first")]),
            SimpleNamespace(stop_reason="max_tokens", content=[text_block("second")]),
            SimpleNamespace(stop_reason="end_turn", content=[text_block("done")]),
        ]
        client = FakeClient(responses)
        messages = [{"role": "user", "content": "write a long answer"}]

        with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
            with patch("mini_claude_code.loop.extract_memories", return_value=0):
                with patch("mini_claude_code.loop.consolidate_memories", return_value=0):
                    agent_loop(messages, client=client)

        self.assertIn("second", str(messages))
        self.assertIn("Output token limit hit", messages[-2]["content"])
        self.assertEqual(messages[-1]["content"], [text_block("done")])

    def test_loop_reactive_compacts_prompt_too_long_only_once(self) -> None:
        client = FakeClient([RuntimeError("prompt_is_too_long"), RuntimeError("prompt_is_too_long")])
        messages = [{"role": "user", "content": "large"}]

        with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
            with patch("mini_claude_code.loop.reactive_compact", return_value=[{"role": "user", "content": "[Reactive compact]"}]) as compact:
                agent_loop(messages, client=client)

        self.assertEqual(compact.call_count, 1)
        self.assertEqual(len(client.messages.calls), 2)
        self.assertIn("Context too large", messages[-1]["content"][0]["text"])

    def test_loop_uses_with_retry_for_529_and_can_switch_model(self) -> None:
        client = FakeClient([
            RuntimeError("529 overloaded"),
            RuntimeError("529 overloaded"),
            RuntimeError("529 overloaded"),
            SimpleNamespace(stop_reason="end_turn", content=[text_block("done")]),
        ])
        messages = [{"role": "user", "content": "hello"}]

        with patch.dict(os.environ, {"MODEL_ID": "primary", "FALLBACK_MODEL_ID": "fallback"}):
            with patch("mini_claude_code.error_recovery.time.sleep", return_value=None):
                with patch("mini_claude_code.loop.extract_memories", return_value=0):
                    with patch("mini_claude_code.loop.consolidate_memories", return_value=0):
                        agent_loop(messages, client=client)

        self.assertEqual(client.messages.calls[-1]["model"], "fallback")
        self.assertEqual(messages[-1]["content"], [text_block("done")])


if __name__ == "__main__":
    unittest.main()
