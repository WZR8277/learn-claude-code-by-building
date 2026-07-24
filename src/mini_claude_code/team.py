"""S15/S16 Agent Team: file inboxes plus request-response protocols."""

from __future__ import annotations

import json
import os
import threading
import time
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

from anthropic import Anthropic

from .task_system import claim_task, complete_task, list_tasks, scan_unclaimed_tasks


ToolHandler = Callable[..., str]

WORKDIR = Path.cwd()
MAILBOX_DIR = WORKDIR / ".mailboxes"
TEAMMATE_MAX_ROUNDS = 10
DEFAULT_IDLE_POLL_SECONDS = 5.0
DEFAULT_IDLE_TIMEOUT_SECONDS = 60.0
PROTOCOL_RESPONSE_TYPES = {
    "shutdown_response",
    "plan_approval_response",
}
TEAMMATE_PROTOCOL_TYPES = {
    "shutdown_request",
    "plan_approval_response",
}


@dataclass
class TeamMessage:
    """一个写入邮箱的结构化消息。教学版只保留最核心字段。"""

    from_agent: str
    to_agent: str
    content: str
    type: str = "message"
    ts: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

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
        metadata: dict[str, Any] | None = None,
    ) -> TeamMessage:
        """向目标 Agent 的邮箱追加一条消息。"""
        message = TeamMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            type=msg_type,
            ts=time.time(),
            metadata=metadata or {},
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


@dataclass
class ProtocolState:
    """Lead 和队友之间一次请求-响应协议的状态记录。"""

    request_id: str
    type: str
    sender: str
    target: str
    status: str
    payload: str
    created_at: float = field(default_factory=time.time)


pending_requests: dict[str, ProtocolState] = {}


def new_request_id() -> str:
    # 教学版沿用上游随机 ID；这里只用它演示 request/response 的关联键。
    return f"req_{random.randint(0, 999999):06d}"


def _expected_response_type(request_type: str) -> str | None:
    return {
        "shutdown": "shutdown_response",
        "plan_approval": "plan_approval_response",
    }.get(request_type)


def match_response(response_type: str, request_id: str, approve: bool) -> str:
    """把协议回复关联回原始请求，并做最小类型校验。

    S16 的关键不是“收到回复就更新”，而是必须同时匹配 request_id 和协议类型。
    这样 plan_approval 的回复不会误伤 shutdown 请求。
    """
    state = pending_requests.get(request_id)
    if state is None:
        return f"Unknown request_id: {request_id}"

    expected = _expected_response_type(state.type)
    if expected != response_type:
        return f"Type mismatch for {request_id}: expected {expected}, got {response_type}"

    if state.status != "pending":
        return f"Request {request_id} already {state.status}"

    state.status = "approved" if approve else "rejected"
    return f"{state.type} {state.status} ({request_id})"


def consume_lead_inbox(route_protocol: bool = True) -> list[dict[str, Any]]:
    """统一读取 Lead 邮箱，并先路由协议回复。

    S15 的 `check_inbox` 和 CLI 唤醒如果各自直接 read_inbox，就可能把协议消息读走，
    但忘了更新 pending_requests。S16 用这个函数统一入口，避免状态和消息脱节。
    """
    messages = BUS.read_inbox("lead")
    if route_protocol:
        for message in messages:
            message_type = message.get("type", "")
            metadata = message.get("metadata", {})
            request_id = metadata.get("request_id", "")
            if request_id and message_type in PROTOCOL_RESPONSE_TYPES:
                match_response(
                    message_type,
                    request_id,
                    bool(metadata.get("approve", False)),
                )
    return messages


def _teammate_tools() -> list[dict[str, Any]]:
    """队友只拿最小工具集。

    S17 新增 list/claim/complete task，让队友可以在空闲时自己看任务板、
    认领任务、完成任务，而不是所有分配都依赖 Lead 手动 send_message。
    """
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
        {
            "name": "submit_plan",
            "description": "Submit a plan to Lead for approval.",
            "input_schema": {
                "type": "object",
                "properties": {"plan": {"type": "string"}},
                "required": ["plan"],
            },
        },
        {
            "name": "list_tasks",
            "description": "List all tasks on the shared task board.",
            "input_schema": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "claim_task",
            "description": "Claim a pending task whose dependencies are completed.",
            "input_schema": {
                "type": "object",
                "properties": {"task_id": {"type": "string"}},
                "required": ["task_id"],
            },
        },
        {
            "name": "complete_task",
            "description": "Mark an in-progress task as completed.",
            "input_schema": {
                "type": "object",
                "properties": {"task_id": {"type": "string"}},
                "required": ["task_id"],
            },
        },
    ]


