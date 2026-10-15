---
name: sql-skill
description: "通用 SQL 编写专业度 Skill — PostgreSQL 视角。Use when writing enterprise PostgreSQL queries, debugging slow queries, deciding between index types (B-Tree / GIN / BRIN / Hash), reading EXPLAIN ANALYZE plans, using JSONB / array / GIN indexes, querying via postgres_fdw cross-DB, handling Chinese schema columns (双引号 / 假名 / date SUBSTR), or evaluating query plan operators (Seq Scan / Index Scan / Hash Join / Sort). Triggers: 'sql skill', 'PG performance', 'index decision', 'EXPLAIN ANALYZE', 'jsonb_path_ops', 'GIN index', 'BRIN time-series', 'taobao.mart_X', 'postgres_fdw', 'pg_stat_statements', 'jsonb @>', 'Chinese column', 'shop_name 假名', 'SUBSTR date', 'array unnest', 'pgbouncer session', 'OFFSET keyset', 'pg 索引', 'explain 解读'."
---

# sql-skill v0.1 — 通用 SQL 专业度(企业 PostgreSQL 视角)

**Source**: `E:/obsidian/SQL/08-sql-skill/` (3 chapter + glossary + patterns + cheatsheet) + `E:/obsidian/SQL/03-use-the-index-luke/` (luke 48 章 + SQLBolt 17 课 + pg-docs 5 章)
**Generated**: 2026-10-14 (Phase 2 启动)
**Purpose**: 让 agent 更专业地编写 / 优化 / 排错 PostgreSQL SQL,**与 evidence-skill 互补**(evidence-skill 讲 Evidence BI / 中文 PG schema 业务侧 / nginx / FDW / MCP,本章讲通用 PG 通用视角)

## How to Use This Skill v2.1(直接 Read + Grep 检索 Obsidian vault)

写任何 SQL / 排错 / 调性能,按 **4 层 lookup 顺序**:

### Layer 0: 直接 Read + Grep 检索 Obsidian SQL vault(NEW · v2.1)
- 跨整个 Obsidian SQL vault 1GB+ 沉淀,通过 Read + Grep + Glob 直接检索
- **优势**:**无需 gbrain ingest**,**无需重启 Claude Code**,**无需 user 操作**,agent 直接读 vault
- **调用方式**:
  ```python
  # 关键词提取(question)
  keywords = extract_sql_keywords(question)  # JOIN, B-Tree, 中文 schema ...
  
  # 跨 vault 全文搜索
  hits = []
  for path in ["E:/obsidian/SQL/08-sql-skill/", 
               "E:/obsidian/SQL/03-use-the-index-luke/",
               "E:/obsidian/SQL/02-sql-tutorial-civilian7/",
               "E:/obsidian/SQL/04-awesome-postgres/",
               "E:/obsidian/SQL/05-sql-style-guide/"]:
      hits += Grep(path, keywords, context=3)
  
  # 取 top-5 排序去重
  return top_k(hits, k=5)
  ```
- **fallback**:Read 单个文件(精读)
- 详 [v2.1 handoff](F:/soft/00selfmade/sql-skill/handoff-sql-skill-v2-rag-2026-10-15.md)

### Layer 0+ (future · v2.2): gbrain semantic recall(可选)
- 当用户设置 `GBRAIN_SOURCE=sql-vault` + 重启 Claude Code 后启用
- 同义词召回 / 上下文理解(优于 Grep 关键词)
- 当前 **gbrain 限制**:MCP source binding + serve PGLite 锁(详 handoff § 限制)

### Layer 1: cheatsheet.md
- 13 决策表 + 18 关键经验(本 skill 沉淀)
- 适用于"快速决策"

### Layer 2: 对应 chapter
- ch01-ch10(本 skill 沉淀,~5161 行)
- 适用于"deep dive"

