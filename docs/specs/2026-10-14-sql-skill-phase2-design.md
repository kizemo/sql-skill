# sql-skill Phase 2 — 设计 spec

**Date**: 2026-10-14
**Phase**: Phase 1 完成 / Phase 2 设计阶段
**Owner**: claude (this session)
**Status**: 待用户 review

---

## 一、设计背景与上下文

### 1.1 项目定位

sql-skill 是面向 **企业 PostgreSQL + Evidence BI** 场景的 SQL 编写专业度 Skill,定位为 **"Skill / Engine / 库"** 形态(非 BI 产品)。让 Claude/OpenClaw agent 写更专业、更准确的 SQL。

### 1.2 与 evidence-skill 关系(互补不重叠)

| Skill | 覆盖 |
|---|---|
| sql-skill (本项目) | 通用 SQL 知识(语法/性能/反模式/PG 特性) — ch01-ch10 |
| evidence-skill | 业务落地知识(Evidence BI / 中文 PG schema / nginx / FDW / MCP) — 18 章 |
| 联动 | Phase 4 目标:sql-skill ch08 通用性能 ↔ evidence-skill ch14 BI 性能互补 |

### 1.3 关键约束(CLAUDE.md 红线)

- ❌ 禁止 rm / Remove-Item / del 任何文件
- ❌ 禁止 git reset --hard / git clean -fd / git checkout --
- ❌ 禁止 DROP / TRUNCATE / DELETE FROM 不带 WHERE
- ❌ 禁止在 E:/obsidian/SQL/ 文件名用 \ / : * ? " < > | 或 emoji
- ✅ 临时文件写 C:\Temp\,不要写 ~/.tmp/

---

## 二、Phase 2 必交付清单

### 2.1 skill 文件输出位置

| 路径 | 用途 |
|---|---|
| `E:/obsidian/SQL/08-sql-skill/SKILL.md` | skill 入口(对应 evidence-skill SKILL.md 结构) |
| `E:/obsidian/SQL/08-sql-skill/glossary.md` | 术语表(按字母排序) |
| `E:/obsidian/SQL/08-sql-skill/patterns.md` | 8-12 大模式(When/How/Trade-offs/反模式总表) |
| `E:/obsidian/SQL/08-sql-skill/cheatsheet.md` | 决策快查表(对应 evidence-skill cheatsheet 14+ 决策表) |
| `E:/obsidian/SQL/08-sql-skill/chapters/ch01-grammar.md` | SQL 语法铁律 |
| `E:/obsidian/SQL/08-sql-skill/chapters/ch07-pg-specific.md` | PG 特有(JSONB / GIN / array / FDW / 中文 schema) |
| `E:/obsidian/SQL/08-sql-skill/chapters/ch08-indexes-perf.md` | **ch08 优先**(索引与性能) |

### 2.2 Phase 2 必完成章节(3 章)

1. **ch08 索引与性能**(priority 1,深度 ~300 行)
2. **ch01 语法铁律**(priority 2,深度 ~200 行)
3. **ch07 PG 特有**(priority 3,深度 ~200 行)

### 2.3 Phase 2 不必完成

- ch02-ch06 / ch09 / ch10(留骨架与 stub,Phase 3 接力)
- 评测集(civilian7 1065 题筛选,Phase 3)
- 联动测试(Phase 4)

---

## 三、整体 skill 形态(对齐 evidence-skill)

### 3.1 SKILL.md 入口

- 顶部:YAML frontmatter(name / description / triggers)
- "How to Use This Skill" 段:无 args / With topic / With chapter / Browse / 决策快查
- Core Frameworks & Mental Models(本会话优先 12 大,后续补)
- Chapter Index(完整 10 章 + 当前完成状态)
- Topic Index(A-Z + 中文)
- Supporting Files
- Scope & Limits(覆盖 / 不覆盖 / 已知 / 升级频率)

### 3.2 glossary.md

