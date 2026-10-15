# sql-skill Phase 3a — 会话交接 handoff

> 会话结束日期: 2026-10-14
> 当前阶段: **Phase 3a 完成 / Phase 3b 待启动**
> 接力目标: 启动 Phase 3b,补齐 ch02 / ch03 / ch04 / ch05 stub → 完整章节

---

## 一、Phase 3a 已沉淀内容

### 1.1 必交付(ch09 反模式综合)

| 路径 | 行数 | 用途 |
|---|---|---|
| `E:/obsidian/SQL/08-sql-skill/chapters/ch09-antipatterns.md` | 429 | SQL 反模式综合 7 节(数据建模 / 查询 / 索引 / NULL / 字符串日期 / 性能 / 安全)25+ 反模式 |

### 1.2 辅助文件更新

| 路径 | 更新 |
|---|---|
| `E:/obsidian/SQL/08-sql-skill/SKILL.md` | Chapter Index ch09 ✅ 完整 + Topic Index + Supporting Files + 调研入口(共 7 处 ch09 引用) |
| `E:/obsidian/SQL/08-sql-skill/glossary.md` | 新增 EAV / N+1 / SELECT * / SQL 注入 / superuser role / wide table 6 词条(共 7 处 ch09 引用) |
| `E:/obsidian/SQL/08-sql-skill/patterns.md` | 反模式总表追加 14 条 ch09 反模式(共 14 处 ch09 引用) |
| `E:/obsidian/SQL/08-sql-skill/cheatsheet.md` | 新增 "9. 反模式决策规则" 决策表(17 条) + 关键经验 13 条 + 调研入口(共 4 处 ch09 引用) |

### 1.3 ch09 9 段结构(对齐 Phase 2)

每 chapter 固定含:Core Idea / Frameworks Introduced / Key Concepts / Mental Models / Anti-patterns / Code Examples / Reference Tables / Key Takeaways / Connects To。ch09 因 7 节内容超过单段容量,4 段(Frameworks/Key Concepts/Mental Models/Anti-patterns)有 "(续)" 段,共 13 个 `## ` 段。

---

## 二、ch09 与已有章节边界(已固化)

