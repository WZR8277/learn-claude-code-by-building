import os

from anthropic import Anthropic

from .tool import TOOLS, TOOL_HANDLERS

# 系统提示词
SYSTEM = f"You are a coding agent at {os.getcwd()}. Use tools to solve tasks. Act, don't explain."


def agent_loop(messages: list, client=None) -> None:
    if client is None:
        client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
    model = os.environ["MODEL_ID"]

    while True:
        response = client.messages.create(
            model=model, system=SYSTEM, messages=messages,
            tools=TOOLS, max_tokens=8192
        )
        # 模型响应加入对话历史
        messages.append({"role": "assistant", "content": response.content})

        # 没有工具调用则直接返回
        if response.stop_reason != "tool_use":
            return

        # 执行工具获取工具调用结果
        result = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"\033[33m> {block.name}\033[0m")
                handler = TOOL_HANDLERS.get(block.name)
                output = handler(**block.input) if handler else f"Unknown: {block.name}"
                print(str(output)[:200])
                result.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output
                })

        messages.append({"role": "user", "content": result})
