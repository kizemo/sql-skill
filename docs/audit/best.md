---
name: sql-skill
description: >-
  Use when writing or debugging PostgreSQL / MySQL / Oracle / SQL Server
  queries — index choice, EXPLAIN ANALYZE, JSONB.
triggers:
  - SQL 性能
  - EXPLAIN ANALYZE
  - postgres_fdw
  - 中文列名
  - MySQL / Oracle / MSSQL
mutating: false
brain_first: exempt
when_to_use: PG SQL + multi-dialect.
version: 0.3.0
---

# sql-skill — 企业 PostgreSQL 编写与调优

**边界**:本 skill 讲**通用 PG 视角**(语法 / 索引 / JOIN / 聚合 / JSONB / 性能)。业务侧(Evidence BI / nginx / FDW 部署 / 中文 schema 假名映射明细 / MCP)归 [evidence-skill](E:/Users/Duanyi/.claude/skills/evidence-skill/)。

**第一站**:`supporting/cheatsheet.md` — 13 决策表 + 18 关键经验(写 SQL / 排错 / 调性能先查这个)。

---

## 12 大核心框架(结论速查 · 详解见对应章)

| # | 结论 | 详解 |
|---|---|---|
| 1 | 执行顺序 FROM→WHERE→GROUP BY→HAVING→SELECT→DISTINCT→ORDER BY→LIMIT;列别名仅 SELECT 后可用 | [ch01 §1](chapters/ch01-grammar.md) |
| 2 | NULL 三值逻辑:`= NULL` 恒 0 行,用 `IS NULL` / `IS DISTINCT FROM` | [ch01 §3](chapters/ch01-grammar.md) |
| 3 | 索引:B-Tree 默认 / GIN 多值 / BRIN 时序 / Hash 几乎不用 | [ch08 §1](chapters/ch08-indexes-perf.md) |
| 4 | WHERE 索引失效:列上函数 / 隐式 cast / 中间通配 LIKE | [ch08 §2](chapters/ch08-indexes-perf.md) |
| 5 | JOIN 算法:Nested Loop(小表+索引)/ Hash Join(大表等值)/ Sort Merge(已排序) | [ch08 §3](chapters/ch08-indexes-perf.md) |
| 6 | ORDER BY / GROUP BY 建索引 → 免 Sort 算子 / 免 HashAggregate | [ch08 §4](chapters/ch08-indexes-perf.md) |
| 7 | 分页:大 OFFSET 禁用,改 keyset(`WHERE id > last_id LIMIT N`) | [ch08 §5](chapters/ch08-indexes-perf.md) |
| 8 | EXPLAIN ANALYZE 才是真相(估算≠实际);rows mismatch → `ANALYZE 表` | [ch08 §6](chapters/ch08-indexes-perf.md) |
| 9 | JSONB 优于 JSON(压缩+去重+可索引);`@>` / `?` 走 GIN,`->>` 不走 | [ch07 §1](chapters/ch07-pg-specific.md) |
| 10 | array:低基数 / `@>` 走 GIN;高频 join 改关联表(array 列无 PK) | [ch07 §2](chapters/ch07-pg-specific.md) |
| 11 | postgres_fdw 只支持 2 段路径;pgbouncer 必 `pool_mode = session` | [ch07 §4](chapters/ch07-pg-specific.md) |
| 12 | 慢 query SOP:`pg_stat_statements` → `EXPLAIN ANALYZE` → 加索引 | [ch08 §6/§8](chapters/ch08-indexes-perf.md) |

---

## Gotchas — 高频反模式(先看这 8 条)

- `NOT IN (子查询)` 遇 NULL 返回 0 行 → 改 `EXISTS` / `LEFT JOIN ... IS NULL`([ch09](chapters/ch09-antipatterns.md))
- `WHERE col = NULL` 恒 0 行 → `IS NULL`([ch01 §3](chapters/ch01-grammar.md))
- 中文列名必须双引号 `"店铺"`;假列名(`ds` / `shop_name`)PG 里不存在 → 查 `information_schema.columns`([ch07 §5](chapters/ch07-pg-specific.md))
- date 列 `SUBSTR(col, 1, 7)` PG 报 function does not exist → `TO_CHAR(col, 'YYYY-MM')`([ch07 §5](chapters/ch07-pg-specific.md))
- `LIKE '%mid%'` 中间通配不走 B-Tree → `pg_trgm` GIN([ch08 §2](chapters/ch08-indexes-perf.md))
- N+1:应用层循环单条查 → 改 1 次批量 + JOIN([ch02 §7](chapters/ch02-joins.md))
- pgbouncer `transaction`-mode 破坏 search_path / statement_timeout / FDW 事务 / prepared statements / advisory locks([ch07 §4](chapters/ch07-pg-specific.md))
- 3 段 FDW 路径 `db.schema.table` → `cross-database references are not implemented`([ch07 §4](chapters/ch07-pg-specific.md))

