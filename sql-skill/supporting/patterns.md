# Patterns — sql-skill v0.1 关键模式

> 8 大模式 + 反模式总表
> 覆盖: ch01 语法铁律 / ch07 PG 特有 / ch08 索引与性能

---

## 1. SQL 执行顺序模式 — 8 子句真实顺序

**When to use**: 写任何复杂 SQL(JOIN + 聚合 + 子查询 + 分页)

**How**:
```
FROM  →  WHERE  →  GROUP BY  →  HAVING  →  SELECT  →  DISTINCT  →  ORDER BY  →  LIMIT
```

**Trade-offs**:
- ✓ 知道顺序就能预判哪里能用别名(SELECT 后才能用列别名,WHERE/GROUP BY 不能)
- ✗ 写 SQL 时仍按书写顺序(声明式),执行顺序是 DB 内部细节
- ✗ WHERE 引用列别名 → 改子查询或表达式复用

---

## 2. 别名作用域模式 — 表别名全局 / 列别名局部

**When to use**: 写 JOIN / 子查询 / CTE 时引用别名

**How**:
```sql
-- ✅ 表别名全局有效(从 FROM 起)
SELECT u.id, u.name FROM users AS u WHERE u.created_at > NOW() - INTERVAL '7 days';

-- ❌ 列别名只在 SELECT 后可用
SELECT amount + 1 AS new_amount FROM orders WHERE new_amount > 100;
-- ERROR: column "new_amount" does not exist

-- ✅ 修法 1:表达式复用
SELECT amount + 1 AS new_amount FROM orders WHERE amount + 1 > 100;

-- ✅ 修法 2:子查询
SELECT * FROM (SELECT amount + 1 AS new_amount FROM orders) sub WHERE new_amount > 100;

-- ✓ 列别名在 ORDER BY 可用(ORDER BY 在 SELECT 后)
SELECT id, amount + 1 AS new_amount FROM orders ORDER BY new_amount DESC;
```

**Trade-offs**:
- ✓ 8 子句顺序一致记忆
- ✗ WHERE 想用列别名必须包子查询,可读性断崖
- ✗ 不要用 MySQL `HAVING` 后用列别名(标准 SQL 不允许)

---

## 3. NULL 三值逻辑模式 — `IS NULL` / `COALESCE` / `NULLIF` / `IS DISTINCT FROM`

**When to use**: 任何含 NULL 字段的过滤、聚合、显示

**How**:
```sql
-- ✅ 判断 NULL 唯一方法
WHERE col IS NULL          -- = NULL 永远 0 行
WHERE col IS NOT NULL      -- != NULL 永远 0 行

-- ✅ 取第一个非 NULL(优于 CASE WHEN)
COALESCE(nickname, name, 'anonymous')
COALESCE(amount, 0)  -- 聚合时把 NULL 当 0 算

-- ✅ 等于某值归 NULL
NULLIF(status, '')  -- 空字符串归 NULL

-- ✅ NULL-safe 等值(NULL 不等于某值 = TRUE)
WHERE col IS DISTINCT FROM 'X'  -- 比 != 安全,NULL 也算
```

**Trade-offs**:
- ✓ 三函数覆盖 90% NULL 场景
- ✗ MySQL `IFNULL` / SQL Server `ISNULL` 在 PG 不可用
- ✗ `COALESCE` 多个参数从左到右扫,极端参数多(< 10)性能下降

---

## 4. JSONB 索引模式 — `jsonb_path_ops` + `@>` / `?` 操作符

**When to use**: JSONB 字段过滤(电商 meta / 用户 profile / 配置项)

**How**:
```sql
-- 表 + JSONB 字段
CREATE TABLE orders (id bigserial PRIMARY KEY, meta jsonb NOT NULL);

-- 推荐:jsonb_path_ops 索引(只支持 @>,体积小一半)
CREATE INDEX idx_orders_meta ON orders USING gin (meta jsonb_path_ops);

-- ✅ 走 GIN 的查询
SELECT * FROM orders WHERE meta @> '{"channel": "taobao"}';
SELECT * FROM orders WHERE meta ? 'coupon';
SELECT * FROM orders WHERE meta ?| ARRAY['refund', 'exchange'];

-- ❌ 不走 GIN 的查询
SELECT * FROM orders WHERE meta->>'channel' = 'taobao';  -- 文本提取,Seq Scan
```