def _format_inbox_payload(messages: list[dict[str, Any]]) -> str:
    return f"<inbox>{json.dumps(messages, ensure_ascii=False)}</inbox>"


def _handle_teammate_protocol_message(
    name: str,
    message: dict[str, Any],
    messages: list[dict[str, Any]],
) -> bool:
    """处理队友收到的协议消息，返回 True 表示队友应该退出。"""
    message_type = message.get("type", "message")
    metadata = message.get("metadata", {})
    request_id = metadata.get("request_id", "")

    if message_type == "shutdown_request":
        # 关机是 S16 的典型握手：Lead 发请求，队友确认后再退出线程。
        BUS.send(
            name,
            "lead",
            "Shutting down gracefully.",
            "shutdown_response",
            {"request_id": request_id, "approve": True},
        )
        return True

    if message_type == "plan_approval_response":
        approved = bool(metadata.get("approve", False))
        if approved:
            messages.append({"role": "user", "content": "[Plan approved] Proceed with the task."})
        else:
            messages.append({
                "role": "user",
                "content": f"[Plan rejected] Feedback: {message.get('content', '')}",
            })
    return False


def _drain_teammate_inbox(name: str, messages: list[dict[str, Any]]) -> bool:
    """把队友 inbox 拆成协议消息和普通消息；返回 True 表示收到关机请求。"""
    inbox_messages = BUS.read_inbox(name)
    ordinary_messages = []
    for message in inbox_messages:
        if message.get("type") in TEAMMATE_PROTOCOL_TYPES:
            should_stop = _handle_teammate_protocol_message(name, message, messages)
            if should_stop:
                return True
        else:
            ordinary_messages.append(message)

    if ordinary_messages:
        messages.append({"role": "user", "content": _format_inbox_payload(ordinary_messages)})
    return False


def _run_teammate_list_tasks() -> str:
    tasks = list_tasks()
    if not tasks:
        return "No tasks."
    return "\n".join(
        f"{task.id}: {task.subject} [{task.status}]"
        for task in tasks
    )


def _idle_poll(
    name: str,
    messages: list[dict[str, Any]],
    idle_poll_seconds: float,
    idle_timeout_seconds: float,
) -> str:
    """S17 的自治 idle 阶段。

    返回值：
    - "work"：收到了普通消息，或自动认领到任务，需要回到 WORK 阶段；
    - "shutdown"：idle 期间收到 shutdown_request，完成握手后退出；
    - "timeout"：一段时间内既无消息也无可认领任务，队友自然退出。
    """
    deadline = time.monotonic() + idle_timeout_seconds
    while time.monotonic() < deadline:
        time.sleep(idle_poll_seconds)

        # inbox 优先级高于任务板，因为里面可能是 shutdown 或审批回执。
        if BUS.peek(name):
            if _drain_teammate_inbox(name, messages):
                return "shutdown"
            return "work"

        # 没有新消息时，队友才去看共享任务板，找可开始且无人认领的任务。
        for task in scan_unclaimed_tasks():
            result = claim_task(task.id, owner=name)
            if result.startswith("Claimed "):
                messages.append({
                    "role": "user",
                    "content": (
                        f"<auto-claimed>Task {task.id}: "
                        f"{task.subject}</auto-claimed>"
                    ),
                })
                return "work"

            # 竞争认领失败时继续看下一个任务；教学版没有文件锁，所以这里要容忍失败。
            if "already owned" in result or "cannot claim" in result:
                continue

        if messages and messages[-1].get("role") == "user":
            return "work"
    return "timeout"


