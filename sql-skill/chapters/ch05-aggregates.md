# Chapter 5: SQL 聚合 / GROUP BY / HAVING / FILTER — PostgreSQL 通用视角

## Core Idea

聚合(Aggregate)是把多行折叠成单行的计算,分两类:① **基础聚合**(`COUNT` / `SUM` / `AVG` / `MIN` / `MAX` + `BOOL_or聚合` + `array_agg` / `string_agg`);② **多维聚合**(`GROUP BY` + `ROLLUP` / `CUBE` / `GROUPING SETS`)。配套组件:① `GROUP BY` 把数据分组(每组一行聚合);② `HAVING` 聚合**后**过滤(详 [ch01 §1 SQL 执行顺序](ch01-grammar.md),`WHERE` 是聚合**前**行级过滤);③ `FILTER` 子句(PG 9.4+)在聚合时条件过滤,优于 `CASE WHEN`(详 [ch01 §3 NULL 处理](ch01-grammar.md))。**聚合与窗口函数的区别**:聚合折叠行,窗口保留行(详 [ch03 §7](ch03-window-functions.md))。**GROUP BY 列建索引免 HashAggregate**(详 [ch08 §4](ch08-indexes-perf.md))。

## Frameworks Introduced

### §1 基础聚合(COUNT / SUM / AVG / MIN / MAX)— 3 条铁律

- **聚合函数把多行折叠成单行**:`COUNT(*)`, `SUM(x)`, `AVG(x)`, `MIN(x)`, `MAX(x)`;PG 还有 `BOOL_or`, `BOOL_and`, `array_agg`, `string_agg`, `jsonb_agg` 等。
- **`COUNT(*)` vs `COUNT(col)`**:`COUNT(*)` 计所有行(含 NULL),`COUNT(col)` 计非 NULL 行(详 [ch01 §3 NULL 三值逻辑](ch01-grammar.md) + [ch09 §4 NULL 反模式](ch09-antipatterns.md))。
- **`SUM` / `AVG` 对 NULL 的处理**:NULL 跳过;`SUM(COALESCE(x, 0))` 显式把 NULL 当 0(详 [ch09 §4](ch09-antipatterns.md))。

### §2 GROUP BY(列表达式 / 隐式列 / ROLLUP / CUBE)— 2 条铁律

- **GROUP BY 列决定分组粒度**:每组产生一行聚合结果;未列在 GROUP BY 的列不能出现在 SELECT(除非包在聚合函数里)。
- **`ROLLUP` / `CUBE` / `GROUPING SETS` 是多维聚合**:`ROLLUP(a, b)` 算 `(a, b)` + `(a)` + `()`;`CUBE(a, b)` 算 `(a, b)` + `(a)` + `(b)` + `()`;`GROUPING SETS` 显式指定维度组合。

### §3 HAVING(聚合后过滤)— 2 条铁律

- **HAVING 是聚合后过滤**:`HAVING COUNT(*) > 5` 在 GROUP BY 聚合结果上过滤;不能引用列别名外的别名(详 [ch01 §1 SQL 执行顺序](ch01-grammar.md))。
- **WHERE vs HAVING**:WHERE 行级过滤(聚合前);HAVING 聚合过滤(聚合后);**WHERE 不能用聚合函数**,HAVING 才能。

### §4 FILTER 子句(PG 9.4+,WHERE 不能替代)— 2 条铁律

- **`FILTER (WHERE ...)` 是聚合内条件过滤**:`COUNT(*) FILTER (WHERE status = 'completed')` 只计 completed 行;等价 `SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END)` 但可读性更好。
- **FILTER 与 WHERE 关键区别**:FILTER 在聚合函数内,WHERE 在聚合前;`SUM(x) FILTER (WHERE ...)` 只对过滤后行求和,不影响其他聚合。

### §5 GROUPING SETS / GROUPING()(多维聚合)— 2 条铁律

