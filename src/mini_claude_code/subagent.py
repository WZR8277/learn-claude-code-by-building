"""S06 subagent loop with a fresh message history."""

import os
from typing import Any

from anthropic import Anthropic

from .hooks import trigger_hooks


SUB_TOOL_NAMES = ("bash", "read_file", "write_file", "edit_file", "glob")
SUB_HANDLERS: dict[str, Any] = {}
MAX_SUBAGENT_TURNS = 30


SUB_TOOLS = [
    {
        "name": "bash",
        "description": "Run a shell command.",
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
    {
        "name": "read_file",
        "description": "Read file contents.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "edit_file",
        "description": "Replace exact text in a file once.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_text": {"type": "string"},
                "new_text": {"type": "string"},
            },
            "required": ["path", "old_text", "new_text"],
        },
    },
    {
        "name": "glob",
        "description": "Find files matching a glob pattern.",
        "input_schema": {
            "type": "object",
            "properties": {"pattern": {"type": "string"}},
            "required": ["pattern"],
        },
    },
]


def _subagent_system() -> str:
    from .tool import WORKDIR

    return (
        f"You are a coding agent at {WORKDIR}. "
        "Complete the task you were given, then return a concise summary. "
        "Do not delegate further."
    )


def _ensure_sub_handlers() -> dict[str, Any]:
    if not SUB_HANDLERS:
        from .tool import run_bash, run_edit, run_glob, run_read, run_write

        SUB_HANDLERS.update({
            "bash": run_bash,
            "read_file": run_read,
            "write_file": run_write,
            "edit_file": run_edit,
            "glob": run_glob,
        })
    return SUB_HANDLERS


def extract_text(content: Any) -> str:
    """把 Anthropic content blocks 中的文本块提取为普通摘要。"""
    if not isinstance(content, list):
        return str(content)
    return "\n".join(
        getattr(block, "text", "")
        for block in content
        if getattr(block, "type", None) == "text"
    )


def spawn_subagent(
    description: str,
    *,
    client: Any | None = None,
    model: str | None = None,
    max_turns: int = MAX_SUBAGENT_TURNS,
) -> str:
    """启动一个同步子 Agent，只把最终摘要交还给父 Agent。"""
    if client is None:
        client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
    model = model or os.environ["MODEL_ID"]
    messages = [{"role": "user", "content": description}]
    handlers = _ensure_sub_handlers()

    print("\n\033[35m[Subagent spawned]\033[0m")
    for _ in range(max_turns):
        response = client.messages.create(
            model=model,
            system=_subagent_system(),
            messages=messages,
            tools=SUB_TOOLS,
            max_tokens=8192,
        )
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            print("\033[35m[Subagent done]\033[0m")
            return extract_text(response.content)

        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            # 子 Agent 是独立上下文，但工具执行仍要经过同一组 Hook/权限边界。
            blocked = trigger_hooks("PreToolUse", block)
            if blocked:
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(blocked),
                })
                continue

            handler = handlers.get(block.name)
            output = handler(**block.input) if handler else f"Unknown: {block.name}"
            trigger_hooks("PostToolUse", block, output)
            print(f"  \033[90m[sub] {block.name}: {str(output)[:100]}\033[0m")
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": output,
            })
        messages.append({"role": "user", "content": results})

    result = ""
    for message in reversed(messages):
        if message["role"] == "assistant":
            result = extract_text(message["content"])
            if result:
                break
    print("\033[35m[Subagent done]\033[0m")
    return result or "Subagent stopped after 30 turns without final answer."
