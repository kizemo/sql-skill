# sql-skill Phase 3b — 会话交接 handoff(完整版)

> 会话结束日期: 2026-10-14
> 当前阶段: **Phase 3a 完成 / Phase 3b 待启动(全量推进)**
> 接力目标: **全量完成 Phase 3b** — ch02 / ch03 / ch04 / ch05 4 个 stub → 完整 9 段章节 + 4 辅助文件更新 + handoff Phase 3c
> 第一个 chapter: **ch02 JOIN 7 种 + 性能差异**

---

## 一、项目总览(新会话必读背景)

### 1.1 sql-skill 项目定位

**通用 SQL 编写专业度 Skill**,面向企业 PostgreSQL + Evidence BI 场景,定位"Skill / Engine / 库"形态(非 BI 产品)。让 Claude/OpenClaw agent 写更专业、更准确的 SQL。

### 1.2 与 evidence-skill 互补关系(已固化边界)

| Skill | 覆盖 |
|---|---|
| **sql-skill**(本项目) | 通用 SQL 知识(语法 / 性能 / 反模式 / PG 特性)— ch01-ch10 |
| evidence-skill | 业务落地知识(Evidence BI / 中文 PG schema / nginx / FDW / MCP)— 18 章 |
| 联动 | sql-skill ch02-09 + evidence-skill ch05/ch07/ch14/ch16 互补 |

**核心边界铁律**(沿用 Phase 2 + 3a,不可破坏):
- sql-skill ch02 不写 nginx immutable / pgbouncer session-mode(归 evidence-skill ch14)
- sql-skill ch02 不重写 postgres_fdw 完整 5 步 SQL(归 evidence-skill ch07,只引简化版 + 引用)
- sql-skill ch02 不重写中文列双引号细节(归 evidence-skill ch05,只提通用)
- ch02 不重复 ch01/ch07/ch08/ch09 已写内容,只引用(详 § 三)

### 1.3 用户技术栈

- **数据库**:企业 PostgreSQL(中文 schema,列名如 `"店铺"` `"订单日期"`)
- **BI 工具**:Evidence BI (Core 2026,生产在跑)
- **Agent 平台**:Claude Code / OpenClaw(已装 evidence-skill 自建 skill)
- **凭据**:环境变量管理(CLAUDE.md 硬编码红线)

---

## 二、Phase 3b 必交付清单(全量)

### 2.1 4 个 chapter 文件(本次必完成)

| 路径 | 深度 | 主题 | 优先级 |
|---|---|---|---|
| `E:/obsidian/SQL/08-sql-skill/chapters/ch02-joins.md` | **~250-300 行** | JOIN 7 种 + 性能差异 | **P1(第一章)** |
| `E:/obsidian/SQL/08-sql-skill/chapters/ch03-window-functions.md` | ~300 行 | 窗口函数(OVER/PARTITION BY/RANK/lead-lag) | P1 |
| `E:/obsidian/SQL/08-sql-skill/chapters/ch04-cte-recursion.md` | ~250 行 | CTE / 递归 CTE / 物化 | P2 |
| `E:/obsidian/SQL/08-sql-skill/chapters/ch05-aggregates.md` | ~200 行 | 聚合 / GROUP BY / HAVING / FILTER | P2 |

### 2.2 4 个辅助文件更新(必做)

| 路径 | 更新 |
|---|---|
| `E:/obsidian/SQL/08-sql-skill/SKILL.md` | Chapter Index 把 ch02-ch05 `🔵 stub` → `✅` 完整 + Topic Index + Supporting Files + 调研入口 |
| `E:/obsidian/SQL/08-sql-skill/glossary.md` | 新增 ch02-ch05 Key Concepts 词条 |
| `E:/obsidian/SQL/08-sql-skill/patterns.md` | 反模式总表追加 ch02-ch05 反模式 |
| `E:/obsidian/SQL/08-sql-skill/cheatsheet.md` | 新增 ch02-ch05 决策表 + 关键经验追加 |

### 2.3 handoff Phase 3c(必做)

`handoff-sql-skill-phase3c-2026-10-14.md` 给 Phase 3c(ch06/ch10)接力

---

## 三、ch02 JOIN 详细设计(第一个 chapter)

### 3.1 ch02 主题与子结构

**JOIN 7 种 + 性能差异**