- **GROUPING SETS 显式指定维度组合**:`GROUPING SETS ((a), (b), ())` 算 a 维度 + b 维度 + 全表;比 ROLLUP / CUBE 灵活。
- **`GROUPING(col)` 标识 NULL 来源**:`GROUPING(col)` 返回 0 / 1,0 表示该列在该行有值,1 表示该行是聚合到 NULL(ROLLUP / CUBE 引入);用于多维报表标签区分。

### §6 聚合反模式(SELECT * + GROUP BY / 隐式 GROUP BY 列)— 2 条铁律

- **`SELECT *` + `GROUP BY`**:列歧义,PG 拒绝执行;必须 explicit columns + 聚合(详 [ch09 §2](ch09-antipatterns.md))。
- **隐式 GROUP BY 列依赖 PG 扩展**:MySQL 允许 `SELECT name, COUNT(*) FROM t GROUP BY id`(name 随机);PG 严格不允许,必须 GROUP BY name。

### §7 窗口聚合 vs GROUP BY(引用 ch03 §4)— 2 条铁律

- **窗口聚合保留行 + 多列聚合**:`SUM(x) OVER (PARTITION BY g)` 每行多一列聚合;GROUP BY 折叠 + 一行一聚合。
- **决策**:累计看趋势用窗口;总计比较用 GROUP BY;不能相互替代(详 [ch03 §7 决策表](ch03-window-functions.md))。

## Key Concepts

### §1 基础聚合

- **`COUNT(*)` / `COUNT(col)` / `COUNT(DISTINCT col)`**:行数 / 非 NULL 数 / 去重数
- **`SUM` / `AVG` / `MIN` / `MAX`**:数值聚合
- **`BOOL_or` / `BOOL_and`**:布尔 OR / AND
- **`array_agg(col)`**:把 col 聚合成 array
- **`string_agg(col, sep)`**:把 text 聚合成 string,用 sep 分隔
- **`jsonb_agg` / `jsonb_object_agg`**:聚合成 JSON
- **`percentile_cont(0.5) WITHIN GROUP (ORDER BY x)`**:中位数(连续分布)

### §2 GROUP BY

- **`GROUP BY col1, col2`**:按 (col1, col2) 组合分组
- **`GROUP BY ROLLUP(a, b)`**:层级聚合,从 (a, b) → (a) → ()
- **`GROUP BY CUBE(a, b)`**:所有维度组合
- **隐式列**(MySQL 扩展,PG 禁止):SELECT 引用未 GROUP BY 列

### §3 HAVING

- **`HAVING <condition>`**:聚合后过滤,可用聚合函数
- **`WHERE <condition>`**:行级过滤,不能用聚合函数

### §4 FILTER

- **`agg(...) FILTER (WHERE <condition>)`**:PG 9.4+,聚合内条件过滤
- **等价 `CASE WHEN`**:可读性更好,query 更简洁

### §5 GROUPING SETS

- **`GROUPING SETS ((a), (b), ())`**:显式维度组合
- **`GROUPING(col)`**:0 = 实际值,1 = 聚合 NULL
- **`GROUPING_ID(a, b)`**:bit mask 标识聚合层级

### §7 窗口聚合 vs GROUP BY

- **聚合**:折叠行 + 一行一聚合
- **窗口聚合**:保留行 + 多一列聚合

## Mental Models

### §1 基础聚合

- **聚合是"折叠行"**:多行 → 一行;NULL 跳过(除 COUNT(*))。
- **`COUNT(*)` 是行数,`COUNT(col)` 是非 NULL 数**:聚合前理解 NULL 处理规则。

### §2 GROUP BY

- **GROUP BY 是"分组 + 每组聚合"**:每组一行聚合;未列在 GROUP BY 的列不能在 SELECT(除聚合函数包)。
- **ROLLUP 是"层级小计"**:从细粒度到粗粒度累计。

### §3 HAVING

- **HAVING 是"组级过滤"**:对每组聚合结果过滤;WHERE 是"行级过滤"。
- **执行顺序**:FROM → WHERE → GROUP BY → HAVING → SELECT(详 [ch01 §1](ch01-grammar.md))。

