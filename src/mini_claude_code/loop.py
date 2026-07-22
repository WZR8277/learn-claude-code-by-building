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
from .error_recovery import (
    CONTINUATION_PROMPT,
    DEFAULT_MAX_TOKENS,
    ESCALATED_MAX_TOKENS,
    MAX_OUTPUT_CONTINUATIONS,
    create_recovery_state,
    is_prompt_too_long_error,
    with_retry,
)
from .hooks import HOOKS, large_output_hook, log_hook, register_hook, summary_hook, trigger_hooks
from .memory import consolidate_memories, extract_memories, load_memories, read_memory_index
from .permission import permission_hook
from .system_prompt import get_system_prompt, update_prompt_context
from .tool import TOOLS, TOOL_HANDLERS

MAX_STOP_CONTINUATIONS = 1
TODO_REMINDER_AFTER = 3


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
    recovery_state = create_recovery_state(model)
    max_tokens = DEFAULT_MAX_TOKENS
    stop_continuations = 0
    rounds_since_todo = 0
    # S09：索引进 system，完整记忆只按需注入当前 user turn，避免每轮常驻大段历史。
    memories_content = load_memories(messages, client=client, model=model)
    # S10：system prompt 来自真实运行态，可在工具轮次后重新组装。
    prompt_context = update_prompt_context(
        os.getcwd(),
        enabled_tools=tuple(TOOL_HANDLERS.keys()),
        memory_index=read_memory_index(),
    )
    system = get_system_prompt(prompt_context)

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
            # S11：429/529 在 with_retry 内部有界重试；prompt 太长等结构性错误交给外层。
            response = with_retry(
                lambda: client.messages.create(
                    model=recovery_state.current_model,
                    system=system,
                    messages=request_messages,
                    tools=TOOLS,
                    max_tokens=max_tokens,
                ),
                recovery_state,
            )
        except Exception as exc:
            if is_prompt_too_long_error(exc):
                if recovery_state.has_attempted_reactive_compact:
                    # 已经做过一次响应式压缩还失败，说明继续压缩只会空转，直接明确结束。
                    messages.append({"role": "assistant", "content": [{
                        "type": "text",
                        "text": "[Error] Context too large after reactive compact.",
                    }]})
                    return
                # 模型明确拒绝过长 prompt 时，只做一次补救压缩，避免失败循环空转。
                print("\033[33m[reactive compact]\033[0m")
                messages[:] = reactive_compact(messages, client=client, model=model)
                recovery_state.has_attempted_reactive_compact = True
                continue
            messages.append({"role": "assistant", "content": [{
                "type": "text",
                "text": f"[Error] {type(exc).__name__}: {str(exc)[:200]}",
            }]})
            return

        if response.stop_reason == "max_tokens":
            if not recovery_state.has_escalated_output:
                # 输出被截断不是输入太长；首次恢复只提高回答预算，messages 保持原样重试。
                # 这样不会把半截 assistant 回答写进历史，也不会触发任何工具副作用。
                max_tokens = ESCALATED_MAX_TOKENS
                recovery_state.has_escalated_output = True
                continue

            # 扩容后仍截断，才保留这段输出并追加续写提示，让模型从中断处继续。
            messages.append({"role": "assistant", "content": response.content})
            if recovery_state.output_continuations < MAX_OUTPUT_CONTINUATIONS:
                recovery_state.output_continuations += 1
                messages.append({"role": "user", "content": CONTINUATION_PROMPT})
                continue
            return

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
            prompt_context = update_prompt_context(
                os.getcwd(),
                enabled_tools=tuple(TOOL_HANDLERS.keys()),
                memory_index=read_memory_index(),
            )
            system = get_system_prompt(prompt_context)


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
