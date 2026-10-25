# handoff — sql-skill v0.2 token 效率优化 · 2026-10-25

> **本会话完成**:sql-skill 按渐进式披露重构,index 231→98 tok / load 5503→1908 tok(每次触发 5734→2006,**-65%**);Phase 4 验证 + Phase 5 评测 MVP
> **新会话任务**:Phase 4 剩余项(Cron B / Channel A / embedding / ingest)+ Phase 5 剩余项(多 DB / hook 内嵌 MCP)
> **接力 prompt**:`prompt-next-session-2026-10-25.md`(同目录)

---

## 一、必读顺序(5 文件,约 20 分钟)

| # | 路径 | 用途 |
|---|---|---|
| 1 | 本文件 | 当前状态 + 下阶段计划 |
| 2 | `F:\soft\00selfmade\skill-optimizer\handover\sql-skill-token-efficiency.md` | 原始审计 + 优化方案(11 条 validator 警告清单) |
| 3 | `F:\soft\00selfmade\sql-skill\docs\audit\sql-skill-audit-2026-10-25.md` | 本次改动的 `## Cost` 实测报告 |
| 4 | `F:\soft\00selfmade\sql-skill\sql-skill\SKILL.md` | 优化后的入口(104 行) |
| 5 | `F:\soft\00selfmade\sql-skill\handoff-phase-4-verify-2026-10-17.md` | Phase 4 验证记录(Channel A/C 实测) |

**可选**:`F:\soft\00selfmade\sql-skill\docs\handoffs\channel-a-debug-plan-2026-10-17.md`(Channel A 排查计划)

---

## 二、本会话完成

### 2.1 sql-skill v0.2 token 效率优化(主交付)

**目标**:遵循渐进式披露,降低触发消耗,同时提高路由准确度。

| 层级 | 优化前 | 优化后 | 预算 | 状态 |
|---|---|---|---|---|
| index(每会话都付) | 231 tok | **98 tok** | ~100 | ✅ ok |
| load(触发时) | 5,503 tok | **1,908 tok** | ~5,000 | ✅ ok |
| files(按需读) | 0 | 2,745 tok | 无限 | ✅ 溢出有去处 |
| **每次触发合计** | **5,734 tok** | **2,006 tok** | — | **-65%** |

- root_cause:`routing` → `other`
- verdict:`refuse` → `accept`
- **validator 警告 11 条 → 0 条**
- SKILL.md:412 行 / 19,894 B → **104 行 / 6,808 B(-66%)**

**执行的 8 项改动**:

| # | 改动 | 省 |
|---|---|---|
| 1 | frontmatter:description 从 101 词缩到 22 词 + "Use when" 开头;19 个内联 triggers → `triggers:` 独立列表 5 条;补 `mutating` / `brain_first` / `when_to_use` / `version` | index -133 |
| 2 | 12 大框架(85 行内联摘要,与 chapters 重复)→ **表格**(保留结论 + 章节指针) | ~1,550 |
| 3 | 新增 `## Gotchas` 段(8 条高频反模式,含指向 ch09/ch01/ch07/ch08 的指针) | 补 validator 第 9 条 |
| 4 | Topic Index(125 行,含 34 行逐字重复)→ 去重 84 条 → `references/topic-index.md` | ~1,900 |
| 5 | "How to Use"(52 行)与"调研/沉淀入口"(57 行)整段重复 → 合并 → `references/retrieval.md` | ~1,600 |
| 6 | Chapter Index 删「状态」列(开发过程信息,非检索信息) | ~200 |
| 7 | Supporting Files 段与 Chapter Index 合并为「文件清单(读条件)」 | ~300 |
| 8 | **修正 Scope & Limits 3 处陈旧事实**(原写"ch02-ch06/09/10 留 stub"、"v0.1 仅 3 章"、"无 git"——实际 10 章完整 + 已有 git) | 防误导 |

**发现但分析文档未提的问题**:
- Topic Index 第 255-290 行是前文的**逐字 copy-paste 重复**(36 行)
- 旧 SKILL.md 里 `[glossary.md](glossary.md)` 相对链接**本来就是断的**(实际在 `supporting/`)→ 新版已修
- glossary.md 166 条定义已覆盖 Topic Index 63%+ → Topic Index 定位为"章节定位"而非"定义",职责分离