| 节 | 主题 | 主要素材 |
|---|---|---|
| § 1 | INNER JOIN(等值 / 非等值 / 自连接) | SQLBolt join + civilian7 |
| § 2 | OUTER JOIN(LEFT / RIGHT / FULL + ON vs WHERE) | SQLBolt + civilian7 |
| § 3 | CROSS JOIN(笛卡尔积 / 隐式逗号 FROM) | SQLBolt + ch09 §2 隐式 JOIN 反模式 |
| § 4 | SELF JOIN(自连接 / 层次结构) | civilian7 |
| § 5 | NATURAL JOIN / USING(列名匹配) | PG docs |
| § 6 | JOIN 算法与性能(NL / Hash / Sort Merge,与 ch08 §3 互补) | luke sql-join-* + ch08 §3 引用 |
| § 7 | JOIN 反模式(隐式逗号 / N+1 / 笛卡尔积 / 大表 JOIN) | ch09 §2 + §6 引用 |

### 3.2 ch02 关键铁律(预估 10+ 条)

每节 1-2 条,共 10+ 条铁律。

### 3.3 ch02 反模式(目标 8+ 条)

每节 1-2 条,共 8+ 条反模式(与 ch09 互补,不重复)。

### 3.4 ch02 跨引用(必须)

- **→ sql-skill ch08 §3 JOIN 算法**:ch02 §6 引用,JOIN 性能底层(ch02 讲语法 + 场景,ch08 §3 讲 EXPLAIN 算子)
- **→ sql-skill ch09 §2 隐式 JOIN 反模式**:ch02 §3 引用
- **→ sql-skill ch09 §6 N+1 反模式**:ch02 §7 引用
- **→ evidence-skill ch07 FDW CTE local scope**:ch02 §6 提及(FDW JOIN 性能差,本 chapter 不重写)

---

## 四、ch03 窗口函数详细设计

### 4.1 ch03 主题与子结构

**窗口函数(OVER/PARTITION BY/RANK/lead-lag)**

| 节 | 主题 |
|---|---|
| § 1 | OVER 子句基础(partition + order + frame) |
| § 2 | 排序函数(ROW_NUMBER / RANK / DENSE_RANK / NTILE) |
| § 3 | 分析函数(LAG / LEAD / FIRST_VALUE / LAST_VALUE / NTH_VALUE) |
| § 4 | 聚合窗口(SUM/AVG/COUNT OVER + 滑动窗口) |
| § 5 | 命名窗口(WINDOW 子句) |
| § 6 | 帧子句(ROWS BETWEEN / RANGE BETWEEN) |
| § 7 | 窗口函数反模式(无 PARTITION 聚合 vs GROUP BY 混用) |

### 4.2 ch03 跨引用

- **→ sql-skill ch08 §5 分页与窗口函数索引**:ch03 §4 引用
- **→ sql-skill ch05 聚合**:ch03 §4 与 ch05 §1 GROUP BY 区分

---

## 五、ch04 CTE 详细设计

### 5.1 ch04 主题与子结构

**CTE / 递归 CTE / 物化**

| 节 | 主题 |
|---|---|
| § 1 | WITH clause 基础(非递归 CTE) |
| § 2 | WITH RECURSIVE(递归 CTE + UNION / UNION ALL) |
| § 3 | MATERIALIZED CTE 决策(PG 12+ AS MATERIALIZED / NOT MATERIALIZED) |
| § 4 | CTE vs 子查询 vs 临时表(性能对比) |
| § 5 | CTE 可读性 + 维护性 |
| § 6 | 递归 CTE 应用场景(层次结构 / 图遍历 / 数字序列) |
| § 7 | CTE 反模式(过度嵌套 / 物化滥用) |

### 5.2 ch04 跨引用

- **→ evidence-skill ch07 FDW CTE local scope**:ch04 §1 引用,FDW 用法

---

## 六、ch05 聚合详细设计

### 6.1 ch05 主题与子结构

**聚合 / GROUP BY / HAVING / FILTER**

| 节 | 主题 |
|---|---|
| § 1 | 基础聚合(COUNT / SUM / AVG / MIN / MAX) |
| § 2 | GROUP BY(列表达式 / 隐式列 / ROLLUP / CUBE) |
| § 3 | HAVING(聚合后过滤) |
| § 4 | FILTER 子句(PG 9.4+,WHERE 不能替代) |
| § 5 | GROUPING SETS / GROUPING()(多维聚合) |
| § 6 | 聚合反模式(SELECT * + GROUP BY / 隐式 GROUP BY 列) |
| § 7 | 窗口聚合 vs GROUP BY(ch03 §4 引用) |

