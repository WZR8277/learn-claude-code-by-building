"""S10 runtime system prompt assembly."""

import json
from pathlib import Path
from typing import Any

from .memory import read_memory_index
from .skills import list_skills


PROMPT_SECTIONS = {
    "identity": "You are a coding agent. Act, don't explain.",
    "tools": "Available tools: {tools}.",
    "workspace": "Working directory: {workspace}",
    "skills": "Skills available:\n{skills}\nUse load_skill to get full details when needed.",
    "memory": "Memories available:\n{memory_index}\nRelevant memories may be injected into the current user turn.",
}

_last_context_key: str | None = None
_last_prompt: str | None = None


def update_prompt_context(
    workdir: Path | str | None = None,
    *,
    enabled_tools: list[str] | tuple[str, ...] | None = None,
    memory_index: str | None = None,
) -> dict[str, Any]:
    """从真实运行态派生 prompt context，而不是从用户文本里猜关键词。"""
    tool_names = list(enabled_tools or [])
    return {
        "workspace": str(workdir or Path.cwd()),
        "enabled_tools": tool_names,
        "skill_catalog": list_skills(),
        "memory_index": read_memory_index() if memory_index is None else memory_index,
    }


def assemble_system_prompt(context: dict[str, Any]) -> str:
    """按稳定顺序拼接 system prompt sections。"""
    tools = ", ".join(context.get("enabled_tools") or []) or "(none)"
    sections = [
        PROMPT_SECTIONS["identity"],
        PROMPT_SECTIONS["tools"].format(tools=tools),
        PROMPT_SECTIONS["workspace"].format(workspace=context.get("workspace", Path.cwd())),
        PROMPT_SECTIONS["skills"].format(
            skills=context.get("skill_catalog") or "(no skills found)"
        ),
    ]

    memory_index = str(context.get("memory_index") or "").strip()
    if memory_index:
        # S10：memory section 是否出现只看真实 MEMORY.md 索引是否有内容。
        sections.append(PROMPT_SECTIONS["memory"].format(memory_index=memory_index))

    return "\n\n".join(sections)


def get_system_prompt(context: dict[str, Any]) -> str:
    """用确定性 cache key 避免同一进程内重复组装字符串。"""
    global _last_context_key, _last_prompt

    key = json.dumps(context, sort_keys=True, ensure_ascii=False, default=str)
    if key == _last_context_key and _last_prompt is not None:
        return _last_prompt

    _last_context_key = key
    _last_prompt = assemble_system_prompt(context)
    return _last_prompt


def reset_system_prompt_cache() -> None:
    """测试用：避免不同用例共享上一次 prompt cache。"""
    global _last_context_key, _last_prompt
    _last_context_key = None
    _last_prompt = None