- 按字母排序
- 每条:term — 定义(chapter 来源,RG 来源)
- 末尾:中文术语分组
- Phase 2 目标 ~80 词条

### 3.3 patterns.md

- 8 大模式起,后续扩到 12
- 每模式:When to use / How / Trade-offs
- 末尾:反模式总表(必避)

### 3.4 cheatsheet.md

- 14+ 大决策表(章节 / 触发 / 立即做 / 因为)
- 12 关键经验(任何新会话开篇必读)
- 12 阶段 actionable(P1-P5 优先级)
- 调研 / 沉淀入口

### 3.5 chapters/<N>-<topic>.md

每章固定结构(对齐 evidence-skill):

```
# Chapter N: <title>
## Core Idea — 一段话核心心智模型
## Frameworks Introduced — N 条铁律(When / How)
## Key Concepts — 关键术语定义
## Mental Models — 抽象心智模型
## Anti-patterns — ❌ / ✅ 对照
## Code Examples — 实战 SQL(可运行)
## Reference Tables — 决策表 / 映射表
## Key Takeaways — N 条要点
## Connects To — 跨章节引用
```

---

## 四、ch08 详细设计(用户已对齐 4 项决定)

### 4.1 ch08 设计决定

| 项 | 决定 |
|---|---|
| 子结构 | **6 节细分** |
| 边界切分 | **ch08 通用 PG / evidence-skill ch14 BI 场景** |
| 实战深度 | **心智模型 + 完整可运行 SQL + EXPLAIN ANALYZE 解读** |
| EXPLAIN | **包含**(pg_stat_statements) |

### 4.2 ch08 6 节子结构(深度 ~300 行)

| 节 | 主题 | 主要素材 |
|---|---|---|
| **§ 1** | 索引结构(B-Tree / Hash / GIN / BRIN) | luke `sql-anatomy-*` (3 章节) + pg-docs `indexes.html` |
| **§ 2** | WHERE 子句索引(函数 / 范围 / 隐式转换 / null) | luke `sql-where-clause-*` (20+ 章节,最丰富) |
| **§ 3** | JOIN 算法(Nested Loop / Hash / Sort Merge / 索引加速) | luke `sql-join-*` (3 章节) + civilian7 |
| **§ 4** | 排序与分组索引(ORDER BY / GROUP BY / ASC DESC NULLS) | luke `sql-sorting-grouping-*` (3 章节) |
| **§ 5** | 分页与窗口函数索引(Top-N / offset / 窗口索引) | luke `sql-partial-results-*` (3 章节) |
| **§ 6** | EXPLAIN 与执行计划 + pg_stat_statements | luke `sql-explain-plan` + pg-docs `performance-tips.html` + civilian7 实战 |

### 4.3 ch08 框架列表(预估 12-15 条铁律)

| # | 框架 | 节 |
|---|---|---|
| 1 | B-Tree 是 PG 默认索引,等值 + 范围 + 前缀匹配适用 | §1 |
| 2 | Hash 索引只支持等值,PG 10+ WAL-logged 可靠 | §1 |
| 3 | GIN 用于多值列(JSONB / array / tsvector),倒排索引 | §1 |
| 4 | BRIN 用于大表时序范围,空间极小(0.1% of B-Tree) | §1 |
| 5 | WHERE 子句上函数破坏索引(`UPPER(col) = X`),要表达式索引或 `col = LOWER(X)` | §2 |
| 6 | 隐式类型转换破坏索引(`where int_col = '123'` 走 Seq Scan) | §2 |
| 7 | `IS NULL` / `IS NOT NULL` 在 B-Tree 上走索引,partial index 优化低基数 | §2 |
| 8 | LIKE 'prefix%' 走索引,LIKE '%suffix' / '%mid%' 不走 | §2 |
| 9 | 范围查询 BETWEEN 与 `>` `<` 走索引,index merge 仅限 12c+ | §2 |
| 10 | Nested Loop 适合小数据集 + 索引,Hash Join 适合大表等值,Sort Merge 适合大表已排序 | §3 |
| 11 | ORDER BY 列建索引可避免 sort(注意 NULLS LAST/FIRST) | §4 |
| 12 | GROUP BY 列建索引可避免 hash aggregate | §4 |
| 13 | Top-N(`ORDER BY ... LIMIT N`)走索引,`OFFSET N` 大值禁用(改 keyset pagination) | §5 |
| 14 | 窗口函数 `OVER (PARTITION BY ...)` 不直接用索引,需配合 ORDER BY 索引 | §5 |
| 15 | EXPLAIN ANALYZE 必读:Seq Scan / Index Scan / Bitmap Heap Scan / Hash Join 4 大算子 | §6 |
| 16 | pg_stat_statements 查 slow query,top-N 抓 hot path | §6 |