### 6.2 ch05 跨引用

- **→ sql-skill ch08 §4 排序与分组索引**:ch05 §2 引用
- **→ sql-skill ch01 §1 SQL 执行顺序**:ch05 §3 HAVING 引用

---

## 七、与已有章节不重叠铁律(沿用 Phase 2/3a)

### 7.1 不重叠矩阵

| 主题 | 已写章节 | ch02-ch05 处理 |
|---|---|---|
| JOIN 算法(EXPLAIN 视角) | ch08 §3 | ch02 §6 引用,不重写 |
| N+1 反模式 | ch09 §6 | ch02 §7 引用,不重写 |
| 隐式 JOIN 反模式 | ch09 §2 | ch02 §3 引用,不重写 |
| 窗口函数索引视角 | ch08 §5 | ch03 §4 引用,不重写 |
| 排序分组索引视角 | ch08 §4 | ch05 §2 引用,不重写 |
| NULL 三值逻辑 | ch01 §3 + ch09 §4 | 不重写,引用 |
| EAV / SELECT * 反模式 | ch09 §1-§2 | ch02 不涉及 |
| FDW 跨 DB | evidence-skill ch07 | ch04 §1 引用,FDW 不重写 |
| 中文 schema 雷区 | evidence-skill ch05 | 不重写 |

### 7.2 9 段结构固定

每 chapter 必含 9 个 `## ` 段:Core Idea / Frameworks Introduced / Key Concepts / Mental Models / Anti-patterns / Code Examples / Reference Tables / Key Takeaways / Connects To。ch09 因 7 节内容超单段容量,4 段用 "(续)" 段。ch02-ch05 单节内容较少,**不必拆 "(续)" 段**,但如需要可拆。

---

## 八、必读顺序(新会话第一件事)

按这个顺序读,5-10 分钟掌握全貌:

1. **本文件**(handoff)— Phase 3b 整体框架
2. **`prompt-next-session-phase3b.md`**(同目录)— 一句话 prompt,引导读必要文档
3. **`E:/obsidian/SQL/08-sql-skill/SKILL.md`** — skill 入口(看 ch02-ch05 已 `🔵 stub`)
4. **`E:/obsidian/SQL/08-sql-skill/chapters/ch09-antipatterns.md`** — ch09 429 行 Phase 3a 最新交付(看 §6 §7 性能 + 安全反模式,ch02 §7 / ch03 §7 / ch04 §7 / ch05 §6 引用)
5. **`E:/obsidian/SQL/08-sql-skill/chapters/ch08-indexes-perf.md`** — ch08 405 行,JOIN 算法 + 索引视角
6. **`E:/obsidian/SQL/08-sql-skill/chapters/ch01-grammar.md`** — ch01 256 行,SQL 执行顺序
7. **`E:/obsidian/SQL/08-sql-skill/cheatsheet.md`** — 决策快查(看 § 9 反模式决策表新增 ch09 引用)
8. (按需) **`F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase3-design.md`** — Phase 3 整体 spec
9. (按需) **`F:/soft/00selfmade/sql-skill/_knowledge_base/research-github-sql-agent-20261013.md`** — 调研笔记

---

## 九、避坑提示

### 9.1 文件名/路径红线(vault 规则)

- 写入 `E:/obsidian/SQL/08-sql-skill/chapters/` 而非 F: 盘
- Windows 禁用字符 `\ / : * ? " < > |` 不用
- 编号格式 `ch0X-<topic>.md`(两段式)
- 文件名 ≤150 字符,完整路径 ≤200 字符

### 9.2 CLAUDE.md 红线

