import os
import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

import mini_claude_code.system_prompt as prompt_module
from mini_claude_code.loop import agent_loop
from mini_claude_code.system_prompt import (
    assemble_system_prompt,
    get_system_prompt,
    reset_system_prompt_cache,
    update_prompt_context,
)
from mini_claude_code.tool import TOOL_HANDLERS


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


def tool_block(block_id: str, name: str = "bash", **input_args):
    return SimpleNamespace(type="tool_use", id=block_id, name=name, input=input_args)


class SystemPromptAssemblyTest(unittest.TestCase):
    def tearDown(self) -> None:
        reset_system_prompt_cache()

    def test_assembly_loads_memory_section_only_when_index_exists(self) -> None:
        context = {
            "workspace": "/workspace",
            "enabled_tools": ["bash", "read_file"],
            "skill_catalog": "- **reviewer**: Review code",
            "memory_index": "",
        }

        system = assemble_system_prompt(context)

        self.assertIn("Available tools: bash, read_file.", system)
        self.assertIn("Working directory: /workspace", system)
        self.assertIn("Skills available:", system)
        self.assertNotIn("Memories available:", system)

        context["memory_index"] = "- [repo](repo.md) — Repository facts"
        system = assemble_system_prompt(context)

        self.assertIn("Memories available:", system)
        self.assertIn("Repository facts", system)

    def test_context_comes_from_runtime_state(self) -> None:
        with patch("mini_claude_code.system_prompt.list_skills", return_value="- **pdf**: Work with PDFs"):
            with patch("mini_claude_code.system_prompt.read_memory_index", return_value="- [tabs](tabs.md) — User prefers tabs"):
                context = update_prompt_context("/workspace", enabled_tools=("bash", "load_skill"))

        self.assertEqual(context["workspace"], "/workspace")
        self.assertEqual(context["enabled_tools"], ["bash", "load_skill"])
        self.assertIn("Work with PDFs", context["skill_catalog"])
        self.assertIn("User prefers tabs", context["memory_index"])

    def test_prompt_cache_uses_deterministic_context_key(self) -> None:
        context = {
            "workspace": "/workspace",
            "enabled_tools": ["bash"],
            "skill_catalog": "(no skills found)",
            "memory_index": "",
        }

        with patch.object(prompt_module, "assemble_system_prompt", wraps=assemble_system_prompt) as assemble:
            self.assertEqual(get_system_prompt(context), get_system_prompt(dict(context)))

        self.assertEqual(assemble.call_count, 1)


class AgentLoopSystemPromptTest(unittest.TestCase):
    def test_loop_refreshes_prompt_context_after_tool_round(self) -> None:
        call = tool_block("toolu_write", "write_file", path=".memory/MEMORY.md", content="- [repo](repo.md) — Repository facts")
        final_block = text_block("done")
        client = FakeClient([
            SimpleNamespace(stop_reason="tool_use", content=[call]),
            SimpleNamespace(stop_reason="end_turn", content=[final_block]),
        ])
        messages = [{"role": "user", "content": "remember this project fact"}]
        contexts = [
            {"workspace": "/workspace", "enabled_tools": ["write_file"], "skill_catalog": "(no skills found)", "memory_index": ""},
            {
                "workspace": "/workspace",
                "enabled_tools": ["write_file"],
                "skill_catalog": "(no skills found)",
                "memory_index": "- [repo](repo.md) — Repository facts",
            },
        ]

        with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
            with patch.dict(TOOL_HANDLERS, {"write_file": lambda path, content: "written"}, clear=True):
                with patch("mini_claude_code.loop.update_prompt_context", side_effect=contexts) as update_context:
                    with patch("mini_claude_code.loop.get_system_prompt", side_effect=["system before", "system after"]) as get_prompt:
                        with patch("mini_claude_code.loop.extract_memories", return_value=0):
                            with patch("mini_claude_code.loop.consolidate_memories", return_value=0):
                                agent_loop(messages, client=client)

        self.assertEqual(update_context.call_count, 2)
        self.assertEqual(get_prompt.call_count, 2)
        self.assertEqual(client.messages.calls[0]["system"], "system before")
        self.assertEqual(client.messages.calls[1]["system"], "system after")


if __name__ == "__main__":
    unittest.main()
