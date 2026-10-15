# sql-skill Phase 3c — ch06/ch10/v1.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (本会话 Native). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Phase 3c 知识抽取,写 ch06 集合操作 + ch10 evidence-bridge 2 个完整 9 段章节 + 更新 4 辅助文件 + 写 handoff v1.0。sql-skill v1.0 完整版 10 章交付。

**Tech Stack:** Markdown / Obsidian vault / Read-write-edit 工具链

**Spec:** `F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase3c-design.md`
**Handoff:** `F:/soft/00selfmade/sql-skill/handoff-sql-skill-phase3c-2026-10-14.md`

## Global Constraints

- **输出路径**:2 chapter → `E:/obsidian/SQL/08-sql-skill/chapters/ch06-set-ops.md` / `ch10-evidence-bridge.md`
- **辅助文件**:4 改 → `E:/obsidian/SQL/08-sql-skill/SKILL.md` / `glossary.md` / `patterns.md` / `cheatsheet.md`
- **handoff v1.0**:1 写 → `F:/soft/00selfmade/sql-skill/handoff-sql-skill-v1-2026-10-14.md`
- **深度目标**:ch06 150-200 / ch10 250 行(对齐 ch09 429 略小)
- **9 段结构固定**:Core Idea / Frameworks Introduced / Key Concepts / Mental Models / Anti-patterns / Code Examples / Reference Tables / Key Takeaways / Connects To
- **跨引用格式**:章节引用 `ch0X §X`,evidence-skill 引用 `evidence-skill ch0X`,luke 引用 `luke/<file>.html`,civilian7 引用 `civilian7/<path>`
- **不重叠 Phase 2/3a/3b + evidence-skill**:ch06/ch10 不重写 ch01-ch05/ch07-ch09 已写铁律;evidence-skill 18 章业务侧权威只引用
- **ch10 边界**:不重写 evidence-skill 18 章内容,只引 + 协作范式;ch10 §1-§6 必含 evidence-skill 18 章 cross-ref
- **CLAUDE.md 红线**:禁 rm/Remove-Item;禁 git reset --hard;禁 DROP/TRUNCATE/DELETE 不带 WHERE;禁文件名用 \ / : * ? " < > |
- **临时文件**:`C:\Temp\`(不写 ~/.tmp/)
- **单次 Write ≤ 400 行 / 8000 tokens**(避 120s abort)
- **Edit 锚定追加**(避免触发新文档生成时单次输入过大)
- **执行方式**:Native(用户预选)

## Review Focus

5 个 spec 涉及但无 task 测试的潜在失误面:

1. **ch06 重写 ch02 JOIN**:补救 — ch06 §4 只引 1 行 UNION vs JOIN 等价场景,不重写 JOIN 7 种细节,完整 reference 走 ch02。
2. **ch10 重写 evidence-skill 18 章内容**:补救 — ch10 §2/§3/§4 引用 evidence-skill ch05/ch07/ch14/ch16 作为业务侧权威,ch10 只讲"协作范式"和"沉淀清单",不重写 nginx immutable / pgbouncer session-mode / FDW 5 步 / MCP 4 道防线具体内容。
3. **ch06 INTERSECT 重复 ch05 聚合**:补救 — ch06 §2 显式区分 INTERSECT(行级集合)与 GROUP BY + HAVING(聚合过滤),各自定义"何时用集合操作 vs 何时用 GROUP BY"。
4. **ch10 评测集与 civilian7 1065 题混淆**:补救 — ch10 §5 引用 civilian7 作为评测源,不重写 1065 题筛选机制。
5. **4 辅助文件更新遗漏**:补救 — Task 5 verification 检查 SKILL.md / glossary.md / patterns.md / cheatsheet.md grep ch06-ch10 引用齐全。

---

## Task 1: ch06 集合操作完整 9 段(第一章节)

**Files:**
- Create: `E:/obsidian/SQL/08-sql-skill/chapters/ch06-set-ops.md`

**Interfaces:**
- ch06 9 段齐全,Frameworks 8+ 条,Anti-patterns 6+ 条
- 跨引用 ch02 JOIN 7 种 / ch05 聚合 / ch09 §2 SELECT *
- 最终 ~150-200 行

- [ ] **Step 1: Write ch06 骨架 + Core Idea + §1 UNION / UNION ALL 完整段**
- [ ] **Step 2: Edit ch06 追加 §2 INTERSECT 完整段(交集,自动去重)**
- [ ] **Step 3: Edit ch06 追加 §3 EXCEPT 完整段(差集,自动去重)**
- [ ] **Step 4: Edit ch06 追加 §4 集合操作与 JOIN 转换完整段(等价表达,引用 ch02)**
- [ ] **Step 5: Edit ch06 追加 §5 集合操作 + ORDER BY / LIMIT 完整段(顶层 vs 子查询)**
- [ ] **Step 6: Edit ch06 追加 §6 集合操作反模式完整段(列数类型不匹配 / ORDER BY 误用)**
- [ ] **Step 7: Edit ch06 追加 Key Takeaways(6-10 条)**
- [ ] **Step 8: Edit ch06 追加 Connects To 段(cross-ref ch02 / ch05 / ch09)**
- [ ] **Step 9: invocation `superpowers:verification-before-completion`**

## Task 2: ch10 evidence-bridge 完整 9 段

**Files:**
- Create: `E:/obsidian/SQL/08-sql-skill/chapters/ch10-evidence-bridge.md`

**Interfaces:**
- ch10 9 段齐全,Frameworks 6+ 条,Anti-patterns 4+ 条
- 跨引用 evidence-skill 18 章(不重写,只引)
- 最终 ~250 行

- [ ] **Step 1: Write ch10 骨架 + Core Idea + §1 sql-skill 与 evidence-skill 边界完整段(已固化)**
- [ ] **Step 2: Edit ch10 追加 §2 SQL Agent 范式(MCP + 4 道防线,引用 evidence-skill ch16)**
- [ ] **Step 3: Edit ch10 追加 §3 中文 schema 假名修复流程(引用 evidence-skill ch05)**
- [ ] **Step 4: Edit ch10 追加 §4 BI 场景性能与 Core 28 page(引用 evidence-skill ch14)**
- [ ] **Step 5: Edit ch10 追加 §5 评测集(引用 civilian7 1065 题)**
- [ ] **Step 6: Edit ch10 追加 §6 sql-skill v1.0 沉淀清单**
- [ ] **Step 7: Edit ch10 追加 Key Takeaways(6-10 条)**
- [ ] **Step 8: Edit ch10 追加 Connects To 段(cross-ref evidence-skill 18 章)**
- [ ] **Step 9: invocation `superpowers:verification-before-completion`**

## Task 3: 4 辅助文件更新

**Files:**
- Edit: `E:/obsidian/SQL/08-sql-skill/SKILL.md`
- Edit: `E:/obsidian/SQL/08-sql-skill/glossary.md`
- Edit: `E:/obsidian/SQL/08-sql-skill/patterns.md`
- Edit: `E:/obsidian/SQL/08-sql-skill/cheatsheet.md`

**Interfaces:**
- SKILL.md Chapter Index 把 ch06 / ch10 `🔵 stub` → `✅` 完整
- glossary.md 新增 ch06 / ch10 词条 ≥ 8 条
- patterns.md 反模式总表追加 ch06 / ch10 反模式 ≥ 8 条
- cheatsheet.md 新增决策表 + 关键经验追加 ≥ 2 条

- [ ] **Step 1: Edit SKILL.md Chapter Index ch06 / ch10 行更新为 `✅` 完整 + 加链接**
- [ ] **Step 2: Edit SKILL.md Topic Index 加 ch06 / ch10 关键术语链接(UNION / INTERSECT / EXCEPT / 集合操作 / evidence-bridge)**
- [ ] **Step 3: Edit SKILL.md Supporting Files 加 ch06 / ch10 链接 + 已知边界加 v1.0 完整版**
- [ ] **Step 4: Edit glossary.md 按字母位置追加 ch06 / ch10 新词条(UNION / INTERSECT / EXCEPT / 集合操作等)**
- [ ] **Step 5: Edit patterns.md 反模式总表追加 ch06 / ch10 反模式条目**
- [ ] **Step 6: Edit cheatsheet.md "9. 反模式决策规则" 段追加 ch06 / ch10 决策条目**
- [ ] **Step 7: Edit cheatsheet.md "11. 必读 12 关键经验" 段追加 1-2 条 ch06 / ch10 关键经验**
- [ ] **Step 8: Edit cheatsheet.md "13. 调研 / 沉淀入口" 段加 ch06 / ch10 链接**
- [ ] **Step 9: invocation `superpowers:verification-before-completion`**

## Task 4: Phase 3c verification + v1.0 handoff

**Files:**
- Verify: 6 个文件存在 + 9 段 + 引用齐全
- Create: `F:/soft/00selfmade/sql-skill/handoff-sql-skill-v1-2026-10-14.md`

- [ ] **Step 1: invocation `superpowers:verification-before-completion`**
- [ ] **Step 2: Verify 9 验收清单**
  - ch06/ch10 9 段齐全(grep "## ")
  - ch06 150-200 / ch10 250 行
  - Frameworks / Anti-patterns 数达标
  - 不重叠 ch01-ch05/ch07-ch09 已写内容
  - ch10 不重写 evidence-skill 18 章
  - SKILL.md / glossary.md / patterns.md / cheatsheet.md ch06-ch10 引用齐全
- [ ] **Step 3: 写 `handoff-sql-skill-v1-2026-10-14.md` 完整版交付**
  - 项目总览(10 章 + 4 辅助文件 / 总行数)
  - 必读顺序(按业务流)
  - 调研入口(luke / civilian7 / nl2sql / evidence-skill)
  - 维护建议(PG 大版本 / 季度 review / 评测集更新)
  - 未来扩展(Phase 4+:评测 / 自动化测试 / 多 DB)
- [ ] **Step 4: Phase 3c ledger 更新**

---

## Execution Handoff

Plan 完成,保存到 `F:/soft/00selfmade/sql-skill/docs/superpowers/plans/2026-10-14-sql-skill-phase3c.md`。

执行方式:用户已选 **Native**(本会话内顺序完成)。ch06 较小 ~150 行,ch10 较大 ~250 行(2-3 次 Write),4 辅助文件 update,1 handoff,合计 7 文件 ~700-800 行。Native 顺序执行最稳。