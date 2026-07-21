import os
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import mini_claude_code.memory as memory_module
from mini_claude_code.loop import agent_loop
from mini_claude_code.memory import (
    consolidate_memories,
    extract_memories,
    list_memory_files,
    load_memories,
    read_memory_file,
    read_memory_index,
    select_relevant_memories,
    write_memory_file,
)
from mini_claude_code.skills import build_system


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


class MemoryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory_dir = Path(self.temp_dir.name)
        self.patches = [
            patch.object(memory_module, "MEMORY_DIR", self.memory_dir),
            patch.object(memory_module, "MEMORY_INDEX", self.memory_dir / "MEMORY.md"),
        ]
        for patcher in self.patches:
            patcher.start()

    def tearDown(self) -> None:
        for patcher in reversed(self.patches):
            patcher.stop()
        self.temp_dir.cleanup()


class MemoryFileTest(MemoryTestCase):
    def test_write_memory_file_rebuilds_lightweight_index(self) -> None:
        path = write_memory_file(
            "user-preference-tabs",
            "user",
            "User prefers tabs",
            "Use tabs for indentation.",
        )

        self.assertEqual(path.name, "user-preference-tabs.md")
        self.assertIn("User prefers tabs", read_memory_index())
        self.assertNotIn("Use tabs for indentation.", read_memory_index())
        self.assertIn("type: user", read_memory_file("user-preference-tabs.md"))

    def test_read_memory_file_rejects_path_escape(self) -> None:
        write_memory_file("safe", "project", "Safe memory", "body")

        self.assertIsNone(read_memory_file("../safe.md"))

    def test_build_system_can_include_memory_index_without_full_body(self) -> None:
        write_memory_file("repo-layout", "project", "Repository uses src layout", "Secret detailed body")

        system = build_system("/workspace", memory_index=read_memory_index())

        self.assertIn("Memories available:", system)
        self.assertIn("Repository uses src layout", system)
        self.assertNotIn("Secret detailed body", system)


class MemorySelectionTest(MemoryTestCase):
    def test_select_relevant_memories_uses_model_indices(self) -> None:
        write_memory_file("tabs", "user", "User prefers tabs", "Use tabs.")
        write_memory_file("quotes", "user", "User prefers single quotes", "Use single quotes.")
        client = FakeClient([SimpleNamespace(content=[text_block("[0]")])])

        selected = select_relevant_memories(
            [{"role": "user", "content": "Please write a string literal."}],
            client=client,
            model="test-model",
        )

        self.assertEqual(selected, ["quotes.md"])

    def test_select_relevant_memories_falls_back_to_keywords(self) -> None:
        write_memory_file("tabs", "user", "User prefers tabs", "Use tabs.")
        client = FakeClient([RuntimeError("offline")])

        selected = select_relevant_memories(
            [{"role": "user", "content": "tabs indentation please"}],
            client=client,
            model="test-model",
        )

        self.assertEqual(selected, ["tabs.md"])

    def test_load_memories_wraps_selected_files(self) -> None:
        write_memory_file("tabs", "user", "User prefers tabs", "Use tabs.")
        client = FakeClient([SimpleNamespace(content=[text_block("[0]")])])

        loaded = load_memories(
            [{"role": "user", "content": "remember my indentation"}],
            client=client,
            model="test-model",
        )

        self.assertIn("<relevant_memories>", loaded)
        self.assertIn("Use tabs.", loaded)


class MemoryExtractionTest(MemoryTestCase):
    def test_extract_memories_writes_new_items_from_json_array(self) -> None:
        client = FakeClient([SimpleNamespace(content=[text_block(
            '[{"name":"single-quotes","type":"user","description":"User prefers single quotes","body":"Use single quotes for strings."}]'
        )])])

        count = extract_memories(
            [{"role": "user", "content": "Remember that I prefer single quotes."}],
            client=client,
            model="test-model",
        )

        self.assertEqual(count, 1)
        self.assertEqual(list_memory_files()[0]["filename"], "single-quotes.md")

    def test_consolidate_memories_replaces_files_after_threshold(self) -> None:
        write_memory_file("tabs-a", "user", "Tabs preference", "Use tabs.")
        write_memory_file("tabs-b", "feedback", "Also tabs", "Tabs, please.")
        client = FakeClient([SimpleNamespace(content=[text_block(
            '[{"name":"tabs","type":"user","description":"User prefers tabs","body":"Use tabs for indentation."}]'
        )])])

        with patch.object(memory_module, "CONSOLIDATE_THRESHOLD", 2):
            count = consolidate_memories(client=client, model="test-model")

        self.assertEqual(count, 1)
        self.assertEqual([memory["filename"] for memory in list_memory_files()], ["tabs.md"])


class AgentLoopMemoryTest(MemoryTestCase):
    def test_loop_injects_relevant_memory_and_extracts_after_final_stop(self) -> None:
        write_memory_file("tabs", "user", "User prefers tabs", "Use tabs.")
        final_block = text_block("done")
        client = FakeClient([
            SimpleNamespace(content=[text_block("[0]")]),
            SimpleNamespace(stop_reason="end_turn", content=[final_block]),
            SimpleNamespace(content=[text_block("[]")]),
        ])
        messages = [{"role": "user", "content": "Create an indented Python snippet."}]

        with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
            agent_loop(messages, client=client)

        self.assertEqual(len(client.messages.calls), 3)
        main_call = client.messages.calls[1]
        self.assertIn("Memories available:", main_call["system"])
        self.assertIn("<relevant_memories>", main_call["messages"][0]["content"])
        self.assertEqual(messages[-1]["content"], [final_block])


if __name__ == "__main__":
    unittest.main()
