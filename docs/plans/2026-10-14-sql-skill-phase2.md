# sql-skill Phase 2 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (本项目无 git,直接 inline 执行). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Phase 2 知识抽取,把 `E:/obsidian/SQL/` 7 个沉淀资料源手工抽取形成 sql-skill v0.1 的 SKILL.md + 3 chapter (ch01/ch07/ch08) + glossary/patterns/cheatsheet,共 7 个 markdown 文件。

**Architecture:** Markdown knowledge synthesis 任务。形态严格对齐 evidence-skill(18 章 skill),每 chapter 9 段固定结构。本项目无 git,verification 走 superpowers:verification-before-completion。

**Tech Stack:** Markdown / Obsidian vault / Read-write-edit 工具链

**Spec:** `F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase2-design.md`

## Global Constraints

- **输出路径锁定**:`E:/obsidian/SQL/08-sql-skill/`(vault 规则,不写 F: 盘)
- **文件名规范**:编号 `ch01`/`ch07`/`ch08` + 英文短词,无 emoji / 无空格 / 无 Windows 禁用字符
- **章节深度**:ch01 ~200 行 / ch07 ~200 行 / ch08 ~300 行 / glossary ~150 行 / patterns ~200 行 / cheatsheet ~250 行 / SKILL.md ~150 行
- **每 chapter 9 段固定结构**:Core Idea / Frameworks Introduced / Key Concepts / Mental Models / Anti-patterns / Code Examples / Reference Tables / Key Takeaways / Connects To
- **跨引用格式**:章节引用 `ch0X`,evidence-skill 引用 `evidence-skill ch0X`,luke 引用 `luke/<file>.html`,pg-docs 引用 `pg-docs/<file>.html`,civilian7 引用 `civilian7/<path>`
- **不重叠 evidence-skill**:ch08 不写 nginx immutable / pgbouncer;ch07 不重写 FDW 5 步 SQL;ch01 不重写中文列双引号细节
- **CLAUDE.md 红线**:禁 rm/Remove-Item;禁 git reset --hard;禁 DROP/TRUNCATE;禁在文件名用 \ / : * ? " < > |
- **临时文件**:`C:\Temp\`(不写 ~/.tmp/)
- **Phase 2 必完成**:ch01 + ch07 + ch08 + SKILL.md + glossary + patterns + cheatsheet(共 7 文件)

## Review Focus

5 个 spec 涉及但无 task 测试的潜在失误面:

1. **章节体例偏离 evidence-skill**:补救 — 每个 chapter task 末尾 verification step 对照 9 段清单。
2. **跨引用断链**:补救 — cheatsheet 末段调研入口 + SKILL.md 沉淀入口双重落地。
3. **EXPLAIN ANALYZE 输出无源**:补救 — Task 5 内 Read luke `sql-explain-plan.html` 摘要。
4. **chapter 间无 index 互通**:补救 — 每个 chapter 的 Connects To 段固定列 cross-ref。
5. **glossary 与 chapter 词条不齐**:补救 — Task 5 前置 Read 3 个 chapter 的 Key Concepts 段。

---

## Task 1: 前置准备 — 验证 spec + 建目标目录

**Files:**
- Read: `F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase2-design.md`
- Create: `E:/obsidian/SQL/08-sql-skill/chapters/`(子目录)

- [ ] **Step 1: 验证 spec**

```bash
ls -la "F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase2-design.md"
```

预期:文件存在,~309 行

- [ ] **Step 2: 验证目标目录状态**

```bash
ls -la "E:/obsidian/SQL/08-sql-skill/" 2>/dev/null || echo "DIR_NOT_EXIST"
```

预期:DIR_NOT_EXIST

- [ ] **Step 3: 创建目录**

```bash
mkdir -p "E:/obsidian/SQL/08-sql-skill/chapters"
```

- [ ] **Step 4: 验证创建成功**

```bash
ls -la "E:/obsidian/SQL/08-sql-skill/chapters/"
```

预期:空目录

---

## Task 2: 写 ch08 §1-§2 索引结构 + WHERE 子句索引

**Files:**
- Read: `E:/obsidian/SQL/03-use-the-index-luke/luke/sql-anatomy-the-tree.html`(摘要)
- Read: `E:/obsidian/SQL/03-use-the-index-luke/luke/sql-anatomy-the-leaf-nodes.html`(摘要)
- Read: `E:/obsidian/SQL/03-use-the-index-luke/luke/sql-where-clause-functions.html`(摘要)
- Read: `E:/obsidian/SQL/03-use-the-index-luke/luke/sql-where-clause-obfuscation.html`(摘要)
- Create/Edit: `E:/obsidian/SQL/08-sql-skill/chapters/ch08-indexes-perf.md`

**Interfaces:** ch08 完整 9 段结构,后续 Task 3-7 追加 §3-§6 + Connects To + Key Takeaways。

- [ ] **Step 1: Read luke sql-anatomy-* 2 章节 + sql-where-clause-functions + sql-where-clause-obfuscation**(摘要读,不必全量)
- [ ] **Step 2: Write ch08 骨架 + Core Idea + §1 索引结构(完整 9 段)**
- [ ] **Step 3: Edit ch08 追加 §2 WHERE 子句索引(完整 9 段)**
- [ ] **Step 4: Verification — §1 + §2 必须含 4 + 4 = 8 条 Frameworks,8 条 Anti-patterns**

---

## Task 3: 写 ch08 §3 JOIN 算法

**Files:**
- Read: `E:/obsidian/SQL/03-use-the-index-luke/luke/sql-join-nested-loops-join-n1-problem.html`(摘要)
- Read: `E:/obsidian/SQL/03-use-the-index-luke/luke/sql-join-hash-join-partial-objects.html`(摘要)
- Read: `E:/obsidian/SQL/03-use-the-index-luke/luke/sql-join-sort-merge-join.html`(摘要)
- Edit: `E:/obsidian/SQL/08-sql/chapters/ch08-indexes-perf.md`

**Interfaces:** 追加 §3,本节 3-4 条 Frameworks。

- [ ] **Step 1: Read luke sql-join-* 3 章节**
- [ ] **Step 2: Edit ch08 追加 §3 JOIN 算法**
- [ ] **Step 3: Verification — §3 含 3-4 条 Frameworks + 3-4 条 Anti-patterns**

---

## Task 4: 写 ch08 §4 排序与分组索引

**Files:**
- Read: `E:/obsidian/SQL/03-use-the-index-luke/luke/sql-sorting-grouping-indexed-order-by.html`(摘要)
- Read: `E:/obsidian/SQL/03-use-the-index-luke/luke/sql-sorting-grouping-indexed-group-by.html`(摘要)
- Read: `E:/obsidian/SQL/03-use-the-index-luke/luke/sql-sorting-grouping-order-by-asc-desc-nulls-last.html`(摘要)
- Edit: `E:/obsidian/SQL/08-sql-skill/chapters/ch08-indexes-perf.md`

- [ ] **Step 1: Read luke sql-sorting-grouping-* 3 章节**
- [ ] **Step 2: Edit ch08 追加 §4 排序与分组索引**
- [ ] **Step 3: Verification — §4 含 3 条 Frameworks + ORDER BY 索引示例**

---

## Task 5: 写 ch08 §5 分页与窗口函数索引

**Files:**
- Read: `E:/obsidian/SQL/03-use-the-index-luke/luke/sql-partial-results-top-n-queries.html`(摘要)
- Read: `E:/obsidian/SQL/03-use-the-index-luke/luke/sql-partial-results-fetch-next-page.html`(摘要)
- Read: `E:/obsidian/SQL/03-use-the-index-luke/luke/sql-partial-results-window-functions.html`(摘要)
- Edit: `E:/obsidian/SQL/08-sql-skill/chapters/ch08-indexes-perf.md`

- [ ] **Step 1: Read luke sql-partial-results-* 3 章节**
- [ ] **Step 2: Edit ch08 追加 §5 分页与窗口函数索引**
- [ ] **Step 3: Verification — §5 含 Top-N / offset / 窗口 3 条 Frameworks**

---

## Task 6: 写 ch08 §6 EXPLAIN + pg_stat_statements

**Files:**
- Read: `E:/obsidian/SQL/03-use-the-index-luke/luke/sql-explain-plan.html`(摘要)
- Read: `E:/obsidian/SQL/03-use-the-index-luke/pg-docs/performance-tips.html`(摘要)
- Edit: `E:/obsidian/SQL/08-sql-skill/chapters/ch08-indexes-perf.md`

**Interfaces:** §6 是 ch08 深度核心,需 EXPLAIN ANALYZE 完整解读。

- [ ] **Step 1: Read luke sql-explain-plan + pg-docs performance-tips**(摘要)
- [ ] **Step 2: Edit ch08 追加 §6 EXPLAIN 与执行计划**
- [ ] **Step 3: Edit ch08 追加 pg_stat_statements 简表 + 慢 query top-N query**
- [ ] **Step 4: Verification — §6 含 4 大算子(Seq Scan / Index Scan / Bitmap Heap Scan / Hash Join)解读 + pg_stat_statements 示例**

---

## Task 7: ch08 Key Takeaways + Connects To + 收尾

**Files:**
- Edit: `E:/obsidian/SQL/08-sql-skill/chapters/ch08-indexes-perf.md`

- [ ] **Step 1: Edit ch08 追加 Key Takeaways 段(8-12 条要点)**
- [ ] **Step 2: Edit ch08 追加 Connects To 段(cross-ref 到 ch01/ch07/evidence-skill ch14)**
- [ ] **Step 3: Verification — 全文 ≥ 250 行,9 段结构齐全**
- [ ] **Step 4: invocation `superpowers:verification-before-completion`**

---

## Task 8: 写 ch01 语法铁律

**Files:**
- Read: `E:/obsidian/SQL/03-use-the-index-luke/sqlbolt/select_queries_with_order_of_execution.html`(摘要)
- Read: `E:/obsidian/SQL/03-use-the-index-luke/sqlbolt/select_queries_with_nulls.html`(摘要)
- Read: `E:/obsidian/SQL/03-use-the-index-luke/sqlbolt/select_queries_with_expressions.html`(摘要)
- Read: `E:/obsidian/SQL/05-sql-style-guide/`(Matt Mazur 风格指南)
- Create: `E:/obsidian/SQL/08-sql-skill/chapters/ch01-grammar.md`

**Interfaces:** ch01 9 段结构,4 节内容,目标 ~200 行。

- [ ] **Step 1: Read SQLBolt order_of_execution + with_nulls + with_expressions**
- [ ] **Step 2: Read sql-style-guide README 摘要**
- [ ] **Step 3: Write ch01 完整 9 段(§1 SQL 执行顺序 / §2 表达式规范 / §3 NULL 三值逻辑 / §4 风格铁律)**
- [ ] **Step 4: Verification — ch01 ≥ 180 行,8+ Frameworks,与 evidence-skill ch05 不重叠(中文列细节归 ch05)**

---

## Task 9: 写 ch07 PG 特有

**Files:**
- Read: `E:/obsidian/SQL/03-use-the-index-luke/pg-docs/functions.html`(摘要,数组/JSONB 函数)
- Read: `E:/obsidian/SQL/03-use-the-index-luke/pg-docs/indexes.html`(摘要,GIN/GIST)
- Read: `E:/Users/Duanyi/.claude/skills/evidence-skill/chapters/ch07-fdw-cross-db.md`(已读摘要,确认边界)
- Read: `E:/Users/Duanyi/.claude/skills/evidence-skill/chapters/ch05-sql-antipatterns.md`(已读摘要,确认边界)
- Create: `E:/obsidian/SQL/08-sql-skill/chapters/ch07-pg-specific.md`

**Interfaces:** ch07 9 段结构,5 节内容,目标 ~200 行。

- [ ] **Step 1: Read pg-docs functions + indexes 摘要**
- [ ] **Step 2: Write ch07 完整 9 段(§1 JSONB / §2 array / §3 GIN/GIST 索引决策 / §4 postgres_fdw 概览 + pgbouncer session-mode / §5 中文 schema 雷区)**
- [ ] **Step 3: Verification — ch07 ≥ 180 行,10+ Frameworks,与 evidence-skill ch05/ch07 不重叠(只补 GIN 决策 + 概览)**

---

## Task 10: 写 glossary.md

**Files:**
- Read: 3 个 chapter 的 Key Concepts 段(Task 2-9 产出后)
- Create: `E:/obsidian/SQL/08-sql-skill/glossary.md`

**Interfaces:** 按字母排序,~80 词条,末尾中文术语分组。

- [ ] **Step 1: Read ch01/ch07/ch08 Key Concepts 段,提取词条**
- [ ] **Step 2: Write glossary.md(字母 A-Z + 中文段,每条 term — 定义 + chapter 来源)**
- [ ] **Step 3: Verification — ≥ 70 词条,无漏掉 chapter Key Concepts 中词汇**

---

## Task 11: 写 patterns.md

**Files:**
- Read: 3 个 chapter 的 Frameworks + Anti-patterns 段
- Create: `E:/obsidian/SQL/08-sql-skill/patterns.md`

**Interfaces:** 8 大模式 + 反模式总表。

- [ ] **Step 1: Read ch01/ch07/ch08 Frameworks + Anti-patterns 段**
- [ ] **Step 2: Write patterns.md(8 大模式,每条 When/How/Trade-offs)**
- [ ] **Step 3: Write 反模式总表(12+ 条 ❌ → ✅ 对照)**
- [ ] **Step 4: Verification — ≥ 8 大模式,≥ 12 条反模式总表**

---

## Task 12: 写 cheatsheet.md

**Files:**
- Create: `E:/obsidian/SQL/08-sql-skill/cheatsheet.md`

**Interfaces:** 14+ 决策表 + 12 关键经验 + 12 阶段 actionable + 调研入口。

- [ ] **Step 1: Write cheatsheet.md(决策表覆盖:索引选择 / WHERE 索引 / JOIN 选择 / ORDER BY / Top-N / EXPLAIN 算子 / JSONB / 中文 schema / GIN / BRIN / Hash / 慢 query / 反模式 + 7 个本地资料源路径)**
- [ ] **Step 2: Write 12 关键经验段**
- [ ] **Step 3: Write 调研 / 沉淀入口段(GBrain recall + 03-use-the-index-luke 子索引 + 7 个本地资料源)**
- [ ] **Step 4: Verification — ≥ 12 决策表,≥ 10 关键经验,调研入口含 03 子索引**

---

## Task 13: 写 SKILL.md

**Files:**
- Create: `E:/obsidian/SQL/08-sql-skill/SKILL.md`

**Interfaces:** YAML frontmatter + How to Use + Core Frameworks(12)+ Chapter Index(10,3 完成 + 7 stub)+ Topic Index + Supporting Files + 调研入口 + Scope & Limits。

- [ ] **Step 1: Write SKILL.md 顶部 YAML frontmatter(name / description / triggers)**
- [ ] **Step 2: Write SKILL.md How to Use + 12 大 Core Frameworks(基于 ch08 12+ 铁律精选)**
- [ ] **Step 3: Write SKILL.md Chapter Index(10 章全景,3 章 ✓ + 7 章 stub)**
- [ ] **Step 4: Write SKILL.md Topic Index(A-Z 关键术语链接到 glossary)**
- [ ] **Step 5: Write SKILL.md Supporting Files + 调研 / 沉淀入口 + Scope & Limits**
- [ ] **Step 6: Verification — ≥ 130 行,12 大 Frameworks 完整,ch02-06/09/10 全部 stub**

---

## Task 14: 全套 verification-before-completion

**Files:**
- Read+verify: 7 个 Phase 2 输出文件

- [ ] **Step 1: invocation `superpowers:verification-before-completion`**
- [ ] **Step 2: 验证 9 个验收清单(见 spec §9.1-9.5)**
  - 7 个文件存在
  - 形态对齐 evidence-skill
  - 内容深度达标
  - 与 evidence-skill 不重叠
  - 沉淀入口完整
- [ ] **Step 3: 写 `handoff-sql-skill-phase2-2026-10-14.md` 给后续会话接力**(必做 — Phase 2 完成,接 Phase 3 stub chapter 写作 + 评测集)

---

## Execution Handoff

Plan 完成,保存到 `F:/soft/00selfmade/sql-skill/docs/superpowers/plans/2026-10-14-sql-skill-phase2.md`。

执行方式:本项目无 git + 14 个 task 跨 7 文件 + 紧密依赖(ch08 → glossary → SKILL.md 顺序),推荐 **Native 执行**(inline,本会话内完成)。subagent-driven 需要 14 个 fresh subagent 上下文,成本高但并行空间小(因为 ch08 内部 §1-§6 强顺序)。
