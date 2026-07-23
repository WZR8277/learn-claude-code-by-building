"""Command-line entry point for the evolving harness."""
import os
import threading
import time

from dotenv import load_dotenv

#处理模型配置
#如果用了自定义 base_url，就清掉可能干扰的官方 环境变量Anthropic token，确保 SDK 用当前 .env 里的 API key 和 base_url
load_dotenv(override=True)
if os.getenv("ANTHROPIC_BASE_URL"):
    os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)

from .loop import agent_loop
from .background import collect_background_results, has_completed_background_result
from .cron_scheduler import agent_lock, start_cron_scheduler, start_queue_processor
from .hooks import context_inject_hook, HOOKS, register_hook, trigger_hooks
from .team import BUS, active_teammates, format_lead_inbox_messages, has_lead_inbox
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
    print("mini-claude-code s15: Agent Teams ready")
    history = []
    had_teammates = False

    def print_latest_assistant_text() -> None:
        if not history:
            return
        latest = history[-1]
        if not isinstance(latest, dict) or latest.get("role") != "assistant":
            return
        content = latest.get("content", "")
        if isinstance(content, str):
            print(content)
            return
        for block in content:
            if getattr(block, "type", None) == "text":
                print(block.text)
            elif isinstance(block, dict) and block.get("type") == "text":
                print(block.get("text", ""))

    def run_scheduled_turn() -> None:
        # queue processor 已持有 agent_lock。
        # 注意：这里复用的就是下面交互循环的同一个 history。
        # 它不额外 append 用户输入，而是让 agent_loop 开头消费 cron_queue，
        # 把定时任务注入到同一条会话历史里，再继续一轮模型调用。
        agent_loop(history)
        print_latest_assistant_text()
        print()

    def build_async_wake_message() -> str:
        """把队友 inbox 和后台任务结果合并成一次 Lead 唤醒消息。"""
        parts = []
        inbox_text = format_lead_inbox_messages(BUS.read_inbox("lead"))
        if inbox_text:
            parts.append(inbox_text)
        parts.extend(collect_background_results())
        return "\n".join(parts)

    def run_async_turn() -> None:
        # 队友结果和后台任务结果没有原始用户输入，但仍然需要交给 Lead 一轮。
        wake_message = build_async_wake_message()
        if not wake_message:
            return
        history.append({"role": "user", "content": wake_message})
        print("\033[33m[wake: async team/background result]\033[0m")
        agent_loop(history)
        print_latest_assistant_text()
        print()

    def async_wake_processor() -> None:
        nonlocal had_teammates
        while True:
            time.sleep(1)
            has_async_result = has_lead_inbox() or has_completed_background_result()
            if has_async_result and agent_lock.acquire(blocking=False):
                try:
                    run_async_turn()
                finally:
                    agent_lock.release()

            # 只在队友全部结束且结果已被 Lead 消费后提示一次，避免终端刷屏。
            if active_teammates:
                had_teammates = True
            elif had_teammates and not has_lead_inbox() and not has_completed_background_result():
                print("\033[32m[all teammates done]\033[0m")
                had_teammates = False

    # S14 的两个后台循环：
    # 1. scheduler：按时间把 due job 放进 cron_queue
    # 2. queue processor：发现 cron_queue 非空且 Agent 空闲时，用同一个 history 继续跑一轮 agent_loop
    start_cron_scheduler()
    start_queue_processor(run_scheduled_turn)
    # S15：队友和后台任务完成时也能唤醒 Lead，不必等用户下一次输入 check_inbox。
    threading.Thread(target=async_wake_processor, daemon=True).start()

    while True:
        try:
            # 在终端里显示一个青色的输入提示
            query = input("\033[36mquery: >> \033[0m")
        except (EOFError, KeyboardInterrupt, OSError):
            break
        #  退出指令
        if query.strip().lower() in ("q", "exit", ""):
            break
        # 用户输入触发的 agent_loop 也要拿同一把 agent_lock，
        # 避免定时任务交付和用户手动提问同时修改 history。
        with agent_lock:
            trigger_hooks("UserPromptSubmit", query, WORKDIR)
            #消息列表加入用户消息
            history.append({"role": "user", "content": query})

            #进入agent loop
            agent_loop(history)

        #获取最后一次模型响应的文本
        print_latest_assistant_text()

        print()
