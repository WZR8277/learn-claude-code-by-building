# Chapter Records

每章建立一个目录 `sXX-short-name/`，包含：

- `guide.md`：本章问题、核心原理、代码落点、验收标准和思考题。
- `reflection.md`：学习者的原始观点，以及整理后的通顺版本。
- `evidence.md`：测试命令、运行结果、commit hash、tag 和主要文件变化。

章节完成后，将三份材料整合为对应的飞书 Wiki 子文档。

跨电脑学习时，章节完成状态以远程 Git tag 为准。开始新章节前先执行
`git fetch --all --tags` 并阅读 [`docs/CROSS_COMPUTER_SYNC.md`](../docs/CROSS_COMPUTER_SYNC.md)，
避免两台电脑基于不同本地记忆重复或跳过章节。
