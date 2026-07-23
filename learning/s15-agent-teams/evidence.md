# s15 Evidence

## 本地验证

已完成语法级验证：

```sh
python -m py_compile src/mini_claude_code/team.py src/mini_claude_code/tool.py src/mini_claude_code/cli.py src/mini_claude_code/background.py tests/test_s15_agent_teams.py
```

结果：通过。

已完成自动化测试：

```sh
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_s15_agent_teams.py
```

结果：`5 passed in 0.46s`。

```sh
PYTHONPATH=src .venv/bin/python -m pytest -q
```

结果：`96 passed in 0.53s`。

## 运行演示建议

可以在本地交互中尝试：

```text
Spawn alice as a backend developer. Ask her to create a file called schema.sql with a users table.
```

观察点：

- `.mailboxes/lead.jsonl` 是否出现队友写给 Lead 的结果；
- CLI 是否在队友结果到达后自动唤醒 Lead；
- Lead 的 history 是否收到 `[Inbox]` 形式的 user message。

## Commit Evidence

学习者已完成 PyCharm diff 审查和本章反思。

待提交、打标签、推送和 Feishu 归档后补充最终证据。
