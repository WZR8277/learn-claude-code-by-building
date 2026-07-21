"""Context compaction helpers for the tutorial agent loop."""

import json
import os
import time
from pathlib import Path
from typing import Any

from anthropic import Anthropic


WORKDIR = Path.cwd()
# S08 只做当前会话的上下文预算控制，不把摘要升级成跨会话记忆。
CONTEXT_LIMIT = 50_000
KEEP_RECENT = 3
PERSIST_THRESHOLD = 30_000
TRANSCRIPT_DIR = WORKDIR / ".transcripts"
TOOL_RESULTS_DIR = WORKDIR / ".task_outputs" / "tool-results"


def estimate_size(messages: list[dict[str, Any]]) -> int:
    return len(str(messages))


def _block_type(block: Any) -> str | None:
    if isinstance(block, dict):
        return block.get("type")
    return getattr(block, "type", None)


def _block_text(block: Any) -> str:
    if isinstance(block, dict):
        return str(block.get("text", ""))
    return str(getattr(block, "text", ""))


def _message_has_tool_use(message: dict[str, Any]) -> bool:
    if message.get("role") != "assistant" or not isinstance(message.get("content"), list):
        return False
    return any(_block_type(block) == "tool_use" for block in message["content"])


def _is_tool_result_message(message: dict[str, Any]) -> bool:
    if message.get("role") != "user" or not isinstance(message.get("content"), list):
        return False
    return any(_block_type(block) == "tool_result" for block in message["content"])


def snip_compact(messages: list[dict[str, Any]], max_messages: int = 50) -> list[dict[str, Any]]:
    if len(messages) <= max_messages:
        return messages

    head_count = min(3, max_messages - 1)
    tail_count = max_messages - head_count - 1

    # assistant 的 tool_use 后面必须紧跟 user 的 tool_result，裁剪时不能把这对协议消息切开。
    if head_count and head_count < len(messages):
        if _message_has_tool_use(messages[head_count - 1]) and _is_tool_result_message(messages[head_count]):
            head_count -= 1

    tail_start = len(messages) - tail_count
    if 0 < tail_start < len(messages):
        if _message_has_tool_use(messages[tail_start - 1]) and _is_tool_result_message(messages[tail_start]):
            tail_start -= 1

    head = messages[:head_count]
    tail = messages[tail_start:]
    snipped = len(messages) - len(head) - len(tail)
    placeholder = {"role": "user", "content": f"[snipped {snipped} messages]"}
    return head + [placeholder] + tail


def collect_tool_results(messages: list[dict[str, Any]]) -> list[tuple[int, int, Any]]:
    results = []
    for message_index, message in enumerate(messages):
        content = message.get("content")
        if message.get("role") != "user" or not isinstance(content, list):
            continue
        for block_index, block in enumerate(content):
            if _block_type(block) == "tool_result":
                results.append((message_index, block_index, block))
    return results


def micro_compact(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = collect_tool_results(messages)
    older_results = results[:-KEEP_RECENT]

    # 只压缩较早且很长的工具结果；最近几次工具输出通常仍是当前任务的直接依据。
    for message_index, block_index, block in older_results:
        content = block.get("content") if isinstance(block, dict) else getattr(block, "content", "")
        if len(str(content)) <= 120:
            continue
        if isinstance(block, dict):
            block["content"] = "[Earlier tool result compacted. Re-run if needed.]"
        else:
            block.content = "[Earlier tool result compacted. Re-run if needed.]"
        messages[message_index]["content"][block_index] = block

    return messages


def persist_large_output(tool_use_id: str, output: str) -> str:
    if len(output) <= PERSIST_THRESHOLD:
        return output

    # 大输出落盘后只把路径和预览留在上下文里，既可追溯，又避免挤爆 prompt。
    TOOL_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = TOOL_RESULTS_DIR / f"{tool_use_id}.txt"
    if not output_path.exists():
        output_path.write_text(output)

    preview = output[:2000]
    return f"[Full output persisted to {output_path}]\n\n{preview}"


def tool_result_budget(messages: list[dict[str, Any]], max_bytes: int = 200_000) -> list[dict[str, Any]]:
    if not messages:
        return messages

    last = messages[-1]
    content = last.get("content")
    if last.get("role") != "user" or not isinstance(content, list):
        return messages

    result_blocks = [
        block for block in content
        if _block_type(block) == "tool_result"
    ]
    total = sum(len(str(block.get("content", "") if isinstance(block, dict) else getattr(block, "content", ""))) for block in result_blocks)
    if total <= max_bytes:
        return messages

    for block in sorted(
        result_blocks,
        key=lambda item: len(str(item.get("content", "") if isinstance(item, dict) else getattr(item, "content", ""))),
        reverse=True,
    ):
        if total <= max_bytes:
            break
        content_value = block.get("content", "") if isinstance(block, dict) else getattr(block, "content", "")
        tool_use_id = block.get("tool_use_id", "unknown") if isinstance(block, dict) else getattr(block, "tool_use_id", "unknown")
        compacted = persist_large_output(str(tool_use_id), str(content_value))
        if isinstance(block, dict):
            block["content"] = compacted
        else:
            block.content = compacted
        total -= len(str(content_value)) - len(compacted)

    return messages


def write_transcript(messages: list[dict[str, Any]]) -> Path:
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    transcript_path = TRANSCRIPT_DIR / f"transcript_{int(time.time())}.jsonl"
    with transcript_path.open("w") as handle:
        for message in messages:
            handle.write(json.dumps(message, default=str) + "\n")
    return transcript_path


def summarize_history(messages: list[dict[str, Any]], client=None, model: str | None = None) -> str:
    if client is None:
        client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
    model = model or os.environ["MODEL_ID"]

    prompt = (
        "Summarize this conversation so the agent can continue after context compaction. "
        "Preserve the current goal, important findings, files changed or inspected, "
        "remaining work, user constraints, and any tool results needed to proceed.\n\n"
        f"{messages}"
    )
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    first_block = response.content[0] if response.content else ""
    return _block_text(first_block) or str(first_block)


def compact_history(messages: list[dict[str, Any]], client=None, model: str | None = None) -> list[dict[str, Any]]:
    # 压缩前先保存原始转录，方便之后核对摘要是否漏掉关键事实。
    write_transcript(messages)
    summary = summarize_history(messages, client=client, model=model)
    return [{"role": "user", "content": f"[Compacted]\n\n{summary}"}]


def reactive_compact(messages: list[dict[str, Any]], client=None, model: str | None = None) -> list[dict[str, Any]]:
    write_transcript(messages)
    tail_start = max(0, len(messages) - 5)
    # 响应式压缩保留最近尾部，让失败前的执行现场尽量还在模型眼前。
    if 0 < tail_start < len(messages):
        if _message_has_tool_use(messages[tail_start - 1]) and _is_tool_result_message(messages[tail_start]):
            tail_start -= 1

    older = messages[:tail_start]
    tail = messages[tail_start:]
    summary = summarize_history(older, client=client, model=model) if older else "No earlier history."
    return [{"role": "user", "content": f"[Reactive compact]\n\n{summary}"}] + tail
