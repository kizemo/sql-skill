# Chapter 3: SQL 窗口函数 — PostgreSQL 通用视角

## Core Idea

窗口函数(Window Function)是 SQL 强大的"分组但保留行"工具,与 GROUP BY 的根本区别是**不折叠行**:每行都保留,只是多一列"窗口聚合结果"。核心组件是 `OVER (PARTITION BY ... ORDER BY ...)` 子句:① **PARTITION BY** 把数据分成多个窗口(类似 GROUP BY);② **ORDER BY** 在窗口内排序;③ **frame 子句**(ROWS / RANGE BETWEEN)定义窗口边界。三类函数:① **排序函数**(ROW_NUMBER / RANK / DENSE_RANK / NTILE);② **分析函数**(LAG / LEAD / FIRST_VALUE / LAST_VALUE / NTH_VALUE);③ **聚合窗口**(SUM / AVG / COUNT OVER + 滑动窗口)。窗口函数与 GROUP BY 互不替代(详 §7)。**窗口函数索引视角**(PARTITION BY 列建索引免 Sort)归 [sql-skill ch08 §5](ch08-indexes-perf.md)。

## Frameworks Introduced

### §1 OVER 子句基础(partition + order + frame)— 3 条铁律

- **OVER 子句是窗口函数的标志**:`<window_function>(...) OVER (PARTITION BY col ORDER BY col [frame_clause])`,没有 OVER 的聚合是 GROUP BY(折叠行)。
- **PARTITION BY 决定窗口边界**:把行分成多个独立分区,每个分区独立计算;省略时整张表是单一窗口。
- **ORDER BY 在窗口内排序**:影响 RANK / ROW_NUMBER / 累计聚合的顺序;省略时结果未定义。

### §2 排序函数(ROW_NUMBER / RANK / DENSE_RANK / NTILE)— 2 条铁律

- **ROW_NUMBER() 唯一连续编号**:1, 2, 3, ... 无并列,适合"分区内唯一序号"。
- **RANK() 并列跳号 / DENSE_RANK() 并列不跳号 / NTILE(n) 分桶**:RANK 是 1,1,3; DENSE_RANK 是 1,1,2; NTILE 把数据均分成 n 桶。

### §3 分析函数(LAG / LEAD / FIRST_VALUE / LAST_VALUE / NTH_VALUE)— 2 条铁律

- **LAG(col, n) / LEAD(col, n) 拿前/后第 n 行**:对比同组前后行(今日 vs 昨日销量);`n` 默认 1,可选第 2 参数作为无前/后行时的默认值。
- **FIRST_VALUE / LAST_VALUE / NTH_VALUE 拿窗口边界值**:`FIRST_VALUE` 窗口第一行,`LAST_VALUE` 窗口最后一行(注意 frame 子句影响),`NTH_VALUE(col, n)` 窗口第 n 行。

### §4 聚合窗口(SUM / AVG / COUNT OVER + 滑动窗口)— 2 条铁律

- **聚合函数 + OVER = 窗口聚合**:`SUM(amount) OVER (PARTITION BY user_id ORDER BY date)` 返回每行累计 SUM,行不折叠(详 §7 vs GROUP BY)。
- **滑动窗口 frame 子句**:`ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` 求 7 天滚动平均;默认 frame 是 `RANGE UNBOUNDED PRECEDING`(累计从分区开始到当前行)。

### §5 命名窗口(WINDOW 子句)— 1 条铁律

- **WINDOW 子句复用 OVER 定义**:`WINDOW w AS (PARTITION BY user_id ORDER BY date)`,多个查询共享同一窗口定义,避免重复。

### §6 帧子句(ROWS BETWEEN / RANGE BETWEEN)— 2 条铁律

- **ROWS BETWEEN n PRECEDING AND m FOLLOWING**:物理行边界,n 行前到 m 行后(例:`ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` 是 7 天滚动窗口)。
- **RANGE BETWEEN INTERVAL ... PRECEDING**:逻辑值边界(同值同行),适合"时间范围滚动"而非"行数滚动";`ROWS` 是行数,`RANGE` 是值域。