### §4 FILTER

- **FILTER 是"聚合内条件"**:每个聚合函数独立过滤;不影响其他聚合或行。
- **FILTER vs CASE WHEN**:FILTER 更简洁,可读性更好。

### §5 GROUPING SETS

- **GROUPING SETS 是"多维报表"**:一次 query 算多个维度的聚合;省多次 GROUP BY。
- **GROUPING() 是"维度标识"**:多维报表中区分"真实 NULL"vs"聚合 NULL"。

### §6 聚合反模式

- **`SELECT *` + GROUP BY 是"列歧义"**:PG 严格不允许;MySQL 是历史包袱。

### §7 窗口聚合 vs GROUP BY

- **聚合折叠 / 窗口保留**:核心区别是"是否丢行";用户维度趋势用窗口,用户总销用 GROUP BY。

## Anti-patterns

### §1

- ❌ `SUM(col)` 不显式归 0 → `SUM(COALESCE(col, 0))`(详 [ch09 §4](ch09-antipatterns.md))
- ❌ `COUNT(*)` vs `COUNT(col)` 混用 → 理解 NULL 处理规则

### §2

- ❌ SELECT 引用未 GROUP BY 列 → PG 严格拒绝,改 GROUP BY 或聚合

### §3

- ❌ `WHERE` 用聚合函数 → 改 HAVING
- ❌ HAVING 不引用聚合别名 → HAVING 必须用聚合函数表达式

### §4

- ❌ `SUM(CASE WHEN ...)` 复杂 → 改 `SUM(...) FILTER (WHERE ...)`

### §5

- ❌ 多 GROUP BY 查询重复写 → 改 GROUPING SETS 一次算

### §6

- ❌ `SELECT *` + GROUP BY → 显式列 + 聚合
- ❌ 依赖 PG 隐式 GROUP BY → 严格写 GROUP BY 所有非聚合列

### §7

- ❌ 累计用 GROUP BY 折叠 → 改窗口函数保留行
- ❌ 总销用窗口函数累加 → 改 GROUP BY 折叠

## Code Examples

### §1 基础聚合

```sql
-- COUNT/SUM/AVG/MIN/MAX
SELECT
  COUNT(*) AS total_orders,
  COUNT(DISTINCT user_id) AS unique_users,
  SUM(amount) AS total_amount,
  AVG(amount) AS avg_amount,
  MIN(amount) AS min_amount,
  MAX(amount) AS max_amount
FROM orders
WHERE created_at > NOW() - INTERVAL '30 days';

-- NULL 显式归 0
SELECT SUM(COALESCE(amount, 0)) FROM orders;  -- NULL 当 0

-- BOOL_or / BOOL_and:多条件布尔
SELECT
  BOOL_or(status = 'completed') AS any_completed,
  BOOL_and(amount > 0) AS all_positive
FROM orders;

-- array_agg / string_agg:聚合成 array / string
SELECT user_id, array_agg(order_id ORDER BY created_at) AS order_ids
FROM orders
GROUP BY user_id;

SELECT shop_id, string_agg(product_name, ', ' ORDER BY product_name) AS products
FROM products
GROUP BY shop_id;

-- 中位数
SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY amount) AS median
FROM orders;
```

### §2 GROUP BY + ROLLUP / CUBE

```sql
-- 基础 GROUP BY:每用户聚合
SELECT user_id, COUNT(*) AS order_count, SUM(amount) AS total
FROM orders
GROUP BY user_id
ORDER BY total DESC;

-- ROLLUP:层级聚合((user_id, status) → (user_id) → 全表)
SELECT user_id, status, COUNT(*) AS cnt, SUM(amount) AS total
FROM orders
GROUP BY ROLLUP (user_id, status);
-- 包含 user_id+status 详细 + user_id 小计 + 全表总计

-- CUBE:所有维度组合
SELECT user_id, status, COUNT(*) AS cnt
FROM orders
GROUP BY CUBE (user_id, status);
-- 包含 (user_id, status) + (user_id) + (status) + ()

-- GROUP BY 索引免 HashAggregate(详 [ch08 §4](ch08-indexes-perf.md))
CREATE INDEX idx_orders_user_id ON orders (user_id);
SELECT user_id, COUNT(*) FROM orders GROUP BY user_id;
-- EXPLAIN:Index Scan + GroupAggregate(无 HashAggregate)
```