### Layer 3: evidence-skill 业务侧
- 业务侧雷区(中文 schema / FDW / BI 性能 / MCP)
- 详 `E:/Users/Duanyi/.claude/skills/evidence-skill/`

### 其他入口

- **Without args** — load 12 大核心 framework + chapter index
- **With topic** — 问 `ch01` / `ch02` / ... / `ch10` / `glossary` / `patterns` / `cheatsheet` → 读对应文件
- **Decision quick check** — 翻 `cheatsheet.md` 13 决策表 + 18 关键经验
- **Pattern match** — 翻 `patterns.md` 8 大模式 + 反模式总表
- **Term lookup** — 翻 `glossary.md` 按字母 / 中文术语分组

---

## Core Frameworks & Mental Models(12 大)

### 1. **SQL 执行顺序** — FROM → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT

- **声明式写,过程式读**:你按书写顺序写,DB 按执行顺序跑;列别名只在 SELECT 后可用,WHERE 不能引用列别名
- **别名作用域**:表别名全局有效(从 FROM 起),列别名局部有效(只在 SELECT 之后)
- 详见 ch01 §1

### 2. **NULL 三值逻辑** — `NULL = NULL` 是 NULL 不是 TRUE

- `WHERE col = NULL` 永远 0 行,用 `IS NULL` / `IS NOT NULL`
- `COALESCE(a, b, c)` 取第一个非 NULL;`NULLIF(a, b)` 等值归 NULL
- `IS DISTINCT FROM` 是 NULL-safe 等值(优于 `!=`)
- 详见 ch01 §3

### 3. **索引选择** — B-Tree 默认 / GIN 多值 / BRIN 时序 / Hash 几乎不用

- B-Tree:等值 / 范围 / 前缀匹配,深度 4-5 覆盖百万级
- GIN:JSONB / array / tsvector,`jsonb_path_ops` 索引小一半(只支持 `@>`)
- BRIN:append-only 时序大表,空间省 99%
- Hash:仅等值,PG 10+ WAL-logged,但 B-Tree 已能覆盖,实际几乎不用
- 详见 ch08 §1

### 4. **WHERE 索引失效** — 函数 / 隐式 cast / 类型不一致 / 通配符

- WHERE 上函数(`UPPER(col)=X`)走 Seq Scan → 表达式索引或反函数
- 隐式 cast(`int_col = '123'`)走 Seq Scan → 类型一致
- LIKE `'%mid%'` 中间通配不走 B-Tree → pg_trgm GIN
- 详见 ch08 §2

### 5. **JOIN 算法** — Nested Loop(小数据+索引) / Hash Join(大表等值) / Sort Merge Join(已排序)

- 三种 JOIN 各有最佳场景,planner 按 cost 选择
- N+1 反模式:应用层 for 循环 N 次单条 query → 改 1 次批量 + JOIN
- 详见 ch08 §3

### 6. **ORDER BY / GROUP BY 索引** — 免 Sort / 免 HashAggregate

- ORDER BY 列建索引免 Sort 算子(`NULLS LAST/FIRST` 必须与索引顺序一致)
- GROUP BY 列建索引免 HashAggregate(改用 Index Scan + GroupAggregate 流式聚合)
- 详见 ch08 §4

### 7. **分页 Top-N vs keyset** — OFFSET 大值禁用,改 keyset

- `ORDER BY idx LIMIT N` 走索引,O(N)
- `OFFSET 100000 LIMIT 20` 让 PG 扫前 N+limit 行再丢弃
- keyset pagination(`WHERE id > last_id LIMIT N`)O(N) 持续不变
- 详见 ch08 §5

### 8. **EXPLAIN ANALYZE 是唯一真相** — 估算 ≠ 真实

- `EXPLAIN` 只显示估算,`EXPLAIN ANALYZE` 真执行并显示 `actual rows` / `actual time`
- rows mismatch(`(rows=100) (actual rows=10000)`)→ 跑 `ANALYZE table_name`
- 4 大核心算子:Seq Scan / Index Scan / Bitmap Heap Scan / Hash Join / Nested Loop / Sort
- 详见 ch08 §6

