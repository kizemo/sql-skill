# Cheatsheet — sql-skill v2.0 决策快查

> 一页纸决策表 — 写 SQL / 排错 / 调性能 / 接 BI 时第一查这个。**本文件优先级最高**。
> 覆盖: ch01 语法铁律 + ch02-ch10 + ch07 PG 特有 + ch08 索引与性能 + Layer 0 gbrain RAG

---

## 1. 写 SQL 决策规则

| 触发 | 立即做 | 因为 |
|---|---|---|
| 写复杂 SQL(JOIN + 聚合 + 分页) | 记住 8 子句执行顺序 | FROM→WHERE→GROUP BY→HAVING→SELECT→DISTINCT→ORDER BY→LIMIT |
| WHERE 想用列别名 | 改子查询或表达式复用 | WHERE 在 SELECT 前,别名未生成 |
| 中文列名 | 双引号包 `"店铺"` `"订单日期"` `"销售金额"` | PG identifier quote,无双引号当 string literal |
| 写假列名 `ds` `shop_name` | 查 `information_schema.columns` 拿真名 | 假名在 PG 不存在 → column does not exist |
| 按月聚合 date 列 | `TO_CHAR("订单日期", 'YYYY-MM')` 或 `"订单日期"::text` cast | `SUBSTR(date, 1, 7)` PG 报 function does not exist |
| NULL 字段判断 | `IS NULL` / `IS NOT NULL`,**不要** `= NULL` | `NULL = NULL` 是 NULL 不是 TRUE |
| 字符串默认值 | `COALESCE(col, 'default')` | 优于 CASE WHEN,可读性强 |
| 等于某值归 NULL | `NULLIF(col, '')` | CASE WHEN 等价,但简洁 |
| 多行转数组 / 数组转多行 | `unnest(array_col)` + LATERAL JOIN | 标准 PG 数组展开 |

## 2. WHERE 索引决策规则

| 触发 | 立即做 | 因为 |
|---|---|---|
| WHERE 上函数(`UPPER(col)=X`) | 表达式索引 `LOWER(col)` 或反函数 `col=LOWER(X)` | 函数让索引"看不见" |
| `WHERE int_col = '123'` | 改 `WHERE int_col = 123` | 隐式 cast 让 Seq Scan |
| `WHERE col LIKE 'abc%'` | ✓ B-Tree 走索引 | 前缀匹配 |
| `WHERE col LIKE '%abc'` 或 `'%abc%'` | 改 pg_trgm GIN 或全文检索 | B-Tree 不走中间/后缀通配 |
| `WHERE col IS NULL` 不走索引 | 建 partial index `WHERE col IS NOT NULL` 或 `INCLUDE NULL` | PG 默认 NULL 不入 B-Tree |
| 高频 WHERE 时间窗 | 必加 `WHERE date_col BETWEEN ... AND ...` | 否则全表扫 |
| 表大但只查特定 status | partial index `WHERE status = 'active'` | 索引体积仅为 10% |
| 跑完慢 query | `ANALYZE table_name` | 统计信息过期,planner 选错 plan |

## 3. JSONB / array 索引决策规则

| 触发 | 立即做 | 因为 |
|---|---|---|
| JSONB 字段过滤 | `CREATE INDEX ... USING gin (col jsonb_path_ops)` | 推荐默认,体积小一半 |
| JSONB 字段用 `?` / `?|` / `?&` | 改 `jsonb_ops` | `jsonb_path_ops` 只支持 `@>` |
| `SELECT jsonb_col->>'k' = 'X'` | 改 `WHERE jsonb_col @> '{"k": "X"}'` | `->>` 文本提取不走索引 |
| 嵌套 JSONB 复杂路径查询 | `jsonb_path_query`,**不走 GIN** | 大数据集改表达式索引或物化 |
| array 列查询 `tags @> ARRAY['x']` | 建 GIN 索引 | 无 GIN 时 Seq Scan |
| array 列高频 join | 改关联表 | array 列无 PK,join 慢 |
| `unnest(array_col)` 转行 | LATERAL JOIN 配合 | 标准模式 |
| 高频 update JSONB / array 列 | 不建 GIN | update cost 高,适合读多写少 |