| 主题 | ch09 处理 | 详章节 |
|---|---|---|
| NULL 三值逻辑 | 引用,不重写 | [ch01 §3](file:///E:/obsidian/SQL/08-sql-skill/chapters/ch01-grammar.md) |
| 中文 schema 雷区 | 引用,不重写假名清单 | evidence-skill ch05 |
| date SUBSTR | ch09 §5 通用规则 | evidence-skill ch05 业务侧实战 |
| 函数索引失效 | ch09 §6 简提 | [ch08 §2](file:///E:/obsidian/SQL/08-sql-skill/chapters/ch08-indexes-perf.md) |
| N+1 / 大 OFFSET | ch09 §6 简提 | ch08 §3 / §5 |
| SQL 注入 4 道防线 | ch09 §7 通用 | evidence-skill ch16 MCP 实战 |
| EAV / SELECT * / 宽表 | ch09 §1-§2 新内容 | — |
| 隐式 cast / date / 字符串拼接 | ch09 §5 新内容(与 ch08 §2 互补) | ch08 §2 |

**核心边界铁律**(沿用 Phase 2):
- ch09 不重写 Phase 2 已写铁律,只引用
- ch09 不重写 evidence-skill 业务侧雷区清单
- ch09 §5 §6 §7 新内容(原 ch01/ch07/ch08 未覆盖的反模式视角)

---

## 三、必 handoff 顺序(Phase 3b 新会话第一件事)

1. **本文件**(handoff) — Phase 3a 整体 + Phase 3b 接力目标
2. **`E:/obsidian/SQL/08-sql-skill/SKILL.md`** — skill 入口(看 ch09 已完成 ✅)
3. **`E:/obsidian/SQL/08-sql-skill/chapters/ch09-antipatterns.md`** — Phase 3a 深度章节
4. **`E:/obsidian/SQL/08-sql-skill/cheatsheet.md`** — 反模式决策表(9 节)
5. (按需) **`F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase3-design.md`** — Phase 3 spec
6. (按需) **`F:/soft/00selfmade/sql-skill/docs/superpowers/plans/2026-10-14-sql-skill-phase3a-ch09.md`** — Phase 3a plan

---

## 四、Phase 3b 必交付

### 4.1 Phase 3b 目标

把 ch02 / ch03 / ch04 / ch05 4 个 stub → 完整 9 段章节。

### 4.2 4 个待写章节(沿用 Phase 3 spec § 3.2)

| # | 主题 | 主要素材 | 优先级 |
|---|---|---|---|
| ch02 | JOIN 7 种 + 性能差异 | SQLBolt join + luke sql-join-* + civilian7 | P1 |
| ch03 | 窗口函数(OVER/PARTITION BY/RANK/lead-lag) | luke sql-partial-results-window-function + civilian7 advanced | P1 |
| ch04 | CTE / 递归 CTE / 物化 | civilian7 advanced + nl2sql-handbook chapter | P2 |
| ch05 | 聚合 / GROUP BY / HAVING / FILTER | SQLBolt aggregates + civilian7 | P2 |

### 4.3 每个章节产出标准

- 9 段结构齐全(与 ch09 一致:可拆 "(续)" 段)
- 深度对齐 Phase 2(ch02 ~250 行 / ch03 ~300 行 / ch04 ~250 行 / ch05 ~200 行)
- 与 ch01/ch07/ch08/ch09 + evidence-skill 互补不重叠
- Frameworks 8+ 条,Anti-patterns 6+ 条
- Connects To 跨章节引用清晰

### 4.4 skill 形态要求

- 形态延续 Phase 2 + Phase 3a:9 段结构 + Frameworks + Anti-patterns + Code Examples + Reference Tables
- 与 evidence-skill 不重叠:ch04 CTE 与 evidence-skill ch07 FDW CTE local scope 协同
- Update SKILL.md Chapter Index(把 🔵 stub → ✅ 完整)
- Update glossary.md / patterns.md / cheatsheet.md 4 文件

---

## 五、避坑提示

### 5.1 文件名/路径红线(沿用 Phase 2)

- 写入 `E:/obsidian/SQL/08-sql-skill/chapters/` 而非 F: 盘
- Windows 禁用字符 `\ / : * ? " < > |` 不用
- 编号格式 `ch0X-<topic>.md`(两段式)

### 5.2 CLAUDE.md 红线(沿用 Phase 2)

- 禁止删除用户文件 / 危险 SQL / git reset --hard 等

### 5.3 ch09 已验证的 9 段结构

每 chapter **必须**含 9 个 `## ` 段。ch09 因 7 节内容超过单段容量,4 段用 "(续)" 段。Phase 3b ch02-ch05 单节内容较少,不必拆 "(续)" 段。

### 5.4 与已有章节不重叠(沿用 Phase 2/3a)

- ch02 JOIN:不重写 ch08 §3 JOIN 算法(那里是 EXPLAIN 视角),ch02 是 JOIN 语法 + 性能差异
- ch03 窗口函数:不重写 ch08 §5 分页与窗口函数索引(那里是索引视角),ch03 是窗口函数语法 + 应用
- ch04 CTE:不重写 evidence-skill ch07 FDW CTE local scope(那里是 FDW 视角),ch04 是 CTE 语法 + 递归 + 物化
- ch05 聚合:不重写 ch08 §4 排序与分组索引(那里是索引视角),ch05 是聚合语法 + GROUP BY + HAVING + FILTER

### 5.5 skill 设计陷阱(沿用 Phase 2/3a)

- 不要重造 BI 产品
- 不要重复 evidence-skill 内容
- 不要重写 Phase 2 + Phase 3a 已写章节内容

---

## 六、环境/基线状态

| 项 | 状态 |
|---|---|
| 工作目录 | `F:/soft/00selfmade/sql-skill/` |
| Git 仓库 | **未 init** |
| Phase | **3a 完成 / 3b 待启动** |
| sql-skill 主沉淀 | `E:/obsidian/SQL/08-sql-skill/` (128KB / Phase 3a 新增 ch09) |
| 8 个 markdown 文件 | SKILL.md + glossary.md + patterns.md + cheatsheet.md + chapters/{ch01,ch07,ch08,ch09}.md |
| evidence-skill | `E:/Users/Duanyi/.claude/skills/evidence-skill/` (18 章已部署) |
| Phase 3a spec | `F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase3-design.md` |
| Phase 3a plan | `F:/soft/00selfmade/sql-skill/docs/superpowers/plans/2026-10-14-sql-skill-phase3a-ch09.md` |
| Phase 3a ledger | `F:/soft/00selfmade/sql-skill/.superpowers/sdd/2026-10-14-sql-skill-phase3a-ch09/progress.md` |

---

## 七、Phase 3b 可能扩展方向

1. **ch02 JOIN 7 种**:cross / inner / left / right / full / self / natural 完整谱 + 性能差异
2. **ch03 窗口函数**:OVER / PARTITION BY / ORDER BY / RANK / DENSE_RANK / ROW_NUMBER / lead / lag / first_value / last_value / nth_value
3. **ch04 CTE / 递归 CTE / 物化**:WITH clause / WITH RECURSIVE / MATERIALIZED CTEs / 数据湖分层
4. **ch05 聚合**:count / sum / avg / min / max / GROUP BY / HAVING / FILTER (PG 9.4+) / GROUPING SETS / ROLLUP / CUBE
5. 联动 evidence-skill ch07(ch04 CTE 与 FDW CTE local scope 联动)

---

## 八、Phase 3b 验收清单(新会话用)

新会话启动 Phase 3b 时,自我验证:

- [ ] 已读 handoff + SKILL.md + ch09 重点
- [ ] 已确认 Phase 3a ch09 存在(429 行 / 9 段齐全)
- [ ] 已确认 4 辅助文件 ch09 引用齐全
- [ ] 已明确 Phase 3b 第一个 chapter 选哪个(建议 ch02 JOIN,与 ch08 §3 JOIN 算法互补)
- [ ] 已调用 `superpowers:brainstorming` 与用户对齐 chapter 设计
- [ ] 已 `superpowers:writing-plans` 写 Phase 3b 详细任务
- [ ] 每个 chapter 完成前 `superpowers:verification-before-completion` 验证(9 段 + Frameworks 8+ + Anti-patterns 6+ + 不重叠)
- [ ] 更新 SKILL.md Chapter Index(把 ch02-ch05 🔵 stub → ✅ 完整)
- [ ] 更新 cheatsheet § 9-14 + 调研入口(加新 chapter 链接)
- [ ] 写 `handoff-sql-skill-phase3b-2026-XX-XX.md` 给 Phase 3c 接力

---

## 九、Phase 3a 已做决定的固定沉淀

1. **ch09 子结构** = 7 节细分(数据建模 / 查询 / 索引 / NULL / 字符串日期 / 性能 / 安全)
2. **ch09 铁律** = 18+ 条(实际 63 条 grep,远超目标)
3. **ch09 反模式** = 25+ 条(实际 21 条 - ❌ 模式,每节 3 条均匀)
4. **ch09 边界** = 不重写 Phase 2 + evidence-skill,只引用
5. **ch09 与 evidence-skill 联动** = ch05 业务侧权威(ch09 §5 引用),ch16 MCP 4 道防线(ch09 §7 引用)
6. **9 段结构固定**(每 chapter 必含 9 段,可拆 "(续)" 段)

新会话请遵守这些已固化决定,如需修改走 brainstorming 流程。