### §7 窗口函数反模式(无 PARTITION 聚合 vs GROUP BY 混用)— 3 条铁律

- **窗口聚合 ≠ GROUP BY**:窗口保留所有行 + 多一列聚合;GROUP BY 折叠行 + 一行一个聚合组;**互不替代**(详 §7 决策)。
- **窗口函数不能放在 WHERE**:WHERE 在 SELECT 前,别名未生成;窗口函数只能在 SELECT / HAVING / ORDER BY 用;过滤窗口结果用子查询包一层。
- **PARTITION BY 列无索引 → Sort 算子开销**:PARTITION BY + ORDER BY 列建索引可避免 Sort(详 [ch08 §5](ch08-indexes-perf.md))。

## Key Concepts

### §1 OVER 子句

- **`OVER`**:窗口函数标志,决定"在哪些行集合上做计算"
- **`PARTITION BY col`**:把数据分成多个窗口分区,每个分区独立计算
- **`ORDER BY col`**:窗口内排序,影响 RANK / 累计聚合等
- **frame_clause**:`ROWS BETWEEN ...` / `RANGE BETWEEN ...`,定义窗口边界

### §2 排序函数

- **`ROW_NUMBER()`**:1, 2, 3, ... 唯一连续编号(无并列)
- **`RANK()`**:1, 1, 3 并列跳号(并列后下一名跳)
- **`DENSE_RANK()`**:1, 1, 2 并列不跳号(并列后下一名连续)
- **`NTILE(n)`**:把数据均分成 n 桶,返回桶号 1..n
- **`PERCENT_RANK() / CUME_DIST()`**:相对排名(0-1 范围)

### §3 分析函数

- **`LAG(col, n, default)`**:拿当前行前第 n 行的 col 值;n 默认 1,default 无前/后行时返回
- **`LEAD(col, n, default)`**:拿当前行后第 n 行的 col 值
- **`FIRST_VALUE(col)`**:窗口第一行的 col
- **`LAST_VALUE(col)`**:窗口最后一行(注意 frame 默认)
- **`NTH_VALUE(col, n)`**:窗口第 n 行的 col

### §4 聚合窗口

- **聚合函数 + OVER**:`SUM / AVG / COUNT / MIN / MAX OVER (...)`,每行多一列聚合结果
- **累计聚合**:`SUM(x) OVER (ORDER BY date)` 默认从窗口第一行累计到当前行
- **滑动窗口**:`ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` 7 天滚动

### §5 命名窗口

- **`WINDOW w AS (...)`**:命名窗口定义,可被多个查询复用
- **好处**:避免重复 PARTITION BY / ORDER BY,改一处生效

### §7 窗口 vs GROUP BY

- **窗口函数**:保留所有行 + 每行多一列聚合(行级信息 + 聚合信息)
- **GROUP BY**:折叠行 + 每个分组一行(纯聚合信息)

## Mental Models

### §1 OVER 子句

- **窗口函数是"虚拟列添加"**:每行不动,但通过 OVER 给每行加一列"窗口聚合结果"。
- **PARTITION BY = 虚拟 GROUP BY**:不真的折叠,但计算按分区独立。

### §2 排序函数

- **ROW_NUMBER vs RANK vs DENSE_RANK**:想象班级排名 — ROW_NUMBER 是"按成绩排学号"(无并列);RANK 是"1,1,3"(并列后跳);DENSE_RANK 是"1,1,2"(并列后连续)。
- **NTILE 是"分桶"**:把 100 行均分到 4 桶,每桶 25 行;返回的桶号可做"前 25%"筛选。

### §3 分析函数

- **LAG/LEO 是"时间旅行"**:不看未来 / 过去的 join,只看同组前后行;典型场景 — 今日 vs 昨日销量对比。

### §4 聚合窗口

