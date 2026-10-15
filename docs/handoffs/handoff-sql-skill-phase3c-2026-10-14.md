# sql-skill Phase 3c — 会话交接 handoff

> 会话结束日期: 2026-10-14
> 当前阶段: **Phase 3a + 3b 完成 / Phase 3c 待启动**
> 接力目标: **完成 ch06 集合操作 + ch10 evidence-skill 协作 / 范式**,把 sql-skill v1.0 落地 10 章完整版
> 第一个 chapter: **ch06 集合操作(UNION / INTERSECT / EXCEPT)**

---

## 一、项目总览(新会话必读背景)

### 1.1 sql-skill 当前完成度

**v1.0 进展(Phase 2 + 3a + 3b 完成)**:
- ✅ ch01 SQL 语法铁律(256 行)
- ✅ ch02 JOIN 7 种 + 性能差异(450 行)
- ✅ ch03 窗口函数(488 行)
- ✅ ch04 CTE / 递归 CTE / 物化(454 行)
- ✅ ch05 聚合 / GROUP BY / HAVING / FILTER(448 行)
- ✅ ch07 PostgreSQL 特有(322 行)
- ✅ ch08 索引与性能(405 行)
- ✅ ch09 SQL 反模式综合(429 行)
- 🔵 ch06 集合操作(UNION/INTERSECT/EXCEPT)— stub
- 🔵 ch10 与 evidence-skill 协作 / 范式 — stub
- 4 辅助文件(SKILL.md / glossary.md / patterns.md / cheatsheet.md)已同步更新

### 1.2 与 evidence-skill 互补关系(已固化边界)

| Skill | 覆盖 |
|---|---|
| **sql-skill**(本项目) | 通用 SQL 知识(语法 / 性能 / 反模式 / PG 特性)— ch01-ch10 |
| evidence-skill | 业务落地知识(Evidence BI / 中文 PG schema / nginx / FDW / MCP)— 18 章 |
| 联动 | sql-skill ch02-09 + evidence-skill ch05/ch07/ch14/ch16 互补 |

**核心边界铁律**(沿用 Phase 2/3a/3b,不可破坏):
- sql-skill ch06 不重写 evidence-skill ch14 BI 场景性能(Core 28 page)
- sql-skill ch10 不重写 evidence-skill 18 章的"业务侧权威";只引简化版 + 跨引用
- 不重写 FDW 5 步 SQL(归 evidence-skill ch07)
- 不重写中文列假名清单(归 evidence-skill ch05)

### 1.3 用户技术栈

- **数据库**:企业 PostgreSQL(中文 schema,列名如 `"店铺"` `"订单日期"`)
- **BI 工具**:Evidence BI (Core 2026,生产在跑)
- **Agent 平台**:Claude Code / OpenClaw(已装 evidence-skill 自建 skill)
- **凭据**:环境变量管理(CLAUDE.md 硬编码红线)

---

## 二、Phase 3c 必交付清单(全量)

### 2.1 2 个 chapter 文件(本次必完成)

| 路径 | 深度 | 主题 | 优先级 |
|---|---|---|---|
| `E:/obsidian/SQL/08-sql-skill/chapters/ch06-set-ops.md` | ~150-200 行 | 集合操作(UNION / INTERSECT / EXCEPT) | **P1(第一个)** |
| `E:/obsidian/SQL/08-sql-skill/chapters/ch10-evidence-bridge.md` | ~250 行 | 与 evidence-skill 协作 / 范式 / 评测 | P2 |

### 2.2 4 个辅助文件更新(必做)

| 路径 | 更新 |
|---|---|
| `E:/obsidian/SQL/08-sql-skill/SKILL.md` | Chapter Index 把 ch06 / ch10 `🔵 stub` → `✅` 完整;Topic Index 加新词条;Supporting Files 链接 |
| `E:/obsidian/SQL/08-sql-skill/glossary.md` | 新增 ch06 / ch10 Key Concepts 词条 |
| `E:/obsidian/SQL/08-sql-skill/patterns.md` | 反模式总表追加 ch06 / ch10 反模式 |
| `E:/obsidian/SQL/08-sql-skill/cheatsheet.md` | 新增 ch06 / ch10 决策表 + 关键经验追加 |

### 2.3 v1.0 完成 handoff(必做)

`handoff-sql-skill-v1-2026-10-14.md` — sql-skill v1.0 完整版交付(10 章 + 4 辅助文件),给后续维护 / 评测 / 拓展用

---

## 三、ch06 集合操作详细设计(第一个 chapter)

### 3.1 主题与子结构

**集合操作(UNION / INTERSECT / EXCEPT)**