### 9. **JSONB vs JSON** — JSONB 二进制 + GIN,JSON 文本几乎不用

- `jsonb_col` 比 `json_col` 好:自动去重 + 压缩 + 支持 GIN
- `@>` / `?` / `?|` / `?&` 走 GIN;`->>` / `->` 文本提取不走索引
- `jsonb_path_query` 复杂嵌套查询不走 GIN,需表达式索引
- 详见 ch07 §1

### 10. **array 列决策** — 低基数 / `@>` 走 GIN / 高频 join 改关联表

- `tags @> ARRAY['x']` / `tags && ARRAY['a','b']` 走 GIN
- `unnest(array_col)` 转行,与 LATERAL JOIN 配合展开
- 高频 join 改关联表(array 列无 PK)
- 详见 ch07 §2

### 11. **postgres_fdw 跨 DB** — 2-segment path + pgbouncer session-mode

- `taobao.mart_X` ✓(erp DB 内 taobao schema 装 foreign tables)
- `taobao.bi.mart_X` ✗(3-segment 触发 `cross-database references are not implemented`)
- pgbouncer 必 `pool_mode = session`,transaction-mode 破坏 5 项(search_path / statement_timeout / FDW 事务 / prepared statements / advisory locks)
- 详见 ch07 §4

### 12. **慢 query 排查 SOP** — `pg_stat_statements` → `EXPLAIN ANALYZE` → 加索引

- 慢 query 80% 问题在 20% plan,先用 `pg_stat_statements` 找 top-N
- 对每条 top query 跑 `EXPLAIN ANALYZE` 看 plan
- 加索引决策:B-Tree / GIN / BRIN 按场景;高频 update 列不建 GIN
- 详见 ch08 §6/§8

---

## Chapter Index(10 章)

### 实战篇 — ch01 / ch07 / ch08 ✅ Phase 2 完成 / + ch02-ch05 ✅ Phase 3b 完成 / + ch06 / ch10 ✅ Phase 3c 完成

| # | 主题 | 关键内容 | 状态 |
|---|---|---|---|
| [ch01](chapters/ch01-grammar.md) | SQL 语法铁律 | 8 子句执行顺序 / 别名作用域 / NULL 三值逻辑 / 风格铁律 | ✅ |
| [ch02](chapters/ch02-joins.md) | JOIN 7 种 + 性能差异 | INNER / OUTER / CROSS / SELF / NATURAL-USING + JOIN 算法 + 反模式 | ✅ |
| [ch03](chapters/ch03-window-functions.md) | 窗口函数 | OVER / PARTITION BY / ROW_NUMBER / RANK / LAG-LEAD / 聚合窗口 / 帧子句 / 命名窗口 | ✅ |
| [ch04](chapters/ch04-cte-recursion.md) | CTE / 递归 CTE / 物化 | WITH clause / WITH RECURSIVE / MATERIALIZED / CTE vs 子查询 vs 临时表 | ✅ |
| [ch05](chapters/ch05-aggregates.md) | 聚合 / GROUP BY / HAVING / FILTER | 基础聚合 / ROLLUP-CUBE / GROUPING SETS / 窗口聚合对比 | ✅ |
| [ch06](chapters/ch06-set-ops.md) | 集合操作 | UNION / UNION ALL / INTERSECT / EXCEPT + 与 JOIN 转换 + ORDER BY/LIMIT 规则 | ✅ |
| [ch07](chapters/ch07-pg-specific.md) | PostgreSQL 特有 | JSONB / array / GIN / FDW 2-segment / 中文 schema 雷区 | ✅ |
| [ch08](chapters/ch08-indexes-perf.md) | 索引与性能 | 索引结构 / WHERE 索引 / JOIN 算法 / 排序分组 / 分页窗口 / EXPLAIN ANALYZE | ✅ |
| [ch09](chapters/ch09-antipatterns.md) | SQL 反模式综合 | 数据建模 / 查询 / 索引 / NULL / 字符串日期 / 性能 / 安全 7 类 25+ 反模式 | ✅ |
| [ch10](chapters/ch10-evidence-bridge.md) | SQL Agent 范式 + evidence-skill 协作 | 三层 lookup / 4 道防线 / 中文 schema 假名修复 / BI 性能 / 评测集 / v1.0 沉淀 | ✅ |