### §3 HAVING

```sql
-- HAVING 聚合后过滤
SELECT user_id, COUNT(*) AS order_count
FROM orders
GROUP BY user_id
HAVING COUNT(*) > 5  -- 只保留订单数 > 5 的用户
ORDER BY order_count DESC;

-- WHERE + HAVING 组合:行级 + 聚合后
SELECT user_id, COUNT(*) AS order_count, SUM(amount) AS total
FROM orders
WHERE created_at > NOW() - INTERVAL '30 days'  -- 行级过滤(聚合前)
GROUP BY user_id
HAVING SUM(amount) > 1000  -- 聚合后过滤
ORDER BY total DESC;

-- ❌ WHERE 用聚合函数(错误)
SELECT user_id, COUNT(*) FROM orders
WHERE COUNT(*) > 5  -- ERROR: aggregate functions not allowed in WHERE
GROUP BY user_id;

-- ✅ 改 HAVING
SELECT user_id, COUNT(*) FROM orders
GROUP BY user_id
HAVING COUNT(*) > 5;
```

### §4 FILTER 子句

```sql
-- FILTER vs CASE WHEN
-- ❌ CASE WHEN 复杂
SELECT
  COUNT(*) AS total,
  SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_count,
  SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_count,
  SUM(CASE WHEN status = 'pending' THEN amount ELSE 0 END) AS pending_amount
FROM orders;

-- ✅ FILTER 简洁
SELECT
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE status = 'completed') AS completed_count,
  COUNT(*) FILTER (WHERE status = 'cancelled') AS cancelled_count,
  SUM(amount) FILTER (WHERE status = 'pending') AS pending_amount
FROM orders;

-- FILTER 多条件组合
SELECT
  user_id,
  COUNT(*) FILTER (WHERE status = 'completed' AND amount > 100) AS high_value_completed,
  COUNT(*) FILTER (WHERE status = 'completed' AND amount <= 100) AS low_value_completed
FROM orders
GROUP BY user_id;
```

### §5 GROUPING SETS + GROUPING()

```sql
-- 多维报表:店铺 + 月份 + 总计
SELECT
  shop_id,
  DATE_TRUNC('month', created_at) AS month,
  COUNT(*) AS order_count,
  SUM(amount) AS total,
  GROUPING(shop_id) AS is_shop_agg,
  GROUPING(DATE_TRUNC('month', created_at)) AS is_month_agg
FROM orders
GROUP BY GROUPING SETS (
  (shop_id, DATE_TRUNC('month', created_at)),  -- 店铺+月 详细
  (shop_id),                                    -- 店铺 小计
  (DATE_TRUNC('month', created_at)),            -- 月 小计
  ()                                            -- 全表总计
)
ORDER BY shop_id NULLS LAST, month NULLS LAST;
-- GROUPING(col) = 1 表示该行是该维度的聚合

-- GROUPING_ID 多列 bitmask
SELECT
  shop_id, status, COUNT(*),
  GROUPING_ID(shop_id, status) AS gid
FROM orders
GROUP BY GROUPING SETS ((shop_id, status), (shop_id), (status), ());
-- gid: 0 = (shop, status), 1 = (shop), 2 = (status), 3 = ()
```

### §6 聚合反模式 + 修法