完整 7 类 25+ 反模式 → [ch09-antipatterns.md](chapters/ch09-antipatterns.md)

---

## Chapter Index(11 章)

| # | 主题 | 关键内容 |
|---|---|---|
| [ch01](chapters/ch01-grammar.md) | SQL 语法铁律 | 8 子句执行顺序 / 别名作用域 / NULL 三值逻辑 / 风格铁律 |
| [ch02](chapters/ch02-joins.md) | JOIN 7 种 + 性能差异 | INNER / OUTER / CROSS / SELF / NATURAL-USING + JOIN 算法 + 反模式 |
| [ch03](chapters/ch03-window-functions.md) | 窗口函数 | OVER / PARTITION BY / ROW_NUMBER / RANK / LAG-LEAD / 帧子句 / 命名窗口 |
| [ch04](chapters/ch04-cte-recursion.md) | CTE / 递归 / 物化 | WITH / WITH RECURSIVE / MATERIALIZED / CTE vs 子查询 vs 临时表 |
| [ch05](chapters/ch05-aggregates.md) | 聚合 / GROUP BY / HAVING / FILTER | 基础聚合 / ROLLUP-CUBE / GROUPING SETS / 窗口聚合对比 |
| [ch06](chapters/ch06-set-ops.md) | 集合操作 | UNION / UNION ALL / INTERSECT / EXCEPT + 与 JOIN 转换 + ORDER BY/LIMIT 规则 |
| [ch07](chapters/ch07-pg-specific.md) | PostgreSQL 特有 | JSONB / array / GIN / FDW 2-segment / 中文 schema 雷区 |
| [ch08](chapters/ch08-indexes-perf.md) | 索引与性能 | 索引结构 / WHERE 索引 / JOIN 算法 / 排序分组 / 分页窗口 / EXPLAIN ANALYZE |
| [ch09](chapters/ch09-antipatterns.md) | SQL 反模式综合 | 数据建模 / 查询 / 索引 / NULL / 字符串日期 / 性能 / 安全 7 类 25+ |
| [ch10](chapters/ch10-evidence-bridge.md) | SQL Agent 范式 + evidence 协作 | 三层 lookup / 4 道防线 / 中文 schema 假名修复 / BI 性能 / 评测集 |
| [ch11](chapters/ch11-multi-db.md) | 多方言 MySQL / Oracle / SQL Server | 语义差异 / 索引模型 / 方言反模式 / 跨库协作 |

---

## 文件清单(读条件)

| 文件 | 用途 | 何时读 |
|---|---|---|
| [supporting/cheatsheet.md](supporting/cheatsheet.md) | 13 决策表 + 18 关键经验 | **写 SQL / 排错第一站** |
| [supporting/glossary.md](supporting/glossary.md) | 166 条术语定义 | 查术语定义 |
| [supporting/patterns.md](supporting/patterns.md) | 8 大模式 + 反模式总表 | 套用现成模式 |
| [references/topic-index.md](references/topic-index.md) | 84 术语 → 章节定位 | 不知道该读哪一章 |
| [references/retrieval.md](references/retrieval.md) | 跨 vault 检索路径 + 优先级 | 要查 skill 外的资料(luke / civilian7 / PG 资源) |
| `chapters/ch01-ch11.md` | 11 章正文(~5516 行) | deep dive |

---

## Scope & Limits

**覆盖**:PostgreSQL 通用视角(语法 / 索引 / JOIN / 聚合 / JSONB / array / GIN / EXPLAIN)· 企业 PG 性能优化(B-Tree / GIN / BRIN / Hash 决策 / EXPLAIN ANALYZE 解读 / pg_stat_statements)· 跨 DB(postgres_fdw + 2 段路径 + pgbouncer session-mode)· 中文 schema 通用规则(双引号 / date SUBSTR / 假名意识)· 慢 query SOP · 多方言差异(MySQL / Oracle / SQL Server:语义地雷 / 索引模型 / 方言反模式 / 跨库协作)。

**不覆盖**:
- Evidence BI 配置 / nginx / FDW 完整 5 步 / 部署细节 / MCP → [evidence-skill](E:/Users/Duanyi/.claude/skills/evidence-skill/)
- 中文 schema 假名映射具体明细(13+ page 待修列名清单)→ evidence-skill ch05
- BI 场景性能(Core 28 page + nginx immutable + pgbouncer)→ evidence-skill ch14
- **方言入门教学**(MySQL / Oracle / SQL Server 基础语法)→ 只讲差异,见 [ch11](chapters/ch11-multi-db.md)

**已知边界**:
- 与 evidence-skill 的边界靠手动维护(spec § 4.5 + cheatsheet § 12),半年 review 一次
- PG 16+ 部分特性(GIN 改进、BRIN 优化)未必覆盖
- 素材源与检索路径见 [references/retrieval.md](references/retrieval.md)