### v1.0 完整版 10 章 ✅ Phase 3c 完成

---

## Topic Index(关键术语 → chapter)

### A-Z

- **AOT / API** → 不在 sql-skill 范围(evidence-skill ch01)
- **array** → ch07 §2
- **anti-pattern** → ch01/ch07/ch08 + cheatsheet §11
- **B-Tree** → ch08 §1
- **Bitmap Heap Scan** → ch08 §6
- **BRIN** → ch08 §1
- **`COALESCE`** → ch01 §3
- **covering index (INCLUDE)** → ch08 §1
- **CROSS JOIN** → ch02 §3
- **CTE / WITH RECURSIVE / MATERIALIZED** → ch04 §1/§2/§3
- **cast (`::` / CAST)** → ch01 §2
- **date 不能 SUBSTR** → ch07 §5
- **DENSE_RANK / NTILE** → ch03 §2
- **DISTINCT ON** → ch01 §4
- **`EXPLAIN ANALYZE`** → ch08 §6
- **expression index** → ch08 §2
- **FILTER 子句** → ch05 §4
- **FIRST_VALUE / LAST_VALUE / NTH_VALUE** → ch03 §3
- **Filter / FROM** → ch01 §1
- **FULL OUTER JOIN** → ch02 §2
- **GIN / GiST** → ch07 §1/§3
- **GROUP BY / HAVING / GROUPING SETS / ROLLUP / CUBE** → ch05 §2/§3/§5
- **GROUPING() / GROUPING_ID()** → ch05 §5
- **Group By / GROUP BY 索引** → ch08 §4
- **Hash Index / Hash Join** → ch08 §1/§3
- **HashAggregate** → ch08 §4/§6
- **INNER JOIN / LEFT JOIN / RIGHT JOIN** → ch02 §1/§2
- **JOIN 7 种** → ch02
- **JOIN 算法** → ch02 §6 / ch08 §3
- **JSONB / JSON** → ch07 §1
- **Keyset pagination** → ch08 §5
- **LAG / LEAD** → ch03 §3
- **LIKE** → ch08 §2
- **LIMIT / OFFSET** → ch08 §5
- **`LATERAL JOIN` + `unnest`** → ch07 §2
- **MATERIALIZED (CTE)** → ch04 §3
- **`MUST` (中文 schema 雷区)** → ch07 §5
- **NATURAL JOIN / USING** → ch02 §5
- **N+1 反模式** → ch02 §7 / ch08 §3 / ch09 §6
- **`NULL` 三值逻辑** → ch01 §3
- **`NULLIF`** → ch01 §3
- **Nested Loop** → ch08 §3
- **OUTER JOIN (LEFT/RIGHT/FULL)** → ch02 §2
- **OVER 子句 (窗口函数)** → ch03 §1
- **operator class** → ch08 §2
- **ORDER BY 索引** → ch08 §4
- **PARTITION BY** → ch03 §1
- **partial index** → ch08 §2
- **percentile_cont / array_agg / string_agg** → ch05 §1
- **INTERSECT (交集)** → ch06 §2
- **INTERSECT ALL** → ch06 §2
- **UNION / UNION ALL** → ch06 §1
- **EXCEPT (差集)** → ch06 §3
- **EXCEPT ALL** → ch06 §3
- **evidence-skill 协作** → ch10 §1-§4
- **三层 lookup (cheatsheet → chapter → evidence-skill)** → ch10 §6
- **4 道防线 (readonly + sqlglot + statement_timeout + LIMIT)** → ch09 §7 / ch10 §2
- **civilian7 评测** → ch10 §5
- **cheatsheet 决策快查** → cheatsheet.md
- **pgbouncer session-mode** → ch07 §4
- **pg_stat_statements** → ch08 §6
- **postgres_fdw** → ch07 §4
- **RANK / DENSE_RANK / NTILE / ROW_NUMBER** → ch03 §2
- **RANGE BETWEEN / ROWS BETWEEN** → ch03 §6
- **Recursion (递归 CTE)** → ch04 §2
- **ROLLUP / CUBE / GROUPING SETS** → ch05 §5
- **SELF JOIN** → ch02 §4
- **Sort (算子)** → ch08 §6
- **Sort Merge Join** → ch08 §3
- **snake_case** → ch01 §4
- **Seq Scan** → ch08 §6
- **Subquery** → ch01 §1/§2
- **Top-N optimization** → ch08 §5
- **`unnest`** → ch07 §2
- **varchar_pattern_ops** → ch08 §2
- **WHERE vs HAVING** → ch05 §3
- **WINDOW 子句 (命名窗口)** → ch03 §5
- **Window Function** → ch03
- **`percentile_cont`** → ch05 §1
- **`array_agg` / `string_agg`** → ch05 §1
- **`EXPLAIN ANALYZE`** → ch08 §6
- **expression index** → ch08 §2
- **Filter / FROM** → ch01 §1
- **GIN / GiST** → ch07 §1/§3
- **Group By / GROUP BY 索引** → ch08 §4
- **Hash Index / Hash Join** → ch08 §1/§3
- **HashAggregate** → ch08 §4/§6
- **JSONB / JSON** → ch07 §1
- **JOIN 算法** → ch08 §3
- **Keyset pagination** → ch08 §5
- **LIKE** → ch08 §2
- **LIMIT / OFFSET** → ch08 §5
- **`LATERAL JOIN` + `unnest`** → ch07 §2
- **`MUST` (中文 schema 雷区)** → ch07 §5
- **`NULL` 三值逻辑** → ch01 §3
- **`NULLIF`** → ch01 §3
- **Nested Loop** → ch08 §3
- **N+1 反模式** → ch08 §3
- **operator class** → ch08 §2
- **ORDER BY 索引** → ch08 §4
- **partial index** → ch08 §2
- **pgbouncer session-mode** → ch07 §4
- **pg_stat_statements** → ch08 §6
- **postgres_fdw** → ch07 §4
- **Recursion (递归 CTE)** → ch02 (Phase 3)
- **Sort (算子)** → ch08 §6
- **Sort Merge Join** → ch08 §3
- **snake_case** → ch01 §4
- **Seq Scan** → ch08 §6
- **Subquery** → ch01 §1/§2
- **Top-N optimization** → ch08 §5
- **`unnest`** → ch07 §2
- **varchar_pattern_ops** → ch08 §2
- **Window Function** → ch02/§5

