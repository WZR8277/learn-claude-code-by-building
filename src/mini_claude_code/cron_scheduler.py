"""Cron-style scheduled work for the evolving agent loop."""

from __future__ import annotations

import json
import random
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable


DURABLE_PATH = Path.cwd() / ".scheduled_tasks.json"


@dataclass
class CronJob:
    # S14 的定时任务只是“到点后要注入给 Agent 的一条 prompt”，不是系统进程任务。
    id: str
    cron: str
    prompt: str
    recurring: bool
    durable: bool


# scheduled_jobs 是任务定义表；cron_queue 是“已经到点、等待交付”的任务队列。
# 两者会被 scheduler 线程、queue processor 线程、用户工具调用同时访问，所以用同一把锁保护。
scheduled_jobs: dict[str, CronJob] = {}
cron_queue: list[CronJob] = []
cron_lock = threading.Lock()
# agent_lock 不保护 cron 数据，而是保护 agent_loop：避免用户输入和定时任务同时跑一轮模型调用。
agent_lock = threading.Lock()
# 记录每个任务上一次触发到哪一分钟，避免同一分钟内 scheduler 每秒轮询时重复入队。
_last_fired: dict[str, str] = {}
_scheduler_started = False


def _cron_field_matches(field: str, value: int) -> bool:
    """Match one cron field. Teaching version supports *, */N, N, N-M, and N,M."""
    if field == "*":
        return True
    if field.startswith("*/"):
        step = int(field[2:])
        return step > 0 and value % step == 0
    if "," in field:
        return any(_cron_field_matches(part.strip(), value) for part in field.split(","))
    if "-" in field:
        low, high = field.split("-", 1)
        return int(low) <= value <= int(high)
    return value == int(field)


def _is_int_in_bounds(text: str, low: int, high: int) -> bool:
    return text.isdigit() and low <= int(text) <= high


def _validate_step_field(field: str) -> str | None:
    """Validate */N. N only needs to be a positive integer in this teaching version."""
    step = field[2:]
    if not step.isdigit():
        return f"Invalid step: {field}"
    if int(step) <= 0:
        return f"Step must be > 0: {field}"
    return None


def _validate_range_field(field: str, low: int, high: int) -> str | None:
    """Validate N-M and make sure both ends are inside the field bounds."""
    start, end = field.split("-", 1)
    if not start.isdigit() or not end.isdigit():
        return f"Invalid range: {field}"

    start_value = int(start)
    end_value = int(end)
    if start_value < low or start_value > high or end_value < low or end_value > high:
        return f"Range {field} out of bounds [{low}-{high}]"
    if start_value > end_value:
        return f"Range start > end: {field}"
    return None


def _validate_list_field(field: str, low: int, high: int) -> str | None:
    """Validate N,M,... by validating each comma-separated part as a normal field."""
    for part in field.split(","):
        error = _validate_cron_field(part.strip(), low, high)
        if error:
            return error
    return None


def _validate_single_number_field(field: str, low: int, high: int) -> str | None:
    """Validate a single numeric cron value."""
    if not field.isdigit():
        return f"Invalid field: {field}"
    if not _is_int_in_bounds(field, low, high):
        return f"Value {int(field)} out of bounds [{low}-{high}]"
    return None


def cron_matches(cron_expr: str, dt: datetime) -> bool:
    """Return whether a five-field cron expression matches a datetime."""
    fields = cron_expr.strip().split()
    if len(fields) != 5:
        return False

    minute, hour, day_of_month, month, day_of_week = fields
    # Python weekday(): Monday=0；cron 里 Sunday=0，所以这里转成 cron 的星期编号。
    cron_day_of_week = (dt.weekday() + 1) % 7

    minute_ok = _cron_field_matches(minute, dt.minute)
    hour_ok = _cron_field_matches(hour, dt.hour)
    month_ok = _cron_field_matches(month, dt.month)
    dom_ok = _cron_field_matches(day_of_month, dt.day)
    dow_ok = _cron_field_matches(day_of_week, cron_day_of_week)

    if not (minute_ok and hour_ok and month_ok):
        return False

    # 标准 cron 语义：日和星期都被约束时，二者满足其一即可触发。
    dom_free = day_of_month == "*"
    dow_free = day_of_week == "*"
    if dom_free and dow_free:
        return True
    if dom_free:
        return dow_ok
    if dow_free:
        return dom_ok
    return dom_ok or dow_ok