### 4.4 ch08 反模式列表(预估 12+ 条)

- ❌ `SELECT *` 大表 → 必须 explicit columns(配合 covering index)
- ❌ WHERE 上函数 → 表达式索引 or 改写法
- ❌ 不指定范围时间 → 必加 WHERE 时间窗
- ❌ `OFFSET 100000 LIMIT 20` → keyset pagination
- ❌ 不分析 EXPLAIN 就上索引 → 验证假设
- ❌ 大表上建 Hash 索引 → B-Tree 更通用
- ❌ 时序列用 B-Tree → BRIN 空间省 99%
- ❌ JSONB 字段不建 GIN → 全表扫描
- ❌ `IS NOT NULL` 不建 partial index → 浪费空间
- ❌ JOIN 不分析数据量分布 → Nested Loop 误用
- ❌ 监控只看 `pg_stat_user_tables` 不看 `pg_stat_statements` → 漏掉真慢 query
- ❌ > 20 sources/page → 拆 partials(与 evidence-skill ch14 联动)

### 4.5 ch08 跨引用

- **→ evidence-skill ch14**:BI 场景适配(Core 28 page + FDW + nginx immutable)
- **→ evidence-skill ch05**:SQL 列名铁律(中文列双引号)
- **→ sql-skill ch07**:PG 特有(JSONB / GIN 联动)
- **→ sql-skill ch09**:反模式综合

---

## 五、ch01 简要设计(深度 ~200 行)

### 5.1 ch01 主题与子结构

**SQL 语法铁律**(执行顺序 / 表达式 / NULL 三值逻辑 / 风格铁律)

| 节 | 主题 | 主要素材 |
|---|---|---|
| § 1 | SQL 执行顺序(不是书写顺序) | SQLBolt `order_of_execution` |
| § 2 | 表达式规范(列别名 / 别名引用 / 类型转换) | civilian7 + sql_style_guide |
| § 3 | NULL 三值逻辑(`IS NULL` / `COALESCE` / `NULLIF`) | SQLBolt `select_queries_with_nulls` |
| § 4 | 风格铁律(关键字大写 / 表名 snake_case / 注释) | sql_style_guide(Matt Mazur) |

### 5.2 ch01 关键铁律(预估 8 条)

- FROM → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT 真实执行顺序
- 列别名只能在 SELECT 阶段使用,GROUP BY / WHERE 不能引用列别名
- NULL = NULL 是 NULL,不是 TRUE,要用 `IS NULL` / `IS NOT NULL`
- `COALESCE(a, b, c)` 取第一个非 NULL,优于 CASE WHEN
- `NULLIF(a, b)` a=b 返回 NULL,否则 a
- 关键字大写 / 表名小写 snake_case / 缩进 2 空格(对齐 sql_style_guide)
- 注释 `-- 单行` / `/* 多行 */`,复杂逻辑必须注释
- `EXPLAIN` 前先 `EXPLAIN ANALYZE` 验证,不要假设

---

