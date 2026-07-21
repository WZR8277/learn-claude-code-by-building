import os

from anthropic import Anthropic

from .hooks import HOOKS, large_output_hook, log_hook, register_hook, summary_hook, trigger_hooks
from .permission import permission_hook
from .tool import TOOLS, TOOL_HANDLERS

# 系统提示词
SYSTEM = f"You are a coding agent at {os.getcwd()}. All destructive operations require user approval."
MAX_STOP_CONTINUATIONS = 1


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

    while True:
        response = client.messages.create(
            model=model, system=SYSTEM, messages=messages,
            tools=TOOLS, max_tokens=8192
        )
        # 模型响应加入对话历史
        messages.append({"role": "assistant", "content": response.content})

        # 没有工具调用时触发 Stop Hook；Hook 可有限度要求模型继续。
        if response.stop_reason != "tool_use":
            stop_result = trigger_hooks("Stop", messages)
            if stop_result and stop_continuations < MAX_STOP_CONTINUATIONS:
                stop_continuations += 1
                messages.append({"role": "user", "content": stop_result})
                continue
            return

        # 每个工具调用先经过 PreToolUse Hook，再交给 s02 的分发表执行。
        result = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            print(f"\033[36m> {block.name}\033[0m")
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
            print(str(output)[:200])
            result.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": output
            })

        messages.append({"role": "user", "content": result})