- **累计 vs 滚动**:累计是"从窗口开始到现在"(unbounded preceding);滚动是"最近 N 个"(rows between n preceding and current row)。
- **窗口聚合保留原表 schema + 加聚合列**:与 GROUP BY 折叠行相反。

### §5 命名窗口

- **WINDOW 是"DRY 原则"**:多个 OVER 共享同一窗口定义,避免复制粘贴出错。

### §6 帧子句

- **ROWS 是物理行(行数)**:第 1 行到第 7 行,与值无关。
- **RANGE 是逻辑值(同值同行)**:日期相同的行视为同一逻辑位置;适合"时间范围滚动"。

### §7 窗口 vs GROUP BY

- **窗口函数 vs GROUP BY 决策**:用户维度销售趋势用窗口(每用户每日累计);用户总销售额用 GROUP BY(每用户一行聚合)。
- **混用 = 错误**:窗口函数不能写在 GROUP BY 内当聚合用,反之亦然。

## Anti-patterns

### §1

- ❌ 窗口函数无 PARTITION BY(全局窗口)→ 明确 PARTITION BY,否则全表当单分区性能差

### §2

- ❌ ROW_NUMBER 当 RANK 用(想去重)→ 理解 ROW_NUMBER 是连续编号,无并列;RANK 才有并列跳号

### §3

- ❌ LAST_VALUE 不带 frame 子句 → 默认 frame UNBOUNDED PRECEDING 是"到当前行",不是真"最后一行";要真最后用 `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`

### §4

- ❌ 累计聚合 vs GROUP BY 混用 → 累计看趋势用窗口;总数比较用 GROUP BY
- ❌ 滑动窗口无 ORDER BY → 顺序未定义,结果未定义

### §5

- ❌ 多个 OVER 重复定义 → 用 WINDOW 子句复用

### §6

- ❌ ROWS / RANGE 混用不区分 → 行数固定用 ROWS,值范围用 RANGE

### §7

- ❌ 窗口函数放 WHERE → 窗口函数只能在 SELECT/HAVING/ORDER BY;过滤用子查询
- ❌ GROUP BY 折叠 + 想要明细 → 改窗口函数保留行
- ❌ PARTITION BY 列无索引 → 加索引免 Sort(详 [ch08 §5](ch08-indexes-perf.md))

## Code Examples

### §1 OVER 子句基础

```sql
-- 基础结构:每行 + 窗口聚合
SELECT
  user_id,
  order_date,
  amount,
  SUM(amount) OVER (PARTITION BY user_id) AS user_total,
  AVG(amount) OVER () AS grand_avg  -- 整表单一窗口
FROM orders;

-- PARTITION BY:每个用户独立聚合
SELECT
  user_id,
  order_date,
  amount,
  SUM(amount) OVER (PARTITION BY user_id ORDER BY order_date) AS user_running_total
FROM orders;
-- 每用户从第一笔累计到当前笔

-- ORDER BY:窗口内排序
SELECT
  user_id,
  order_date,
  amount,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_date) AS seq
FROM orders;
```

### §2 排序函数

```sql
-- ROW_NUMBER 唯一连续编号(分区内)
SELECT
  user_id,
  amount,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY amount DESC) AS rn
FROM orders;
-- 每个用户按 amount 降序唯一编号 1, 2, 3, ...

-- RANK 并列跳号 vs DENSE_RANK 并列不跳号
SELECT
  user_id,
  amount,
  RANK() OVER (ORDER BY amount DESC) AS rk,
  DENSE_RANK() OVER (ORDER BY amount DESC) AS drk
FROM orders;
-- 假设 amount = 100, 100, 90:
-- RANK: 1, 1, 3 (并列后跳)
-- DENSE_RANK: 1, 1, 2 (并列后连续)

-- NTILE 分桶(分位数)
SELECT
  user_id,
  amount,
  NTILE(4) OVER (ORDER BY amount DESC) AS quartile  -- 分 4 桶
FROM orders;
-- 1 = top 25%, 4 = bottom 25%

-- PERCENT_RANK 相对排名
SELECT
  user_id,
  amount,
  PERCENT_RANK() OVER (ORDER BY amount) AS pct_rank  -- 0.0 到 1.0
FROM orders;
```

