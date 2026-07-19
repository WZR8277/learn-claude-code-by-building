# Learn Claude Code by Building

通过 20 个连续章节，从零构建一个可运行的 mini Claude Code。学习主线参考：

- https://github.com/shareAI-lab/learn-claude-code
- 根目录新版教程 `s01_agent_loop` 到 `s20_comprehensive`

本项目不会复制 Claude Code 的正式内部实现，也不会逐字照抄教学仓库；目标是理解 Agent Harness 的核心机制，并形成自己的代码、观点和 Git 历史。

## 演进方式

- 代码始终在同一套 `src/mini_claude_code/` 上演进。
- 每章只引入一个清晰的机制。
- 每章完成一次提交，并创建对应 Git tag。
- 每章学习材料保存在 `learning/sXX-*/`，最终同步到飞书子文档。

## 当前状态

`s00`：仓库和学习协议初始化，尚未实现 Agent Loop。

## 本地准备

```bash
conda env create -f environment.yml
conda activate LearnClaudeCode
uv pip install --python "$CONDA_PREFIX/bin/python" -r requirements.lock
uv pip install --python "$CONDA_PREFIX/bin/python" --no-deps -e .
cp .env.example .env
```

Conda 负责独立的 Python 3.12 环境，`uv` 根据 `requirements.lock` 快速安装精确版本的 Python 依赖，并以 editable 模式安装当前项目。这里使用 `uv pip install` 而不是 `uv pip sync`，避免后者删除 Conda 管理但未列入 Python 依赖锁的基础包。项目已配置清华 PyPI 镜像；在 `.env` 中填写模型配置，`.env` 已被 Git 忽略。

以后进入项目先运行 `conda activate LearnClaudeCode`。依赖发生变化时，先重新生成 `requirements.lock`，再同步环境。

## 验证基线

```bash
python -m mini_claude_code
pytest -q
```

## 章节完成协议

```text
本章导读 → 阅读与讨论 → 实现 → 测试/演示 → 个人观点 → 单章提交 → 飞书子文档
```