def _validate_cron_field(field: str, low: int, high: int) -> str | None:
    """Validate one cron field against its numeric bounds.

    这一层只负责分发语法类型：
    - * 表示任意值
    - */N 表示按步长匹配
    - N,M 表示多个候选值
    - N-M 表示闭区间
    - N 表示单个数字
    """
    if field == "*":
        return None
    if field.startswith("*/"):
        return _validate_step_field(field)
    if "," in field:
        return _validate_list_field(field, low, high)
    if "-" in field:
        return _validate_range_field(field, low, high)
    return _validate_single_number_field(field, low, high)


def validate_cron(cron_expr: str) -> str | None:
    """Validate five cron fields. Returns an error string, or None when valid."""
    fields = cron_expr.strip().split()
    if len(fields) != 5:
        return f"Expected 5 fields, got {len(fields)}"

    bounds = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 6)]
    names = ["minute", "hour", "day-of-month", "month", "day-of-week"]
    for field, (low, high), name in zip(fields, bounds, names):
        error = _validate_cron_field(field, low, high)
        if error:
            return f"{name}: {error}"
    return None


def save_durable_jobs() -> None:
    """Persist durable job definitions. The scheduler thread itself is not persistent."""
    # durable 只保存“任务定义”，不保存线程、队列、上次触发状态。
    # 进程退出后调度器会停；下次启动时重新读取这些定义继续检查时间。
    durable_jobs = [asdict(job) for job in scheduled_jobs.values() if job.durable]
    DURABLE_PATH.write_text(json.dumps(durable_jobs, indent=2, ensure_ascii=False))


def load_durable_jobs() -> None:
    """Load durable job definitions from disk and skip invalid records."""
    if not DURABLE_PATH.exists():
        return
    try:
        records = json.loads(DURABLE_PATH.read_text())
    except Exception:
        return

    with cron_lock:
        for record in records:
            try:
                job = CronJob(**record)
            except TypeError:
                continue
            # 教学版对损坏记录采取跳过策略，避免一个坏任务让整个 scheduler 无法启动。
            if validate_cron(job.cron):
                continue
            scheduled_jobs[job.id] = job


def schedule_job(
    cron: str,
    prompt: str,
    recurring: bool = True,
    durable: bool = True,
) -> CronJob | str:
    """Register a cron job. Returns CronJob on success, or an error string."""
    error = validate_cron(cron)
    if error:
        return error

    # 上游教学版使用随机 ID；这里保持章节行为，不升级成更强的 ID 生成策略。
    job = CronJob(
        id=f"cron_{random.randint(0, 999999):06d}",
        cron=cron,
        prompt=prompt,
        recurring=recurring,
        durable=durable,
    )
    with cron_lock:
        scheduled_jobs[job.id] = job
    # 只有 durable=True 的任务写入磁盘；session-only 任务只存在于内存。
    if durable:
        save_durable_jobs()
    return job


def cancel_job(job_id: str) -> str:
    """Cancel a registered job."""
    with cron_lock:
        job = scheduled_jobs.pop(job_id, None)
    if job is None:
        return f"Job {job_id} not found"
    if job.durable:
        save_durable_jobs()
    return f"Cancelled {job_id}"


def _minute_marker(now: datetime) -> str:
    """Return the de-duplication key for one cron minute."""
    # 用日期+分钟作为去重标记：同一分钟内不重复触发，第二天同一分钟仍然可以触发。
    return now.strftime("%Y-%m-%d %H:%M")


def _is_due_for_marker(job: CronJob, now: datetime, marker: str) -> bool:
    """Check both cron matching and same-minute de-duplication."""
    if not cron_matches(job.cron, now):
        return False
    return _last_fired.get(job.id) != marker


def _enqueue_fired_job(job: CronJob, marker: str) -> None:
    """Record that a job fired and hand it to the agent-side queue."""
    cron_queue.append(job)
    _last_fired[job.id] = marker


def _retire_if_one_shot(job: CronJob) -> bool:
    """Remove one-shot jobs after firing. Returns whether durable storage changed."""
    if job.recurring:
        return False
    # one-shot 任务触发后从任务定义表删除；已经入队的 job 仍会被 agent_loop 消费。
    scheduled_jobs.pop(job.id, None)
    return job.durable


def _collect_due_jobs_locked(now: datetime) -> tuple[list[CronJob], bool]:
    """Find due jobs, enqueue them, and update in-memory cron state.

    Caller must hold cron_lock. The return value separates “业务结果”
    from “是否需要写磁盘”，让 fire_due_jobs 不再混着处理所有细节。
    """
    fired: list[CronJob] = []
    should_save = False
    marker = _minute_marker(now)

    for job in list(scheduled_jobs.values()):
        if not _is_due_for_marker(job, now, marker):
            continue
        _enqueue_fired_job(job, marker)
        fired.append(job)
        should_save = _retire_if_one_shot(job) or should_save

    return fired, should_save


