"""Lifecycle hooks introduced by s04."""

from collections.abc import Callable
from pathlib import Path
from typing import Any


Hook = Callable[..., str | None]


HOOKS: dict[str, list[Hook]] = {
    "UserPromptSubmit": [],
    "PreToolUse": [],
    "PostToolUse": [],
    "Stop": [],
}


def register_hook(event: str, hook: Hook) -> None:
    if event not in HOOKS:
        raise ValueError(f"Unknown hook event: {event}")
    HOOKS[event].append(hook)


def trigger_hooks(event: str, *args: Any) -> str | None:
    if event not in HOOKS:
        raise ValueError(f"Unknown hook event: {event}")

    for hook in HOOKS[event]:
        try:
            result = hook(*args)
        except Exception as exc:
            result = f"Hook error: {exc}"
        if result:
            return result
    return None


def log_hook(block: Any) -> None:
    """PreToolUse：记录每次工具调用，证明扩展逻辑已从循环中抽离。"""
    args_preview = str(list(block.input.values())[:2])[:60]
    print(f"\033[90m[HOOK] {block.name}({args_preview})\033[0m")


def large_output_hook(block: Any, output: str) -> None:
    """PostToolUse：工具执行后观察结果，但不改变 tool_result 协议。"""
    if len(str(output)) > 100_000:
        print(f"\033[33m[HOOK] Large output from {block.name}: {len(str(output))} chars\033[0m")


def context_inject_hook(query: str, workdir: Path | None = None) -> None:
    """UserPromptSubmit：在用户消息进入历史前运行。"""
    if workdir is not None:
        print(f"\033[90m[HOOK] UserPromptSubmit: working in {workdir}\033[0m")


def summary_hook(messages: list) -> None:
    """Stop：模型不再请求工具时统计本轮使用过的工具结果。"""
    tool_count = sum(
        1
        for message in messages
        for block in (message.get("content") if isinstance(message.get("content"), list) else [])
        if isinstance(block, dict) and block.get("type") == "tool_result"
    )
    print(f"\033[90m[HOOK] Stop: session used {tool_count} tool calls\033[0m")