**部署**:三处 md5 一致(`698fed1e...`):
- `F:\soft\00selfmade\sql-skill\sql-skill\SKILL.md`(仓库源)
- `E:\Users\Duanyi\.claude\skills\sql-skill\SKILL.md`(Claude Code 实际加载)
- `E:\obsidian\SQL\08-sql-skill\SKILL.md`(vault,4 通道同步源)
- 新增 `references/`(topic-index.md + retrieval.md)同步到后两处

### 2.2 Phase 4 验证(前序任务,已交付)

- **Channel A**:手动 hook 模拟 payload 正常(队列写入 + debounce);**但 Claude Code 自动 PostToolUse 在本 session 完全没触发**(加 debug_log 后日志空 → Claude Code 没调 hook)。根因收敛到 H2(settings.json 本 session 未重读)。排查计划见 `docs/handoffs/channel-a-debug-plan-2026-10-17.md`。
- **Channel C**:consumer 脚本 dry-run + 真实执行均通过,成功写入 brain filesystem。
- **Channel B**:工具就绪,**Cron 任务未注册**(等用户跑 register-cron-sync.ps1)。
- **gbrain**:锁已自动恢复(PID 46940 消亡)。`gbrain doctor --json` 可跑,`embedding_key_source` 缺 `VOYAGE_API_KEY` → embedding 未启用。

### 2.3 Phase 5 评测 MVP

- `tools/eval_civilian7.py`(481 行)—— 3 模式:`count` / `skill-aware` / `baseline`(需 `--db`)
- 题数 **1090**(INDEX 写 1065,实测 1090)
- **覆盖率 100.0%**(1090/1090),每章覆盖:ch01 918 / ch05 468 / ch02 280 / ch04 267 / ch03 245 / ch07 139 / ch06 101 / ch08 44 / ch09 59
- 4 路匹配:tags + metadata.concepts + type + title/body_en 文本兜底
- 报告:`eval_civilian7_report.json` + `eval_civilian7_report.md`
- **优化后回归重跑:仍 100% 覆盖,无回归**

---

## 三、测试证据

| 检查 | 命令 | 结果 |
|---|---|---|
| token 三层实测 | `python -m scripts.run --skill F:/soft/00selfmade/sql-skill/sql-skill --scope audit-only`(在 `F:\soft\00selfmade\skill-optimizer\skill-forge`) | index 98 / load 1908 / files 2745,verdict accept |
| validator 警告 | `validate_skill_frontmatter() + validate_skill_body()` | **0 条** |
| YAML 合法性 | `yaml.safe_load` | 7 键齐全,desc 22 词,triggers 5 |
| 路由实测 | Claude Code skill 列表 | 新 frontmatter 已实时生效 |
| 邻居混淆 | 对比 evidence-skill frontmatter | 触发词无重叠;"evidence 报表加了个新过滤维度" → 只命中 evidence-skill |
| 评测回归 | `python tools/eval_civilian7.py --mode skill-aware` | 100% 覆盖(1090/1090) |
| 部署一致性 | `md5sum` × 3 | 唯一 1 个 |

---

## 四、改动文件清单(**全部未 commit**)

```
 M sql-skill/SKILL.md                          ← 重写(412→104 行)
 M tools/post-write-auto-sync.py               ← 加 debug_log(Channel A 诊断)
?? sql-skill/references/topic-index.md         ← 新建(84 条去重索引)
?? sql-skill/references/retrieval.md           ← 新建(检索策略 + 资源 + 联动)
?? sql-skill/.skill-forge-baseline.json        ← skill-forge 漂移检测基线
?? sql-skill/.skill-forge-snapshot-SKILL.md    ← skill-forge 快照
?? tools/eval_civilian7.py                     ← 新建(评测 MVP)
?? eval_civilian7_report.json / .md            ← 评测报告
?? docs/audit/                                 ← skill-forge 产物(audit-report / best.md / benchmark)
?? docs/handoffs/channel-a-debug-plan-2026-10-17.md
?? handoff-phase-4-verify-2026-10-17.md
?? handoff-sql-skill-v0-2-token-optimization-2026-10-25.md ← 本文件
```

**未 commit 是有意的** —— 等用户确认后再提。

**skill-forge 产物位置**:`skill-forge` 会把 `audit-report.md` / `best.md` / `skillopt-benchmark.jsonl` 写进它被指向的 skill 目录。本次已移出到 `docs/audit/`,避免污染部署目录。**下次跑 skill-forge 需先移到 scratch 目录**。

---

## 五、下一步必交付(优先级)