```sql
-- ❌ SELECT * + GROUP BY(列歧义)
SELECT * FROM orders GROUP BY user_id;
-- ERROR: column "orders.id" must appear in GROUP BY clause or be used in aggregate function

-- ✅ explicit columns
SELECT user_id, COUNT(*) FROM orders GROUP BY user_id;

-- ❌ 隐式 GROUP BY(PG 严格)
SELECT user_id, amount, COUNT(*) FROM orders GROUP BY user_id;
-- ERROR: column "orders.amount" must appear in GROUP BY clause

-- ✅ 加 amount 到 GROUP BY 或聚合
SELECT user_id, amount, COUNT(*) FROM orders GROUP BY user_id, amount;
-- 或
SELECT user_id, SUM(amount), COUNT(*) FROM orders GROUP BY user_id;

-- ❌ SUM(col) 不归 0(NULL 跳过)
SELECT SUM(amount) FROM orders;  -- 全 NULL 时返回 NULL

-- ✅ 显式归 0
SELECT SUM(COALESCE(amount, 0)) FROM orders;
```

### §7 窗口聚合 vs GROUP BY

```sql
-- 累计看趋势用窗口
SELECT user_id, sale_date, amount,
       SUM(amount) OVER (PARTITION BY user_id ORDER BY sale_date) AS running_total
FROM daily_sales;
-- 保留每行 + 多一列累计

-- 总计用 GROUP BY
SELECT user_id, SUM(amount) AS total
FROM daily_sales
GROUP BY user_id;
-- 折叠行 + 每用户一行

-- 混用合法:GROUP BY 计算基础聚合,窗口排名
SELECT user_id, SUM(amount) AS total,
       RANK() OVER (ORDER BY SUM(amount) DESC) AS user_rank
FROM orders
GROUP BY user_id;

## Reference Tables

### §1 基础聚合速查

| 场景 | 函数 | NULL 处理 |
|---|---|---|
| 总数 | `COUNT(*)` | 含 NULL 行 |
| 非 NULL 数 | `COUNT(col)` | 跳 NULL |
| 去重数 | `COUNT(DISTINCT col)` | 跳 NULL |
| 总和 | `SUM(col)` | 跳 NULL;全 NULL → NULL |
| 均值 | `AVG(col)` | 跳 NULL |
| 最小 / 最大 | `MIN(col)` / `MAX(col)` | 跳 NULL |
| 布尔 OR / AND | `BOOL_or` / `BOOL_and` | 跳 NULL |
| 聚合成 array | `array_agg(col)` | 含 NULL |
| 聚合成 string | `string_agg(col, sep)` | 跳 NULL |
| 聚合成 JSON | `jsonb_agg` / `jsonb_object_agg` | — |
| 中位数 | `percentile_cont(0.5) WITHIN GROUP (ORDER BY x)` | — |

### §2 GROUP BY 决策表

| 场景 | 写法 |
|---|---|
| 单维度分组 | `GROUP BY col` |
| 多维度分组 | `GROUP BY col1, col2` |
| 层级小计 | `GROUP BY ROLLUP (a, b)` ((a,b) → (a) → ()) |
| 所有维度组合 | `GROUP BY CUBE (a, b)` |
| 显式维度 | `GROUP BY GROUPING SETS ((a), (b), ())` |
| 列建索引 | `CREATE INDEX ON t (col)` 免 HashAggregate |

### §3 WHERE vs HAVING 决策

| 场景 | 用 WHERE | 用 HAVING |
|---|---|---|
| 行级过滤(聚合前) | ✓ | — |
| 聚合后过滤 | — | ✓ |
| 用聚合函数 | ✗ | ✓ |
| 引用列别名 | ✗(聚合前) | ✓ |

### §4 FILTER 子句决策表

| 场景 | 用 FILTER | 用 CASE WHEN |
|---|---|---|
| 聚合内条件过滤 | ✓ | 略繁 |
| 多条件并行聚合 | ✓ | ✓ |
| 可读性优先 | ✓ | 略繁 |

### §5 GROUPING SETS 决策表

| 场景 | 选 | 原因 |
|---|---|---|
| 已知层级 | `ROLLUP` | 自动层级 |
| 所有维度组合 | `CUBE` | 笛卡尔积 |
| 显式控制 | `GROUPING SETS` | 灵活 |
| 区分聚合 NULL | `GROUPING(col)` | 标识维度层级 |

### §6 聚合反模式决策表

| 反模式 | 替代 |
|---|---|
| `SELECT *` + GROUP BY | explicit columns + 聚合 |
| `WHERE` 用聚合 | 改 HAVING |
| `SUM(col)` 不归 0 | `SUM(COALESCE(col, 0))` |
| 隐式 GROUP BY(列未在 GROUP) | 严格写 GROUP BY |

### §7 窗口聚合 vs GROUP BY 决策表

| 场景 | 用窗口 | 用 GROUP BY |
|---|---|---|
| 累计 / 趋势 | ✓ | — |
| 总计 / 比较 | — | ✓ |
| 保留每行 + 加聚合 | ✓ | — |
| 折叠行 | — | ✓ |
| 排名 / 序号 | ✓ | — |

## Key Takeaways

1. **聚合折叠行 + 一行一聚合**:`COUNT / SUM / AVG / MIN / MAX`;窗口函数保留行 + 多一列聚合(详 [ch03](ch03-window-functions.md))
2. **`COUNT(*)` 是行数,`COUNT(col)` 是非 NULL 数**:`SUM` / `AVG` 跳 NULL;`SUM(COALESCE(col, 0))` 显式归 0(详 [ch09 §4](ch09-antipatterns.md))
3. **GROUP BY 列决定分组粒度**:未列在 GROUP BY 的列不能 SELECT(除非包在聚合);PG 严格,MySQL 历史包袱允许
4. **ROLLUP / CUBE / GROUPING SETS 是多维聚合**:一次 query 算多个维度,省多次 GROUP BY
5. **HAVING 是聚合后过滤**:WHERE 是行级过滤;**WHERE 不能用聚合函数**,HAVING 才能;执行顺序详 [ch01 §1](ch01-grammar.md)
6. **FILTER 子句(PG 9.4+)是聚合内条件过滤**:`COUNT(*) FILTER (WHERE status = 'completed')` 比 `SUM(CASE WHEN ...)` 简洁可读
8. **`GROUPING(col)` 区分多维报表聚合 NULL vs 真实 NULL**:返回 0 / 1 标识;`GROUPING_ID` 多列 bitmask
9. **`SELECT *` + GROUP BY 是列歧义**:PG 严格拒绝,必须 explicit columns + 聚合(详 [ch09 §2](ch09-antipatterns.md))
10. **GROUP BY 列建索引免 HashAggregate**:planner 改 Index Scan + GroupAggregate,内存占用大幅下降(详 [ch08 §4](ch08-indexes-perf.md))
11. **窗口聚合 vs GROUP BY 决策**:累计看趋势用窗口;总计比较用 GROUP BY;不能相互替代(详 [ch03 §7](ch03-window-functions.md))
12. **聚合与 HAVING / WHERE / ORDER BY 顺序**:`FROM` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY` → `LIMIT`(详 [ch01 §1](ch01-grammar.md))

## Connects To

- **sql-skill ch01**:SQL 执行顺序(HAVING 在 WHERE 后,SELECT 前;列别名不可用)
- **sql-skill ch03**:窗口函数(累计看趋势用窗口,总计比较用 GROUP BY;详 [ch03 §7](ch03-window-functions.md))
- **sql-skill ch07**:PG 特有(`percentile_cont`, `array_agg`, `string_agg` 等 PG 特有聚合函数)
- **sql-skill ch08**:索引与性能(GROUP BY 列建索引免 HashAggregate,详 [ch08 §4](ch08-indexes-perf.md);EXPLAIN 看 HashAggregate 算子)
- **sql-skill ch09**:反模式综合(SELECT * + GROUP BY / 隐式 GROUP BY 列 / `SUM(col)` 不归 0)