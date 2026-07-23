# s16 Evidence

## 本地验证

已完成语法级验证：

```sh
python -m py_compile src/mini_claude_code/team.py src/mini_claude_code/tool.py src/mini_claude_code/cli.py tests/test_s15_agent_teams.py tests/test_s16_team_protocols.py
```

结果：通过。

已完成自动化测试：

```sh
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_s15_agent_teams.py tests/test_s16_team_protocols.py
```

结果：`13 passed in 0.54s`。

```sh
PYTHONPATH=src .venv/bin/python -m pytest -q
```

结果：`104 passed in 0.51s`。

## 运行演示建议

可以在本地交互中尝试：

```text
Spawn alice as a backend dev. Ask her to create a file. Then request her shutdown.
```

观察点：

- `request_shutdown` 是否创建 `ProtocolState`；
- 发给队友的邮箱消息是否带有 `metadata.request_id`；
- 队友 idle 后是否能收到 `shutdown_request` 并回复 `shutdown_response`；
- Lead 读取 inbox 后是否把对应请求状态更新为 `approved`。

## Commit Evidence

- Commit: `5dbfa15`
- Tag: `s16-team-protocols`
- Home Feishu child: `https://jcneiirfaiic.feishu.cn/wiki/JaUYwV00qitUSikgOlQcLwjBnvd`
- Parent directory updated: S16 is marked complete and S17 is marked as the next chapter.
