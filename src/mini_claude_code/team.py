"""S15 Agent Team: file inboxes plus teammate background loops."""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from anthropic import Anthropic


ToolHandler = Callable[..., str]

WORKDIR = Path.cwd()
MAILBOX_DIR = WORKDIR / ".mailboxes"
TEAMMATE_MAX_ROUNDS = 10


@dataclass
class TeamMessage:
    """一个写入邮箱的结构化消息。教学版只保留最核心字段。"""

    from_agent: str
    to_agent: str
    content: str
    type: str = "message"
    ts: float = 0.0

    def to_json_line(self) -> str:
        payload = asdict(self)
        # 上游教程使用 from/to；dataclass 字段避开 Python 关键字后，在落盘时再转回协议名。
        payload["from"] = payload.pop("from_agent")
        payload["to"] = payload.pop("to_agent")
        return json.dumps(payload, ensure_ascii=False) + "\n"


class MessageBus:
    """基于文件的简单消息总线，每个 Agent 一个 JSONL 收件箱。"""

    def __init__(self, mailbox_dir: Path | None = None) -> None:
        self.mailbox_dir = mailbox_dir or MAILBOX_DIR
        self.mailbox_dir.mkdir(parents=True, exist_ok=True)

    def inbox_path(self, agent: str) -> Path:
        # Agent 名会变成文件名；这里做最小净化，避免把邮箱写到目录外。
        safe_name = agent.replace("/", "_").replace("..", "_")
        return self.mailbox_dir / f"{safe_name}.jsonl"

    def send(
        self,
        from_agent: str,
        to_agent: str,
        content: str,
        msg_type: str = "message",
    ) -> TeamMessage:
        """向目标 Agent 的邮箱追加一条消息。"""
        message = TeamMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            type=msg_type,
            ts=time.time(),
        )
        with self.inbox_path(to_agent).open("a", encoding="utf-8") as inbox:
            inbox.write(message.to_json_line())
        return message

    def read_inbox(self, agent: str) -> list[dict[str, Any]]:
        """读取并删除邮箱。

        这是消费式读取：Lead 或队友看到消息后，消息就从文件系统消失。
        教学版故意保持简单；生产系统需要文件锁避免并发读写丢消息。
        """
        inbox = self.inbox_path(agent)
        if not inbox.exists():
            return []

        messages = []
        for line in inbox.read_text(encoding="utf-8").splitlines():
            if line.strip():
                messages.append(json.loads(line))
        inbox.unlink()
        return messages

    def peek(self, agent: str) -> bool:
        """只判断邮箱是否有内容，不消费消息。CLI poller 用它决定是否唤醒 Lead。"""
        inbox = self.inbox_path(agent)
        return inbox.exists() and inbox.stat().st_size > 0


BUS = MessageBus()
active_teammates: dict[str, bool] = {}
_teammate_lock = threading.Lock()


def _teammate_tools() -> list[dict[str, Any]]:
    """队友只拿最小工具集，体现 S15 的教学重点：能工作、能发消息。"""
    return [
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
            "name": "send_message",
            "description": "Send a message to another agent.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["to", "content"],
            },
        },
    ]


def _extract_last_text(messages: list[dict[str, Any]]) -> str:
    """从队友历史里拿最后一段文本，作为完成后发给 Lead 的摘要。"""
    for message in reversed(messages):
        if message.get("role") != "assistant":
            continue
        content = message.get("content", "")
        if isinstance(content, str) and content.strip():
            return content
        if isinstance(content, list):
            for block in content:
                if getattr(block, "type", None) == "text":
                    return block.text
                if isinstance(block, dict) and block.get("type") == "text":
                    return block.get("text", "")
    return "Done."


def _run_teammate_loop(
    name: str,
    role: str,
    prompt: str,
    handlers: dict[str, ToolHandler],
    client: Any | None = None,
    model: str | None = None,
) -> None:
    """队友自己的迷你 Agent Loop。

    它和 Lead 使用不同 messages；只有通过 MessageBus 才能共享信息。
    这正是 S15 和 S06 一次性 subagent 的差别。
    """
    client = client or Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
    model = model or os.environ["MODEL_ID"]
    system = (
        f"You are '{name}', a {role}. Use tools to complete tasks. "
        "Send results via send_message to 'lead'."
    )
    messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]

    teammate_handlers = {
        "bash": handlers["bash"],
        "read_file": handlers["read_file"],
        "write_file": handlers["write_file"],
        "send_message": lambda to, content: (
            BUS.send(name, to, content),
            "Sent",
        )[1],
    }

    for _ in range(TEAMMATE_MAX_ROUNDS):
        # 队友每轮先读取自己的邮箱，让 Lead 或其他队友可以异步补充信息。
        inbox_messages = BUS.read_inbox(name)
        if inbox_messages:
            messages.append({
                "role": "user",
                "content": f"<inbox>{json.dumps(inbox_messages, ensure_ascii=False)}</inbox>",
            })

        try:
            response = client.messages.create(
                model=model,
                system=system,
                messages=messages[-20:],
                tools=_teammate_tools(),
                max_tokens=8_000,
            )
        except Exception as exc:
            messages.append({
                "role": "assistant",
                "content": f"[Error] {type(exc).__name__}: {str(exc)[:200]}",
            })
            break

        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            break

        tool_results = []
        for block in response.content:
            if getattr(block, "type", None) != "tool_use":
                continue
            handler = teammate_handlers.get(block.name)
            output = handler(**block.input) if handler else f"Unknown tool: {block.name}"
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": str(output),
            })
        messages.append({"role": "user", "content": tool_results})

    BUS.send(name, "lead", _extract_last_text(messages), "result")
    with _teammate_lock:
        active_teammates.pop(name, None)


def spawn_teammate_thread(
    name: str,
    role: str,
    prompt: str,
    handlers: dict[str, ToolHandler],
    client: Any | None = None,
    model: str | None = None,
) -> str:
    """启动一个队友线程，并立即把控制权还给 Lead。"""
    with _teammate_lock:
        if name in active_teammates:
            return f"Teammate '{name}' already exists"
        active_teammates[name] = True

    thread = threading.Thread(
        target=_run_teammate_loop,
        args=(name, role, prompt, handlers, client, model),
        daemon=True,
    )
    thread.start()
    return f"Teammate '{name}' spawned as {role}"


def run_send_message(to: str, content: str) -> str:
    BUS.send("lead", to, content)
    return f"Sent to {to}"


def run_check_inbox() -> str:
    messages = BUS.read_inbox("lead")
    if not messages:
        return "(inbox empty)"
    return "\n".join(
        f"  [{message['from']}] {message['content'][:200]}"
        for message in messages
    )


def format_lead_inbox_messages(messages: list[dict[str, Any]]) -> str:
    """把 Lead 收到的队友消息整理成一条 user message 注入 history。"""
    if not messages:
        return ""
    lines = [
        f"From {message['from']}: {message['content'][:200]}"
        for message in messages
    ]
    return "[Inbox]\n" + "\n".join(lines)


def has_lead_inbox() -> bool:
    return BUS.peek("lead")


def reset_team_state(mailbox_dir: Path | None = None) -> None:
    """测试用：清空队友注册表，并可切换邮箱目录。"""
    global BUS
    with _teammate_lock:
        active_teammates.clear()
    if mailbox_dir is not None:
        BUS = MessageBus(mailbox_dir)