## 4. JOIN 算法决策规则

| 触发 | 立即做 | 因为 |
|---|---|---|
| outer 小 + inner 有索引 | Nested Loop | 每次 lookup 1 行 |
| 两边都大 + 等值 | Hash Join | 内存 hash;内存不足 spill 磁盘 |
| 两边都已排序 + 非等值 | Sort Merge Join | merge 两边排序流 |
| 应用层 for 循环 N 次单条 query | 改 1 次批量 query + JOIN | N+1 反模式 |
| JOIN 顺序不写 explicit | 让 planner 选,但 EXPLAIN 验证 plan | planner 选错 → `ANALYZE` |
| JOIN 大表 + 无索引 | 加索引或预聚合本地 | Nested Loop 必须有索引 |

## 5. ORDER BY / GROUP BY 索引决策规则

| 触发 | 立即做 | 因为 |
|---|---|---|
| ORDER BY 列加索引 | `CREATE INDEX ... ON t (col DESC)` | planner 选 Index Scan,免 Sort |
| `NULLS LAST` / `NULLS FIRST` 与索引顺序不一致 | 调整索引顺序 | 否则仍走 Sort |
| GROUP BY 列加索引 | `CREATE INDEX ... ON t (col)` | 改用 GroupAggregate 流式聚合,免 HashAggregate |
| GROUP BY 列顺序 `(a, b)` | 建 `(a, b)` 索引,不是 `(b, a)` | B-Tree 前缀匹配 |
| ORDER BY + LIMIT N 远小于表大 | Top-N 优化,扫 N 条即停 | planner 自动启用 |

## 6. 分页决策规则

| 触发 | 立即做 | 因为 |
|---|---|---|
| 第一页 / 小 N | `ORDER BY idx LIMIT N` | Index Scan,O(N) |
| 大 OFFSET(`OFFSET 100000 LIMIT 20`) | 改 keyset pagination(`WHERE id > last_id LIMIT N`) | OFFSET 让 PG 扫前 N 行再丢弃 |
| cursor 分页 | keyset pagination | O(1) per page |
| 窗口函数 PARTITION BY | 在 PARTITION BY 列建索引 | 免 Sort 算子 |

## 7. EXPLAIN 决策规则

| 触发 | 立即做 | 因为 |
|---|---|---|
| 看 query 计划 | `EXPLAIN ANALYZE` 不是 `EXPLAIN` | EXPLAIN 只显示估算,EXPLAIN ANALYZE 真执行 |
| `(rows=100) (actual rows=10000)` mismatch | 跑 `ANALYZE table_name` | 统计信息过期,planner 估算错 |
| `actual time=12.345..12.350` 慢算子 | 看哪个算子耗时,加索引 / 改 SQL | 慢算子就是瓶颈 |
| 大表 Seq Scan | 加索引或 partial index | B-Tree / GIN / BRIN 按场景 |
| Sort 算子内存 spike | ORDER BY 列建索引 / 增加 `work_mem` | 内存排序 spill 磁盘慢 |
| Hash Join spill to disk | 改 Nested Loop 或增加 `work_mem` | 内存不足 spill 磁盘 |
| `Bitmap Heap Scan` 回表多 | B-Tree INCLUDE covering index | Index Only Scan 免回表 |

## 8. 跨 DB FDW 决策规则

| 触发 | 立即做 | 因为 |
|---|---|---|
| 1 个本地 DB 读多个 PG server 表 | postgres_fdw + 5 步建表 | 见 evidence-skill ch07 |
| 跨 DB 查询 | `taobao.mart_X` 2-segment path | 3-segment `taobao.bi.mart_X` 报 cross-database error |
| pgbouncer + FDW | `pool_mode = session` | transaction-mode 破坏 FDW 事务 + search_path 等 5 项 |
| 高频跨 DB JOIN | 预聚合本地表,cron 刷新 | 每次 query 走网络,大批聚合性能差 |
| 新增 mart 表 | `CREATE FOREIGN TABLE` + force-recreate | 跨 DB 新增要重建 foreign table |

