import os
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import mini_claude_code.skills as skills_module
from mini_claude_code.loop import agent_loop
from mini_claude_code.skills import build_system, list_skills, load_skill, parse_frontmatter, refresh_skill_registry
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


class SkillRegistryTest(unittest.TestCase):
    def setUp(self) -> None:
        self._original_registry = dict(skills_module.SKILL_REGISTRY)

    def tearDown(self) -> None:
        skills_module.SKILL_REGISTRY.clear()
        skills_module.SKILL_REGISTRY.update(self._original_registry)

    def make_skill(self, root: Path, directory: str, content: str) -> None:
        skill_dir = root / directory
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(content)

    def test_parse_frontmatter_extracts_metadata_without_dropping_body(self) -> None:
        metadata, body = parse_frontmatter("---\nname: reviewer\ndescription: Review code\n---\n# Full guide")

        self.assertEqual(metadata, {"name": "reviewer", "description": "Review code"})
        self.assertEqual(body, "# Full guide")

    def test_skill_registry_scans_catalog_and_loads_full_content_on_demand(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.make_skill(
                root,
                "code-review",
                "---\nname: code-review\ndescription: Review changes\n---\n# Code Review\nFull checklist",
            )

            registry = refresh_skill_registry(root)

        self.assertIn("code-review", registry)
        self.assertEqual(list_skills(), "- **code-review**: Review changes")
        self.assertIn("Full checklist", load_skill("code-review"))

    def test_skill_name_falls_back_to_directory_and_description_to_heading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.make_skill(root, "plain", "# Plain Skill\nBody")

            registry = refresh_skill_registry(root)

        self.assertEqual(registry["plain"]["description"], "Plain Skill")

    def test_missing_or_unknown_skill_has_tutorial_result(self) -> None:
        refresh_skill_registry(Path("/path/that/does/not/exist"))

        self.assertEqual(list_skills(), "(no skills found)")
        self.assertEqual(load_skill("missing"), "Skill not found: missing")

    def test_system_prompt_contains_catalog_not_full_skill_body(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.make_skill(
                root,
                "pdf",
                "---\nname: pdf\ndescription: Work with PDFs\n---\nSECRET FULL BODY",
            )
            refresh_skill_registry(root)

        system = build_system("/workspace")

        self.assertIn("Skills available:", system)
        self.assertIn("- **pdf**: Work with PDFs", system)
        self.assertIn("Use load_skill to get full details when needed.", system)
        self.assertNotIn("SECRET FULL BODY", system)


class SkillToolTest(unittest.TestCase):
    def test_load_skill_is_registered_as_s07_tool(self) -> None:
        self.assertIn("load_skill", [tool["name"] for tool in TOOLS])
        self.assertIs(TOOL_HANDLERS["load_skill"], load_skill)

    def test_agent_loop_returns_loaded_skill_as_tool_result(self) -> None:
        tool_block = SimpleNamespace(
            type="tool_use",
            id="toolu_skill",
            name="load_skill",
            input={"name": "code-review"},
        )
        final_block = SimpleNamespace(type="text", text="done")
        client = FakeClient([
            SimpleNamespace(stop_reason="tool_use", content=[tool_block]),
            SimpleNamespace(stop_reason="end_turn", content=[final_block]),
        ])
        messages = [{"role": "user", "content": "load review skill"}]

        with patch.dict(TOOL_HANDLERS, {"load_skill": lambda name: "# Code Review"}, clear=True):
            with patch("mini_claude_code.loop.build_system", return_value="system with catalog"):
                with patch.dict(os.environ, {"MODEL_ID": "test-model"}):
                    agent_loop(messages, client=client)

        self.assertEqual(client.messages.calls[0]["system"], "system with catalog")
        self.assertEqual(
            messages[2]["content"],
            [{"type": "tool_result", "tool_use_id": "toolu_skill", "content": "# Code Review"}],
        )


if __name__ == "__main__":
    unittest.main()
