# sql-skill v2.2 — 完整 handoff(2026-10-15)

> **本会话完成**:v1.0 沉淀 + v2.2 部署到 Claude Code + GitHub push + 4 通道同步机制(部分注册)
> **新会话任务**:接力 Phase 4+(评测自动化 / 多 DB / embedding / 继续完善 4 通道)
> **接力 prompt**:`prompt-next-session-v2-2-deployed.md`(同目录)
> **必读 7 文件**:详 § 一 必读顺序

---

## 一、必读顺序(7 文件,30 分钟掌握全貌)

| # | 路径 | 用途 | 必读段 |
|---|---|---|---|
| 1 | 本文件 | 当前状态 + 下阶段计划 | 全部 |
| 2 | `prompt-next-session-v2-2-deployed.md` | 一句话 prompt,先读 | 全部 |
| 3 | `E:/Users/Duanyi/.claude/skills/sql-skill/SKILL.md` | 已部署的 skill 入口 | 12 framework + How to Use |
| 4 | `E:/Users/Duanyi/.claude/skills/sql-skill/INDEX.md` | 资源索引 | 全部 |
| 5 | `F:/soft/00selfmade/sql-skill/README.md` | GitHub README,3 部署方法 | § 二 + § 三 |
| 6 | `F:/soft/00selfmade/sql-skill/handoff-sql-skill-v2-rag-2026-10-15.md` | v2.2 详细设计(9.5K) | § 四 4 通道 + § 限制 |
| 7 | `E:/Users/Duanyi/.claude/settings.json` | 4 通道 hook 注册状态 | PostToolUse + SessionStart 段 |

**可选深入**:`docs/specs/2026-10-15-sql-skill-v2-rag-design.md` + `docs/plans/2026-10-15-sql-skill-v2-rag.md` + 7 个历史 handoff(`docs/handoffs/handoff-sql-skill-*.md`)

---

## 二、本会话完成(2026-10-14 ~ 2026-10-15)

### 2.1 sql-skill v1.0 沉淀(Phase 2 + 3a + 3b + 3c)

- **10 章 + 4 辅助文件** = ~5161 行
- 7 个阶段 handoff(spec + plan + handoff 三件套)
- 4 阶段证据链可追溯

### 2.2 sql-skill v2.2 gbrain RAG 集成

| 路径 | 探索 | 结果 |
|---|---|---|
| v2.0 | 假设 gbrain ingest 可直接跑 | ❌ 失败:PGLite 单写锁 + source-guard |
| v2.1 | Read+Grep 直接读 vault | ✅ 可用,无需 gbrain |
| v2.2 | 复用 evidence-skill 路径(`mcp__put_page` 走 default) | ✅ 突破,10 章全部 ingest |

**v2.2 关键发现**:
- evidence-skill 6 页 frontmatter 是 `mcp:put_page` 路径
- 走 default 单一 source 避免 source-guard
- 批量 `put_pages` 4+4+2 章,共 11 pages + 1 index

### 2.3 4 通道动态同步(设计 + 部分注册)

| 通道 | 工具 | 状态 | 注册位置 |
|---|---|---|---|
| A. PostToolUse hook | `tools/post-write-auto-sync.py` | ✅ 已写 + 已注册 | `~/.claude/settings.json` PostToolUse 段 |
| B. Cron 周期同步 | `tools/cron-sync-sql-skill.sh` + `register-cron-sync.ps1` | ✅ 工具已写,❌ **Cron 未注册**(等用户跑) | — |
| C. SessionStart queue consumer | `tools/sync-queue-consumer.py` | ✅ 已写 + 已注册 + ✅ **已测试通过** | `~/.claude/settings.json` SessionStart 段 |
| D. Manual sync | `sync_to_brain()` in post-write-auto-sync.py | ✅ | — |

**测试验证**(2026-10-15):
- ✅ Channel C queue→brain filesystem 写入成功(test-001.json 处理)
- ✅ 4-channel 设计在 handoff § 四 完整记录