### ① Cron 通道 B 注册(用户执行,系统级)

```powershell
PowerShell -ExecutionPolicy Bypass -File F:\soft\00selfmade\sql-skill\tools\register-cron-sync.ps1
```

验证:`Get-ScheduledTask -TaskName "gbrain-sql-skill-sync"`

### ② Channel A 自动 PostToolUse 修复

根因:H2 —— 本 session 未重读 settings.json。
**最小动作**:重启 Claude Code session → 写一个 vault .md → 查 `~/.claude/.cache/post-write-auto-sync.log` 有无 `HOOK ENTRY`。
若仍无 → 按 `docs/handoffs/channel-a-debug-plan-2026-10-17.md` 的 H1(matcher 数组格式)试。

### ③ gbrain embedding enable(用户配 key)

`gbrain doctor --json` 显示缺 `VOYAGE_API_KEY`。配环境变量后:
- enable embedding provider
- ingest 优先级 2 vault:`E:/obsidian/SQL/04-awesome-postgres/` + `05-sql-style-guide/`

### ④ Phase 5 剩余

- 多 DB 支持(MySQL / Oracle / SQL Server 各自 anti-pattern + ch10 加 multi-db 协作)
- hook 内嵌 MCP 客户端(即写即同步,消除 queue 中转延迟)
- eval_civilian7 扩展:`--mode claude-api`(需 API key)+ `--mode baseline` 需先生成 SQLite 测试 DB(`E:/obsidian/SQL/02-sql-tutorial-civilian7/src/cli/generate.py`)

### ⑤ 本次改动待用户决定

- 是否 commit(建议:一次 commit,`feat(skill): v0.2 token 效率优化,index 231→98 / load 5503→1908 tok`)
- 是否 push 到 GitHub(仓库 https://github.com/kizemo/sql-skill)
- skill-forge Phase 2-4 完整 LLM-judge 回归(需 `gbrain skillopt` + 预算,本次未做)

---

## 六、环境 / 分支 / 基线

- 分支:`main`,HEAD `5825eac`(chore: remove duplicate SKILL.md from supporting/ subdir)
- 工作区:**有未 commit 改动**(见 § 四)
- Python:`C:\Python314\python.exe`(3.14.6)
- gbrain:`E:\Users\Duanyi\.claude\Cache\.bun\bin\gbrain.exe`,live serve PID 254540 持 brain 锁
- skill-forge:`F:\soft\00selfmade\skill-optimizer\skill-forge\scripts\run.py`
- 部署副本:仓库 / `E:\Users\Duanyi\.claude\skills\sql-skill\` / `E:\obsidian\SQL\08-sql-skill\` **三处需手动同步**(非 junction)

---

## 七、避坑提示

- **skill-forge 写入 skill 目录** → 跑之前先 `cp -r` 到 scratch 目录,或跑完把 3 个产物移走
- **三处副本非 junction** → 改完必须 `cp` 三份,别只改仓库
- **index tier 预算 100 tok 是硬心理线** → description 22 词 + triggers 5 条已是当前最优配比,再加词就超
- **triggers 应放"问题词"不是"方案词"** → "OFFSET keyset"(方案)被删,"SQL 性能"(问题)被留
- **`python -m scripts.run` 必须在 skill-forge 目录下跑**(sys.path 依赖 `scripts._lib`)
- **Windows 上 Python print 中文会 GBK 崩** → 加 `PYTHONIOENCODING=utf-8` 或 `sys.stdout.reconfigure(encoding='utf-8')`
- **eval_civilian7 路径是 `E:/obsidian/...`**(不是 F:)→ 曾写错,已修
- **civilian7 的 `lectures/` 目录 difficulty 标的是 `beginner`** → 计数时别漏

---

## 八、任务状态

| # | 任务 | 状态 |
|---|---|---|
| 1 | ② enable gbrain embedding + ingest 优先级 2 vault | in_progress(锁已恢复,等 API key) |
| 2 | ① Cron 通道 B 注册 + Channel A 实测 | completed(基础设施验证通过;B 待用户注册) |
| 3 | ③ Phase 5:评测自动化 + 多 DB + hook 升级 | in_progress(eval MVP 完成,多 DB / hook 升级待做) |
| 4 | 排查 Channel A 自动 PostToolUse 未触发 | pending(根因 H2,待重启 session 验证) |
| 5 | sql-skill token 效率优化 | **completed** |
