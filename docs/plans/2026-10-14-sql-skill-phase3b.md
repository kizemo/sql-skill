# sql-skill Phase 3b — ch02/ch03/ch04/ch05 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (本会话 Native). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Phase 3b 知识抽取,写 ch02 JOIN 7 种 + ch03 窗口函数 + ch04 CTE/递归 + ch05 聚合 4 个完整 9 段章节 + 更新 4 辅助文件 + 写 handoff Phase 3c。

**Tech Stack:** Markdown / Obsidian vault / Read-write-edit 工具链

**Spec:** `F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase3b-design.md`
**Handoff:** `F:/soft/00selfmade/sql-skill/handoff-sql-skill-phase3b-2026-10-14.md`

## Global Constraints

- **输出路径**:4 chapter → `E:/obsidian/SQL/08-sql-skill/chapters/ch02-joins.md` / `ch03-window-functions.md` / `ch04-cte-recursion.md` / `ch05-aggregates.md`
- **辅助文件**:4 改 → `E:/obsidian/SQL/08-sql-skill/SKILL.md` / `glossary.md` / `patterns.md` / `cheatsheet.md`
- **handoff**:1 写 → `F:/soft/00selfmade/sql-skill/handoff-sql-skill-phase3c-2026-10-14.md`
- **深度目标**:ch02 250-300 / ch03 300 / ch04 250 / ch05 200 行(对齐 ch09 429 行)
- **9 段结构固定**:Core Idea / Frameworks Introduced / Key Concepts / Mental Models / Anti-patterns / Code Examples / Reference Tables / Key Takeaways / Connects To
- **跨引用格式**:章节引用 `ch0X §X`,evidence-skill 引用 `evidence-skill ch0X`,luke 引用 `luke/<file>.html`,civilian7 引用 `civilian7/<path>`
- **不重叠 Phase 2 + evidence-skill**:ch02-ch05 不重写 ch01/ch07/ch08/ch09 已写铁律;evidence-skill ch05/ch07/ch14/ch16 业务侧权威只引用
- **CLAUDE.md 红线**:禁 rm/Remove-Item;禁 git reset --hard;禁 DROP/TRUNCATE/DELETE 不带 WHERE;禁文件名用 \ / : * ? " < > |
- **临时文件**:`C:\Temp\`(不写 ~/.tmp/)
- **单次 Write ≤ 400 行 / 8000 tokens**(避 120s abort)
- **Edit 锚定追加**(避免触发新文档生成时单次输入过大)
- **执行方式**:Native(用户预选)

## Review Focus

5 个 spec 涉及但无 task 测试的潜在失误面:

1. **ch02 重写 ch08 §3 JOIN 算法**:补救 — ch02 §6 只引 1 行,不重写 EXPLAIN 算子细节,完整 reference 走 ch08 §3。
2. **ch03 窗口函数重写 ch05 聚合**:补救 — ch03 §4 与 ch05 §1 GROUP BY 显式区分,各自定义"何时用窗口 vs 何时用 GROUP BY"。
3. **ch04 CTE 与 ch09 §6 N+1 反模式混淆**:补救 — ch04 §4 CTE vs 子查询性能对比,不混 N+1 反模式(归 ch09 §6)。
4. **ch05 HAVING 与 WHERE 混淆**:补救 — ch05 §3 显式引用 ch01 §1 SQL 执行顺序,WHERE 行过滤 vs HAVING 聚合后过滤。
5. **4 辅助文件更新遗漏**:补救 — Task 6 verification 检查 SKILL.md / glossary.md / patterns.md / cheatsheet.md grep ch02-ch05 引用齐全。

---

## Task 1: ch02 JOIN 完整 9 段(第一章节)

**Files:**
- Create: `E:/obsidian/SQL/08-sql-skill/chapters/ch02-joins.md`(骨架 + §1-§7 完整)

**Interfaces:**
- ch02 9 段齐全,Frameworks 10+ 条,Anti-patterns 8+ 条
- 跨引用 ch08 §3 / ch09 §2 / ch09 §6 / evidence-skill ch07
- 最终 ~250-300 行

- [ ] **Step 1: Write ch02 骨架 + Core Idea + §1 INNER JOIN 完整段**
- [ ] **Step 2: Edit ch02 追加 §2 OUTER JOIN 完整段(LEFT / RIGHT / FULL + ON vs WHERE)**
- [ ] **Step 3: Edit ch02 追加 §3 CROSS JOIN 完整段(笛卡尔积 / 隐式逗号 FROM)**
- [ ] **Step 4: Edit ch02 追加 §4 SELF JOIN 完整段(自连接 / 层次结构)**
- [ ] **Step 5: Edit ch02 追加 §5 NATURAL JOIN / USING 完整段**
- [ ] **Step 6: Edit ch02 追加 §6 JOIN 算法与性能 完整段(NL / Hash / Sort Merge,引用 ch08 §3)**
- [ ] **Step 7: Edit ch02 追加 §7 JOIN 反模式完整段(隐式逗号 / N+1 / 笛卡尔积 / 大表 JOIN)**
- [ ] **Step 8: Edit ch02 追加 Key Takeaways(8-12 条)**
- [ ] **Step 9: Edit ch02 追加 Connects To 段(cross-ref ch01/ch07/ch08/ch09 + evidence-skill ch07)**
- [ ] **Step 10: invocation `superpowers:verification-before-completion`**

## Task 2: ch03 窗口函数完整 9 段

**Files:**
- Create: `E:/obsidian/SQL/08-sql-skill/chapters/ch03-window-functions.md`

**Interfaces:**
- ch03 9 段齐全,Frameworks 8+ 条,Anti-patterns 6+ 条
- 跨引用 ch08 §5 / ch05 §1
- 最终 ~300 行

- [ ] **Step 1: Write ch03 骨架 + Core Idea + §1 OVER 子句基础完整段**
- [ ] **Step 2: Edit ch03 追加 §2 排序函数(ROW_NUMBER / RANK / DENSE_RANK / NTILE)**
- [ ] **Step 3: Edit ch03 追加 §3 分析函数(LAG / LEAD / FIRST_VALUE / LAST_VALUE / NTH_VALUE)**
- [ ] **Step 4: Edit ch03 追加 §4 聚合窗口(SUM/AVG/COUNT OVER + 滑动窗口)**
- [ ] **Step 5: Edit ch03 追加 §5 命名窗口(WINDOW 子句)**
- [ ] **Step 6: Edit ch03 追加 §6 帧子句(ROWS BETWEEN / RANGE BETWEEN)**
- [ ] **Step 7: Edit ch03 追加 §7 窗口函数反模式**
- [ ] **Step 8: Edit ch03 追加 Key Takeaways(8-12 条)**
- [ ] **Step 9: Edit ch03 追加 Connects To 段(cross-ref ch05 / ch08)**
- [ ] **Step 10: invocation `superpowers:verification-before-completion`**

## Task 3: ch04 CTE/递归完整 9 段

**Files:**
- Create: `E:/obsidian/SQL/08-sql-skill/chapters/ch04-cte-recursion.md`

**Interfaces:**
- ch04 9 段齐全,Frameworks 6+ 条,Anti-patterns 8+ 条
- 跨引用 evidence-skill ch07 FDW CTE local scope
- 最终 ~250 行

- [ ] **Step 1: Write ch04 骨架 + Core Idea + §1 WITH clause 基础完整段**
- [ ] **Step 2: Edit ch04 追加 §2 WITH RECURSIVE(递归 CTE + UNION / UNION ALL)**
- [ ] **Step 3: Edit ch04 追加 §3 MATERIALIZED CTE 决策(PG 12+)**
- [ ] **Step 4: Edit ch04 追加 §4 CTE vs 子查询 vs 临时表(性能对比)**
- [ ] **Step 5: Edit ch04 追加 §5 CTE 可读性 + 维护性**
- [ ] **Step 6: Edit ch04 追加 §6 递归 CTE 应用场景(层次结构 / 图遍历 / 数字序列)**
- [ ] **Step 7: Edit ch04 追加 §7 CTE 反模式(过度嵌套 / 物化滥用)**
- [ ] **Step 8: Edit ch04 追加 Key Takeaways(8-12 条)**
- [ ] **Step 9: Edit ch04 追加 Connects To 段(cross-ref ch01 / evidence-skill ch07)**
- [ ] **Step 10: invocation `superpowers:verification-before-completion`**

## Task 4: ch05 聚合完整 9 段

**Files:**
- Create: `E:/obsidian/SQL/08-sql-skill/chapters/ch05-aggregates.md`

**Interfaces:**
- ch05 9 段齐全,Frameworks 6+ 条,Anti-patterns 8+ 条
- 跨引用 ch01 §1 / ch08 §4
- 最终 ~200 行

- [ ] **Step 1: Write ch05 骨架 + Core Idea + §1 基础聚合完整段(COUNT / SUM / AVG / MIN / MAX)**
- [ ] **Step 2: Edit ch05 追加 §2 GROUP BY(列表达式 / 隐式列 / ROLLUP / CUBE)**
- [ ] **Step 3: Edit ch05 追加 §3 HAVING(聚合后过滤,引用 ch01 §1 执行顺序)**
- [ ] **Step 4: Edit ch05 追加 §4 FILTER 子句(PG 9.4+)**
- [ ] **Step 5: Edit ch05 追加 §5 GROUPING SETS / GROUPING()(多维聚合)**
- [ ] **Step 6: Edit ch05 追加 §6 聚合反模式**
- [ ] **Step 7: Edit ch05 追加 §7 窗口聚合 vs GROUP BY(引用 ch03 §4)**
- [ ] **Step 8: Edit ch05 追加 Key Takeaways(8-12 条)**
- [ ] **Step 9: Edit ch05 追加 Connects To 段(cross-ref ch01 / ch03 / ch08)**
- [ ] **Step 10: invocation `superpowers:verification-before-completion`**

## Task 5: 4 辅助文件更新

**Files:**
- Edit: `E:/obsidian/SQL/08-sql-skill/SKILL.md`
- Edit: `E:/obsidian/SQL/08-sql-skill/glossary.md`
- Edit: `E:/obsidian/SQL/08-sql-skill/patterns.md`
- Edit: `E:/obsidian/SQL/08-sql-skill/cheatsheet.md`

**Interfaces:**
- SKILL.md Chapter Index 把 ch02-ch05 `🔵 stub` → `✅` 完整
- glossary.md 新增 ch02-ch05 词条 ≥ 15 条
- patterns.md 反模式总表追加 ch02-ch05 反模式 ≥ 15 条
- cheatsheet.md 新增 1-2 张决策表 + 关键经验追加 ≥ 1 条

- [ ] **Step 1: Edit SKILL.md Chapter Index ch02-ch05 行更新为 `✅` 完整 + 加链接**
- [ ] **Step 2: Edit SKILL.md Topic Index 加 ch02-ch05 关键术语链接**
- [ ] **Step 3: Edit SKILL.md Supporting Files 加 ch02-ch05 链接**
- [ ] **Step 4: Edit glossary.md 按字母位置追加 ch02-ch05 新词条**
- [ ] **Step 5: Edit patterns.md 反模式总表追加 ch02-ch05 反模式条目**
- [ ] **Step 6: Edit cheatsheet.md "9. 反模式决策规则" 段追加 ch02-ch05 决策条目**
- [ ] **Step 7: Edit cheatsheet.md "11. 必读 12 关键经验" 段追加 1-2 条 ch02-ch05 关键经验**
- [ ] **Step 8: Edit cheatsheet.md "13. 调研 / 沉淀入口" 段加 ch02-ch05 链接**
- [ ] **Step 9: invocation `superpowers:verification-before-completion`**

## Task 6: Phase 3b verification + handoff

**Files:**
- Verify: 5 个文件存在 + 9 段 + 引用齐全
- Create: `F:/soft/00selfmade/sql-skill/handoff-sql-skill-phase3c-2026-10-14.md`

- [ ] **Step 1: invocation `superpowers:verification-before-completion`**
- [ ] **Step 2: Verify 9 验收清单**
  - ch02/ch03/ch04/ch05 9 段齐全(grep "## ")
  - ch02 250-300 / ch03 300 / ch04 250 / ch05 200 行
  - Frameworks 累计 ≥ 30 条
  - Anti-patterns 累计 ≥ 30 条
  - 不重叠 ch01/ch07/ch08/ch09 已写内容
  - SKILL.md / glossary.md / patterns.md / cheatsheet.md ch02-ch05 引用齐全
- [ ] **Step 3: 写 `handoff-sql-skill-phase3c-2026-10-14.md` 给 Phase 3c 接力(ch06 集合操作 + ch10 evidence-bridge)**
- [ ] **Step 4: Phase 3b ledger 更新**

---

## Execution Handoff

Plan 完成,保存到 `F:/soft/00selfmade/sql-skill/docs/superpowers/plans/2026-10-14-sql-skill-phase3b.md`。

执行方式:用户已选 **Native**(本会话内顺序完成)。subagent-driven 需要 7 个 fresh subagent 上下文 + 跨 subagent 引用 ch08/ch09 决策表,但 ch02-ch05 4 章可顺序 Native 完成,引用 handoff + 已读文件已足够,成本更低。

Native 执行顺序:ch02 → ch03 → ch04 → ch05 → 4 辅助文件 → handoff。每章完成后 invocation `superpowers:verification-before-completion` 验证。