### §3 分析函数 LAG / LEAD

```sql
-- LAG 拿前一行 / LEAD 拿后一行
SELECT
  user_id,
  order_date,
  amount,
  LAG(amount, 1, 0) OVER (PARTITION BY user_id ORDER BY order_date) AS prev_amount,
  LEAD(amount, 1, 0) OVER (PARTITION BY user_id ORDER BY order_date) AS next_amount
FROM orders;

-- 今日 vs 昨日销量对比
SELECT
  shop_id,
  sale_date,
  amount,
  amount - LAG(amount, 1, 0) OVER (PARTITION BY shop_id ORDER BY sale_date) AS day_over_day
FROM daily_sales;

-- FIRST_VALUE / LAST_VALUE / NTH_VALUE
SELECT
  user_id,
  amount,
  FIRST_VALUE(amount) OVER (PARTITION BY user_id ORDER BY amount DESC) AS user_max,
  LAST_VALUE(amount) OVER (
    PARTITION BY user_id ORDER BY amount DESC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING  -- 真最后一行
  ) AS user_min,  -- 排序降序所以最后 = 最小
  NTH_VALUE(amount, 2) OVER (PARTITION BY user_id ORDER BY amount DESC) AS user_second_max
FROM orders;
```

### §4 聚合窗口 + 滑动窗口

```sql
-- 累计聚合(默认 RANGE UNBOUNDED PRECEDING)
SELECT
  user_id,
  order_date,
  amount,
  SUM(amount) OVER (PARTITION BY user_id ORDER BY order_date) AS running_total
FROM orders;

-- 7 天滚动平均(ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
SELECT
  shop_id,
  sale_date,
  amount,
  AVG(amount) OVER (
    PARTITION BY shop_id ORDER BY sale_date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS avg_7d,
  SUM(amount) OVER (
    PARTITION BY shop_id ORDER BY sale_date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS sum_7d
FROM daily_sales;

-- 30 天滚动 vs 上月同期对比
SELECT
  shop_id,
  sale_date,
  amount,
  AVG(amount) OVER (PARTITION BY shop_id ORDER BY sale_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS avg_30d,
  AVG(amount) OVER (PARTITION BY shop_id ORDER BY sale_date ROWS BETWEEN 59 PRECEDING AND 30 PRECEDING) AS avg_prev_30d
FROM daily_sales;
```

### §5 命名窗口

```sql
-- WINDOW 子句复用定义
SELECT
  user_id,
  order_date,
  amount,
  SUM(amount) OVER w AS running_total,
  AVG(amount) OVER w AS running_avg,
  COUNT(*) OVER w AS running_count
FROM orders
WINDOW w AS (PARTITION BY user_id ORDER BY order_date);
-- 三个窗口函数共享同一窗口定义 w

-- 多窗口(不同 partition)
SELECT
  user_id,
  shop_id,
  amount,
  SUM(amount) OVER w_user AS user_total,
  SUM(amount) OVER w_shop AS shop_total
FROM orders
WINDOW
  w_user AS (PARTITION BY user_id),
  w_shop AS (PARTITION BY shop_id);
```

### §6 帧子句 ROWS vs RANGE

```sql
-- ROWS BETWEEN:物理行(行数固定)
SELECT
  user_id,
  sale_date,
  amount,
  SUM(amount) OVER (
    PARTITION BY user_id ORDER BY sale_date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS sum_7rows
FROM daily_sales;
-- 不管日期是否连续,取前 7 行

-- RANGE BETWEEN:逻辑值(同值同行)
SELECT
  user_id,
  sale_date,
  amount,
  SUM(amount) OVER (
    PARTITION BY user_id ORDER BY sale_date
    RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW
  ) AS sum_7days
FROM daily_sales;
-- 取 sale_date 在当前行 6 天内的所有行(含同一天多行)

-- 默认 frame: RANGE UNBOUNDED PRECEDING
SELECT
  user_id,
  sale_date,
  amount,
  SUM(amount) OVER (PARTITION BY user_id ORDER BY sale_date) AS default_frame
FROM daily_sales;
-- 默认 frame = RANGE UNBOUNDED PRECEDING,累计从分区开始到当前行
```

