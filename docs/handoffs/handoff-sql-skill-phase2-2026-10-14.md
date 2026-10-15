# sql-skill Phase 2 — 会话交接 handoff

> 会话结束日期: 2026-10-14
> 当前阶段: **Phase 2 完成 / Phase 3 待启动**
> 接力目标: 启动 Phase 3,补齐 ch02-ch06 / ch09 / ch10 stub → 完整章节

---

## 一、项目定位与已沉淀内容

### 1.1 项目定位

sql-skill 是面向 **企业 PostgreSQL + Evidence BI** 场景的 **通用 SQL 编写专业度 Skill**,定位为 **"Skill / Engine / 库"** 形态(非 BI 产品)。

### 1.2 已沉淀(Phase 2 本会话交付)

| 路径 | 行数 | 用途 |
|---|---|---|
| `E:/obsidian/SQL/08-sql-skill/SKILL.md` | 261 | skill 入口(YAML frontmatter + 12 Frameworks + 10 章 Index) |
| `E:/obsidian/SQL/08-sql-skill/glossary.md` | 158 | 关键术语表(A-Z + 中文段) |
| `E:/obsidian/SQL/08-sql-skill/patterns.md` | 247 | 8 大模式 + 反模式总表(20 条) |
| `E:/obsidian/SQL/08-sql-skill/cheatsheet.md` | 190 | 13 决策表 + 12 关键经验 + 12 actionable + 调研入口 |
| `E:/obsidian/SQL/08-sql-skill/chapters/ch01-grammar.md` | 256 | SQL 语法铁律 |
| `E:/obsidian/SQL/08-sql-skill/chapters/ch07-pg-specific.md` | 322 | PG 特有(JSONB / array / GIN / FDW / 中文 schema) |
| `E:/obsidian/SQL/08-sql-skill/chapters/ch08-indexes-perf.md` | 405 | 索引与性能(EXPLAIN ANALYZE 完整解读) |
| **总计** | **1839** | **92KB** |

### 1.3 9 段结构(对齐 evidence-skill)

每个 chapter 固定含:Core Idea / Frameworks Introduced / Key Concepts / Mental Models / Anti-patterns / Code Examples / Reference Tables / Key Takeaways / Connects To。

---

## 二、与 evidence-skill 边界(已固化)

| 主题 | sql-skill | evidence-skill |
|---|---|---|
| 中文列双引号 / `ds` 假名 | ch07 §5 提通用规则 | ch05 业务侧 13+ page 假名清单 |
| postgres_fdw 跨 DB | ch07 §4 决策要点 + 简化版 SQL | ch07 完整 5 步 SQL + 4 mart 表实战 |
| 索引与性能 | ch08 通用 PG(B-Tree/GIN/BRIN/Hash + EXPLAIN ANALYZE) | ch14 BI 场景(Core 28 page + nginx immutable + pgbouncer session-mode) |
| SQL 语法铁律 | ch01 通用 | ch05 中文 PG schema 业务雷区 |

**核心边界铁律**:
- ch08 不写 nginx immutable / pgbouncer session-mode(归 evidence-skill ch14)
- ch07 不写完整 FDW 5 步 SQL(归 evidence-skill ch07)
- ch01 不写中文列双引号细节(归 evidence-skill ch05)

---

## 三、必读顺序(新会话第一件事)

按这个顺序读,最快 5 分钟掌握全貌:

1. **本文件** (handoff) — Phase 2 整体框架 + Phase 3 接力目标
2. **`E:/obsidian/SQL/08-sql-skill/SKILL.md`** — skill 入口(12 Frameworks + 10 章 Index + Topic Index)
3. **`E:/obsidian/SQL/08-sql-skill/cheatsheet.md`** — 13 决策表 + 12 关键经验(决策快查)
4. **`E:/obsidian/SQL/08-sql-skill/chapters/ch08-indexes-perf.md`** — Phase 2 深度章节(EXPLAIN ANALYZE 完整解读)
5. (按需) **`F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase2-design.md`** — Phase 2 设计 spec
6. (按需) **`F:/soft/00selfmade/sql-skill/_knowledge_base/research-github-sql-agent-20261013.md`** — 调研笔记
7. (按需) **`E:/obsidian/SQL/00-索引.md`** — 7 个资料源全景