### 中文

- **"店铺" / "订单日期" / "销售金额"** → ch07 §5
- **中文列双引号** → ch07 §5 + evidence-skill ch05
- **`ds` / `shop_name` / `stat_date` 假名** → ch07 §5 + evidence-skill ch05
- **date SUBSTR 陷阱** → ch07 §5 + evidence-skill ch05

---

## Supporting Files

- [chapters/ch01-grammar.md](chapters/ch01-grammar.md) — SQL 语法铁律(256 行)
- [chapters/ch02-joins.md](chapters/ch02-joins.md) — JOIN 7 种 + 性能差异(450 行)
- [chapters/ch03-window-functions.md](chapters/ch03-window-functions.md) — 窗口函数(488 行)
- [chapters/ch04-cte-recursion.md](chapters/ch04-cte-recursion.md) — CTE / 递归 CTE / 物化(454 行)
- [chapters/ch05-aggregates.md](chapters/ch05-aggregates.md) — 聚合 / GROUP BY / HAVING / FILTER(448 行)
- [chapters/ch06-set-ops.md](chapters/ch06-set-ops.md) — 集合操作(352 行)
- [chapters/ch07-pg-specific.md](chapters/ch07-pg-specific.md) — PG 特有(322 行)
- [chapters/ch08-indexes-perf.md](chapters/ch08-indexes-perf.md) — 索引与性能(405 行)
- [chapters/ch09-antipatterns.md](chapters/ch09-antipatterns.md) — SQL 反模式综合(429 行)
- [chapters/ch10-evidence-bridge.md](chapters/ch10-evidence-bridge.md) — SQL Agent 范式 + evidence-skill 协作(314 行)
- [glossary.md](glossary.md) — 关键术语表
- [patterns.md](patterns.md) — 8 大模式 + 反模式总表
- [cheatsheet.md](cheatsheet.md) — 13 决策表 + 18 关键经验