## 9. 反模式决策规则 (ch09 + ch02-ch05 综合)

| 触发 | 立即做 | 因为 |
|---|---|---|
| 写动态属性表 | 用 JSONB + GIN | EAV 三列动态属性难维护 |
| 写 200+ 列宽表 | 拆表按业务域 | 频繁 update 行迁移开销 |
| `SELECT *` | explicit columns | 大表 IO 浪费 + schema 耦合 |
| 隐式 JOIN(逗号 FROM) | 显式 INNER JOIN + ON | 防笛卡尔积 |
| 全列建索引 | 只建高频 WHERE/JOIN/ORDER BY 列 | 写放大 + 维护成本 |
| `pg_stat_user_indexes.idx_scan = 0` | `DROP INDEX CONCURRENTLY` | 无用索引 |
| `WHERE col = NULL` | `IS NULL` | NULL = NULL 是 NULL |
| `col1 \|\| col2` 不 COALESCE | `COALESCE(col1, '') \|\| COALESCE(col2, '')` | NULL 拼接传染 |
| `SUM(col)` 不显式归 0 | `SUM(COALESCE(col, 0))` | NULL 跳过 |
| `WHERE int_col = '123'` | `WHERE int_col = 123` | 隐式 cast 索引失效 |
| `STR(date_col, 1, 7)` | `TO_CHAR` 或 `::text` | date 不支持 SUBSTR |
| f-string / `+` 拼 SQL | 参数化绑定 | SQL 注入 |
| 应用层 N+1 for 循环 | 批量 + JOIN | N+1 反模式 |
| `OFFSET 100000 LIMIT 20` | keyset pagination `WHERE id > last_id` | 大 OFFSET 扫 M 行 |
| `WHERE UPPER(col) = 'X'` | 表达式索引或反函数 | 函数索引失效 |
| superuser 跑 agent | readonly + sqlglot + timeout + LIMIT 4 道防线 | SQL 注入 + 破坏性操作 |
| DDL/DML 未白名单 | AST 白名单 + DENY | DROP/TRUNCATE 防护 |
| 隐式逗号 FROM 漏 WHERE | 显式 `INNER JOIN ... ON` | 笛卡尔积定时炸弹 |
| 大表 × 大表 CROSS JOIN | 拆段 + 加 WHERE + 明示意图 | O(m*n) OOM |
| NATURAL JOIN 依赖隐式 | 显式 ON + 控制 schema 演化 | 加列 silently 改语义 |
| OUTER JOIN 后 WHERE 误过滤 unmatched | 把条件移到 ON | 变 INNER JOIN 语义 |
| 大表 JOIN 无索引 | 加索引或预聚合本地表 | O(m*n) 笛卡尔积扫表 |
| 窗口函数放 WHERE | 子查询 `SELECT * FROM (...) WHERE ...` | 窗口函数不能在 WHERE |
| LAST_VALUE 不带 frame | `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` | 默认 frame 只到当前行 |
| 累计用 GROUP BY 折叠 | 窗口函数保留行 | GROUP BY 折叠行 |
| CTE 嵌套 5+ 层 | 子查询或临时表 | 可读性下降 |
| 大 CTE NOT MATERIALIZED 多次引用 | `AS MATERIALIZED` 或临时表 | 多次引用重复算 |
| CTE 期望建索引 | 临时表 + CREATE INDEX | CTE 不能建索引 |
| 递归 CTE 无终止条件 | `WHERE depth < N` 或 `statement_timeout` | 无限递归 |
| `SELECT *` + GROUP BY | explicit columns + 聚合 | PG 严格拒绝列歧义 |
| `WHERE` 用聚合函数 | 改 HAVING | WHERE 不能用聚合 |
| `SUM(CASE WHEN ...)` 复杂 | `SUM(...) FILTER (WHERE ...)` | PG 9.4+ 简洁可读 |
| 能用 `UNION ALL` 用 `UNION` | `UNION ALL` + 外部 `DISTINCT` | UNION 内部 sort 去重慢 |
| INTERSECT 重复 `INNER JOIN + DISTINCT` | 看场景,INTERSECT 整行匹配可读性高 | 集合操作可读但失去下推 |
| EXCEPT 顺序错 | 明确 `A EXCEPT B` 语义 | 顺序敏感,反向写 |
| 集合操作内 `ORDER BY` / `LIMIT` 放子查询 | 放整个集合操作后 | 子查询 LIMIT 只限该子查询 |
| 集合操作列数不匹配 | 补 `NULL` 占位 | syntax error |
| 集合操作列类型不兼容 | 显式 `::int` cast | type error |
| `SELECT *` + 集合操作 | explicit columns | 列变化 silently 改语义 |
| AI agent 跑 SQL 漏 4 道防线 | readonly + sqlglot + timeout + LIMIT | 纵深防御任一被攻破其他兜底 |
| 重复 evidence-skill 18 章 | 只引 + 协作范式 | 不重写业务侧权威 |
| 中文 schema 假名未修复 | 查 `information_schema.columns` | 假名在 PG 不存在 |
| BI 性能套用通用 EXPLAIN | 走 evidence-skill ch14 | 业务侧权威 |
| 写 SQL 不查 cheatsheet | 13 决策表先查 | 三层 lookup 顺序 |
| 业务侧雷区查 sql-skill 通用层 | 走 evidence-skill ch05/ch07/ch14/ch16 | 业务侧权威 |