def fire_due_jobs(now: datetime) -> list[CronJob]:
    """Move due jobs into the queue once per minute marker."""
    # 这个函数是 scheduler 的主业务动作：找出到点任务并放进交付队列。
    # 具体的“匹配、去重、入队、one-shot 删除”拆到 helper 里，避免一坨流程硬读。
    with cron_lock:
        fired, should_save = _collect_due_jobs_locked(now)

    if should_save:
        save_durable_jobs()
    return fired


def cron_scheduler_loop(
    *,
    poll_seconds: float = 1,
    now_func: Callable[[], datetime] = datetime.now,
) -> None:
    """Daemon producer: check time and enqueue due jobs."""
    while True:
        time.sleep(poll_seconds)
        try:
            # scheduler 只负责“生产队列项”，不调用模型、不修改 messages。
            # 这样定时检查和 Agent 执行可以解耦。
            fire_due_jobs(now_func())
        except Exception as exc:
            print(f"\033[31m[cron error] {exc}\033[0m")


def start_cron_scheduler() -> None:
    """Start the scheduler once for the current process."""
    global _scheduler_started
    if _scheduler_started:
        return
    # CLI 启动时加载 durable 任务，然后启动一个 daemon 线程轮询时间。
    # daemon=True 意味着主进程退出时这个线程不会阻止退出。
    load_durable_jobs()
    threading.Thread(target=cron_scheduler_loop, daemon=True).start()
    _scheduler_started = True


def consume_cron_queue() -> list[CronJob]:
    """Consume fired jobs. The agent loop is the single writer of conversation history."""
    # 队列在这里一次性清空：被消费出来的 job 之后会被 agent_loop 注入 messages。
    with cron_lock:
        fired = list(cron_queue)
        cron_queue.clear()
    return fired


def has_cron_queue() -> bool:
    with cron_lock:
        return bool(cron_queue)


def _try_acquire_agent_for_cron() -> bool:
    """Try to reserve the shared conversation for scheduled work delivery."""
    if not has_cron_queue():
        return False
    # acquire(False) 是“试着拿锁”：如果用户正在交互触发 agent_loop，就先跳过。
    return agent_lock.acquire(blocking=False)


def _deliver_cron_if_still_needed(run_agent_turn: Callable[[], None]) -> None:
    """Run one agent turn if queued cron work still exists after acquiring the lock."""
    # 拿锁前后各检查一次队列：拿锁期间用户那边可能已经消费过队列。
    if has_cron_queue():
        # run_agent_turn 内部会调用 agent_loop；agent_loop 再消费 cron_queue 并写入消息。
        run_agent_turn()


def queue_processor_loop(run_agent_turn: Callable[[], None], poll_seconds: float = 0.2) -> None:
    """Deliver queued cron work by starting an agent turn only when the agent is idle."""
    while True:
        time.sleep(poll_seconds)
        if not _try_acquire_agent_for_cron():
            continue
        try:
            _deliver_cron_if_still_needed(run_agent_turn)
        finally:
            agent_lock.release()


def start_queue_processor(run_agent_turn: Callable[[], None]) -> None:
    threading.Thread(target=queue_processor_loop, args=(run_agent_turn,), daemon=True).start()


def run_schedule_cron(
    cron: str,
    prompt: str,
    recurring: bool = True,
    durable: bool = True,
) -> str:
    result = schedule_job(cron, prompt, recurring, durable)
    if isinstance(result, str):
        return f"Error: {result}"
    return f"Scheduled {result.id}: '{cron}' -> {prompt}"


def run_list_crons() -> str:
    with cron_lock:
        jobs = list(scheduled_jobs.values())
    if not jobs:
        return "No cron jobs. Use schedule_cron to add one."

    lines = []
    for job in jobs:
        recurrence = "recurring" if job.recurring else "one-shot"
        durability = "durable" if job.durable else "session"
        lines.append(
            f"  {job.id}: '{job.cron}' -> {job.prompt[:40]} "
            f"[{recurrence}, {durability}]"
        )
    return "\n".join(lines)


def run_cancel_cron(job_id: str) -> str:
    return cancel_job(job_id)


def reset_cron_state() -> None:
    """Reset module state for deterministic tests."""
    global _scheduler_started
    with cron_lock:
        scheduled_jobs.clear()
        cron_queue.clear()
        _last_fired.clear()
    _scheduler_started = False