### 2.4 Claude Code 本地部署

**位置**:`E:/Users/Duanyi/.claude/skills/sql-skill/`

| 文件 | 用途 |
|---|---|
| `SKILL.md` | skill 入口(19.9K),YAML frontmatter 含 name + description + 触发词 |
| `INDEX.md` | 资源索引 |
| `chapters/ch01-ch10.md` | 10 章正文 |
| `supporting/cheatsheet.md` + `glossary.md` + `patterns.md` | 3 辅助文件 |

**系统确认**:`sql-skill` 在当前 session 的可用 skills 列表(system reminder)。

### 2.5 GitHub push

**仓库**:https://github.com/kizemo/sql-skill
- 公开 + MIT License
- 62 文件,~800KB
- 包含 sql-skill + 4 通道工具 + 8 篇 luke 关键章节 + 完整 docs
- 提交历史:
  - `5080d97` sql-skill v2.2: 10 chapters + 4 supporting + 4-channel sync + gbrain RAG integration
  - `7c70a89` fix: move SKILL.md to skill root for Claude Code auto-discovery

### 2.6 当前 gbrain brain 状态

- **18 pages**:6 evidence-skill + 10 sql-skill chapters + 1 index + 1 test
- **110 chunks**
- **34 links**(跨章 wikilinks)
- **0 embeddings**(conservative keyless 模式禁 vector)

---

## 三、CLAUDE.md 红线遵守记录

- ✅ 禁 rm(只删了 `sql-vault` source,无用户文件)
- ✅ 禁 git reset / clean
- ✅ 禁 DROP / TRUNCATE(只调 gbrain CLI sources add/remove)
- ✅ 临时文件放 `C:\Temp\`
- ✅ 单次 Write ≤ 400 行
- ✅ Edit 锚定追加
- ✅ 禁在 Claude settings 中挂"skip permissions"
- ✅ 禁单条命令触碰多个用户文件
- ✅ git 操作用 force-push 替换占位 README(用户授权,无重要内容)

---

## 四、当前文件树(F:/soft/00selfmade/sql-skill/)

```
sql-skill/                                       ← 本仓库
├── README.md                                    ← 部署文档(3 方式)
├── LICENSE                                      ← MIT
├── .gitignore                                   ← 排除 sync queue / logs
│
├── sql-skill/                                   ← skill 核心
│   ├── SKILL.md                                 ← 入口
│   ├── INDEX.md                                 ← 资源索引
│   ├── chapters/                                ← 10 章
│   └── supporting/                              ← 4 辅助
│
├── tools/                                       ← 4 通道工具
│   ├── post-write-auto-sync.py                  ← 通道 A
│   ├── sync-queue-consumer.py                   ← 通道 C
│   ├── cron-sync-sql-skill.sh                   ← 通道 B
│   ├── register-cron-sync.ps1                   ← 通道 B 注册
│   └── lookup-sql-vault.md                      ← Layer 0 检索规范
│
├── references/luke/                             ← 8 篇 luke 关键章节
│
└── docs/
    ├── handoffs/                                ← 7 handoff + 3 prompt
    ├── specs/                                   ← 5 spec
    └── plans/                                   ← 5 plan
