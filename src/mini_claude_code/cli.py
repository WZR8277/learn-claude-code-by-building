"""Command-line entry point for the evolving harness."""
import os

from dotenv import load_dotenv

#处理模型配置
#如果用了自定义 base_url，就清掉可能干扰的官方 环境变量Anthropic token，确保 SDK 用当前 .env 里的 API key 和 base_url
load_dotenv(override=True)
if os.getenv("ANTHROPIC_BASE_URL"):
    os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)

from .loop import agent_loop
from .hooks import context_inject_hook, HOOKS, register_hook, trigger_hooks
from .tool import WORKDIR


if context_inject_hook not in HOOKS["UserPromptSubmit"]:
    register_hook("UserPromptSubmit", context_inject_hook)


try:
    import readline
    # macOS 的 libedit 在处理中文输入时有退格问题，这四行修复它
    readline.parse_and_bind('set bind-tty-special-chars off')
    readline.parse_and_bind('set input-meta on')
    readline.parse_and_bind('set output-meta on')
    readline.parse_and_bind('set convert-meta off')
except ImportError:
    pass


def main() -> None:
    print("mini-claude-code s04: Hooks ready")
    history = []
    while True:
        try:
            # 在终端里显示一个青色的输入提示
            query = input("\033[36mquery: >> \033[0m")
        except (EOFError, KeyboardInterrupt, OSError):
            break
        #  退出指令
        if query.strip().lower() in ("q", "exit", ""):
            break
        trigger_hooks("UserPromptSubmit", query, WORKDIR)
        #消息列表加入用户消息
        history.append({"role": "user", "content": query})

        #进入agent loop
        agent_loop(history)

        #获取最后一次模型响应的文本
        response = history[-1]["content"]

        # 每个 block 可能是 text，也可能是 tool_use 只打印text类型的block
        if isinstance(response, list):
            for block in response:
                if getattr(block, "type", None) == "text":
                    print(block.text)

        print()
