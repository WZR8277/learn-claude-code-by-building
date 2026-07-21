# s03 Permission — 验证证据

**状态：** 已完成权限增量、自动化测试、离线演示、diff 审查、个人反思、单一提交、标签和公司飞书归档。

## 环境

- 日期：2026-07-21
- Python：3.12（Conda 环境 `LearnClaudeCode`）
- 网络：测试与演示均不调用真实模型或外部网络
- 副作用：权限演示不执行任何工具

## 自动化测试

```bash
PYTHONPATH=src "$CONDA_PREFIX/bin/python" -m unittest discover -s tests -v
```

结果：

```text
Ran 13 tests
OK
```

覆盖范围：

- 硬拒绝不询问用户，也不调用 handler；
- 规则命中后每次调用分别询问，允许与拒绝只影响当前调用；
- 拒绝结果保留原始 `tool_use_id`；
- `ask_user()` 只接受明确的 `y` / `yes`；
- s01 Agent Loop、s02 五工具与路径边界全部回归通过。

## 离线演示

演示直接构造四种权限输入，不执行真实工具：硬拒绝、询问后拒绝、询问后允许、普通直接允许。

```text
⛔ Blocked: 'sudo' is on the deny list
hard deny: False
ask -> deny: False
ask -> allow: True
normal allow: True
```

## 边界

本章的字符串规则只是权限管线教学示意。即使规则返回允许，文件工具仍受 `safe_path()` 约束；权限策略也不等于进程或操作系统级沙箱。

## 学习者观察

教学版以简单、显然的字符串规则展示权限管线；生产环境通常还需要确定性规则、结构化分析、上下文判断、模型风险复核、人工审批和系统级隔离。小模型可以做复杂输入的风险 double check，但不应成为唯一安全边界。详见 `reflection.md`。

## 归档证据

- Git 标签：`s03-permission`
- 飞书子文档：`https://trip.larkenterprise.com/wiki/DqXEw21KWiuzWDkCA6CcYzLAn4g`
- 公司父目录：`https://trip.larkenterprise.com/wiki/S8X8wpgTCio65Yk3C76ceTYMnBc`