---

## 调研 / 沉淀入口(v2.1 Read + Grep 跨 vault 检索)

### Layer 0: 直接 Read + Grep 跨 Obsidian SQL vault(NEW · v2.1)

**已纳入检索的目录**(2026-10-15 起的 v2.1 阶段):

| 目录 | 范围 | 优先级 |
|---|---|---|
| `E:/obsidian/SQL/00-索引.md` | 资源总索引 | 1 |
| `E:/obsidian/SQL/08-sql-skill/` | sql-skill 自身 10 章 + 4 辅助 | 1 |
| `E:/obsidian/SQL/03-use-the-index-luke/` | luke 48 章 + pg-docs 5 章 + SQLBolt 17 课 | 1 |
| `E:/obsidian/SQL/02-sql-tutorial-civilian7/` | 1065 题评测 | 2 |
| `E:/obsidian/SQL/04-awesome-postgres/` | PG 资源汇总 | 2 |
| `E:/obsidian/SQL/05-sql-style-guide/` | SQL 风格 | 3 |
| `E:/obsidian/SQL/01-nl2sql-handbook/` | NL2SQL 综述 199M(跳过) | 3 |

**检索方式**:Read + Grep + Glob 跨 vault 关键词全文检索。无需 gbrain / 无需 ingest / 无需重启 Claude Code。

**调用**:
```python
# agent 接到 SQL 问题时
hits = Grep("E:/obsidian/SQL/**/ch*.md", keyword, context=3)
# 配合 Read 单文件精读
content = Read(f"E:/obsidian/SQL/08-sql-skill/chapters/{chapter}.md")
```

**优势**:**无外部依赖 / 立即生效 / 跨 1GB+ vault / 关键词精准**。

**未来 v2.2 可选升级**(gbrain semantic recall):
- 用户设置 `GBRAIN_SOURCE=sql-vault` + 重启 Claude Code 后启用
- 同义词召回 / 上下文理解(优于 Grep 关键词)
- 详 [v2.1 handoff](F:/soft/00selfmade/sql-skill/handoff-sql-skill-v2-rag-2026-10-15.md) § 三

### 本地资源

| 资源 | 路径 |
|---|---|
| 资源总索引 | `E:/obsidian/SQL/00-索引.md` |
| luke 48 章 | `E:/obsidian/SQL/03-use-the-index-luke/` |
| pg-docs 5 章 | `E:/obsidian/SQL/03-use-the-index-luke/pg-docs/` |
| SQLBolt 17 课 | `E:/obsidian/SQL/03-use-the-index-luke/sqlbolt/` |
| civilian7 1065 题 | `E:/obsidian/SQL/02-sql-tutorial-civilian7/` |
| nl2sql-handbook 综述 | `E:/obsidian/SQL/01-nl2sql-handbook/`(199M) |