```

---

## 五、Phase 4+ 后续任务(新会话接力)

### 5.1 必做(下次 session 第一件事)

1. **注册 Cron 通道 B**(`register-cron-sync.ps1`)
   - 用户需跑:`PowerShell -ExecutionPolicy Bypass -File F:\soft\00selfmade\sql-skill\tools\register-cron-sync.ps1`
   - 注册成功验证:`Get-ScheduledTask -TaskName "gbrain-sql-skill-sync"`

2. **测试 Channel A**(PostToolUse hook 实际触发)
   - Claude 写一个测试 .md 到 `E:/obsidian/SQL/08-sql-skill/chapters/`
   - 检查 `~/.claude/.cache/sql-skill-sync-queue/` 有新文件
   - 验证:下个 session 启动时 queue consumer 消费该文件

### 5.2 增强(可分阶段)

3. **enable gbrain embedding**:
   - 当前 `embedding_state: disabled`(conservative keyless 模式)
   - 影响:只能用 keyword 搜索,不能 semantic 召回
   - 解决:用户跑 `gbrain doctor --json` 看 enable command;启用 embedding provider

4. **ingest 外部 vault**:
   - 优先级 2(可选):`E:/obsidian/SQL/04-awesome-postgres/`(PG 资源)
   - 优先级 3(可选):`E:/obsidian/SQL/05-sql-style-guide/`(风格)
   - 跳过:`E:/obsidian/SQL/01-nl2sql-handbook/`(199M,按需 sub-ingest)
   - 用法:让 Claude 通过 `mcp__gbrain__put_pages` 批量 ingest

5. **luke 全部 48 章 ingest**(如需):
   - 当前 `references/luke/` 8 篇关键章节
   - 剩余 40 章可分批 ingest,每批 5 章 < 8MB 限额

### 5.3 Phase 5+ 远期(可选)

6. **评测集自动化**:
   - 跑 civilian7 1065 题 + Claude 答 + 评分
   - 工具:`tools/eval_civilian7.py`(待写)

7. **多 DB 支持**:
   - MySQL / Oracle / SQL Server 各自 anti-pattern
   - ch10 加 multi-db 协作

8. **hook 升级**:
   - 当前 hook 进程无 MCP 客户端,用 queue 模式中转
   - Phase 5:hook 进程内嵌 MCP,Claude 写完即同步

---

## 六、避坑沉淀(新会话直接复用)

### 6.1 gbrain RAG 集成

- ✅ **不要假设 gbrain 多 source 可并行** — source-guard 锁住所有写
- ✅ **先看别人怎么做的** — evidence-skill 6 页 frontmatter = `mcp:put_page` 路径
- ✅ **CLI `gbrain sources add/remove` 即使 serve 锁仍可用**(只 import/feed/sync 锁)
- ⚠️ **vector embedding 在 conservative keyless 模式被禁** — 只能 keyword
- ⚠️ **mention_links / git_state 队列异步推进** — 无需手动等

### 6.2 Claude Code skill 部署

- ✅ **SKILL.md 必须在 skill 目录根** — `~/.claude/skills/<name>/SKILL.md`,不是子目录
- ✅ **frontmatter 触发词越具体,自动发现越准** — Use when + Triggers 必填
- ⚠️ **GitHub push 后用户必须把 skill 复制到 `~/.claude/skills/`** — push 不等于部署

### 6.3 4 通道同步

- ✅ **hook 进程无 MCP 客户端** — 用 queue 模式中转
- ✅ **5min debounce 防频繁触发** — 同文件不重复同步
- ✅ **Channel C 在 SessionStart 跑** — 消费 hook 写入的 queue

### 6.4 Obsidian vault 集成

- ✅ **不要写 bash 脚本假设 Windows 有 bash** — 用 `C:\Program Files\Git\usr\bin\bash.exe` 全路径
- ✅ **不假设能 kill Claude Code** — agent 找其他路径
- ✅ **大 vault 1GB+ 不可全 ingest** — 优先级分层(本 skill 10 章 > luke 8 篇 > civilian7 索引)

---

## 七、关键路径速查

### 7.1 项目路径

| 用途 | 路径 |
|---|---|
| 项目根 | `F:/soft/00selfmade/sql-skill/` |
| GitHub 仓库 | https://github.com/kizemo/sql-skill |
| 已部署 skill | `E:/Users/Duanyi/.claude/skills/sql-skill/` |
| Obsidian sql-skill vault | `E:/obsidian/SQL/08-sql-skill/` |
| gbrain brain filesystem | `C:\Users\Duanyi\.gbrain\content\cf1c1488-e14c-4364-9800-018a9698ddae\default\` |
| Hooks 配置文件 | `E:/Users/Duanyi/.claude/settings.json` |
| Sync queue | `~/.claude/.cache/sql-skill-sync-queue/` |
| Cron 日志 | `F:\soft\00selfmade\sql-skill\logs\sync-cron.log` |

### 7.2 文档路径

| 文档 | 路径 |
|---|---|
| v1.0 handoff | `F:/soft/00selfmade/sql-skill/docs/handoffs/handoff-sql-skill-v1-2026-10-14.md` |
| v2.2 handoff | `F:/soft/00selfmade/sql-skill/handoff-sql-skill-v2-rag-2026-10-15.md` |
| v2.2 spec | `F:/soft/00selfmade/sql-skill/docs/specs/2026-10-15-sql-skill-v2-rag-design.md` |
| v2.2 plan | `F:/soft/00selfmade/sql-skill/docs/plans/2026-10-15-sql-skill-v2-rag.md` |
| GitHub README | `F:/soft/00selfmade/sql-skill/README.md` |
| Lookup 规范 | `F:/soft/00selfmade/sql-skill/tools/lookup-sql-vault.md` |

### 7.3 gbrain 工具

| 命令 | 用途 |
|---|---|
| `gbrain sources list` | 查 source 列表(应只有 default) |
| `gbrain sources add <id> --path <p> --force` | 加 source(本项目已用完) |
| `gbrain sources remove <id> --confirm-destructive` | 删 source |
| `gbrain sweep --once` | 推进 mention_links + git_state |
| `gbrain query "<question>" --limit 5` | 跨 brain semantic/keyword 召回 |
| `gbrain search "<query>" --limit 5` | 纯 keyword 搜索 |
| `gbrain get stats` | 查 brain 状态(18 pages / 110 chunks) |
| `gbrain doctor --json` | 诊断(可看 enable embedding 命令) |

---

## 八、调用 sql-skill 测试

新 session 启动后,问 Claude:

> "如何优化大 OFFSET 性能"

预期:
1. 自动调 `Skill tool: sql-skill`
2. 加载 `~/.claude/skills/sql-skill/SKILL.md`
3. 推荐:ch08 §5 + 关键 takeaway `keyset pagination WHERE id > last_id`
4. 引用:luke `sql-partial-results-top-n-queries.html`(在 references/luke/)

如果没自动调,需检查:
- `~/.claude/skills/sql-skill/SKILL.md` frontmatter description 触发词是否覆盖"SQL 性能"
- Claude 是否在前一轮 memory 里有"用 sql-skill"指令

---

## 九、版本历史(完整)

| 版本 | 日期 | 关键 |
|---|---|---|
| v0.1 | 2026-10-14 上午(Phase 2) | ch01 + ch07 + ch08 + 4 辅助 |
| v1.0 | 2026-10-14 下午(Phase 3a+3b+3c) | + ch02/03/04/05/06/09/10,~5161 行 |
| v2.0 | 2026-10-15 上午 | gbrain ingest 设计,失败(PGLite 锁) |
| v2.1 | 2026-10-15 中午 | Read+Grep 务实方案,Layer 0 直接检索 vault |
| **v2.2** | **2026-10-15 下午** | **gbrain RAG 集成 + 4 通道 + GitHub push + Claude Code 部署** |

---

## 十、致谢与历史

- **2026-10-14 上午**:sql-skill v0.1 启动(3 章)
- **2026-10-14 下午**:v1.0 完整版(10 章)
- **2026-10-15 上午**:v2.0 失败 → v2.1 务实方案
- **2026-10-15 下午**:v2.2 突破 + GitHub push + Claude Code 部署
- **未来 Phase 4+**:评测自动化 / 多 DB / embedding / Phase 5 多 skill 协同

---

**新会话可立即接力** — 必读顺序 § 一,接 Phase 4+ 任务(§ 五)。无需重做 Phase 2-3c + v2.0-v2.2 工作,所有沉淀已 git 化 + 部署化。