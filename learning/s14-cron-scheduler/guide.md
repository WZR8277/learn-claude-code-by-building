# s14：Cron Scheduler

## 本章要解决的问题

S13 解决的是“慢工具不要阻塞主 loop”，但触发仍然来自用户或模型的当前回合。S14 新增 Cron Scheduler，让 Agent 可以按时间表自动生产工作：到点后把 prompt 放进队列，再在 Agent 空闲时交付给 `agent_loop`。

本章重点不是系统级常驻任务，也不是完整生产调度器，而是理解调度与执行解耦：时间判断由 scheduler 线程负责，消息历史仍由主 Agent Loop 单一写入。

## 相比 s13 的精确增量

本章只增加：

- `CronJob` 数据结构：`id / cron / prompt / recurring / durable`；
- 五段式 cron 表达式匹配：支持 `*`、`*/N`、`N`、`N-M`、`N,M`；
- `validate_cron()`：注册前做教学版格式校验；
- `schedule_job()`、`cancel_job()`、`run_list_crons()`；
- `cron_queue`：调度线程写入、agent loop 消费；
- `cron_scheduler_loop()`：独立 daemon 线程每秒检查一次；
- `queue_processor_loop()`：Agent 空闲时自动拉起一轮；
- `.scheduled_tasks.json`：仅保存 durable 任务定义；
- 三个工具：`schedule_cron`、`list_crons`、`cancel_cron`。

它不是生产级调度系统：本章没有进程外常驻、错过时间补偿、复杂优先级、分布式锁、任务超时或系统 crontab 集成。

## 核心数据流

```text
schedule_cron 工具
  -> scheduled_jobs / .scheduled_tasks.json

cron_scheduler_loop
  -> cron_matches(now)
  -> cron_queue.append(job)

queue_processor_loop
  -> agent idle
  -> agent_loop()

agent_loop
  -> consume_cron_queue()
  -> messages.append("[Scheduled] ...")
```

关键点是：调度线程不直接调用模型，也不直接改 messages。它只是把到点任务放进队列；真正写入对话历史的仍然是 `agent_loop`。

## diff 审查关注点

1. `cron_scheduler.py` 是否把 cron 匹配、持久化、队列和线程边界集中管理。
2. `agent_loop` 是否只消费已触发队列，并把 `[Scheduled] prompt` 作为 user message 注入。
3. `schedule_cron/list_crons/cancel_cron` 是否只是工具层包装，没有提前引入后续 Agent Team 机制。
4. `cron_lock` 是否保护任务表、队列和 last-fired 标记。
5. `agent_lock` 是否只用于避免 queue processor 和用户输入同时启动 agent turn。
6. 测试是否使用确定性时间，不依赖真实等待几分钟。

## 当前审查状态

- [x] 已同步远端 `origin/main` 和 tags。
- [x] 已确认最新章节标签为 `s13-background-tasks`，当前应继续 `s14 Cron Scheduler`。
- [x] 已用本地上游副本比较 `s14_cron_scheduler` 与 `s13_background_tasks`。
- [x] 已按 diff-first 流程实现未提交代码和测试。
- [x] 学习者在 PyCharm 中审查 diff 并提出问题或确认。
- [x] 学习者完成本章个人观点。
- [x] 最终测试通过。
- [x] commit、tag 和飞书归档。
