# sql-skill v2.2 — 通用 SQL 专业度 Skill

> **企业 PostgreSQL 视角的通用 SQL 知识沉淀**,与 [evidence-skill](https://github.com/kizemo/evidence-skill) 业务侧严格互补。
> 10 章完整版 + 4 辅助文件 + 4 通道动态同步 + gbrain RAG 增强(2026-10-15)

[![GitHub](https://img.shields.io/badge/GitHub-kizemo%2Fsql--skill-blue)](https://github.com/kizemo/sql-skill)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-blue)](https://www.postgresql.org/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-blueviolet)](https://claude.com/claude-code)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 一、sql-skill 是什么

`sql-skill` 是一个**通用 SQL 编写专业度 Skill**,沉淀企业 PostgreSQL 视角的 SQL 知识(语法 / 索引 / JOIN / 窗口 / CTE / 聚合 / 集合 / 反模式),让 Claude / OpenClaw agent 写 SQL 更专业、更准确。

**与 [evidence-skill](https://github.com/kizemo/evidence-skill) 互补**:
- **sql-skill**:PostgreSQL 通用视角(10 章,~5161 行)
- **evidence-skill**:Evidence BI / 中文 PG schema / nginx / FDW / MCP 业务侧(18 章)

### 1.1 v2.2 核心能力

| 维度 | v2.2 实现 |
|---|---|
| **知识覆盖** | 10 章 + 4 辅助文件 + 8 篇 luke 关键章节(~5161 行 + 252K luke 引用) |
| **检索方式** | **双模式**:gbrain semantic recall + Read+Grep 全文检索 |
| **新增知识同步** | **4 通道**:PostToolUse hook / Cron / Agent 主动 / Manual |
| **evidence-skill 联动** | ch10 边界固化,业务侧雷区走 evidence-skill |

### 1.2 10 章索引

| # | 章节 | 主题 | 行数 |
|---|---|---|---|
| 1 | [ch01-grammar.md](sql-skill/chapters/ch01-grammar.md) | SQL 语法铁律(执行顺序 / 别名 / NULL / 风格) | 256 |
| 2 | [ch02-joins.md](sql-skill/chapters/ch02-joins.md) | JOIN 7 种 + 性能差异 | 450 |
| 3 | [ch03-window-functions.md](sql-skill/chapters/ch03-window-functions.md) | 窗口函数(OVER / RANK / LAG-LEAD / 帧) | 488 |
| 4 | [ch04-cte-recursion.md](sql-skill/chapters/ch04-cte-recursion.md) | CTE / 递归 CTE / 物化 | 454 |
| 5 | [ch05-aggregates.md](sql-skill/chapters/ch05-aggregates.md) | 聚合 / GROUP BY / HAVING / FILTER | 448 |
| 6 | [ch06-set-ops.md](sql-skill/chapters/ch06-set-ops.md) | 集合操作(UNION / INTERSECT / EXCEPT) | 352 |
| 7 | [ch07-pg-specific.md](sql-skill/chapters/ch07-pg-specific.md) | PG 特有(JSONB / array / GIN / FDW / 中文 schema) | 322 |
| 8 | [ch08-indexes-perf.md](sql-skill/chapters/ch08-indexes-perf.md) | 索引与性能 | 405 |
| 9 | [ch09-antipatterns.md](sql-skill/chapters/ch09-antipatterns.md) | SQL 反模式综合(7 类 25+) | 429 |
| 10 | [ch10-evidence-bridge.md](sql-skill/chapters/ch10-evidence-bridge.md) | SQL Agent 范式 + evidence-skill 协作 | 314 |
| — | [SKILL.md](sql-skill/SKILL.md) | skill 入口 + 12 framework + chapter index | — |
| — | [cheatsheet.md](sql-skill/supporting/cheatsheet.md) | 13 决策表 + 18 关键经验 | — |
| — | [glossary.md](sql-skill/supporting/glossary.md) | 关键术语 | — |
| — | [patterns.md](sql-skill/supporting/patterns.md) | 8 模式 + 反模式总表 | — |

---

## 二、部署方法

### 2.1 方式 A:本地 Claude Code 部署(推荐)

#### 步骤 1:克隆仓库

```bash
git clone https://github.com/kizemo/sql-skill.git
cd sql-skill
```

#### 步骤 2:把 sql-skill 复制到 Obsidian vault(可选,用于 Read+Grep 模式)

```bash
# 推荐:放在 Obsidian SQL 子 vault 的 08-sql-skill/ 目录
cp -r sql-skill/ E:/obsidian/SQL/08-sql-skill/

# Obsidian 打开 vault,即可看到 10 章 + 4 辅助文件
```

#### 步骤 3:Claude Code 配置 SKILL.md

Claude Code 自动加载以下位置:
- `~/.claude/skills/<name>/SKILL.md`(用户全局)
- `<project>/.claude/skills/<name>/SKILL.md`(项目级)

```bash
# 推荐:用户全局安装
mkdir -p ~/.claude/skills/sql-skill
cp -r sql-skill/* ~/.claude/skills/sql-skill/

# 验证
ls ~/.claude/skills/sql-skill/
# 应该看到: SKILL.md  chapters/  supporting/  INDEX.md
```

#### 步骤 4:配置 Obsidian vault 路径(可选,Read+Grep 模式需要)

在 SKILL.md 的 frontmatter 或 cheatsheet 中确认 vault 路径:

```yaml
---
name: sql-skill
description: "通用 SQL 编写专业度 Skill ..."
---
```

vault 默认路径:`E:/obsidian/SQL/`(可在 SKILL.md 调整)

#### 步骤 5:验证部署

问 Claude 一个 SQL 问题:

> "如何优化大 OFFSET 性能"

Claude 应该:
1. 优先查 `cheatsheet.md` Layer 1 决策快查
2. 查 `chapters/ch08-indexes-perf.md` Layer 2 deep dive
3. 用 luke `sql-partial-results-top-n-queries.html` Reference 章节
4. 给出 keyset pagination `WHERE id > last_id LIMIT N` 答案

### 2.2 方式 B: gbrain RAG 增强部署(可选,推荐)

如果希望 Claude 通过 gbrain semantic recall(而非 Read+Grep)检索知识,需要:

#### 前提条件

- 已安装 [gbrain](https://github.com/garrytan/gbrain) v0.60+
- gbrain MCP 已 connected(查 `~/.claude/settings.json` 是否有 `gbrain@gbrain` 启用)
- `default` source 是唯一 source(避免 source-guard 锁)

#### ingest sql-skill 到 gbrain

```bash
# 1. 验证 gbrain 状态
gbrain sources list  # 应该只看到 default

# 2. 如果有 sql-vault 残留,先删除(避免 source-guard)
gbrain sources remove sql-vault --confirm-destructive

# 3. ingest sql-skill 10 章(用本仓库的工具)
cd sql-skill/tools
# 详见 § 三.4 通道 D 手动 ingest

# 或通过 Claude agent:
# 让 Claude 用 mcp__plugin_gbrain_gbrain__put_pages 批量 ingest
```

#### 验证 gbrain recall

问 Claude:
> "JSONB GIN 索引大小如何优化"

Claude 会通过 `mcp__gbrain_gbrain__query` 召回 ch07-pg-specific + ch08-indexes-perf,返回 `jsonb_path_ops` operator class 的建议。

### 2.3 方式 C: 仅 git clone 不配置(轻量)

如果只想要 sql-skill 文件供参考,不需要 Claude 自动加载:

```bash
git clone https://github.com/kizemo/sql-skill.git
# 浏览器或编辑器阅读 sql-skill/chapters/ 即可
```

---

## 三、4 通道动态同步机制

知识库内容变动后(sql-skill 10 章 / 4 辅助文件 / Obsidian 文档),通过 4 通道自动同步:

### 3.1 通道 A:Claude Code PostToolUse hook(自动)

**已写**:`tools/post-write-auto-sync.py`
**已注册**:`~/.claude/settings.json` 包含 PostToolUse 段
**触发**:Claude 写新 chapter / 编辑文件到 `E:/obsidian/SQL/08-sql-skill/`
**机制**:5min debounce → 写 queue 文件 `~/.claude/.cache/sql-skill-sync-queue/`
**消费**:下个 Claude session 启动时(通道 C)

```json
// settings.json 已有
"PostToolUse": [
  {
    "matcher": "Write|Edit|MultiEdit",
    "hooks": [
      {
        "type": "command",
        "command": "C:\\Python314\\python.exe \"F:\\soft\\00selfmade\\sql-skill\\tools\\post-write-auto-sync.py\"",
        "timeout": 60
      }
    ]
  }
]
```

### 3.2 通道 B:Cron 周期同步(每日 02:00)

**已写**:`tools/cron-sync-sql-skill.sh` + `tools/register-cron-sync.ps1`

**注册**:
```powershell
PowerShell -ExecutionPolicy Bypass -File F:\soft\00selfmade\sql-skill\tools\register-cron-sync.ps1
```

**任务**:
- 名称:`gbrain-sql-skill-sync`
- 触发:每日 02:00
- 命令:`bash F:/soft/00selfmade/sql-skill/tools/cron-sync-sql-skill.sh`
- 日志:`F:\soft\00selfmade\sql-skill\logs\sync-cron.log`

**适用**:Obsidian app 编辑(外部,Claude 看不到)

### 3.3 通道 C:Agent 主动消费 queue(每次 Claude 启动)

**已写**:`tools/sync-queue-consumer.py`
**已注册**:`~/.claude/settings.json` 包含 SessionStart 段

```json
// settings.json 已有
"SessionStart": [
  {
    "matcher": "startup",
    "hooks": [
      ...
      {
        "type": "command",
        "command": "C:\\Python314\\python.exe \"F:\\soft\\00selfmade\\sql-skill\\tools\\sync-queue-consumer.py\"",
        "timeout": 60
      }
    ]
  }
]
```

**机制**:Claude session 启动时消费所有 queue 文件,每个 entry 调 gbrain put_page 同步。

### 3.4 通道 D:Manual 手动同步(应急)

```bash
# 手动 ingest 单个文件
python F:/soft/00selfmade/sql-skill/tools/post-write-auto-sync.py \
  --file E:/obsidian/SQL/08-sql-skill/chapters/ch01-grammar.md
# queue 文件会写入,下个 Claude session 消费
```

或通过 gbrain MCP 直接:
```python
mcp__plugin_gbrain_gbrain__put_page(
    slug="sql-skill/chapters/ch01-grammar",
    content="<file content>",
    content_origin="user_said"
)
```

### 3.5 4 通道对比

| 通道 | 触发 | 适用 | 频率 |
|---|---|---|---|
| **A. PostToolUse hook** | Claude 写 .md 到 vault | 即时同步 Claude 写的内容 | 即时(5min debounce) |
| **B. Cron** | 每日 02:00 | 同步 Obsidian app 外部编辑 | 每日 |
| **C. Agent 主动** | Claude session 启动 | 消费 hook 写入的 queue | 每次 session 启动 |
| **D. Manual** | 用户主动 | 应急 / 大批 ingest / 调试 | 临时 |

---

## 四、4 层 lookup(固定顺序)

```text
Layer 0: gbrain semantic recall          ← 跨 10 章 + 4 辅助 + 8 luke 关键章节
       (或 Read+Grep 跨 E:/obsidian/SQL/)
  ↓
Layer 1: cheatsheet.md                    ← 13 决策表 + 18 关键经验
  ↓
Layer 2: 对应 chapter (ch01-ch10)         ← deep dive
  ↓
Layer 3: evidence-skill 业务侧           ← 中文 schema / FDW / BI / MCP
```

---

## 五、项目结构

```
sql-skill/
├── README.md                              ← 本文件
├── LICENSE                                ← MIT
├── .gitignore
│
├── sql-skill/                             ← skill 核心
│   ├── SKILL.md                           ← skill 入口 + 12 framework
│   ├── INDEX.md                           ← 资源索引(来自 Obsidian 00-索引.md)
│   ├── chapters/                          ← 10 章正文
│   │   ├── ch01-grammar.md
│   │   ├── ch02-joins.md
│   │   ├── ch03-window-functions.md
│   │   ├── ch04-cte-recursion.md
│   │   ├── ch05-aggregates.md
│   │   ├── ch06-set-ops.md
│   │   ├── ch07-pg-specific.md
│   │   ├── ch08-indexes-perf.md
│   │   ├── ch09-antipatterns.md
│   │   └── ch10-evidence-bridge.md
│   └── supporting/                         ← 4 辅助文件
│       ├── cheatsheet.md
│       ├── glossary.md
│       └── patterns.md
│
├── tools/                                  ← 4 通道同步工具
│   ├── post-write-auto-sync.py            ← 通道 A:PostToolUse hook
│   ├── sync-queue-consumer.py             ← 通道 C:SessionStart 消费 queue
│   ├── cron-sync-sql-skill.sh             ← 通道 B:Cron 周期同步
│   ├── register-cron-sync.ps1             ← 通道 B:Windows Task Scheduler 注册
│   └── lookup-sql-vault.md                 ← Layer 0 检索规范(Read+Grep)
│
├── references/                             ← 引用资源
│   └── luke/                               ← 8 篇 luke 关键章节
│       ├── README.md
│       ├── sql-anatomy-the-tree.html        (B-Tree)
│       ├── sql-explain-plan.html           (EXPLAIN)
│       ├── sql-join-hash-join-partial-objects.html
│       ├── sql-join-nested-loops-join-n1-problem.html
│       ├── sql-join-sort-merge-join.html
│       ├── sql-where-clause-functions-case-insensitive-search.html
│       ├── sql-partial-results-top-n-queries.html
│       └── sql-partial-results-window-functions.html
│
├── docs/                                   ← 项目开发文档
│   ├── handoffs/                          ← 阶段 handoff + 下一会话 prompt
│   ├── specs/                             ← 各阶段 spec
│   ├── plans/                             ← 各阶段 plan
│   └── superpowers/                       ← superpowers 框架原始文件
│
└── _knowledge_base/                       ← 调研笔记(暂不强制需要)
```

---

## 六、依赖与兼容性

| 依赖 | 版本 | 用途 |
|---|---|---|
| PostgreSQL | 14+ | 所有 SQL 例子针对 PG 14+ |
| Python | 3.14+ | sync-queue-consumer.py / post-write-auto-sync.py |
| Git Bash | 4.0+ | cron-sync-sql-skill.sh |
| PowerShell | 5.1+ | register-cron-sync.ps1 |
| gbrain(可选) | 0.60.214+ | gbrain RAG 模式 |

---

## 七、贡献

### 7.1 修改 sql-skill 章节

```bash
# 1. 克隆并编辑
git clone https://github.com/kizemo/sql-skill.git
cd sql-skill
# 编辑 sql-skill/chapters/ch01-grammar.md 等

# 2. 提交
git add .
git commit -m "ch01: 补充 NULL 三值逻辑案例"
git push origin main
```

### 7.2 新增章节

1. 复制模板:`cp sql-skill/chapters/ch09-antipatterns.md sql-skill/chapters/ch11-new-topic.md`
2. 替换内容(保留 9 段结构)
3. 在 `SKILL.md` Chapter Index 添加行
4. 在 `cheatsheet.md` 关键经验追加
5. 提交 PR

### 7.3 同步到本地 Obsidian vault

```bash
# 拉取最新
git pull origin main
# 复制到 vault
cp -r sql-skill/ E:/obsidian/SQL/08-sql-skill/
# Claude 下次 session 启动时,4 通道同步会自动 ingest
```

---

## 八、v2.2 关键决策沉淀

1. **复用 evidence-skill ingest 路径**:`mcp__gbrain_gbrain__put_pages` 走 default source(单 source 避免 source-guard)
2. **batch ingest 分 3 批**:ch01-04 / ch05-08 / ch09-10,各 4 章 + 2 章,每批 < 8MB
3. **混合检索策略**:gbrain semantic + Read+Grep keyword 互补
4. **hook 进程用 queue 模式**:hook 无 MCP 客户端 → 写文件 → 下个 session 消费
5. **4 通道同步**:
   - A:Claude 写 .md → hook → queue
   - B:Cron → 跑 gbrain sweep
   - C:SessionStart → 消费 queue
   - D:Manual → put_page 直接

---

## 九、已知限制

1. **embedding_state: disabled**:`gbrain` conservative keyless 模式禁 vector search,只能 keyword 召回(已能 80% 覆盖)
2. **mention_links: queued**:跨章 wikilinks 异步 sweep,无需手动等
3. **git_state: queued**:filesystem 已有 markdown,gbrain serve 周期 commit
4. **199M nl2sql-handbook 未 ingest**:v2.2 跳过(按需 sub-ingest)
5. **外部 vault 1GB+ 未全 ingest**:luke 8 章关键引用已带,其余按需

---

## 十、版本历史

| 版本 | 日期 | 阶段 | 关键 |
|---|---|---|---|
| v0.1 | 2026-10-14 (Phase 2) | 3 章 | ch01 + ch07 + ch08 + 4 辅助 |
| v1.0 | 2026-10-14 (Phase 3) | 10 章 | + ch02/03/04/05/06/09/10 |
| v2.0 | 2026-10-15 | gbrain 设计 | ingest 设计,失败(PGLite 锁) |
| v2.1 | 2026-10-15 | 务实方案 | Read+Grep 直接检索 vault |
| **v2.2** | **2026-10-15** | **gbrain RAG 集成** | **10 章成功 ingest + 4 通道同步** |

---

## 十一、致谢

- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [Use The Index, Luke!](https://use-the-index-luke.com/) — Markus Winand
- [Mark Mazur SQL Style Guide](https://github.com/mattm/sql-style-guide)
- [evidence-skill](https://github.com/kizemo/evidence-skill) — 业务侧 skill 互补
- [gbrain](https://github.com/garrytan/gbrain) — semantic RAG 基础设施

---

**License**: MIT
**Maintainer**: kizemo
**Repository**: https://github.com/kizemo/sql-skill