## 10. 中文 schema 决策规则

| 触发 | 立即做 | 因为 |
|---|---|---|
| 写中文列名 SQL | 双引号包 `"店铺"` `"订单日期"` `"销售金额"` | PG identifier quote |
| `ds` 假名出现 | 改 `"订单日期"`(raw 表)或 `source_year_month`(mart 表) | 假名在 PG 不存在 |
| `shop_name` 假名出现 | 改 `"店铺"` | 13+ page 待修 |
| `stat_date` 假名出现 | 改 `"订单日期"` 或 `source_year_month` | mart vs raw 表列名差异 |
| 按月聚合 date 列 | `TO_CHAR("订单日期", 'YYYY-MM')` 或 `"订单日期"::text` | `SUBSTR(date, 1, 7)` 不支持 |
| 不确定真列名 | 查 `information_schema.columns` | 不要靠 spec 记忆 |

## 10. MCP / 自动化 SQL 决策规则

| 触发 | 立即做 | 因为 |
|---|---|---|
| AI agent 跑 SQL | 4 道防线 (readonly + sqlglot + statement_timeout + LIMIT) | 防 DROP / TRUNCATE / 慢 query |
| `run_query` tool 暴露 | statement_timeout 10s + LIMIT 10000 | 防拖死 DB |
| 多数据库 schema | schema 选择 + 权限治理(BM25 75-97% 减 token) | schemagate 借鉴 |
| 中文 schema 误报 | 中文列双引号自动 wrap | 防 column does not exist |
| `get_connection_info` | yaml.safe_load + strip password | 永不含 password |

## 11. 必读 12 关键经验(任何新会话开篇)

