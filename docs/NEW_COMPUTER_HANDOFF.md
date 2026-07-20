# 新电脑接续指南

这份文档用于在另一台电脑恢复本学习项目。即使原 Codex 对话不可见，仓库中的 `AGENTS.md` 与 `.planning/` 也保存了项目目标、约束、路线图、研究结论和当前进度。

## 1. 克隆项目

使用拥有该私有仓库权限的 GitHub 账号：

```bash
mkdir -p ~/agentprojects
cd ~/agentprojects
git clone https://github.com/WZR8277/learn-claude-code-by-building.git
cd learn-claude-code-by-building
```

确认提交和工作区：

```bash
git log --oneline -5
git status --short --branch
git fetch --all --tags
git tag --list 's*' --sort=v:refname
```

开始任何新章节前，先按 [`docs/CROSS_COMPUTER_SYNC.md`](CROSS_COMPUTER_SYNC.md)
确认远程 tag 中已经完成到哪一章。不要只依赖本机 Codex 对话记忆来判断进度。

## 2. 恢复 Python 环境

项目使用 Conda 管理独立解释器，使用 uv 根据锁文件安装 Python 依赖。

```bash
conda env create -f environment.yml
conda activate LearnClaudeCode
uv pip install --python "$CONDA_PREFIX/bin/python" -r requirements.lock
uv pip install --python "$CONDA_PREFIX/bin/python" --no-deps -e .
```

如果新电脑尚未安装 uv：

```bash
python -m pip install --user uv
```

不要使用 `uv sync` 接管项目环境；本项目约定由 Conda 管理解释器和基础包，uv 只负责向指定 Conda Python 安装依赖。

## 3. 配置模型

复制配置模板：

```bash
cp .env.example .env
chmod 600 .env
```

然后在 `.env` 中填写新生成或安全保存的密钥：

```dotenv
ANTHROPIC_API_KEY=填写你的密钥
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
MODEL_ID=deepseek-v4-flash
```

`.env` 已被 Git 忽略，不会从旧电脑同步，也绝不能提交。曾经出现在聊天中的密钥应先轮换，再写入新电脑。

## 4. 验证环境

```bash
conda activate LearnClaudeCode
python -m pip check
pytest -q
python -m mini_claude_code
```

基线预期：依赖检查无冲突、测试通过、CLI 可启动并显示当前章节状态。

## 5. 恢复项目上下文

在新电脑的 Codex 中打开仓库根目录后，先让 Agent 完整读取：

1. `AGENTS.md`
2. `.planning/PROJECT.md`
3. `.planning/STATE.md`
4. `.planning/ROADMAP.md`
5. `.planning/REQUIREMENTS.md`
6. `.planning/research/SUMMARY.md`

可以直接发送以下开场提示：

> 请先执行跨电脑同步检查，读取 AGENTS.md 和 .planning 中的 PROJECT.md、STATE.md、ROADMAP.md、REQUIREMENTS.md、CROSS_COMPUTER_SYNC.md、FEISHU_SYNC.md、CODING_WORKFLOW.md、research/SUMMARY.md，恢复 Learn Claude Code by Building 项目上下文。严格遵守：这是 Agent 学习项目，不允许调用任何名称以 trn- 开头的 skill。先汇报远程最新 `sXX-*` tag、当前阶段、学习协议、环境状态和下一步。

如果全局尚未安装 GSD，可先安装并重启 Codex；项目级规划文件本身不依赖旧电脑的聊天记录。

## 6. 继续下一章

上下文恢复并完成环境验证后，发送：

> 根据远程 tags 判断下一章。先帮我梳理本章目标、核心控制流、代码阅读顺序、关键问题和完成标准；讨论清楚后，按 `.planning/CODING_WORKFLOW.md` 进入实现、测试、演示、个人观点、单章提交和飞书子文档流程。

每章固定遵循：

```text
同步 tags → 本章导读 → 阅读与讨论 → Codex 实现差量 → PyCharm diff 审查/讨论 → 测试/演示 → 个人观点 → 单章提交/标签 → 飞书子文档
```

## 7. 云端与本地内容边界

会随 Git 仓库同步：

- 源代码、测试和章节提交
- `AGENTS.md` 项目约束
- `.planning/` 中的 GSD 项目记忆
- Git tags, which are the cross-computer chapter completion markers
- 环境声明和依赖锁文件
- 本接续指南

不会随 Git 仓库同步：

- Codex 本地对话原文
- `.env` 和 API 密钥
- Conda 环境本体
- Git stash、未提交改动和 IDE 本地状态

s01 已完成并打上 `s01-agent-loop` tag。新电脑应从远程 tag 判断下一章，当前应继续 s02，除非远程已经出现更后的 `sXX-*` tag。

## 8. 飞书学习文档

飞书父文档按当前电脑环境选择：

- 在家：<https://jcneiirfaiic.feishu.cn/wiki/UDZJwVXukitwJ3kvOlecXYOMnng>
- 在公司：<https://trip.larkenterprise.com/wiki/S8X8wpgTCio65Yk3C76ceTYMnBc>

更新飞书父目录或创建章节子文档前，Agent 必须先询问用户当前是在家还是在公司。

章节子文档只在该章代码、测试、个人观点、提交和标签全部完成后创建。每章一个子文档，父文档维护目录和进度。
飞书子文档必须是美观、清晰、简洁的复习文档，不要直接上传本地 Markdown 记录拼接稿作为最终版本。

## 故障恢复

- Agent 不清楚项目目标：重新要求读取 `AGENTS.md` 和 `.planning/STATE.md`。
- GSD 找不到项目：确认当前目录是仓库根目录，并检查 `.planning/config.json`。
- 依赖不一致：激活 `LearnClaudeCode` 后按 `requirements.lock` 重新执行两条 `uv pip install`。
- 模型调用失败：只检查 `.env` 的三个变量是否存在，不要在聊天或日志中输出密钥。
- Git 出现意外改动：先运行 `git status` 和 `git diff`，不要使用破坏性 reset。