| 节 | 主题 | 主要素材 |
|---|---|---|
| § 1 | UNION / UNION ALL(合并去重 / 保留重复) | SQLBolt + civilian7 |
| § 2 | INTERSECT(交集,自动去重) | civilian7 |
| § 3 | EXCEPT(差集,自动去重) | civilian7 |
| § 4 | 集合操作与 JOIN 转换(等价表达) | civilian7 |
| § 5 | 集合操作 + ORDER BY / LIMIT(顶层 vs 子查询) | PG docs |
| § 6 | 集合操作反模式(列数类型不匹配 / ORDER BY 误用) | civilian7 + ch09 |

### 3.2 ch06 关键铁律(目标 8+ 条)

每节 1-2 条,共 8+ 条铁律。

### 3.3 ch06 反模式(目标 6+ 条)

每节 1-2 条,共 6+ 条反模式(与 ch09 互补,不重复)。

### 3.4 ch06 跨引用(必须)

- **→ sql-skill ch02 JOIN 7 种**:ch06 §4 引用,UNION 与 JOIN 的等价场景
- **→ sql-skill ch09 §2 SELECT * 反模式**:ch06 §6 引用,集合操作必须 explicit columns
- **→ sql-skill ch05 聚合 / GROUP BY**:ch06 §2 INTERSECT 引用与 HAVING 区分

---

## 五、ch10 evidence-bridge 详细设计

### 5.1 主题与子结构

**与 evidence-skill 协作 / 范式**

| 节 | 主题 |
|---|---|
| § 1 | sql-skill 与 evidence-skill 边界(已固化) |
| § 2 | SQL Agent 范式(MCP + 4 道防线,详 evidence-skill ch16) |
| § 3 | 中文 schema 假名修复流程(详 evidence-skill ch05) |
| § 4 | BI 场景性能与 Core 28 page(详 evidence-skill ch14) |
| § 5 | 评测集(沿用 civilian7 1065 题) |
| § 6 | sql-skill v1.0 沉淀清单 |

### 5.2 ch10 关键铁律(目标 6+ 条)

### 5.3 ch10 反模式(目标 4+ 条)

### 5.4 ch10 跨引用(必须)

- **→ evidence-skill ch05**:中文 schema 业务侧权威
- **→ evidence-skill ch07**:postgres_fdw 跨 DB
- **→ evidence-skill ch14**:BI 场景性能
- **→ evidence-skill ch16**:MCP self-host 4 道 SQL 防线

---

## 六、v1.0 完成 handoff 必交付清单

`handoff-sql-skill-v1-2026-10-14.md` 内容:

1. **项目总览**:v1.0 完成 10 章 + 4 辅助文件 / 总行数 / 与 evidence-skill 边界
2. **必读顺序**:ch01 → ch05 → ch07 → ch08 → ch09 → ch06 → ch10(按业务流)
3. **调研入口**:luke 48 章 + civilian7 1065 题 + nl2sql-handbook + evidence-skill 18 章
4. **维护建议**:PG 大版本升级 / 季度 review / 评测集更新
5. **未来扩展**:Phase 4+(评测 / 自动化测试 / 多 DB 支持)

---

## 七、与已有章节不重叠铁律(沿用 Phase 2/3a/3b)

### 7.1 不重叠矩阵

| 主题 | 已写章节 | ch06/ch10 处理 |
|---|---|---|
| JOIN 7 种 | ch02 | ch06 §4 引用,UNION vs JOIN 等价场景 |
| SELECT * 反模式 | ch09 §2 | ch06 §6 引用 |
| 中文 schema | evidence-skill ch05 | ch10 §3 引用 |
| BI 场景性能 | evidence-skill ch14 | ch10 §4 引用 |
| FDW 5 步 | evidence-skill ch07 | ch10 §2 引用 |
| MCP 4 道防线 | evidence-skill ch16 + ch09 §7 | ch10 §2 引用 |

### 7.2 9 段结构固定

每 chapter 必含 9 段:Core Idea / Frameworks Introduced / Key Concepts / Mental Models / Anti-patterns / Code Examples / Reference Tables / Key Takeaways / Connects To。

ch06/ch10 内容较少,**不必拆 "(续)" 段**。

---

## 八、必读顺序(新会话第一件事)

按这个顺序读,5-10 分钟掌握全貌:

1. **本文件**(handoff)— Phase 3c 整体框架
2. **`prompt-next-session-phase3c.md`**(同目录)— 一句话 prompt
3. **`E:/obsidian/SQL/08-sql-skill/SKILL.md`** — skill 入口(ch06/ch10 已 `🔵 stub`)
4. **`E:/obsidian/SQL/08-sql-skill/chapters/ch09-antipatterns.md`** — ch09 429 行,反模式参考(看 §2 / §6 引用 ch06 / ch10)
5. **`E:/obsidian/SQL/08-sql-skill/chapters/ch02-joins.md`** — ch02 450 行,JOIN 7 种(看 §6 JOIN 算法,ch06 §4 引用)
6. **`E:/obsidian/SQL/08-sql-skill/chapters/ch03-window-functions.md`** — ch03 488 行,窗口函数(看 §7 窗口 vs GROUP BY,ch10 §5 评测引用)
7. (按需) **`F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase3b-design.md`** — Phase 3b spec
8. (按需) **`F:/soft/00selfmade/sql-skill/docs/superpowers/plans/2026-10-14-sql-skill-phase3b.md`** — Phase 3b plan
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