0. **写任何 SQL / 排错 / 调性能,v2.1 起第一查**:Read + Grep 跨 `E:/obsidian/SQL/` 7 目录(luke / civilian7 / pg-docs / SQLBolt / 08-sql-skill 等)关键词检索 top-5;fallback Read 单文件(详 [v2.1 handoff](F:/soft/00selfmade/sql-skill/handoff-sql-skill-v2-rag-2026-10-15.md))
1. **SQL 执行顺序** = FROM → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT;列别名只在 SELECT 后可用
2. **`NULL = NULL` 是 NULL**,用 `IS NULL` / `IS NOT NULL`,不要 `= NULL`
3. **中文列双引号 + 假名映射**:`"店铺"` `"订单日期"`,`ds` / `shop_name` 是假名(详见 evidence-skill ch05)
4. **date 不能 SUBSTR**:用 `TO_CHAR` 或 `::text` cast
5. **WHERE 上函数破坏索引**:用表达式索引或反函数
6. **JSONB `->>` 不走索引**:`@>` / `?` 操作符走 GIN
7. **GIN 适合读多写少**;高频 update 列不建 GIN
8. **OFFSET 大值禁用**:keyset pagination (`WHERE id > last_id`)
9. **postgres_fdw 2-segment path**:`taobao.mart_X` ✓,3-segment ✗;pgbouncer 必 session-mode
10. **EXPLAIN ANALYZE 是唯一真相**;估算 vs 真实 mismatch → `ANALYZE table_name`
11. **pg_stat_statements 找 top-N 慢 query**,逐条 EXPLAIN ANALYZE 看 plan
12. **BI 场景性能** (Core 28 page + nginx immutable + pgbouncer)归 [evidence-skill ch14](../../Users/Duanyi/.claude/skills/evidence-skill/chapters/ch14-performance.md),**不重复**
13. **SQL 反模式综合** (25+ 反模式 / EAV / SELECT * / N+1 / SQL 注入)详 [ch09](chapters/ch09-antipatterns.md),业务侧雷区归 evidence-skill ch05
14. **JOIN 7 种** = INNER / LEFT / RIGHT / FULL / CROSS / SELF / NATURAL-USING;**隐式逗号 FROM 是笛卡尔积定时炸弹**,改显式 `INNER JOIN ... ON`(详 [ch02](chapters/ch02-joins.md))
15. **窗口函数保留行 + 多一列聚合**:累计看趋势用窗口,总计比较用 GROUP BY;不能相互替代(详 [ch03](chapters/ch03-window-functions.md) + [ch05](chapters/ch05-aggregates.md))
16. **CTE 是命名临时结果集**:PG 12+ 默认 MATERIALIZED;大结果集 + 高频 JOIN 改临时表(可建索引);递归 CTE 用 `WHERE depth < N` 防无限(详 [ch04](chapters/ch04-cte-recursion.md))
17. **集合操作行级扩展 vs JOIN 列级扩展**:UNION 加行 / JOIN 加列;能容忍重复用 `UNION ALL` 性能更好;`ORDER BY`/`LIMIT` 放整个集合操作后(详 [ch06](chapters/ch06-set-ops.md))
18. **三层 lookup 顺序**:cheatsheet → chapter → evidence-skill;**4 道防线必齐**(readonly + sqlglot + statement_timeout + LIMIT);中文 schema 假名查 `information_schema.columns`(详 [ch10](chapters/ch10-evidence-bridge.md))

## 12. 12 阶段 actionable (5 阶段路线)

| 优先级 | 任务 | 引用 |
|---|---|---|
| **P1 立刻** | 跑 `ANALYZE` 所有大表,统计信息新鲜 | ch08 §6/§8 |
| **P1 立刻** | 中文 schema 假名修复(`ds` → `"订单日期"` 等) | evidence-skill ch05 |
| **P1 立刻** | 中文列双引号 wrap 自动检查 | evidence-skill ch05 |
| **P1 立刻** | EXPLAIN ANALYZE 慢 query top-10 解读 | ch08 §7/§8 |
| **P2 本周** | JSONB / array 字段建 GIN(`jsonb_path_ops` 优先) | ch07 §1/§3 |
| **P2 本周** | WHERE 函数列建表达式索引 | ch08 §2 |
| **P2 本周** | 大 OFFSET 改 keyset pagination | ch08 §5/§6 |
| **P2 本周** | B-Tree 索引 ORDER BY 列,免 Sort | ch08 §4/§5 |
| **P3 本月** | 高频跨 DB JOIN 预聚合本地表 | ch07 §4 |
| **P3 本月** | 时序大表改 BRIN,省空间 99% | ch08 §1 |
| **P3 本月** | pg_stat_statements 接入监控告警 | ch08 §6/§8 |
| **P4 评估期** | MCP 4 道防线部署(若接 AI agent 跑 SQL) | evidence-skill ch16 |

