"""S07 skill catalog and on-demand SKILL.md loading."""

from pathlib import Path
from typing import Any

import yaml


SKILLS_DIR = Path.cwd() / "skills"
SKILL_REGISTRY: dict[str, dict[str, str]] = {}


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """解析 SKILL.md 顶部 YAML，只用于提取目录所需的少量元数据。"""
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    try:
        metadata = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        metadata = {}
    return metadata, parts[2].strip()


def scan_skills(skills_dir: Path | None = None) -> dict[str, dict[str, str]]:
    """扫描 skills/ 目录，建立 name -> SKILL.md 内容的注册表。"""
    root = skills_dir or SKILLS_DIR
    registry: dict[str, dict[str, str]] = {}
    if not root.exists():
        return registry

    for directory in sorted(root.iterdir()):
        if not directory.is_dir():
            continue

        manifest = directory / "SKILL.md"
        if not manifest.exists():
            continue

        raw = manifest.read_text()
        metadata, _body = parse_frontmatter(raw)
        name = str(metadata.get("name") or directory.name)
        description = str(
            metadata.get("description")
            or raw.splitlines()[0].lstrip("#").strip()
            or "(no description)"
        )
        registry[name] = {
            "name": name,
            "description": description,
            "content": raw,
        }

    return registry


def refresh_skill_registry(skills_dir: Path | None = None) -> dict[str, dict[str, str]]:
    SKILL_REGISTRY.clear()
    SKILL_REGISTRY.update(scan_skills(skills_dir))
    return SKILL_REGISTRY


def list_skills() -> str:
    """只列技能名称和一句话描述，避免把完整规范提前塞进 system prompt。"""
    if not SKILL_REGISTRY:
        return "(no skills found)"
    return "\n".join(
        f"- **{skill['name']}**: {skill['description']}"
        for skill in SKILL_REGISTRY.values()
    )


def build_system(
    workdir: Path | str | None = None,
    memory_index: str = "",
    enabled_tools: list[str] | tuple[str, ...] | None = None,
) -> str:
    """S10 后保留旧入口，但实际 prompt 由 system_prompt 模块组装。"""
    from .system_prompt import assemble_system_prompt, update_prompt_context

    context = update_prompt_context(
        workdir,
        enabled_tools=enabled_tools,
        memory_index=memory_index,
    )
    return assemble_system_prompt(context)


def load_skill(name: str) -> str:
    """按注册表加载完整 SKILL.md，避免把工具参数当成任意文件路径。"""
    skill = SKILL_REGISTRY.get(name)
    if not skill:
        return f"Skill not found: {name}"
    return skill["content"]


refresh_skill_registry()