- **禁止删除用户文件** (rm / Remove-Item / del / rmdir / Move-Item)
- **禁止单条命令触碰多个用户文件** (rm *.txt)
- **禁止写危险 SQL** (DROP / TRUNCATE / DELETE FROM 不带 WHERE)
- **禁止 git reset --hard / git clean -fd / git checkout --**
- **临时文件写 `C:\Temp\`**(不要写 `~/.tmp/`)

### 9.3 skill 设计陷阱(沿用 Phase 2/3a)

- 不要重造 BI 产品(已被 DB-GPT/WrenAI/SQLBot 堵死赛道)
- 不要重复 evidence-skill 内容
- 不要重复 Phase 2 + Phase 3a 已写章节内容
- 每 chapter 必含 9 段(可拆 "(续)" 段但不能省)

### 9.4 Write/Edit 单次大小红线(2026-09-05 沉淀)

- 单次 Write ≤ 400 行 / 8000 tokens(避 120s abort)
- 大文档先 Write 骨架后 Edit 补内容
- Edit 锚定 old_string 追加,输入大小可预测

---

## 十、环境/基线状态

| 项 | 状态 |
|---|---|
| 工作目录 | `F:/soft/00selfmade/sql-skill/` |
| Git 仓库 | **未 init** |
| Phase | **3a 完成 / 3b 待启动** |
| sql-skill 主沉淀 | `E:/obsidian/SQL/08-sql-skill/` (128KB / 8 markdown) |
| 8 个 markdown 文件 | SKILL.md + glossary.md + patterns.md + cheatsheet.md + chapters/{ch01,ch07,ch08,ch09}.md |
| evidence-skill | `E:/Users/Duanyi/.claude/skills/evidence-skill/` (18 章已部署) |
| Phase 3a spec | `F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase3-design.md` |
| Phase 3a plan | `F:/soft/00selfmade/sql-skill/docs/superpowers/plans/2026-10-14-sql-skill-phase3a-ch09.md` |
| Phase 3a ledger | `F:/soft/00selfmade/sql-skill/.superpowers/sdd/2026-10-14-sql-skill-phase3a-ch09/progress.md` |

---

## 十一、Phase 3b 执行流程(新会话遵循)

按 superpowers 流程:

1. invocation **`superpowers:brainstorming`** — 与用户对齐(如本次已对齐,直接 spec)
2. **Write spec**:`F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase3b-design.md`(覆盖 ch02-ch05 4 chapter + 4 辅助文件)
3. **Spec review + 用户 approve**
4. invocation **`superpowers:writing-plans`** — 写 plan:`2026-10-14-sql-skill-phase3b.md`
5. **Plan review + 用户选执行方式**(建议 Native,本批已大)
6. invocation **`superpowers:executing-plans`** — 写 4 chapter + 4 辅助文件 + handoff
7. **每 chapter 完成前**:`superpowers:verification-before-completion`
8. **写 handoff Phase 3c**:`handoff-sql-skill-phase3c-2026-10-14.md`

---

## 十二、Phase 3b 验收清单(新会话用)

新会话启动 Phase 3b 时,自我验证:

- [ ] 已读 handoff + SKILL.md + ch09 + ch08 + ch01 重点
- [ ] 已确认 Phase 3a ch09 + 4 辅助文件存在(429 行 / 8 markdown)
- [ ] 已确认 ch02-ch05 stub 状态(SKILL.md Chapter Index `🔵 stub`)
- [ ] 已明确 4 个 chapter 顺序:ch02 JOIN → ch03 窗口 → ch04 CTE → ch05 聚合
- [ ] 已调用 `superpowers:brainstorming` 与用户对齐(本次已对齐:全量 + ch02 第一 + 对齐 ch09 深度)
- [ ] 已 `superpowers:writing-plans` 写 Phase 3b 详细任务
- [ ] 每个 chapter 完成前 `superpowers:verification-before-completion` 验证(9 段 + Frameworks 8+ + Anti-patterns 6+ + 不重叠)
- [ ] 更新 SKILL.md Chapter Index(把 ch02-ch05 `🔵 stub` → `✅` 完整)
- [ ] 更新 glossary/patterns/cheatsheet 4 文件
- [ ] 写 `handoff-sql-skill-phase3c-2026-10-14.md` 给 Phase 3c 接力

---

## 十三、Phase 3a 已做决定的固定沉淀(沿用)

1. **ch09 7 节细分**(数据建模 / 查询 / 索引 / NULL / 字符串日期 / 性能 / 安全)
2. **ch09 Frameworks 63 条 + Anti-patterns 21 条**
3. **ch09 行数 429**(略超 ch08 405,但内容质量优先)
4. **ch09 不重写 Phase 2 + evidence-skill,只引用**
5. **9 段结构固定**(每 chapter 必含 9 段,可拆 "(续)" 段)

新会话请遵守这些已固化决定,如需修改走 brainstorming 流程。