## 13. 调研 / 沉淀入口

### 本地资源

| 资源 | 路径 |
|---|---|
| 资源总索引 | `E:/obsidian/SQL/00-索引.md` |
| luke 索引圣经 | `E:/obsidian/SQL/03-use-the-index-luke/README.md`(48 章) |
| PG 官方文档 | `E:/obsidian/SQL/03-use-the-index-luke/pg-docs/`(5 章) |
| SQLBolt 互动教程 | `E:/obsidian/SQL/03-use-the-index-luke/sqlbolt/`(17 课) |
| civilian7 实战 + 评测 | `E:/obsidian/SQL/02-sql-tutorial-civilian7/`(1065 题) |
| awesome-postgres | `E:/obsidian/SQL/04-awesome-postgres/` |
| sql-style-guide | `E:/obsidian/SQL/05-sql-style-guide/` |
| nl2sql-handbook | `E:/obsidian/SQL/01-nl2sql-handbook/`(199M 综述 + slides) |

### 章节源

| 章节 | 路径 |
|---|---|
| ch01 语法铁律 | `E:/obsidian/SQL/08-sql-skill/chapters/ch01-grammar.md` |
| ch02 JOIN 7 种 | `E:/obsidian/SQL/08-sql-skill/chapters/ch02-joins.md` |
| ch03 窗口函数 | `E:/obsidian/SQL/08-sql-skill/chapters/ch03-window-functions.md` |
| ch04 CTE/递归 | `E:/obsidian/SQL/08-sql-skill/chapters/ch04-cte-recursion.md` |
| ch05 聚合 | `E:/obsidian/SQL/08-sql-skill/chapters/ch05-aggregates.md` |
| ch06 集合操作 | `E:/obsidian/SQL/08-sql-skill/chapters/ch06-set-ops.md` |
| ch07 PG 特有 | `E:/obsidian/SQL/08-sql-skill/chapters/ch07-pg-specific.md` |
| ch08 索引与性能 | `E:/obsidian/SQL/08-sql-skill/chapters/ch08-indexes-perf.md` |
| ch09 反模式综合 | `E:/obsidian/SQL/08-sql-skill/chapters/ch09-antipatterns.md` |
| ch10 evidence-bridge | `E:/obsidian/SQL/08-sql-skill/chapters/ch10-evidence-bridge.md` |
| glossary | `E:/obsidian/SQL/08-sql-skill/glossary.md` |
| patterns | `E:/obsidian/SQL/08-sql-skill/patterns.md` |

### 联动 skill

| Skill | 路径 |
|---|---|
| evidence-skill (BI / 中文 PG / FDW / nginx / MCP) | `E:/Users/Duanyi/.claude/skills/evidence-skill/` |
| 调研笔记 | `F:/soft/00selfmade/sql-skill/_knowledge_base/research-github-sql-agent-20261013.md` |
| spec | `F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase2-design.md` |
| plan | `F:/soft/00selfmade/sql-skill/docs/superpowers/plans/2026-10-14-sql-skill-phase2.md` |
| handoff (本次会话) | `F:/soft/00selfmade/sql-skill/handoff-sql-skill-phase2-2026-10-14.md` |
| Phase 3a spec | `F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-14-sql-skill-phase3-design.md` |
| Phase 3a plan | `F:/soft/00selfmade/sql-skill/docs/superpowers/plans/2026-10-14-sql-skill-phase3a-ch09.md` |
| Phase 3a handoff | `F:/soft/00selfmade/sql-skill/handoff-sql-skill-phase3a-2026-10-14.md` |

---

**本文件优先级最高** — 任何 SQL 决策先查这里,再翻 chapter / luke / pg-docs。
