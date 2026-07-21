import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from mini_claude_code.cli import main
from mini_claude_code.hooks import HOOKS, register_hook, trigger_hooks
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


class HookTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._original_hooks = {event: list(hooks) for event, hooks in HOOKS.items()}

    def tearDown(self) -> None:
        for event, hooks in self._original_hooks.items():
            HOOKS[event] = hooks


class HookRegistryTest(HookTestCase):
    def test_hooks_run_in_registration_order_and_capture_errors(self) -> None:
        calls = []

        register_hook("UserPromptSubmit", lambda query: calls.append("first") or None)
        register_hook("UserPromptSubmit", lambda query: (_ for _ in ()).throw(RuntimeError("boom")))
        register_hook("UserPromptSubmit", lambda query: calls.append("third") or "note")

        self.assertEqual(
            trigger_hooks("UserPromptSubmit", "hello"),
            "Hook error: boom",
        )
        self.assertEqual(calls, ["first"])

    def test_unknown_hook_event_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            register_hook("MissingEvent", lambda context: None)

    def test_cli_triggers_user_prompt_submit_before_agent_loop(self) -> None:
        calls = []

        def record_prompt(query: str, workdir) -> None:
            calls.append((query, workdir))

        HOOKS["UserPromptSubmit"] = [record_prompt]
        with patch("builtins.input", side_effect=["hello", ""]):
            with patch("mini_claude_code.cli.agent_loop") as loop_mock:
                main()

        loop_mock.assert_called_once()
        self.assertEqual(calls[0][0], "hello")


class AgentLoopHookTest(HookTestCase):
    def run_tool_blocks(self, blocks, responses=None):
        final_block = SimpleNamespace(type="text", text="done")
        model_responses = responses or [
            SimpleNamespace(stop_reason="tool_use", content=blocks),
            SimpleNamespace(stop_reason="end_turn", content=[final_block]),
        ]
        client = FakeClient(model_responses)
        messages = [{"role": "user", "content": "run tools"}]
        with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
            with patch("mini_claude_code.loop.extract_memories", return_value=0):
                with patch("mini_claude_code.loop.consolidate_memories", return_value=0):
                    agent_loop(messages, client=client)
        return client, messages

    def test_pre_tool_hook_can_block_without_running_handler(self) -> None:
        block = SimpleNamespace(type="tool_use", id="toolu_block", name="bash", input={"command": "pwd"})
        handler = Mock(return_value="ran")

        HOOKS["PreToolUse"] = [lambda block: "blocked by hook"]
        with patch.dict(TOOL_HANDLERS, {"bash": handler}, clear=True):
            _client, messages = self.run_tool_blocks([block])

        handler.assert_not_called()
        self.assertEqual(
            messages[2]["content"],
            [{"type": "tool_result", "tool_use_id": "toolu_block", "content": "blocked by hook"}],
        )

    def test_post_tool_hook_runs_once_after_successful_dispatch(self) -> None:
        block = SimpleNamespace(type="tool_use", id="toolu_post", name="bash", input={"command": "pwd"})
        post_hook = Mock(return_value=None)

        HOOKS["PreToolUse"] = []
        HOOKS["PostToolUse"] = [post_hook]
        with patch.dict(TOOL_HANDLERS, {"bash": lambda command: f"ran {command}"}, clear=True):
            _client, messages = self.run_tool_blocks([block])

        post_hook.assert_called_once()
        self.assertEqual(post_hook.call_args.args, (block, "ran pwd"))
        self.assertEqual(messages[2]["content"][0]["content"], "ran pwd")

    def test_stop_hook_can_request_one_bounded_continuation(self) -> None:
        first_final = SimpleNamespace(type="text", text="pause")
        second_final = SimpleNamespace(type="text", text="done")
        client, messages = self.run_tool_blocks(
            [],
            responses=[
                SimpleNamespace(stop_reason="end_turn", content=[first_final]),
                SimpleNamespace(stop_reason="end_turn", content=[second_final]),
            ],
        )

        self.assertEqual(len(client.messages.calls), 1)
        self.assertEqual(messages[-1]["content"], [first_final])

        HOOKS["Stop"] = [lambda messages: "please continue"]
        client = FakeClient([
            SimpleNamespace(stop_reason="end_turn", content=[first_final]),
            SimpleNamespace(stop_reason="end_turn", content=[second_final]),
        ])
        messages = [{"role": "user", "content": "hello"}]
        with patch("mini_claude_code.loop.extract_memories", return_value=0):
            with patch("mini_claude_code.loop.consolidate_memories", return_value=0):
                with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
                    agent_loop(messages, client=client)

        self.assertEqual(len(client.messages.calls), 2)
        self.assertEqual(messages[2], {"role": "user", "content": "please continue"})
        self.assertEqual(messages[-1]["content"], [second_final])


if __name__ == "__main__":
    unittest.main()