## 六、ch07 简要设计(深度 ~200 行)

### 6.1 ch07 主题与子结构

**PG 特有(JSONB / GIN / array / postgres_fdw / 中文 schema)**

| 节 | 主题 | 主要素材 |
|---|---|---|
| § 1 | JSONB(`@>` / `?` / `jsonb_path_query`) | pg-docs + civilian7 |
| § 2 | array(`ANY` / `@>` / `unnest`) | pg-docs |
| § 3 | GIN / GIST 索引(JSONB + array + tsvector) | pg-docs + awesome-postgres |
| § 4 | postgres_fdw 跨 DB | evidence-skill ch07 联动 + pg-docs |
| § 5 | 中文 schema 雷区(双引号 / `ds` 假名 / date SUBSTR) | evidence-skill ch05 联动 |

### 6.2 ch07 关键铁律(预估 10 条)

- JSONB 比 JSON 好,自动去重 + 二进制存储
- `jsonb_col @> '{"key": "val"}'` 走 GIN 索引,`->>` / `->` 不走
- array 列 `WHERE col @> ARRAY[1,2]` 走 GIN
- `unnest(array_col)` 转行,与 LATERAL JOIN 配合
- postgres_fdw 跨 DB,2-segment path `taobao.mart_X`
- 中文列名必双引号 `"店铺"` `"订单日期"`
- `ds` `shop_name` `stat_date` 是假名,要查真列名
- date 类型不能 SUBSTR,改 `TO_CHAR` / `::text`
- pgbouncer 必 session-mode,transaction-mode 破坏 5 项
- GIN 索引 update cost 高,适合读多写少

---

## 七、ch02-ch06 / ch09-ch10 骨架(stub 形式)

Phase 2 不必完成,但 SKILL.md 需给完整 10 章 mapping。给每个 chapter 留 ~5 行 stub:

| # | 主题 | 主要素材 | 阶段 |
|---|---|---|---|
| ch02 | JOIN 7 种 + 性能差异 | SQLBolt join + luke sql-join-* + civilian7 | Phase 3 |
| ch03 | 窗口函数 (OVER/PARTITION BY/RANK/lead-lag) | luke sql-partial-results-window-function + civilian7 advanced | Phase 3 |
| ch04 | CTE / 递归 CTE / 物化 | civilian7 advanced + nl2sql-handbook chapter | Phase 3 |
| ch05 | 聚合 / GROUP BY / HAVING / FILTER | SQLBolt aggregates + civilian7 | Phase 3 |
| ch06 | 集合操作 (UNION/INTERSECT/EXCEPT) | civilian7 + PG docs | Phase 3 |
| ch09 | 反模式 (25+ SQL Antipatterns) | civilian7 实战 + evidence-skill ch05 联动 | Phase 3 |
| ch10 | 与 evidence-skill 协作 / 范式 | nl2sql-handbook + awesome-text2sql | Phase 3 |

---

## 八、命名规范与形态

### 8.1 文件名

按 `E:/obsidian/AGENTS.md`:
- 编号格式 `ch01` / `ch07` / `ch08`(两段式)
- 主题英文短词 `grammar` / `pg-specific` / `indexes-perf`
- 不带 emoji、不带空格、不带 Windows 禁用字符

### 8.2 章节深度(目标)

- ch01 / ch07 ~200 行
- ch08 ~300 行(因含 EXPLAIN ANALYZE 完整解读)
- glossary ~150 行
- patterns ~200 行
- cheatsheet ~250 行
- SKILL.md ~150 行

### 8.3 跨引用规则

- 章节内引用其它章节用 `ch0X` 格式
- 引用 evidence-skill 用 `evidence-skill ch0X` 格式
- 引用 luke 章节用 `luke/.html` 相对路径
- 引用 pg-docs 用 `pg-docs/.html` 相对路径
- 引用 civilian7 用 `civilian7/<path>` 相对路径

---

