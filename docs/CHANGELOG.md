# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式,版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [v0.3.0] — 2026-10-26

### 新增

- **ch11-multi-db.md(434 行)** —— 多方言章节:MySQL 8.0 / Oracle / SQL Server 的语义地雷(隐式转换方向、空串语义、分页原子性、DDL 事务性)、索引模型差异、方言反模式、跨方言对照表、跨库协作模式选型。
- **`references/topic-index.md`** —— 从 84 术语扩到 99 术语,新增「多方言术语」小节。
- **`eval_civilian7.py --mode claude-api`** —— 让模型答 SQL,在真实 SQLite 上执行,和 reference SQL 的**结果集**对拍(执行准确率,不是字符串比对)。支持 `--context none|skill` 做 A/B、`--seed` 固定抽样、`--model` / `--api-sample`。
- **`eval_civilian7.py --mode baseline`** —— 修复后可用,reference SQL 可执行率 **95.6%**。
- **hook 内嵌 MCP 客户端** —— `post-write-auto-sync.py` 新增最小 MCP streamable-HTTP 客户端(initialize → notifications/initialized → tools/call),JSON 与 SSE 两种响应模式都支持。

### 变更

- **SKILL.md frontmatter** —— description 改为覆盖 4 个方言(`Use when writing or debugging PostgreSQL / MySQL / Oracle / SQL Server queries`);triggers 去掉与 description 重复的 `index decision`,新增 `MySQL / Oracle / MSSQL`;version → 0.3.0。
- **ch10** —— 新增 §7「多 DB 协作」,并把 §1-§6 的章节引用从 ch01-ch10 更新到 ch01-ch11。
- **Channel A 从「排队」改为「即写即同步」** —— hook 写完文件直接 `gbrain put`,**不再等下一次 session**;实测写文件 → brain 可查 ≈ 1 秒。queue 降级为兜底。
- **Channel A 三层降级** —— MCP over HTTP → gbrain CLI(`stdin` 传内容,避开 Windows 32KB 命令行上限)→ queue 文件。

### 修复

- **Windows hook 命令全部失效(根因修复)** —— Claude Code 用 `/usr/bin/bash -c "<cmd>"` 执行 hook,settings.json 里**未加引号**的 Windows 可执行路径(`C:\Python314\python.exe`)被 bash 当转义符吃掉反斜杠 → `command not found` → hook 静默不执行。11 条 hook 里 10 条是死的(含 `no-delete-gate.py` 删除护栏)。全部改为正斜杠。
- **hook payload 解析** —— 改为单次二进制读 + 显式 UTF-8 解码(不依赖 locale 编码),解析失败时落原始字节到 `~/.claude/.cache/post-write-auto-sync.payload.err` 便于诊断。
- **`reference_sql` 形态 bug** —— 题目里 `reference_sql` 有 str(238 题)和 dict(852 题)两种形态,原代码只处理 dict → `AttributeError` 崩溃。
- **reference SQL 多语句** —— `sqlite3.execute` 一次只能跑一条 → 16% 的题报 `You can only execute one statement at a time`。现按 `sqlite3.complete_statement` 拆分逐条执行。
- **SQLite 方言适配** —— 剥掉 `DELIMITER`(MySQL 客户端指令)与 `BEGIN/COMMIT/START TRANSACTION`(与 Python sqlite3 隐式事务冲突);`CREATE VIEW/TABLE` 前先 `DROP ... IF EXISTS`。
- **错误分类** —— 区分 `dialect_not_applicable`(方言专属构造)/ `expected_error`(题目**故意**触发约束违例)/ 真错误,避免把正常题算成坏题。

### 指标

| 指标 | v0.2 | v0.3 |
|---|---:|---:|
| index(每会话都付) | 98 tok | **100 tok** |
| load(触发时) | 1,908 tok | **2,005 tok** |
| 单次触发合计 | 2,006 tok | **2,105 tok** |
| validator 警告 | 0 | **0** |
| 章节数 | 10 | **11** |
| 章节正文行数 | 3,918 | **4,375** |
| 术语索引 | 84 | **99** |
| 评测题数 | 1,090 | **1,090** |
| 知识覆盖率 | 100% | **100%** |
| reference SQL 可执行率 | — | **95.6%** |

---

## [v0.2.0] — 2026-10-25

### 变更

按渐进式披露重构,降低触发消耗同时提高路由准确度。

- frontmatter:description 从 101 词缩到 22 词 + `Use when` 开头;19 个内联 triggers → `triggers:` 独立列表 5 条;补齐 `mutating` / `brain_first` / `when_to_use` / `version`。
- 12 大框架(85 行内联摘要,与 chapters 重复)→ 表格(保留结论 + 章节指针)。
- 新增 `## Gotchas` 段(8 条高频反模式)。
- Topic Index(125 行,含 34 行逐字重复)→ 去重 84 条 → `references/topic-index.md`。
- 「How to Use」与「调研/沉淀入口」整段重复 → 合并 → `references/retrieval.md`。
- Chapter Index 删「状态」列;Supporting Files 段与 Chapter Index 合并。
- 修正 Scope & Limits 3 处陈旧事实。

### 指标

| 层级 | v0.1 | v0.2 | 降幅 |
|---|---:|---:|---:|
| index | 231 tok | 98 tok | -57% |
| load | 5,503 tok | 1,908 tok | -65% |
| **单次触发合计** | **5,734 tok** | **2,006 tok** | **-65%** |

- root_cause:`routing` → `other`;verdict:`refuse` → `accept`;validator 警告 **11 条 → 0 条**。
- SKILL.md:412 行 / 19,894 B → 104 行 / 6,808 B(-66%)。

---

## [v2.2.0] — 2026-10-15

- 10 章成功 ingest 进 gbrain(default source,单 source 避免 source-guard)。
- 4 通道同步机制落地(PostToolUse hook / Cron / SessionStart 消费 / Manual)。
- 批量 ingest 分 3 批(ch01-04 / ch05-08 / ch09-10),每批 < 8MB。

> 命名说明:v2.0-v2.2 是**部署形态**的版本号(对应 evidence-skill 的 v2.x 体系);v0.1-v0.3 是**内容与成本**的版本号(对应 skill-forge 的优化序列)。v0.3 之后统一用 v0.x。

---

## [v1.0.0] — 2026-10-14

- 10 章完整版 + 4 辅助文件(cheatsheet / glossary / patterns / INDEX)。

## [v0.1.0] — 2026-10-14

- Phase 2:ch01 语法 + ch07 PG 特有 + ch08 索引性能 + 4 辅助文件。

---

[Unreleased]: https://github.com/kizemo/sql-skill/compare/v0.3.0...HEAD
[v0.3.0]: https://github.com/kizemo/sql-skill/compare/v0.2.0...v0.3.0
[v0.2.0]: https://github.com/kizemo/sql-skill/compare/v0.1.0...v0.2.0
[v0.1.0]: https://github.com/kizemo/sql-skill/releases/tag/v0.1.0