### 9.3 skill 设计陷阱(沿用 Phase 2/3a/3b)

- 不要重造 BI 产品(已被 DB-GPT/WrenAI/SQLBot 堵死赛道)
- 不要重复 evidence-skill 内容
- 不要重复 Phase 2/3a/3b 已写章节内容
- 每 chapter 必含 9 段(可拆 "(续)" 段但不能省)

### 9.4 Write/Edit 单次大小红线

- 单次 Write ≤ 400 行 / 8000 tokens(避 120s abort)
- 大文档先 Write 骨架后 Edit 补内容
- Edit 锚定 old_string 追加,输入大小可预测

---

## 十、环境/基线状态

| 项 | 状态 |
|---|---|
| 工作目录 | `F:/soft/00selfmade/sql-skill/` |
| Git 仓库 | **未 init** |
| Phase | **3a + 3b 完成 / 3c 待启动** |
| sql-skill 主沉淀 | `E:/obsidian/SQL/08-sql-skill/` (8 chapter + 4 supporting) |
| 8 个 chapter 文件 | ch01(256) / ch02(450) / ch03(488) / ch04(454) / ch05(448) / ch07(322) / ch08(405) / ch09(429) |
| 4 个 supporting 文件 | SKILL.md / glossary.md / patterns.md / cheatsheet.md(已更新 ch02-ch05) |
| evidence-skill | `E:/Users/Duanyi/.claude/skills/evidence-skill/` (18 章已部署) |
| Phase 3b spec | `F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase3b-design.md` |
| Phase 3b plan | `F:/soft/00selfmade/sql-skill/docs/superpowers/plans/2026-10-14-sql-skill-phase3b.md` |
| Phase 3b ledger | `F:/soft/00selfmade/sql-skill/.superpowers/sdd/2026-10-14-sql-skill-phase3b/progress.md` |

---

## 十一、Phase 3c 执行流程(新会话遵循)

按 superpowers 流程:

1. invocation **`superpowers:brainstorming`** — 与用户对齐(如已对齐,直接 spec)
2. **写 spec**:`F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase3c-design.md`
3. **Spec review + 用户 approve**
4. invocation **`superpowers:writing-plans`** — 写 plan:`2026-10-14-sql-skill-phase3c.md`
5. **Plan review + 用户选执行方式**(推荐 Native,本批 2 chapter 较小)
6. invocation **`superpowers:executing-plans`** — 写 2 chapter + 4 辅助文件 + handoff v1
7. **每 chapter 完成前**:`superpowers:verification-before-completion`
8. **写 v1.0 handoff**:`handoff-sql-skill-v1-2026-10-14.md`

---

## 十二、Phase 3c 验收清单(新会话用)

新会话启动 Phase 3c 时,自我验证:

- [ ] 已读 handoff + SKILL.md + ch09 + ch02 + ch03 重点
- [ ] 已确认 Phase 3b 8 chapter + 4 辅助文件齐全(总行数 ~3252)
- [ ] 已确认 ch06/ch10 stub 状态(SKILL.md Chapter Index `🔵 stub`)
- [ ] 已明确 2 个 chapter 顺序:ch06 集合操作 → ch10 evidence-bridge
- [ ] 已 `superpowers:writing-plans` 写 Phase 3c 详细任务
- [ ] 每个 chapter 完成前 `superpowers:verification-before-completion` 验证
- [ ] 更新 SKILL.md Chapter Index(把 ch06/ch10 `🔵 stub` → `✅` 完整)
- [ ] 更新 glossary/patterns/cheatsheet 4 文件
- [ ] 写 `handoff-sql-skill-v1-2026-10-14.md` 完整版交付

---

## 十三、Phase 3a/3b 已做决定的固定沉淀(沿用)

1. **ch09 7 节细分**(数据建模 / 查询 / 索引 / NULL / 字符串日期 / 性能 / 安全)
2. **ch02-ch05 7 节细分**(每章按主题分 7 节,§7 留作反模式)
3. **9 段结构固定**(每 chapter 必含 9 段,可拆 "(续)" 段)
4. **不重叠 Phase 2 + evidence-skill**(ch02-ch10 不重写 ch01/ch07/ch08/ch09 已写铁律;evidence-skill 业务侧权威只引用)

新会话请遵守这些已固化决定,如需修改走 brainstorming 流程。