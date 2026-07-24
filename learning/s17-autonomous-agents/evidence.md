# s17 Evidence

## 本地验证

已完成 S17 新增测试：

```sh
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_s17_autonomous_agents.py
```

结果：`4 passed in 0.53s`。

已完成相关章节回归：

```sh
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_s12_task_system.py tests/test_s15_agent_teams.py tests/test_s16_team_protocols.py tests/test_s17_autonomous_agents.py
```

结果：`27 passed in 0.54s`。

已完成当前未提交 diff 的全量回归：

```sh
PYTHONPATH=src .venv/bin/python -m pytest -q
```

结果：`110 passed in 0.80s`。

## 运行演示建议

可以在本地交互中尝试：

```text
Create 3 tasks on the board, then spawn alice and bob. Let them auto-claim and complete available work.
```

观察点：

- 队友没有收到 Lead 手动分配时，是否会在 IDLE 阶段自动认领任务；
- 已有 owner 的任务是否不会被其他队友二次认领；
- 有 blockedBy 的任务是否必须等依赖完成后才会被扫描出来；
- IDLE 阶段收到 `request_shutdown` 是否仍会回复 `shutdown_response`；
- Lead 是否能通过 async wake 或 `check_inbox` 看到队友 result。

## Commit Evidence

- Commit: pending
- Tag: pending
- Feishu child: pending
