import os
from copy import deepcopy

from anthropic import Anthropic

from .compact import (
    CONTEXT_LIMIT,
    compact_history,
    estimate_size,
    micro_compact,
    reactive_compact,
    snip_compact,
    tool_result_budget,
)
from .hooks import HOOKS, large_output_hook, log_hook, register_hook, summary_hook, trigger_hooks
from .memory import consolidate_memories, extract_memories, load_memories, read_memory_index
from .permission import permission_hook
from .skills import build_system
from .tool import TOOLS, TOOL_HANDLERS

MAX_STOP_CONTINUATIONS = 1
TODO_REMINDER_AFTER = 3
MAX_REACTIVE_RETRIES = 1


if permission_hook not in HOOKS["PreToolUse"]:
    register_hook("PreToolUse", permission_hook)
if log_hook not in HOOKS["PreToolUse"]:
    register_hook("PreToolUse", log_hook)
if large_output_hook not in HOOKS["PostToolUse"]:
    register_hook("PostToolUse", large_output_hook)
if summary_hook not in HOOKS["Stop"]:
    register_hook("Stop", summary_hook)


def agent_loop(messages: list, client=None) -> None:
    if client is None:
        client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
    model = os.environ["MODEL_ID"]
    stop_continuations = 0
    rounds_since_todo = 0
    reactive_retries = 0
    # S09：索引进 system，完整记忆只按需注入当前 user turn，避免每轮常驻大段历史。
    memory_index = read_memory_index()
    memories_content = load_memories(messages, client=client, model=model)
    system = build_system(os.getcwd(), memory_index=memory_index)

    while True:
        pre_compress = deepcopy(messages)
        # s05 的 TODO 提醒只影响当前会话上下文，不会持久化为任务系统。
        if rounds_since_todo >= TODO_REMINDER_AFTER and messages:
            messages.append({"role": "user", "content": "<reminder>Update your todos.</reminder>"})
            rounds_since_todo = 0

        # S08 在模型调用前先缩减上下文；这仍然是会话内整理，不是长期记忆。
        messages[:] = tool_result_budget(messages)
        messages[:] = snip_compact(messages)
        messages[:] = micro_compact(messages)
        if estimate_size(messages) > CONTEXT_LIMIT:
            print("\033[33m[auto compact]\033[0m")
            messages[:] = compact_history(messages, client=client, model=model)

        try:
            request_messages = messages
            if memories_content:
                request_messages = _inject_memories(messages, memories_content)
            response = client.messages.create(
                model=model, system=system, messages=request_messages,
                tools=TOOLS, max_tokens=8192
            )
        except Exception as exc:
            error = str(exc).lower()
            if (
                ("prompt_too_long" in error or "too many tokens" in error)
                and reactive_retries < MAX_REACTIVE_RETRIES
            ):
                # 模型明确拒绝过长 prompt 时，只做一次补救压缩，避免失败循环空转。
                print("\033[33m[reactive compact]\033[0m")
                messages[:] = reactive_compact(messages, client=client, model=model)
                reactive_retries += 1
                continue
            raise

        reactive_retries = 0
        # 模型响应加入对话历史
        messages.append({"role": "assistant", "content": response.content})

        # 没有工具调用时触发 Stop Hook；Hook 可有限度要求模型继续。
        if response.stop_reason != "tool_use":
            stop_result = trigger_hooks("Stop", messages)
            if stop_result and stop_continuations < MAX_STOP_CONTINUATIONS:
                stop_continuations += 1
                messages.append({"role": "user", "content": stop_result})
                continue
            # S09：最终停止后再提取，且用压缩前快照，尽量避免从摘要里二次学习失真内容。
            extract_memories(pre_compress, client=client, model=model)
            consolidate_memories(client=client, model=model)
            return

        rounds_since_todo += 1
        # 每个工具调用先经过 PreToolUse Hook，再交给 s02 的分发表执行。
        result = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            print(f"\033[36m> {block.name}\033[0m")
            if block.name == "compact":
                # compact 是 loop 内置控制工具；保留本轮 tool_use/result，避免产生孤儿 tool_result。
                compacted = compact_history(messages, client=client, model=model)
                messages[:] = compacted + [
                    {"role": "assistant", "content": response.content},
                    {
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": "[Compacted. Conversation history has been summarized.]",
                        }],
                    },
                ]
                result = []
                break

            blocked = trigger_hooks("PreToolUse", block)
            if blocked:
                result.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(blocked)
                })
                continue

            handler = TOOL_HANDLERS.get(block.name)
            output = handler(**block.input) if handler else f"Unknown: {block.name}"
            trigger_hooks("PostToolUse", block, output)
            if block.name == "todo_write":
                rounds_since_todo = 0
            print(str(output)[:200])
            result.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": output
            })

        if result:
            messages.append({"role": "user", "content": result})


def _inject_memories(messages: list, memories_content: str) -> list:
    request_messages = list(messages)
    for index in range(len(request_messages) - 1, -1, -1):
        message = request_messages[index]
        if message.get("role") == "user" and isinstance(message.get("content"), str):
            request_messages[index] = {
                **message,
                "content": memories_content + "\n\n" + message["content"],
            }
            break
    return request_messages
