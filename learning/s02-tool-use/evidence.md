# s02 Tool Use — 验证证据

**状态：** 实现、离线验证、PyCharm diff 审查、个人反思、单一提交、标签和公司飞书归档均已完成。

## 环境

- 日期：2026-07-21
- Python：3.12（Conda 环境 `LearnClaudeCode`）
- 网络：测试与演示均不调用真实模型或外部网络
- 文件副作用：文件工具演示只写入 `TemporaryDirectory`

## 自动化测试

可跨电脑复现的命令：

```bash
PYTHONPATH=src "$CONDA_PREFIX/bin/python" -m unittest discover -s tests -v
```

覆盖范围：

- s01 的停止条件、模型 seam 和 `tool_use_id` 关联回归；
- 五个工具定义与 `TOOL_HANDLERS` 的名称对应；
- 教程版写入、首次匹配编辑、限制行数读取和 glob；
- `safe_path()` 对路径穿越和符号链接逃逸的阻止；
- 多个工具按模型返回顺序执行并逐一关联 ID；
- 未知工具返回 `Unknown: <name>` 后继续 Agent Loop。

Codex 内置 Python 没有安装项目声明的 `anthropic` 和 `python-dotenv`，因此验证使用项目规定的 Conda `LearnClaudeCode` 环境。最终结果：

```text
Ran 9 tests
OK
```

## 安全离线演示

演示在系统临时目录中通过教程同款 handler 依次执行写入、编辑、读取和 glob：

```bash
PYTHONPATH=src "$CONDA_PREFIX/bin/python" -c 'import tempfile; from pathlib import Path; import mini_claude_code.tool as tools; temp=tempfile.TemporaryDirectory(); tools.WORKDIR=Path(temp.name).resolve(); print("handlers:", ", ".join(tools.TOOL_HANDLERS)); print(tools.run_write("demo/note.txt", "alpha\nbeta\n")); print(tools.run_edit("demo/note.txt", "beta", "gamma")); print(tools.run_read("demo/note.txt")); print(tools.run_glob("*/*.txt")); temp.cleanup()'
```

实际输出：

```text
handlers: bash, read_file, write_file, edit_file, glob
Wrote 11 bytes to demo/note.txt
Edited demo/note.txt
alpha
gamma
demo/note.txt
```

## 审查后补充

- 学习者个人观点：本章初步建立了路径校验和统一多工具处理的认识；真实工具管理还需要执行失败管理、沙箱、权限问询和描述优化。工具结果截断也与上下文预算有关，执行前还需要请求字段校验与合理缺省值兜底；这些应留在后续对应章节学习。详见 `reflection.md`。
- 最终测试结果：9 tests，OK。
- Commit：本文件所在提交（由 tag `s02-tool-use` 唯一解析）。
- Tag：`s02-tool-use`。
- Feishu：`https://trip.larkenterprise.com/wiki/MwfHwn0Lwi4b9XkWNNUcFUmgnth`。
