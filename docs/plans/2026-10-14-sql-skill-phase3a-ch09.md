# sql-skill Phase 3a — ch09 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (本会话 native). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Phase 3a 知识抽取,写 ch09 反模式综合 + 更新 4 个辅助文件(SKILL.md / glossary.md / patterns.md / cheatsheet.md),给 sql-skill v0.9 落地第 9 章。

**Architecture:** Markdown knowledge synthesis 任务。形态严格对齐 Phase 2 沉淀(ch01/ch07/ch08 + supporting 文件),每 chapter 9 段固定结构。ch09 反模式综合 7 节 + civilian7 1065 题筛选 + evidence-skill ch05 联动。

**Tech Stack:** Markdown / Obsidian vault / Read-write-edit 工具链

**Spec:** `F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase3-design.md`

## Global Constraints

- **ch09 输出路径**:`E:/obsidian/SQL/08-sql-skill/chapters/ch09-antipatterns.md`
- **文件名规范**:编号 `ch09` + 英文短词 `antipatterns`,无 emoji / 无空格 / 无 Windows 禁用字符
- **ch09 深度目标**:~350 行(对齐 ch08 405 行);Frameworks 18+ 条;Anti-patterns 25+ 条
- **每 chapter 9 段固定结构**:Core Idea / Frameworks Introduced / Key Concepts / Mental Models / Anti-patterns / Code Examples / Reference Tables / Key Takeaways / Connects To
- **跨引用格式**:章节引用 `ch0X`,evidence-skill 引用 `evidence-skill ch0X`,luke 引用 `luke/<file>.html`,civilian7 引用 `civilian7/<path>`
- **不重叠 Phase 2 + evidence-skill**:ch09 不重写 ch01/ch07/ch08 已写铁律;evidence-skill ch05 业务侧雷区权威归 ch05,ch09 只引用
- **CLAUDE.md 红线**:禁 rm/Remove-Item;禁 git reset --hard;禁 DROP/TRUNCATE;禁在文件名用 \ / : * ? " < > |
- **临时文件**:`C:\Temp\`(不写 ~/.tmp/)
- **单次 Write ≤ 400 行 / 8000 tokens**(避 120s abort)

## Review Focus

5 个 spec 涉及但无 task 测试的潜在失误面:

1. **ch09 反模式重复 ch01/ch07/ch08**:补救 — 每节 Frameworks 显式标注"详 ch0X §X",避免重写。
2. **civilian7 引用无源**:补救 — 每个反模式标注 civilian7 引用路径(`civilian7/exercises/beginner/...`)。
3. **ch09 与 evidence-skill ch05 边界**:补救 — ch09 §5 字符串/日期引用 evidence-skill ch05 作为业务侧权威,不重写假名清单。
4. **4 个辅助文件更新遗漏**:补救 — Task 5 verification 检查 4 文件 grep ch09 引用。
5. **chapter 间 index 互通**:补救 — ch09 Connects To 段固定列 cross-ref 到 ch01/ch07/ch08 + evidence-skill ch05/ch14。

---

## Task 1: ch09 §1-§3 数据建模 + 查询 + 索引反模式

**Files:**
- Create: `E:/obsidian/SQL/08-sql-skill/chapters/ch09-antipatterns.md`(骨架 + §1-§3)
- Edit: 同文件追加 §4-§7(在 Task 2)

**Interfaces:**
- ch09 完整 9 段结构,后续 Task 2 追加 §4-§7 + Connects To
- 最终 ~350 行

- [ ] **Step 1: Write ch09 完整骨架 + Core Idea + §1 数据建模反模式(EAV 9 段完整)**
- [ ] **Step 2: Edit ch09 追加 §2 查询编写反模式(SELECT * / 隐式 JOIN 9 段完整)**
- [ ] **Step 3: Edit ch09 追加 §3 索引使用反模式(过度索引 / 无用索引 9 段完整)**
- [ ] **Step 4: Verification — §1-§3 各含 2-3 条 Frameworks + 3-5 条 Anti-patterns + Code Examples**

## Task 2: ch09 §4-§7 NULL + 字符串日期 + 性能 + 安全反模式

**Files:**
- Edit: `E:/obsidian/SQL/08-sql-skill/chapters/ch09-antipatterns.md`

- [ ] **Step 1: Edit ch09 追加 §4 NULL 处理反模式(NULL 拼接 / NULL 聚合 / NULL 比较)**
- [ ] **Step 2: Edit ch09 追加 §5 字符串/日期反模式(隐式 cast / date SUBSTR / 中文列)**(引用 evidence-skill ch05 业务侧权威)
- [ ] **Step 3: Edit ch09 追加 §6 性能反模式(N+1 / 大 OFFSET / 函数索引失效)**(引用 ch08)
- [ ] **Step 4: Edit ch09 追加 §7 安全反模式(SQL 注入 / 字符串拼接 query)**(引用 evidence-skill ch16 MCP 防线)
- [ ] **Step 5: Edit ch09 追加 Key Takeaways(8-12 条要点)**
- [ ] **Step 6: Edit ch09 追加 Connects To 段(cross-ref ch01/ch07/ch08 + evidence-skill ch05/ch14/ch16)**
- [ ] **Step 7: Verification — ch09 全文 ≥ 320 行,9 段结构齐全,Frameworks ≥ 18,Anti-patterns ≥ 25**

## Task 3: 更新 SKILL.md Chapter Index

**Files:**
- Edit: `E:/obsidian/SQL/08-sql-skill/SKILL.md`

**Interfaces:** ch09: 🔵 stub → ✅ 完整,Ch09 链接到新文件,Topic Index 加 ch09 关键术语

- [ ] **Step 1: Edit SKILL.md "Chapter Index" 段把 ch09 状态 `🔵 stub` → `✅` 完整,加 ch09 链接**
- [ ] **Step 2: Edit SKILL.md "Chapter Index" 段 ch09 行加关键内容(25+ 反模式 + civilian7 + evidence-skill ch05 联动)**
- [ ] **Step 3: Edit SKILL.md "Topic Index" 段加 ch09 关键术语链接(EAV / SELECT * / SQL 注入 / N+1 等)**
- [ ] **Step 4: Edit SKILL.md "Supporting Files" 段加 ch09 链接和行数**
- [ ] **Step 5: Edit SKILL.md "调研 / 沉淀入口" 段加 ch09 链接**
- [ ] **Step 6: Verification — SKILL.md grep ch09 ≥ 5 处引用**

## Task 4: 更新 glossary.md 加 ch09 词条

**Files:**
- Edit: `E:/obsidian/SQL/08-sql-skill/glossary.md`

**Interfaces:** 按字母排序,从 ch09 Key Concepts 提取 ~15 新词条

- [ ] **Step 1: Read ch09 Key Concepts 段,提取 ~15 新词条(EAV / SQL injection / N+1 / 隐式 cast 等)**
- [ ] **Step 2: Edit glossary.md 按字母位置追加新词条**
- [ ] **Step 3: Verification — glossary.md 词条数 ≥ 90(原 ~80 + 新 ~15)**

## Task 5: 更新 patterns.md 加 ch09 反模式

**Files:**
- Edit: `E:/obsidian/SQL/08-sql-skill/patterns.md`

**Interfaces:** 反模式总表追加 ~10 条 ch09 反模式

- [ ] **Step 1: Read ch09 Anti-patterns 段,提取 ~10 关键反模式**
- [ ] **Step 2: Edit patterns.md "反模式总表" 追加 ch09 反模式(每条 ❌ → ✅ + chapter 来源)**
- [ ] **Step 3: Verification — patterns.md 反模式总表 ≥ 30 条(原 20 + 新 10)**

## Task 6: 更新 cheatsheet.md 加 ch09 决策表

**Files:**
- Edit: `E:/obsidian/SQL/08-sql-skill/cheatsheet.md`

**Interfaces:** 决策表追加 1-2 张 ch09 决策表 + 12 关键经验追加

- [ ] **Step 1: Edit cheatsheet.md 追加 "9. 反模式决策表" 段(ch09 反模式决策 / EAV / SELECT * / 字符串日期 / 安全)**
- [ ] **Step 2: Edit cheatsheet.md "12 关键经验" 段追加 1-2 条 ch09 要点(避免 SELECT * / SQL 注入)**
- [ ] **Step 3: Edit cheatsheet.md "调研 / 沉淀入口" 段加 ch09 链接**
- [ ] **Step 4: Verification — cheatsheet.md 决策表 ≥ 14 张,关键经验 ≥ 13 条**

## Task 7: Phase 3a verification + handoff

**Files:**
- Verify: 5 个文件存在 + 9 段 + 反模式数
- Create: `F:/soft/00selfmade/sql-skill/handoff-sql-skill-phase3a-2026-10-14.md`

- [ ] **Step 1: invocation `superpowers:verification-before-completion`**
- [ ] **Step 2: Verify 9 验收清单**
  - ch09 9 段齐全(grep "## ")
  - ch09 Frameworks ≥ 18 条
  - ch09 Anti-patterns ≥ 25 条
  - SKILL.md / glossary.md / patterns.md / cheatsheet.md ch09 引用齐全
  - 与 Phase 2 + evidence-skill 不重叠
  - handoff 写完
- [ ] **Step 3: 写 `handoff-sql-skill-phase3a-2026-10-14.md` 给 Phase 3b 接力**(ch02/ch03/ch04/ch05 4 个 stub → 完整章节)
- [ ] **Step 4: Phase 3a ledger 更新**

---

## Execution Handoff

Plan 完成,保存到 `F:/soft/00selfmade/sql-skill/docs/superpowers/plans/2026-10-14-sql-skill-phase3a-ch09.md`。

执行方式:本项目无 git + 7 个 task 跨 5 文件 + ch09 内部 §1-§7 强顺序,推荐 **Native 执行**(inline,本会话内完成)。subagent-driven 需要 7 个 fresh subagent 上下文,但 ch09 §1-§7 强顺序依赖,并行空间小,成本高。
