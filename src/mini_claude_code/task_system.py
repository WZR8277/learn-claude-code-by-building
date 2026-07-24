"""S12 file-persisted task graph."""

from __future__ import annotations

import json
import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path


WORKDIR = Path.cwd()
TASKS_DIR = WORKDIR / ".tasks"
TASK_STATUSES = {"pending", "in_progress", "completed"}


@dataclass
class Task:
    id: str
    subject: str
    description: str
    status: str
    owner: str | None
    blockedBy: list[str]


def _ensure_tasks_dir() -> None:
    TASKS_DIR.mkdir(parents=True, exist_ok=True)


def _task_path(task_id: str) -> Path:
    # 教学版任务 ID 由系统生成；这里仍然限制文件名，避免工具参数变成任意路径。
    safe_id = task_id.replace("/", "-").replace("..", "-")
    return TASKS_DIR / f"{safe_id}.json"


def _new_task_id() -> str:
    return f"task_{int(time.time())}_{random.randint(0, 9999):04d}"


def _task_to_json(task: Task) -> str:
    return json.dumps(asdict(task), indent=2, ensure_ascii=False)


def save_task(task: Task) -> None:
    """把任务状态写回磁盘；S12 的跨会话恢复就靠这些 JSON 文件。"""
    _ensure_tasks_dir()
    _task_path(task.id).write_text(_task_to_json(task))


def load_task(task_id: str) -> Task:
    """读取单个任务；调用方负责决定缺失任务要报错还是视为 blocked。"""
    data = json.loads(_task_path(task_id).read_text())
    blocked_by = data.get("blockedBy") or []
    return Task(
        id=str(data["id"]),
        subject=str(data["subject"]),
        description=str(data.get("description") or ""),
        status=str(data.get("status") or "pending"),
        owner=data.get("owner"),
        blockedBy=[str(dep) for dep in blocked_by],
    )


def list_tasks() -> list[Task]:
    if not TASKS_DIR.exists():
        return []
    return [load_task(path.stem) for path in sorted(TASKS_DIR.glob("task_*.json"))]


def create_task(
    subject: str,
    description: str = "",
    blockedBy: list[str] | None = None,
) -> Task:
    """创建 pending 任务。

    blockedBy 是“我依赖谁”：只有这些上游任务都 completed，当前任务才能 claim。
    本章只演示依赖检查，不做 DAG 环检测、锁、release 或后台执行。
    """
    task = Task(
        id=_new_task_id(),
        subject=subject,
        description=description,
        status="pending",
        owner=None,
        blockedBy=list(blockedBy or []),
    )
    save_task(task)
    return task


def get_task(task_id: str) -> str:
    return _task_to_json(load_task(task_id))


def can_start(task_id: str) -> bool:
    """判断任务是否可开始。

    缺失依赖被视为 blocked，而不是忽略；否则写错依赖 ID 会让任务错误地提前开始。
    """
    task = load_task(task_id)
    for dep_id in task.blockedBy:
        try:
            dependency = load_task(dep_id)
        except FileNotFoundError:
            return False
        if dependency.status != "completed":
            return False
    return True


def blocked_dependencies(task: Task) -> list[str]:
    """返回尚未完成的上游依赖，供 claim 失败时解释原因。"""
    blocked = []
    for dep_id in task.blockedBy:
        try:
            dependency = load_task(dep_id)
        except FileNotFoundError:
            blocked.append(dep_id)
            continue
        if dependency.status != "completed":
            blocked.append(dep_id)
    return blocked


def claim_task(task_id: str, owner: str = "agent") -> str:
    """pending -> in_progress，并写入 owner。

    S17 开始 owner 不只是展示字段：自治队友会靠它判断任务是否已经被别人拿走。
    教学版仍没有文件锁，所以这里先做最小的“读到已有 owner 就拒绝”。
    """
    task = load_task(task_id)
    if task.status != "pending":
        return f"Task {task_id} is {task.status}, cannot claim"
    if task.owner:
        return f"Task {task_id} already owned by {task.owner}"

    blocked = blocked_dependencies(task)
    if blocked:
        return f"Blocked by: {blocked}"

    task.owner = owner
    task.status = "in_progress"
    save_task(task)
    return f"Claimed {task.id} ({task.subject})"


def scan_unclaimed_tasks() -> list[Task]:
    """扫描可由自治队友认领的任务。

    S17 的“自己看板，自己认领”只看三个条件：
    1. 状态仍是 pending；
    2. 没有 owner；
    3. blockedBy 指向的上游任务都已经 completed。
    """
    return [
        task
        for task in list_tasks()
        if task.status == "pending" and not task.owner and can_start(task.id)
    ]


def complete_task(task_id: str) -> str:
    """in_progress -> completed，并报告被当前任务解锁的下游任务。"""
    task = load_task(task_id)
    if task.status != "in_progress":
        return f"Task {task_id} is {task.status}, cannot complete"

    task.status = "completed"
    save_task(task)

    # 完成一个任务后扫描所有 pending 任务，找出所有依赖现在都满足的下游任务。
    unblocked = [
        candidate.subject
        for candidate in list_tasks()
        if candidate.status == "pending" and candidate.blockedBy and can_start(candidate.id)
    ]
    message = f"Completed {task.id} ({task.subject})"
    if unblocked:
        message += f"\nUnblocked: {', '.join(unblocked)}"
    return message


def run_create_task(subject: str, description: str = "", blockedBy: list[str] | None = None) -> str:
    task = create_task(subject, description, blockedBy)
    deps = f" (blockedBy: {', '.join(task.blockedBy)})" if task.blockedBy else ""
    return f"Created {task.id}: {task.subject}{deps}"


def run_list_tasks() -> str:
    tasks = list_tasks()
    if not tasks:
        return "No tasks. Use create_task to add some."

    lines = []
    icons = {"pending": "○", "in_progress": "●", "completed": "✓"}
    for task in tasks:
        owner = f" [{task.owner}]" if task.owner else ""
        deps = f" (blockedBy: {', '.join(task.blockedBy)})" if task.blockedBy else ""
        lines.append(
            f"{icons.get(task.status, '?')} {task.id}: {task.subject} "
            f"[{task.status}]{owner}{deps}"
        )
    return "\n".join(lines)


def run_get_task(task_id: str) -> str:
    try:
        return get_task(task_id)
    except FileNotFoundError:
        return f"Error: Task {task_id} not found"


def run_claim_task(task_id: str) -> str:
    try:
        return claim_task(task_id, owner="agent")
    except FileNotFoundError:
        return f"Error: Task {task_id} not found"


def run_complete_task(task_id: str) -> str:
    try:
        return complete_task(task_id)
    except FileNotFoundError:
        return f"Error: Task {task_id} not found"