### 联动 skill / 项目文档

| 文档 | 路径 |
|---|---|
| evidence-skill (BI / 中文 PG 业务侧 / nginx / FDW 5 步 / MCP) | `E:/Users/Duanyi/.claude/skills/evidence-skill/` |
| 调研笔记 | `F:/soft/00selfmade/sql-skill/_knowledge_base/research-github-sql-agent-20261013.md` |
| Phase 3a spec | `F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase3-design.md` |
| Phase 3a plan | `F:/soft/00selfmade/sql-skill/docs/superpowers/plans/2026-10-14-sql-skill-phase3a-ch09.md` |
| handoff(本次) | `F:/soft/00selfmade/sql-skill/handoff-sql-skill-phase3a-2026-10-14.md` |
| Phase 2 spec | `F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase2-design.md` |
| Phase 2 plan | `F:/soft/00selfmade/sql-skill/docs/superpowers/plans/2026-10-14-sql-skill-phase2.md` |
| handoff(本次) | `F:/soft/00selfmade/sql-skill/handoff-sql-skill-phase2-2026-10-14.md` |

---

## Scope & Limits

### 覆盖

- **PostgreSQL 通用视角**:语法 / 索引 / JOIN / 聚合 / JSONB / array / GIN / EXPLAIN
- **企业 PG 性能优化**:B-Tree / GIN / BRIN / Hash 决策 / EXPLAIN ANALYZE 解读 / pg_stat_statements
- **跨 DB**:postgres_fdw + 2-segment path + pgbouncer session-mode
- **中文 schema 通用规则**:中文列双引号 / date SUBSTR / 假名意识
- **慢 query SOP**:`pg_stat_statements` → EXPLAIN → 加索引
- **与 evidence-skill 互补**:业务侧雷区 / nginx / Evidence BI / MCP 归 evidence-skill

### 不覆盖

- Evidence BI 配置 / nginx / FDW 完整 5 步 SQL / 部署细节 → [evidence-skill](../../Users/Duanyi/.claude/skills/evidence-skill/SKILL.md)
- 中文 schema 假名映射具体细节(13+ page 待修列名清单)→ evidence-skill ch05
- BI 场景性能(Core 28 page + nginx immutable + pgbouncer)→ evidence-skill ch14
- ch02-ch06 / ch09 / ch10 → Phase 3 stub,留骨架
- 评测集 / 联动测试 → Phase 3+
- MySQL / Oracle / SQL Server / SQLite 等其他数据库 → Phase 4+

### 已知边界

- v0.1 仅 3 章 + 4 supporting 文件,ch02-ch06/09/10 留 stub
- 与 evidence-skill 边界靠手动维护(spec § 4.5 + cheatsheet § 12)
- 无 git,版本管理靠 spec + plan + handoff 文档(无 commit hash)
- PG 16+ 部分特性(GIN 改进、BRIN 优化)未必覆盖
- **v1.0 进展(Phase 2 + 3a + 3b + 3c 完成)**:10 章完整(ch01-ch10),详 handoff-sql-skill-v1-2026-10-14.md
- **v2.1 进展(2026-10-15 起)**:Layer 0 = Read + Grep 直接检索 Obsidian SQL vault 1GB+,无需 gbrain / 无需 ingest / 无需重启;v2.2 可选升级 gbrain RAG;详 handoff-sql-skill-v2-rag-2026-10-15.md

### 升级频率建议

- PG 大版本升级时:re-read luke `sql-anatomy-*` + pg-docs `indexes.html` + `performance-tips.html` 看新特性
- 每月跑 `ANALYZE` + 看 `pg_stat_statements` top-20 慢 query
- 每季 review 一次索引决策(B-Tree / GIN / BRIN / Hash 是否仍最优)
- 半年 review 与 evidence-skill 边界(避免重叠)