def _teammate_submit_plan(from_name: str, plan: str) -> str:
    """队友向 Lead 提交计划审批请求。

    教学版只演示协议流转，不做真正的工具执行门控；也就是说，
    是否等 approval 再动手仍依赖模型遵守协议。
    """
    request_id = new_request_id()
    pending_requests[request_id] = ProtocolState(
        request_id=request_id,
        type="plan_approval",
        sender=from_name,
        target="lead",
        status="pending",
        payload=plan,
    )
    BUS.send(
        from_name,
        "lead",
        plan,
        "plan_approval_request",
        {"request_id": request_id},
    )
    return f"Plan submitted ({request_id}). Waiting for approval..."


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
    idle_poll_seconds: float = DEFAULT_IDLE_POLL_SECONDS,
    idle_timeout_seconds: float = DEFAULT_IDLE_TIMEOUT_SECONDS,
) -> None:
    """队友自己的迷你 Agent Loop。

    它和 Lead 使用不同 messages；只有通过 MessageBus 才能共享信息。
    S17 把生命周期改成 WORK -> IDLE -> WORK/SHUTDOWN：
    WORK 负责调用模型和执行工具，IDLE 负责等 inbox 或自动认领任务。
    """
    client = client or Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
    model = model or os.environ["MODEL_ID"]
    system = (
        f"You are '{name}', a {role}. Use tools to complete tasks. "
        "You can list and claim tasks from the board. "
        "Use submit_plan before risky work. Check inbox for protocol messages."
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
        "submit_plan": lambda plan: _teammate_submit_plan(name, plan),
        "list_tasks": _run_teammate_list_tasks,
        "claim_task": lambda task_id: claim_task(task_id, owner=name),
        "complete_task": complete_task,
    }

    round_count = 0
    should_stop = False
    while not should_stop and round_count < TEAMMATE_MAX_ROUNDS:
        # 压缩后 messages 可能只剩摘要；教学版没有真实 system prompt 保留机制，
        # 所以每个 WORK 周期开始时做一次轻量身份重注入。
        if len(messages) <= 3:
            messages.insert(0, {
                "role": "user",
                "content": f"<identity>You are '{name}', role: {role}. Continue your work.</identity>",
            })

        # 队友每轮先读取自己的邮箱；协议消息会被 handler 消费，普通消息注入上下文。
        should_stop = _drain_teammate_inbox(name, messages)
        if should_stop:
            break

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

        round_count += 1
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            # S17：一轮 WORK 自然结束后进入 IDLE。IDLE 可能收到消息、自动认领任务，
            # 也可能超时并让队友进入 SHUTDOWN。
            idle_result = _idle_poll(name, messages, idle_poll_seconds, idle_timeout_seconds)
            if idle_result == "work":
                continue
            should_stop = True
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
    idle_poll_seconds: float = DEFAULT_IDLE_POLL_SECONDS,
    idle_timeout_seconds: float = DEFAULT_IDLE_TIMEOUT_SECONDS,
) -> str:
    """启动一个自治队友线程，并立即把控制权还给 Lead。"""
    with _teammate_lock:
        if name in active_teammates:
            return f"Teammate '{name}' already exists"
        active_teammates[name] = True

    thread = threading.Thread(
        target=_run_teammate_loop,
        args=(
            name,
            role,
            prompt,
            handlers,
            client,
            model,
            idle_poll_seconds,
            idle_timeout_seconds,
        ),
        daemon=True,
    )
    thread.start()
    return f"Teammate '{name}' spawned as {role} (autonomous)"


def run_send_message(to: str, content: str) -> str:
    BUS.send("lead", to, content)
    return f"Sent to {to}"


def run_check_inbox() -> str:
    messages = consume_lead_inbox(route_protocol=True)
    if not messages:
        return "(inbox empty)"
    return "\n".join(
        _format_lead_inbox_line(message)
        for message in messages
    )


def _format_lead_inbox_line(message: dict[str, Any]) -> str:
    metadata = message.get("metadata", {})
    request_id = metadata.get("request_id", "")
    type_suffix = f" {message.get('type', 'message')}"
    if request_id:
        type_suffix += f" req:{request_id}"
    return f"  [{message['from']}][{type_suffix.strip()}] {message['content'][:200]}"


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


def run_request_shutdown(teammate: str) -> str:
    request_id = new_request_id()
    pending_requests[request_id] = ProtocolState(
        request_id=request_id,
        type="shutdown",
        sender="lead",
        target=teammate,
        status="pending",
        payload="",
    )
    BUS.send(
        "lead",
        teammate,
        "Please shut down gracefully.",
        "shutdown_request",
        {"request_id": request_id},
    )
    return f"Shutdown request sent to {teammate} (req: {request_id})"


def run_request_plan(teammate: str, task: str) -> str:
    BUS.send("lead", teammate, f"Please submit a plan for: {task}")
    return f"Asked {teammate} to submit a plan"


def run_review_plan(request_id: str, approve: bool, feedback: str = "") -> str:
    state = pending_requests.get(request_id)
    if state is None:
        return f"Request {request_id} not found"
    if state.type != "plan_approval":
        return f"Request {request_id} is {state.type}, not plan_approval"
    if state.status != "pending":
        return f"Request {request_id} already {state.status}"

    state.status = "approved" if approve else "rejected"
    BUS.send(
        "lead",
        state.sender,
        feedback or ("Approved" if approve else "Rejected"),
        "plan_approval_response",
        {"request_id": request_id, "approve": approve},
    )
    return f"Plan {'approved' if approve else 'rejected'} ({request_id})"


def reset_team_state(mailbox_dir: Path | None = None) -> None:
    """测试用：清空队友注册表，并可切换邮箱目录。"""
    global BUS
    with _teammate_lock:
        active_teammates.clear()
    pending_requests.clear()
    if mailbox_dir is not None:
        BUS = MessageBus(mailbox_dir)