### §7 窗口 vs GROUP BY + 过滤子查询

```sql
-- ❌ 窗口函数放 WHERE(错误)
SELECT
  user_id,
  amount,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY amount DESC) AS rn
FROM orders
WHERE ROW_NUMBER() OVER (...) = 1;  -- ERROR: window functions not allowed in WHERE

-- ✅ 子查询过滤窗口结果
SELECT * FROM (
  SELECT
    user_id,
    amount,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY amount DESC) AS rn
  FROM orders
) sub
WHERE rn = 1;
-- 拿每用户 amount 最大的一笔

-- 累计 vs GROUP BY 对比
-- 累计:每用户每日累计销量(保留每行)
SELECT user_id, sale_date, amount,
       SUM(amount) OVER (PARTITION BY user_id ORDER BY sale_date) AS running
FROM daily_sales;

-- 总计:每用户总销量(折叠行)
SELECT user_id, SUM(amount) AS total
FROM daily_sales
GROUP BY user_id;

-- 混用:窗口聚合 + GROUP BY 分组
SELECT
  user_id,
  SUM(amount) AS user_total,
  RANK() OVER (ORDER BY SUM(amount) DESC) AS user_rank
FROM orders
GROUP BY user_id;
-- GROUP BY 计算每用户总销量,窗口函数给总销量排名

## Reference Tables

### §1 OVER 子句组件速查

| 组件 | 作用 | 省略时 |
|---|---|---|
| `OVER` | 窗口函数标志 | — |
| `PARTITION BY` | 窗口分区边界 | 整表当单分区 |
| `ORDER BY` | 窗口内排序 | 顺序未定义 |
| `ROWS BETWEEN` | 物理行边界(frame) | 默认 UNBOUNDED PRECEDING |
| `RANGE BETWEEN` | 逻辑值边界(frame) | 默认 UNBOUNDED PRECEDING |

### §2 排序函数决策表

| 场景 | 函数 | 关键点 |
|---|---|---|
| 唯一连续编号 | `ROW_NUMBER()` | 无并列,1, 2, 3, ... |
| 并列跳号 | `RANK()` | 1, 1, 3(并列后跳) |
| 并列不跳号 | `DENSE_RANK()` | 1, 1, 2(并列后连续) |
| 分位数 / 桶 | `NTILE(n)` | 分 n 桶 |
| 相对排名 | `PERCENT_RANK() / CUME_DIST()` | 0.0-1.0 范围 |

### §3 分析函数决策表

| 场景 | 函数 | 关键点 |
|---|---|---|
| 拿前一行 | `LAG(col, n, default)` | 默认 default 0/NULL |
| 拿后一行 | `LEAD(col, n, default)` | 默认 default 0/NULL |
| 窗口第一行 | `FIRST_VALUE(col)` | 不依赖 frame |
| 窗口最后一行 | `LAST_VALUE(col)` | **必须**显式 frame UNBOUNDED FOLLOWING |
| 窗口第 n 行 | `NTH_VALUE(col, n)` | n > 1 时返回 NULL |

### §4 聚合窗口决策表

| 场景 | 写法 |
|---|---|
| 累计聚合 | `SUM(x) OVER (PARTITION BY g ORDER BY t)`(默认 UNBOUNDED PRECEDING) |
| N 行滚动 | `SUM(x) OVER (... ROWS BETWEEN N-1 PRECEDING AND CURRENT ROW)` |
| N 天滚动 | `SUM(x) OVER (... RANGE BETWEEN INTERVAL 'N-1 days' PRECEDING AND CURRENT ROW)` |
| 移动平均 | `AVG(x) OVER (... ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` |

### §5 命名窗口

| 场景 | 写法 |
|---|---|
| 复用窗口定义 | `WINDOW w AS (...)`,查询内 `OVER w` |
| 多窗口 | `WINDOW w1 AS (...), w2 AS (...)` |

### §6 ROWS vs RANGE 决策

| 场景 | 选 | 原因 |
|---|---|---|
| 固定行数窗口 | `ROWS BETWEEN N PRECEDING ...` | 行数确定 |
| 时间范围窗口 | `RANGE BETWEEN INTERVAL ...` | 同值同行 |
| 默认累计 | `RANGE UNBOUNDED PRECEDING` | 从 partition 起点 |

### §7 窗口 vs GROUP BY 决策

| 场景 | 用窗口 | 用 GROUP BY |
|---|---|---|
| 保留每行 + 加聚合列 | ✓ | — |
| 折叠行 + 一行一聚合 | — | ✓ |
| 累计 / 趋势 | ✓ | — |
| 总计 / 比较 | — | ✓ |
| 排名 / 序号 | ✓ | — |
| 跨组聚合 + 组内聚合 | 混用 | 混用 |

## Key Takeaways

1. **窗口函数是"分组但保留行"**:每行保留 + 多一列聚合结果;GROUP BY 折叠行(详 [ch05 §1](ch05-aggregates.md))
2. **OVER (PARTITION BY ... ORDER BY ...)** 是窗口函数标志;PARTITION BY 决定窗口边界,ORDER BY 决定窗口内顺序
3. **三类窗口函数**:① 排序(ROW_NUMBER / RANK / DENSE_RANK / NTILE);② 分析(LAG / LEAD / FIRST_VALUE / LAST_VALUE / NTH_VALUE);③ 聚合(SUM/AVG/COUNT OVER + 滑动窗口)
4. **ROW_NUMBER vs RANK vs DENSE_RANK**:ROW_NUMBER 连续编号无并列;RANK 并列跳号(1,1,3);DENSE_RANK 并列不跳号(1,1,2)
5. **LAG / LEAD 是"时间旅行"**:拿同组前/后第 n 行;典型场景 — 今日 vs 昨日销量对比
6. **LAST_VALUE 必须显式 frame**:`ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`,否则默认 frame 只到当前行
7. **ROWS vs RANGE**:ROWS 是物理行(行数);RANGE 是逻辑值(同值同行);时间范围滚动用 RANGE
8. **WINDOW 子句复用 OVER 定义**:多个查询共享同一窗口,DRY 原则
9. **窗口函数不能放 WHERE**:窗口函数只能在 SELECT/HAVING/ORDER BY;过滤用子查询包一层
10. **累计看趋势用窗口,总计比较用 GROUP BY**:两者不替代(详 [ch05 §1](ch05-aggregates.md))
11. **PARTITION BY 列建索引免 Sort 算子**(详 [ch08 §5](ch08-indexes-perf.md));`EXPLAIN` 看是否有 Sort
12. **窗口函数 + GROUP BY 混用合法**:`SUM(...) GROUP BY` 后再用 `RANK() OVER (ORDER BY SUM(...))` 给总销量排名

## Connects To

- **sql-skill ch01**:SQL 执行顺序(SELECT 在 WHERE 后,窗口函数不能在 WHERE 用)
- **sql-skill ch05**:聚合函数(SUM/AVG/COUNT)与窗口函数的关系;GROUP BY vs 窗口聚合(详 [ch05 §1](ch05-aggregates.md))
- **sql-skill ch07**:PG 特有(LATERAL JOIN + unnest + 窗口函数组合场景)
- **sql-skill ch08**:索引与性能(PARTITION BY 列建索引免 Sort 详 [ch08 §5](ch08-indexes-perf.md);Top-N optimization 详 [ch08 §5](ch08-indexes-perf.md))
- **sql-skill ch09**:反模式综合(窗口函数混用 GROUP BY 等反模式)
```