**Trade-offs**:
- ✓ `@>` / `?` 是走索引的"包含"语义
- ✗ `jsonb_path_ops` 不支持 `?` / `?|` / `?&` 操作符
- ✗ GIN update cost 高,适合读多写少

---

## 5. array 列模式 — `@>` / `&&` / `unnest`

**When to use**: 低基数(< 100)多值列(用户 tags / 商品标签 / 配置 flags)

**How**:
```sql
-- array 列 + GIN
CREATE TABLE users (id bigserial PRIMARY KEY, tags text[]);
CREATE INDEX idx_users_tags ON users USING gin (tags);

-- ✅ 走 GIN
SELECT * FROM users WHERE tags @> ARRAY['vip'];     -- 包含
SELECT * FROM users WHERE tags && ARRAY['a', 'b'];  -- 任一重叠

-- unnest 转行(LATERAL JOIN)
SELECT u.id, u.name, tag
FROM users u,
LATERAL unnest(u.tags) AS tag;
```

**Trade-offs**:
- ✓ GIN 让 array 等值查询 O(log N)
- ✗ array 列无 PK,高频 join 改关联表
- ✗ GIN update cost 高

---

## 6. 跨 DB FDW 模式 — 2-segment path + pgbouncer session-mode

**When to use**: 1 个 Core/agent 要读多个 PG database 的表

**How**:
```sql
-- 完整 5 步 SQL 见 evidence-skill ch07,这里只列决策要点

-- ✅ 2-segment path
SELECT * FROM taobao.mart_shop_kpi_daily WHERE stat_date > '2026-09-01';

-- ❌ 3-segment path 错
SELECT * FROM taobao.bi.mart_shop_kpi_daily;  -- cross-database references not implemented

-- pgbouncer.ini
pool_mode = session  -- 必 session,transaction 破坏 5 项
```

**Trade-offs**:
- ✓ 1 个本地 deployment 够用,跨 DB 透明
- ✗ 每次 query 走网络,大批聚合性能差(需本地物化 view)
- ✗ pgbouncer transaction-mode 与 FDW 不兼容

---

## 7. EXPLAIN ANALYZE 模式 — 估算 vs 真实对照

**When to use**: 任何"修完慢 query 宣布成功"前

**How**:
```sql
EXPLAIN ANALYZE
SELECT u.name, count(*) FROM users u
JOIN orders o ON o.user_id = u.id
WHERE u.created_at > NOW() - INTERVAL '30 days'
GROUP BY u.name
ORDER BY count(*) DESC LIMIT 100;
```

读 4 件事:
1. `(cost=... rows=100) (actual rows=10000)` — 估算 vs 真实 mismatch → `ANALYZE users`
2. `actual time=12.345..12.350` — 慢算子定位
3. `Seq Scan on orders` — 大表全表扫 → 加索引
4. `Hash Join` spill to disk — 内存不足 → 增加 `work_mem`

**Trade-offs**:
- ✓ 唯一真相,估算可能差几个数量级
- ✗ EXPLAIN(无 ANALYZE)只显示估算,不执行
- ✗ 慢 query 80% 问题在 20% plan,先用 `pg_stat_statements` 找 top-N

---

## 8. 慢 query 排查模式 — `pg_stat_statements` + EXPLAIN + 索引决策

**When to use**: 任何性能问题第一响应

**How**:
```sql
-- 1. 启用 pg_stat_statements(需 shared_preload_libraries 配置)
-- postgresql.conf:
-- shared_preload_libraries = 'pg_stat_statements'
-- pg_stat_statements.track = top

CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 2. 找 top-N 慢 query
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- 3. 对 top query 跑 EXPLAIN ANALYZE 看 plan

-- 4. 加索引决策:
-- - 等值 / 范围 / 前缀匹配 → B-Tree
-- - JSONB / array / tsvector → GIN
-- - 时序大表 → BRIN
-- - 高频 update 列不建 GIN
```

**Trade-offs**:
- ✓ 数据驱动找 hot path,不要靠猜
- ✗ `pg_stat_statements` 默认只跟踪 top 100 query,可配
- ✗ 索引会拖慢 update,只建必要的

---

## 反模式总表(必避)