## 九、Phase 2 验收清单

### 9.1 skill 文件存在性

- [ ] `E:/obsidian/SQL/08-sql-skill/SKILL.md`
- [ ] `E:/obsidian/SQL/08-sql-skill/glossary.md`
- [ ] `E:/obsidian/SQL/08-sql-skill/patterns.md`
- [ ] `E:/obsidian/SQL/08-sql-skill/cheatsheet.md`
- [ ] `E:/obsidian/SQL/08-sql-skill/chapters/ch01-grammar.md`
- [ ] `E:/obsidian/SQL/08-sql-skill/chapters/ch07-pg-specific.md`
- [ ] `E:/obsidian/SQL/08-sql-skill/chapters/ch08-indexes-perf.md`

### 9.2 形态对齐(对照 evidence-skill)

- [ ] SKILL.md 含 12 大 Core Frameworks(ch08 优先 12 条)
- [ ] glossary.md 按字母排序,~80 词条
- [ ] patterns.md 8 大模式 + 反模式总表
- [ ] cheatsheet.md 14+ 决策表 + 12 关键经验
- [ ] 每 chapter 含 Core Idea / Frameworks / Key Concepts / Mental Models / Anti-patterns / Code Examples / Reference Tables / Key Takeaways / Connects To 9 段

### 9.3 内容深度

- [ ] ch08 ≥ 6 节细分,含 EXPLAIN ANALYZE 完整解读
- [ ] ch08 含 12+ 反模式 + 12+ Frameworks
- [ ] ch01 含 8+ 铁律
- [ ] ch07 含 10+ 铁律

### 9.4 与 evidence-skill 不重叠

- [ ] ch08 不写 nginx immutable / pgbouncer session-mode(归 evidence-skill ch14)
- [ ] ch07 不重写 postgres_fdw 5 步 SQL(留 evidence-skill ch07),只补 GIN / 索引决策
- [ ] ch01 不写中文列双引号细节(归 evidence-skill ch05),只讲通用语法

### 9.5 沉淀入口

- [ ] SKILL.md "调研 / 沉淀入口" 段含 GBrain recall 命令 / 03-use-the-index-luke 子索引
- [ ] cheatsheet 末段含 7 个本地资料源路径(01-07 目录)

---

## 十、Phase 2 不做的事(明确边界)

- ❌ 不实现评测集 / 联动测试(Phase 3+)
- ❌ 不写 ch02-ch06 / ch09 / ch10(留 stub)
- ❌ 不写 PDF / EPUB(Phase 3+)
- ❌ 不 git init 项目根(本项目无 git,CLAUDE.md 提到新会话如需可 init)
- ❌ 不修 evidence-skill(独立 skill,边界清晰)
- ❌ 不重复 handoff 内容

---

## 十一、风险与避坑

| 风险 | 避坑 |
|---|---|
| Write 工具调用 >120s abort | 每 chapter 分批 Write ≤ 400 行,先骨架后 Edit 补内容 |
| ch08 与 evidence-skill ch14 重叠 | § 4.5 跨引用清单 + 9.4 不重叠清单 |
| EXPLAIN ANALYZE 解读无真实数据 | 用 luke + pg-docs 公开示例,标注 source |
| file_path 红线 | E:/obsidian/SQL/ 路径已对齐 vault 规则 |
| 系统级 token 限制 | 每个 chapter Write 前先 Read 已沉淀资源,luke 子目录 HTML 文件优先用 Read 摘要而非全量 |

---

## 十二、下一步(用户 approve 后)

1. **Invoke `superpowers:writing-plans`** 写 Phase 2 实施计划
2. 计划包含:每 chapter 的具体 task(task by task)+ 资源引用 + verification 步骤
3. 计划批准后:实施 ch08 → ch01 → ch07 顺序
4. 每章完成前:`superpowers:verification-before-completion`

---

**Spec 写完,等待用户 review。**