---

## 四、下一步必交付(Phase 3 — ch02-ch06/09/10 stub → 完整章节)

### 4.1 Phase 3 目标

把 ch02 / ch03 / ch04 / ch05 / ch06 / ch09 / ch10 7 个 stub → 完整 9 段章节,让 sql-skill v1.0 完整覆盖 10 章。

### 4.2 7 个待写章节

| # | 主题 | 主要素材 | 优先级 |
|---|---|---|---|
| ch02 | JOIN 7 种 + 性能差异 | SQLBolt join + luke sql-join-* + civilian7 | P1 |
| ch03 | 窗口函数 (OVER/PARTITION BY/RANK/lead-lag) | luke `sql-partial-results-window-function` + civilian7 advanced | P1 |
| ch04 | CTE / 递归 CTE / 物化 | civilian7 advanced + nl2sql-handbook chapter | P2 |
| ch05 | 聚合 / GROUP BY / HAVING / FILTER | SQLBolt aggregates + civilian7 | P2 |
| ch06 | 集合操作 (UNION/INTERSECT/EXCEPT) | civilian7 + PG docs | P3 |
| ch09 | 反模式 (25+ SQL Antipatterns) | civilian7 实战 + evidence-skill ch05 联动 | P1 |
| ch10 | 与 evidence-skill 协作 / 范式 | nl2sql-handbook + awesome-text2sql | P3 |

### 4.3 每个章节产出标准

- 9 段结构齐全
- 深度对齐 Phase 2 章节(ch02/ch03/ch09 ~300 行,ch04/ch05 ~250 行,ch06/ch10 ~200 行)
- 与已沉淀 ch01/ch07/ch08 互补不重叠
- Frameworks 10+ 条,Anti-patterns 8+ 条
- Connects To 跨章节引用清晰

### 4.4 skill 形态要求

- 形态延续 Phase 2:9 段结构 + Frameworks + Anti-patterns + Code Examples + Reference Tables
- 与 evidence-skill 不重叠:ch09 反模式与 evidence-skill ch05 联动,ch10 与 evidence-skill 全 18 章协作
- Update SKILL.md Chapter Index(把 🔵 stub → ✅ 完整)

---

## 五、避坑提示

### 5.1 文件名/路径红线(vault 规则)

- 写入 `E:/obsidian/SQL/08-sql-skill/chapters/` 而非 F: 盘
- Windows 禁用字符 `\ / : * ? " < > |` 不用
- Emoji 不用,中文【】替代
- 文件名 ≤150 字符,完整路径 ≤200 字符
- 编号格式 `ch0X-<topic>.md`(两段式)

### 5.2 CLAUDE.md 红线

- **禁止删除用户文件** (rm / Remove-Item / del / rmdir)
- **禁止单条命令触碰多个用户文件**
- **禁止写危险 SQL** (DROP / TRUNCATE / DELETE FROM 不带 WHERE)
- **禁止 git reset --hard / git clean -fd** 在用户仓库下要 ask
- 临时文件写 `C:\Temp\`,不要写 `~/.tmp/`

### 5.3 Phase 2 已验证的 9 段结构

每个 chapter **必须**含 9 个 `## ` 段(Core Idea / Frameworks / Key Concepts / Mental Models / Anti-patterns / Code Examples / Reference Tables / Key Takeaways / Connects To)。已 grep 验证 ch01/ch07/ch08 全部 9/9。

### 5.4 与 evidence-skill 不重叠(已在 ch08/ch07/ch01 验证)

- ch08 中 nginx/pgbouncer 提及位置**全部是引用 evidence-skill ch14**(grep 验证)
- ch07 FDW 部分只给简化版 + 显式引用 evidence-skill ch07 作为权威(grep 验证)
- ch01 中文列细节不写,只提"归 evidence-skill ch05"

### 5.5 skill 设计陷阱(沿用 Phase 2)

- 不要重造 BI 产品(已被 DB-GPT/WrenAI/SQLBot 堵死赛道)
- 不要重复 evidence-skill 内容,做"通用 PG"层
- 不要重写 FDW 5 步 SQL / nginx patch / 假名清单