| 反模式 | 替代 | 章节 |
|---|---|---|
| ❌ WHERE 引用列别名 | ✅ 子查询或表达式复用 | ch01 §1/§2 |
| ❌ `WHERE col = NULL` | ✅ `WHERE col IS NULL` | ch01 §3 |
| ❌ `WHERE col != NULL` | ✅ `WHERE col IS NOT NULL` | ch01 §3 |
| ❌ 中文列无双引号 | ✅ `"店铺"` `"订单日期"` | ch07 §5 |
| ❌ `ds` `shop_name` 假名 | ✅ 查 `information_schema.columns` | ch07 §5 |
| ❌ `SUBSTR(date_col, 1, 7)` | ✅ `TO_CHAR(date_col, 'YYYY-MM')` | ch07 §5 |
| ❌ `jsonb_col->>'k' = 'X'` | ✅ `WHERE jsonb_col @> '{"k": "X"}'` | ch07 §1 |
| ❌ `taobao.bi.mart_X` 3-segment | ✅ `taobao.mart_X` 2-segment | ch07 §4 |
| ❌ `pgbouncer transaction-mode` + FDW | ✅ `pool_mode = session` | ch07 §4 |
| ❌ WHERE 上函数(`UPPER(col)=X`) | ✅ 表达式索引或反函数(`col=LOWER(X)`) | ch08 §2 |
| ❌ `WHERE int_col = '123'` 隐式 cast | ✅ `WHERE int_col = 123` | ch08 §2 |
| ❌ `LIKE '%mid%'` 中间通配 | ✅ pg_trgm GIN | ch08 §2 |
| ❌ `OFFSET 100000 LIMIT 20` | ✅ keyset pagination(`WHERE id > last_id`) | ch08 §5 |
| ❌ 高频 update 列建 GIN | ✅ 读多写少才建 | ch07 §3, ch08 §1 |
| ❌ 时序列用 B-Tree | ✅ BRIN 空间省 99% | ch08 §1 |
| ❌ 只看 EXPLAIN(估算) | ✅ EXPLAIN ANALYZE(真实) | ch08 §6 |
| ❌ 不 ANALYZE 统计信息过期 | ✅ `ANALYZE table_name` 周期跑 | ch08 §6 |
| ❌ 应用层 N+1 for 循环 | ✅ 单次批量 query + JOIN | ch08 §3, ch02 §7, ch09 §6 |
| ❌ 数组列高频 join | ✅ 改关联表 | ch07 §2 |
| ❌ 监控只看 `pg_stat_user_tables.seq_scan` | ✅ `pg_stat_statements` 看具体 query | ch08 §6 |
| ❌ EAV 三列动态属性 | ✅ 关系表 + JSONB 兜底 | ch09 §1 |
| ❌ 200 列宽表 | ✅ 拆表按业务域,JOIN 链 ≤ 3 层 | ch09 §1 |
| ❌ `SELECT *` | ✅ explicit columns | ch09 §2 |
| ❌ 隐式 JOIN(逗号 FROM + WHERE) | ✅ 显式 INNER JOIN + ON | ch09 §2, ch02 §3, ch02 §7 |
| ❌ 过度索引(全列建索引) | ✅ 只建高频 WHERE/JOIN/ORDER BY 列 | ch09 §3 |
| ❌ 不查 `pg_stat_user_indexes` 找无用索引 | ✅ 季度 review + `DROP INDEX CONCURRENTLY` | ch09 §3 |
| ❌ NULL 拼接 `col1 \|\| col2` 不 COALESCE | ✅ `COALESCE(col1, '') \|\| COALESCE(col2, '')` | ch09 §4 |
| ❌ `SUM(col)` 不显式归 0 | ✅ `SUM(COALESCE(col, 0))` | ch09 §4 |
| ❌ `SUBSTR(date_col, 1, 7)` | ✅ `TO_CHAR(date_col, 'YYYY-MM')` 或 `::text` | ch09 §5 |
| ❌ f-string / `+` 拼 SQL | ✅ 参数化绑定(psycopg2 / database/sql / JDBC) | ch09 §5, ch09 §7 |
| ❌ `OFFSET 100000 LIMIT 20` | ✅ keyset pagination `WHERE id > last_id` | ch09 §6 |
| ❌ `WHERE UPPER(col) = 'X'` 函数索引失效 | ✅ 表达式索引或反函数 | ch09 §6 |
| ❌ superuser role 跑 agent | ✅ readonly role + sqlglot + statement_timeout + LIMIT 4 道防线 | ch09 §7 |
| ❌ 隐式逗号 FROM(漏 WHERE 笛卡尔积) | ✅ 显式 `INNER JOIN ... ON` | ch02 §3, ch02 §7 |
| ❌ 大表 × 大表 笛卡尔积 | ✅ 拆段 + 加 WHERE + 明示意图 | ch02 §3, ch02 §7 |
| ❌ SELF JOIN 无别名 | ✅ 必加 `e1`, `e2` 区分 | ch02 §4 |
| ❌ NATURAL JOIN 依赖隐式同名列 | ✅ 显式 `INNER JOIN ... ON`,控制 schema 演化风险 | ch02 §5, ch02 §7 |
| ❌ OUTER JOIN 后 WHERE 误用 | ✅ 把条件移到 ON,或确认 anti-join 意图 | ch02 §2, ch02 §7 |
| ❌ 大表 JOIN 无索引(O(m*n)) | ✅ 加索引或预聚合本地表 | ch02 §6, ch02 §7 |
| ❌ 窗口函数放 WHERE | ✅ 改子查询 `SELECT * FROM (...) WHERE ...` | ch03 §7 |
| ❌ LAST_VALUE 不显式 `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` | ✅ 显式 frame 子句 | ch03 §7 |
| ❌ 累计用 GROUP BY 折叠 | ✅ 改窗口函数保留行 | ch03 §7, ch05 §7 |
| ❌ 总销用窗口函数累加 | ✅ 改 GROUP BY 折叠 | ch03 §7, ch05 §7 |
| ❌ PARTITION BY 列无索引 | ✅ 加索引免 Sort 算子 | ch03 §7, ch08 §5 |
| ❌ CTE 嵌套 5+ 层 | ✅ 子查询或临时表(每步独立验证) | ch04 §7 |
| ❌ 大 CTE NOT MATERIALIZED 多次引用 | ✅ `AS MATERIALIZED` 或临时表 | ch04 §3, ch04 §7 |
| ❌ CTE 期望建索引 | ✅ 临时表 + CREATE INDEX | ch04 §4, ch04 §7 |
| ❌ 递归 CTE 无终止条件 | ✅ `WHERE depth < N` 或 `statement_timeout` | ch04 §7 |
| ❌ `SELECT *` + GROUP BY | ✅ explicit columns + 聚合 | ch05 §6 |
| ❌ `WHERE` 用聚合函数 | ✅ 改 HAVING | ch05 §3, ch05 §6 |
| ❌ `SUM(CASE WHEN ...)` 复杂聚合 | ✅ `SUM(...) FILTER (WHERE ...)` | ch05 §4, ch05 §6 |
| ❌ 能用 `UNION ALL` 的场景用 `UNION` | ✅ `UNION ALL` + 外部 `SELECT DISTINCT` 控制去重范围 | ch06 §1, ch06 §6 |
| ❌ INTERSECT 重复用 `INNER JOIN + DISTINCT` | ✅ 看场景,INTERSECT 整行匹配可读性更好 | ch06 §2, ch06 §6 |
| ❌ EXCEPT 顺序搞错 | ✅ 明确 `A EXCEPT B` 语义,反向写 `B EXCEPT A` | ch06 §3, ch06 §6 |
| ❌ 集合操作 + `ORDER BY` / `LIMIT` 放子查询内 | ✅ 改放整个集合操作最后 | ch06 §5, ch06 §6 |
| ❌ 集合操作列数不匹配 | ✅ 补 `NULL` 占位或重写 SQL | ch06 §5, ch06 §6 |
| ❌ 集合操作列类型严重不兼容 | ✅ 显式 `::int` cast 统一类型 | ch06 §5, ch06 §6 |
| ❌ `SELECT *` + 集合操作 | ✅ explicit columns(详 [ch09 §2](ch09-antipatterns.md)) | ch06 §6, ch09 §2 |
| ❌ AI agent 跑 SQL 漏 4 道防线 | ✅ readonly + sqlglot + statement_timeout + LIMIT 必齐 | ch09 §7, ch10 §2 |
| ❌ 重复 evidence-skill 18 章内容 | ✅ 只引 + 协作范式 | ch10 §1 |
| ❌ 中文 schema 假名未修复 | ✅ 查 `information_schema.columns` 拿真列名 | ch07 §5, ch10 §3 |
| ❌ BI 性能问题套用通用 EXPLAIN | ✅ 走 evidence-skill ch14 BI 场景适配 | ch08 §6, ch10 §4 |
| ❌ 写 SQL 不查 cheatsheet | ✅ 13 决策表先查,再翻 chapter | ch10 §6 |
| ❌ 业务侧雷区查 sql-skill 通用层 | ✅ 走 evidence-skill ch05/ch07/ch14/ch16 | ch10 §1, ch10 §6 |