---

## 六、环境/基线状态

| 项 | 状态 |
|---|---|
| 工作目录 | `F:/soft/00selfmade/sql-skill/` |
| Git 仓库 | **未 init** (CLAUDE.md 提到新会话如需可 init) |
| Phase | **2 完成 / 3 待启动** |
| sql-skill 主沉淀 | `E:/obsidian/SQL/08-sql-skill/` (1839 行 / 92KB) |
| evidence-skill | `E:/Users/Duanyi/.claude/skills/evidence-skill/` (18 章已部署) |
| Phase 2 spec | `F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase2-design.md` |
| Phase 2 plan | `F:/soft/00selfmade/sql-skill/docs/superpowers/plans/2026-10-14-sql-skill-phase2.md` |
| Phase 2 ledger | `F:/soft/00selfmade/sql-skill/.superpowers/sdd/2026-10-14-sql-skill-phase2/progress.md` |
| 网络环境 | GitHub `gh` CLI 正常(Phase 1 已验证) |
| Claude 模型 | 当前为 MiniMax-M3 |

---

## 七、Phase 3 可能的扩展方向(可选)

1. **ch09 反模式综合**:civilian7 1065 题筛选 25+ 反模式,与 evidence-skill ch05 联动
2. **ch10 协作范式**:AI agent 调 Evidence BI + MCP 4 道防线 + 渐进式 schema 披露(schemagate 借鉴)
3. **评测集**:civilian7 1065 题筛选 100-200 题作为 sql-skill v1.0 评测
4. **联动测试**:sql-skill + evidence-skill 双加载场景测试
5. **PDF/EPUB 处理**:用户购买 SQL Antipatterns / SQL Performance Explained 后,用 `book-to-skill` 处理
6. **多语言**:国际化版本(目前 sql-style-guide 有中文版可参考)
7. **CI 集成**:sql-skill 自身用 TDD 维护(用 `superpowers:test-driven-development`)

---

## 八、验收清单(新会话用)

新会话启动 Phase 3 时,自我验证:

- [ ] 已读 handoff + SKILL.md + cheatsheet.md + ch08 重点
- [ ] 已确认 Phase 2 7 个文件存在
- [ ] 已确认 9 段结构(grep "## " 验证)
- [ ] 已确认与 evidence-skill 边界(grep nginx/pgbouncer 引用而非实现)
- [ ] 已明确 Phase 3 第一个 chapter 选哪个(建议 ch09 反模式,与 evidence-skill ch05 联动最强)
- [ ] 已调用 `superpowers:brainstorming` 与用户对齐 chapter 设计
- [ ] 已 `superpowers:writing-plans` 写 Phase 3 详细任务
- [ ] 每个 chapter 完成前 `superpowers:verification-before-completion` 验证(9 段结构 + Frameworks ≥10 + 不重叠)
- [ ] 更新 SKILL.md Chapter Index(把 🔵 stub → ✅ 完整)
- [ ] 更新 cheatsheet § 13 调研入口(加新 chapter 链接)
- [ ] 写 `handoff-sql-skill-phase3-2026-XX-XX.md` 给后续会话接力

---

## 九、Phase 2 已做决定的固定沉淀

1. **ch08 子结构** = 6 节细分(索引结构 / WHERE 子句索引 / JOIN 算法 / 排序与分组索引 / 分页与窗口函数索引 / EXPLAIN 与执行计划)
2. **ch08 与 evidence-skill ch14 边界** = ch08 通用 PG / ch14 BI 场景
3. **ch08 实战深度** = 心智模型 + 完整可运行 SQL + EXPLAIN ANALYZE 解读(深度 ~300 行)
4. **ch08 §6 EXPL** = 包含(EXPLAIN ANALYZE + pg_stat_statements)
5. **不重叠 evidence-skill**(nginx / pgbouncer / FDW 完整 SQL / 中文列假名细节)
6. **9 段结构固定**(每 chapter 必含 9 段)

新会话请遵守这些已固化决定,如需修改走 brainstorming 流程。
