# Chapter 2: SQL JOIN 7 种 + 性能差异 — PostgreSQL 通用视角

## Core Idea

SQL JOIN 是多表查询的核心,7 种类型覆盖所有业务场景:① **INNER JOIN** 等值匹配(最常用);② **OUTER JOIN** 保留 unmatched 行(LEFT/RIGHT/FULL);③ **CROSS JOIN** 笛卡尔积(谨慎使用);④ **SELF JOIN** 自连接(层次结构);⑤ **NATURAL JOIN / USING** 列名匹配(隐式但危险);⑥ **JOIN 算法** 由 planner 选(Nested Loop / Hash / Sort Merge);⑦ **JOIN 反模式** 防 N+1 / 笛卡尔积炸表。**JOIN 算法底层**(EXPLAIN 视角)与 **BI 场景适配**(FDW 跨 DB JOIN)分别归 [sql-skill ch08 §3](ch08-indexes-perf.md) 与 [evidence-skill ch07](../../evidence/evidence-skill/chapters/ch07-fdw.md),本章专注 JOIN 语法 + 场景 + 反模式。

## Frameworks Introduced

### §1 INNER JOIN(等值 / 非等值 / 自连接)— 3 条铁律

- **等值 INNER JOIN 是最常用 JOIN**:返回两表 ON 条件匹配的交集行,`INNER` 关键字可省略(`JOIN` 默认就是 INNER JOIN)。
- **非等值 INNER JOIN**:`ON a.price BETWEEN b.min_price AND b.max_price`(范围匹配),少见但有时用于"价格区间匹配折扣档位"。
- **INNER JOIN 与 WHERE 过滤的差异**:JOIN ON 只决定两表匹配规则,WHERE 在 JOIN 结果上行级过滤;两者顺序对 INNER JOIN 结果相同(集合交换律),但语义不同。

### §2 OUTER JOIN(LEFT / RIGHT / FULL + ON vs WHERE)— 3 条铁律

- **LEFT JOIN 是 OUTER JOIN 主力**:保留左表所有行,右表无匹配填 NULL;`RIGHT JOIN` 较少用(可改写为 LEFT JOIN)。
- **FULL JOIN 保留两侧所有行**:两边无匹配都填 NULL;用于"两边都有缺失数据"的场景,如左右侧分别独立的字典表。
- **ON vs WHERE 在 OUTER JOIN 中的关键区别**:`LEFT JOIN ... ON` 决定匹配规则(`WHERE` 后置过滤 unmatched 行);`LEFT JOIN ... WHERE` 会把 unmatched 行过滤掉,变成 INNER JOIN 语义。**这是 OUTER JOIN 第一踩坑点**(详 §7 反模式)。

### §3 CROSS JOIN(笛卡尔积 / 隐式逗号 FROM)— 1 条铁律

- **CROSS JOIN 返回两表笛卡尔积**:A 表 m 行 × B 表 n 行 = m*n 行;无匹配条件。常用于"日期 × 维度表生成完整网格"或"组合枚举"。

### §4 SELF JOIN(自连接 / 层次结构)— 1 条铁律

- **SELF JOIN 是表与自身的 JOIN**:用不同表别名(`e1`, `e2`)区分;典型场景是层次结构(员工-经理)、序列对比(同店铺相邻日销量对比)、找同组相似行。

### §5 NATURAL JOIN / USING(列名匹配)— 1 条铁律

- **NATURAL JOIN 自动按同名列匹配**:省略 ON 条件,PG 自动找两表所有同名列匹配;**生产环境禁用**,加列后 silently 改语义。`USING(col1, col2)` 显式指定列名,比 NATURAL 略好但仍隐式。

### §6 JOIN 算法与性能(NL / Hash / Sort Merge)— 2 条铁律

- **JOIN 算法由 planner 选,不显式指定**:`EXPLAIN ANALYZE` 看实际用 Nested Loop / Hash Join / Sort Merge;根据表大小 + 索引 + 是否排序自动选(详 [ch08 §3](ch08-indexes-perf.md))。
- **FDW 跨 DB JOIN 性能差**:postgres_fdw 跨 DB JOIN 每次 query 走网络,大批数据 JOIN 性能断崖;高频 JOIN 必预聚合本地表(详 [evidence-skill ch07](../../evidence/evidence-skill/chapters/ch07-fdw.md))。

### §7 JOIN 反模式(隐式逗号 / N+1 / 笛卡尔积 / 大表 JOIN)— 3 条铁律

- **隐式逗号 FROM 是笛卡尔积的根源**:`FROM orders, users WHERE orders.user_id = users.id` — 漏 WHERE 就是 m*n 行;显式 `INNER JOIN ... ON` 强制写匹配条件,reviewer 一眼可见(详 [ch09 §2](ch09-antipatterns.md))。
- **N+1 反模式 = 应用层 for 循环 + 单条 query**:每次循环一次 DB 往返,应改 1 次批量 query + JOIN(详 [ch09 §6](ch09-antipatterns.md))。
- **大表 JOIN 无索引 = 全表扫 × 全表扫**:两边都大 + 无索引 → O(m*n) 笛卡尔积扫表,几百万行就 OOM;高频 JOIN 必须双方有索引或预聚合。

## Key Concepts

### §1 INNER JOIN

- **INNER JOIN**:返回两表 ON 条件匹配的交集行
- **等值 JOIN (equi-join)**:`ON a.id = b.a_id`,最常见形式
- **非等值 JOIN (non-equi-join)**:`ON a.price BETWEEN b.min AND b.max`,范围匹配
- **`JOIN` 默认 INNER JOIN**:`FROM a JOIN b ON ...` 等价 `FROM a INNER JOIN b ON ...`

### §2 OUTER JOIN

- **LEFT [OUTER] JOIN**:保留左表所有行,右表无匹配填 NULL;`OUTER` 关键字可省略
- **RIGHT [OUTER] JOIN**:保留右表所有行,左表无匹配填 NULL;几乎不用,改写为 LEFT
- **FULL [OUTER] JOIN**:保留两侧所有行,两边无匹配都填 NULL
- **ON vs WHERE**:OUTER JOIN 中 ON 是匹配规则,WHERE 后置过滤;WHERE 引用右表列会把 unmatched 行过滤掉

### §3 CROSS JOIN

- **CROSS JOIN**:两表笛卡尔积,m × n 行;无 ON 条件
- **隐式 CROSS JOIN**:`FROM a, b` 等价 `FROM a CROSS JOIN b`(逗号语法)
- **合法用途**:日期 × 维度表生成完整网格、组合枚举(衬衫尺码 × 颜色 × 款式)

### §4 SELF JOIN

- **SELF JOIN**:表与自身 JOIN,用不同别名区分
- **典型场景**:员工-经理层次结构(`e1.manager_id = e2.id`)、同表序列对比(`t1.date = t2.date - INTERVAL '1 day'`)
- **必须用表别名**:`FROM employees e1 JOIN employees e2 ON ...`,否则列引用歧义

### §5 NATURAL JOIN / USING

- **NATURAL JOIN**:自动按同名列匹配,无 ON;**生产禁用**
- **USING(col)**:显式指定列名匹配;比 NATURAL 安全但仍隐式
- **风险**:表 schema 加列后 silently 改变 NATURAL JOIN 语义,bug 难发现

### §6 JOIN 算法

- **Nested Loop (NL)**:outer 小 + inner 有索引场景,每次 lookup 1 行(详 [ch08 §3](ch08-indexes-perf.md))
- **Hash Join**:大表等值 JOIN,内存建 hash 表;PG 8.3+ 默认(详 [ch08 §3](ch08-indexes-perf.md))
- **Sort Merge Join**:两边都已排序的非等值 JOIN(详 [ch08 §3](ch08-indexes-perf.md))
- **planner 自动选**:cost-based,无需显式指定;`EXPLAIN ANALYZE` 验证

### §7 JOIN 反模式

- **隐式逗号 FROM**:`FROM a, b WHERE a.id = b.id`,易漏 WHERE 笛卡尔积
- **N+1 problem**:应用层 for 循环 N 次单条 query
- **笛卡尔积炸表**:大表 + 无索引 + CROSS JOIN
- **大表 JOIN 无索引**:O(m*n) 扫表
- **OUTER JOIN 中 WHERE 误用**:把 LEFT JOIN 变 INNER JOIN 语义

## Mental Models

### §1 INNER JOIN

- **INNER JOIN 是"双向筛选"**:只保留两边都满足的行,等价"集合交集";不保留任何一侧的 unmatched 行。
- **JOIN ON vs WHERE 顺序**:对 INNER JOIN 结果相同(集合交换律),但语义不同 — ON 是匹配规则,WHERE 是结果过滤;代码可读性优先。

### §2 OUTER JOIN

- **LEFT JOIN 是"以左表为锚"**:左表全保留,右表是补充信息;NULL 表示"右表无对应行"。
- **ON 是"匹配条件",WHERE 是"结果过滤"**:LEFT JOIN ... WHERE col IS NULL 是经典反连接 anti-join 模式(找左表无关联的行),但 LEFT JOIN ... WHERE col = X 把 unmatched 过滤掉,等价 INNER JOIN。

### §3 CROSS JOIN

- **CROSS JOIN 是"无匹配条件"**:无 ON 等价"所有组合都要";这是 CROSS JOIN 与 INNER JOIN 的根本区别 — INNER JOIN 是"有匹配条件"。
- **笛卡尔积的危险**:大表 × 大表 = m*n 行的爆炸;只有当两表都很小(维度表)或刻意生成网格时才用。

### §4 SELF JOIN

- **SELF JOIN 是"行与同行比"**:同表内多行之间的关联,例如"我和我经理"、"今天和昨天";用别名区分不同"角色"。

### §5 NATURAL JOIN

- **NATURAL JOIN 是"信任 schema"**:假设两表设计时就约定好同名列语义一致;实际业务中 schema 演化(加列、改名)会让 NATURAL JOIN 语义 silently 改变。

### §6 JOIN 算法

- **JOIN 算法是 planner 决策**:不是 SQL 写法决策;同一段 SQL 在不同数据量下 planner 可能选不同算法(Nested Loop → Hash Join)。`EXPLAIN ANALYZE` 是真相。
- **索引是 JOIN 性能的"加速器"**:Nested Loop 必 inner 有索引;Hash Join 内存够就不用 spill;Sort Merge 必两边已排序。

### §7 JOIN 反模式

- **隐式逗号 FROM 是"笛卡尔积定时炸弹"**:漏 WHERE = 全表笛卡尔积,几秒内 OOM;显式 `INNER JOIN ... ON` 强制写条件,reviewer 也好审查。
- **N+1 是"应用层 IO 错配"**:DB 适合 batch IO,应用层 for 循环 = 每次 IPC,IO cost 数十倍放大。

## Anti-patterns

### §1

- ❌ `FROM a, b WHERE a.id = b.id`(隐式逗号)→ 显式 `FROM a INNER JOIN b ON a.id = b.id`
- ❌ `INNER JOIN` 期望保留 unmatched → 改 `LEFT JOIN`(语义错配)

### §2

- ❌ `LEFT JOIN ... ON ... WHERE right.col = X` 把 unmatched 行过滤掉 → 把 WHERE 条件移到 ON,或确认这是 anti-join 意图
- ❌ 不区分 LEFT/RIGHT → 统一用 LEFT JOIN(易读)

### §3

- ❌ 大表 × 大表 CROSS JOIN → 拆段、加 WHERE、明示意图
- ❌ `FROM a, b` 无 WHERE → 必加 WHERE 或显式 CROSS JOIN + 明示意图

### §4

- ❌ SELF JOIN 无表别名 → 必加 `e1`, `e2` 区分
- ❌ SELF JOIN 用 ON 关联同列 → 明确层次结构语义

### §5

- ❌ NATURAL JOIN 依赖隐式同名列 → 改显式 ON,控制 schema 演化风险
- ❌ USING 多列 → 仍隐式,改 `ON a.col = b.col AND ...`

### §6

- ❌ JOIN 算法由 SQL 写法决定(误解)→ planner 选,EXPLAIN ANALYZE 验证
- ❌ 大表 JOIN 不看 EXPLAIN → 加索引或预聚合

### §7

- ❌ 隐式逗号 FROM → 显式 INNER JOIN + ON(详 [ch09 §2](ch09-antipatterns.md))
- ❌ 应用层 N+1 for 循环 → 批量 query + JOIN(详 [ch09 §6](ch09-antipatterns.md))
- ❌ 大表 JOIN 无索引 → 加索引或预聚合本地表
- ❌ OUTER JOIN 后 WHERE 误过滤 unmatched → 把条件移到 ON

## Code Examples

### §1 INNER JOIN 演示

```sql
-- 等值 INNER JOIN:用户和订单
SELECT u.id, u.name, o.id AS order_id, o.amount
FROM users AS u
INNER JOIN orders AS o ON o.user_id = u.id
WHERE u.created_at > NOW() - INTERVAL '30 days';

-- 非等值 INNER JOIN:订单价格匹配折扣档位
SELECT o.id AS order_id, o.amount, d.discount_rate
FROM orders AS o
INNER JOIN discount_tiers AS d
  ON o.amount BETWEEN d.min_amount AND d.max_amount;

-- INNER JOIN 与 WHERE 顺序(对 INNER 等价)
SELECT u.id, u.name, o.amount
FROM users AS u INNER JOIN orders AS o ON o.user_id = u.id
WHERE o.amount > 100;
-- 等价
SELECT u.id, u.name, o.amount
FROM users AS u, orders AS o
WHERE o.user_id = u.id AND o.amount > 100;
-- 结果相同(集合交换律),但前者显式 JOIN 更清晰
```

### §2 OUTER JOIN 演示

```sql
-- LEFT JOIN:用户及其订单(含无订单用户)
SELECT u.id, u.name, o.id AS order_id, o.amount
FROM users AS u
LEFT JOIN orders AS o ON o.user_id = u.id;
-- 无订单用户:order_id = NULL, amount = NULL

-- LEFT JOIN ... WHERE right.col IS NULL:anti-join(找无订单用户)
SELECT u.id, u.name
FROM users AS u
LEFT JOIN orders AS o ON o.user_id = u.id
WHERE o.id IS NULL;

-- ❌ 错误:WHERE 把 unmatched 过滤掉,变 INNER JOIN 语义
SELECT u.id, u.name, o.amount  -- 只返回有订单的用户
FROM users AS u
LEFT JOIN orders AS o ON o.user_id = u.id
WHERE o.amount > 100;  -- LEFT JOIN 的 unmatched 行 amount = NULL,被 WHERE 过滤

-- ✅ 修正:把条件移到 ON
SELECT u.id, u.name, o.amount
FROM users AS u
LEFT JOIN orders AS o ON o.user_id = u.id AND o.amount > 100;
-- 现在 unmatched 用户 amount = NULL 仍保留

-- FULL JOIN:两侧都保留
SELECT u.id AS user_id, o.id AS order_id
FROM users AS u
FULL JOIN orders AS o ON o.user_id = u.id;
-- 无订单用户 + 无用户订单 都返回
```

### §3 CROSS JOIN 演示

```sql
-- 日期 × 店铺 完整网格(用于"店铺每日销售"补 0 销量日)
SELECT d.date, s.shop_id, COALESCE(sa.amount, 0) AS amount
FROM (
  SELECT generate_series('2026-01-01'::date, '2026-01-31'::date, '1 day') AS date
) AS d
CROSS JOIN shops AS s
LEFT JOIN daily_shop_sales AS sa ON sa.shop_id = s.shop_id AND sa.date = d.date;
-- CROSS JOIN 生成 31 天 × N 店铺行,LEFT JOIN 补 sales

-- 隐式逗号(等价 CROSS JOIN,但不推荐)
SELECT d.date, s.shop_id
FROM (SELECT generate_series(...) AS date) d, shops s;
-- ❌ 易漏 WHERE 变笛卡尔积;显式 CROSS JOIN 更安全

-- ❌ 危险:大表 × 大表
SELECT * FROM orders CROSS JOIN users;  -- 几百万 × 几十万 = OOM
```

### §4 SELF JOIN 演示

```sql
-- 员工-经理层次结构
SELECT
  e1.id AS employee_id,
  e1.name AS employee_name,
  e2.id AS manager_id,
  e2.name AS manager_name
FROM employees AS e1
LEFT JOIN employees AS e2 ON e2.id = e1.manager_id;
-- e2 是 e1 的经理;e1.manager_id = NULL 时,e2 是 NULL(顶级员工无经理)

-- 同表相邻日对比:今天销量 vs 昨天销量
SELECT
  t1.shop_id,
  t1.date AS today,
  t1.amount AS today_amount,
  t2.amount AS yesterday_amount,
  t1.amount - t2.amount AS diff
FROM daily_shop_sales AS t1
INNER JOIN daily_shop_sales AS t2
  ON t2.shop_id = t1.shop_id
  AND t2.date = t1.date - INTERVAL '1 day';

-- 找同店铺最相似的两个订单(简化演示)
SELECT
  o1.id AS order1, o2.id AS order2,
  ABS(o1.amount - o2.amount) AS amount_diff
FROM orders AS o1
INNER JOIN orders AS o2
  ON o1.shop_id = o2.shop_id
  AND o1.id < o2.id  -- 避免 (A,B) (B,A) 重复
WHERE ABS(o1.amount - o2.amount) < 10;
```

### §5 NATURAL JOIN / USING 演示

```sql
-- NATURAL JOIN:自动按同名 id 匹配(危险)
CREATE TABLE users_legacy (id int, name text);
CREATE TABLE orders_legacy (id int, user_id int, amount numeric);
SELECT u.id, u.name, o.amount
FROM users_legacy u NATURAL JOIN orders_legacy o;  -- 实际按 user_id 匹配?错!按所有同名列(id)匹配,语义错!
-- 实际匹配的是 users.id = orders.id,完全错

-- USING(col):显式指定列名
SELECT u.id, u.name, o.amount
FROM users u JOIN orders o USING (user_id);
-- 等价 INNER JOIN ... ON u.user_id = o.user_id
-- 但 USING 输出的 user_id 列不带表名前缀(SELECT user_id)

-- ✅ 推荐:显式 ON,语义可控
SELECT u.id AS user_id, u.name, o.amount
FROM users u INNER JOIN orders o ON o.user_id = u.id;
```

### §6 JOIN 算法 EXPLAIN

```sql
-- Nested Loop:小数据集 + 索引
EXPLAIN ANALYZE
SELECT u.id, u.name, o.amount
FROM users AS u
INNER JOIN orders AS o ON o.user_id = u.id
WHERE u.created_at > NOW() - INTERVAL '7 days';
-- 典型 plan:Hash Join 或 Nested Loop(取决于 users 数)

-- Hash Join:大表等值 JOIN
EXPLAIN ANALYZE
SELECT u.name, SUM(o.amount)
FROM users AS u
JOIN orders AS o ON o.user_id = u.id
GROUP BY u.name;
-- 典型 plan:Hash Join(两边都大,等值条件)

-- 完整解读详 [ch08 §3](ch08-indexes-perf.md) 与 [ch08 §6](ch08-indexes-perf.md)
```

### §7 JOIN 反模式 + 修法

```sql
-- ❌ 隐式逗号 FROM
SELECT * FROM orders, users WHERE orders.user_id = users.id;
-- 漏 WHERE = orders × users 笛卡尔积

-- ✅ 显式 INNER JOIN
SELECT * FROM orders AS o
INNER JOIN users AS u ON u.id = o.user_id;

-- ❌ N+1(应用层 for 循环)
-- for user in users:
--   orders = cursor.execute("SELECT * FROM orders WHERE user_id = %s", (user.id,))
-- 1000 用户 = 1001 次 DB 往返

-- ✅ 1 次 JOIN
SELECT u.id, u.name, o.*
FROM users AS u
LEFT JOIN orders AS o ON o.user_id = u.id
WHERE u.created_at > NOW() - INTERVAL '7 days';
-- 1 次 DB 往返,JOIN 批量拉数据

-- ❌ 大表 JOIN 无索引
SELECT * FROM big_orders o JOIN big_users u ON o.user_id = u.id;
-- O(orders × users) 笛卡尔积,几秒内 OOM

-- ✅ 加索引或预聚合
CREATE INDEX idx_orders_user_id ON orders (user_id);
CREATE INDEX idx_users_id ON users (id);
-- 或高频场景预聚合本地表

-- ❌ LEFT JOIN 后 WHERE 误过滤 unmatched
SELECT u.id, u.name, o.amount
FROM users u LEFT JOIN orders o ON o.user_id = u.id
WHERE o.amount > 100;  -- LEFT JOIN unmatched 行 amount=NULL 被过滤,变 INNER 语义

-- ✅ 把条件移到 ON 或显式声明 anti-join
SELECT u.id, u.name, o.amount
FROM users u LEFT JOIN orders o ON o.user_id = u.id AND o.amount > 100;
-- 或 anti-join 找无大单用户:
SELECT u.id, u.name
FROM users u LEFT JOIN orders o ON o.user_id = u.id AND o.amount > 100
WHERE o.id IS NULL;

## Reference Tables

### §1 INNER JOIN 决策表

| 场景 | 语法 | 关键点 |
|---|---|---|
| 等值匹配 | `INNER JOIN ... ON a.id = b.a_id` | 最常用,显式 JOIN 优先 |
| 范围匹配 | `INNER JOIN ... ON a.x BETWEEN b.min AND b.max` | 非等值 JOIN,价格区间 |
| 多表 JOIN | `FROM a JOIN b ON ... JOIN c ON ...` | 每步显式 JOIN,避免笛卡尔积 |
| 隐式 JOIN(等价) | `FROM a, b WHERE a.id = b.id` | ❌ 不推荐,易笛卡尔积 |

### §2 OUTER JOIN 决策表

| 场景 | 语法 | 关键点 |
|---|---|---|
| 保留左表所有行 | `LEFT JOIN ... ON ...` | 最常用 OUTER JOIN |
| 保留右表所有行 | `RIGHT JOIN ... ON ...` | 几乎不用,改 LEFT |
| 两侧都保留 | `FULL JOIN ... ON ...` | 两侧字典表对齐场景 |
| anti-join(找无关联) | `LEFT JOIN ... WHERE right.id IS NULL` | 经典模式 |
| ON vs WHERE | ON 是匹配规则,WHERE 是结果过滤 | WHERE 引用右表列会过滤 unmatched |

### §3 CROSS JOIN 决策表

| 场景 | 语法 | 关键点 |
|---|---|---|
| 完整网格生成 | `date_table CROSS JOIN dim_table` | 日期 × 维度 |
| 组合枚举 | `sizes CROSS JOIN colors` | 衬衫尺码 × 颜色 |
| 危险 | 大表 × 大表 | ❌ O(m*n),几秒 OOM |

### §4 SELF JOIN 决策表

| 场景 | 关键点 |
|---|---|
| 员工-经理层次 | `e1.manager_id = e2.id` |
| 同表相邻日对比 | `t2.date = t1.date - INTERVAL '1 day'` |
| 同组相似行 | `o1.id < o2.id` 防 (A,B)(B,A) 重复 |
| 关键 | 必须用不同表别名 `e1`, `e2` |

### §5 NATURAL JOIN / USING 决策表

| 场景 | 风险 | 推荐 |
|---|---|---|
| NATURAL JOIN | 加列 silently 改语义 | ❌ 生产禁用 |
| USING(col) | 仍隐式多列匹配 | 略好,仍不推荐 |
| 显式 ON | 语义可控 | ✅ 推荐 |

### §6 JOIN 算法决策表(详 [ch08 §3](ch08-indexes-perf.md))

| 数据分布 | planner 选 | 原因 |
|---|---|---|
| outer 小 + inner 索引 | Nested Loop | 每次 lookup 1 行 |
| 两边都大 + 等值 | Hash Join | 内存 hash |
| 两边都已排序 + 非等值 | Sort Merge Join | merge 排序流 |

## Key Takeaways

1. **JOIN 7 种** = INNER / OUTER (LEFT/RIGHT/FULL) / CROSS / SELF / NATURAL-USING,JOIN 关系 SQL 多表查询核心
2. **INNER JOIN 是默认**,最常用;`JOIN` 关键字等价 `INNER JOIN`
3. **LEFT JOIN 是 OUTER 主力**,RIGHT 几乎不用,FULL 用于两侧缺失数据场景
4. **ON vs WHERE 在 OUTER JOIN 中语义不同**:ON 是匹配规则,WHERE 是结果过滤;WHERE 引用右表列会把 unmatched 行过滤掉(变 INNER 语义)
5. **CROSS JOIN 是笛卡尔积**,m × n 行;用于日期×维度完整网格,**大表×大表禁用**
6. **SELF JOIN 用不同别名**(`e1`, `e2`)区分,典型场景:员工-经理层次、同表序列对比
7. **NATURAL JOIN / USING 生产禁用**,显式 `INNER JOIN ... ON` 语义可控,加列不会 silently 改语义
8. **JOIN 算法由 planner 选**(Nested Loop / Hash / Sort Merge),`EXPLAIN ANALYZE` 验证;**不重写 EXPLAIN 细节**详 [ch08 §3](ch08-indexes-perf.md)
9. **隐式逗号 FROM 是笛卡尔积定时炸弹** → 显式 `INNER JOIN ... ON`(详 [ch09 §2](ch09-antipatterns.md))
10. **N+1 反模式**:应用层 for 循环 → 批量 query + JOIN(详 [ch09 §6](ch09-antipatterns.md))
11. **大表 JOIN 无索引 = O(m*n) 笛卡尔积** → 加索引或预聚合本地表
12. **FDW 跨 DB JOIN 性能差** → 高频 JOIN 必预聚合本地表(详 [evidence-skill ch07](../../evidence/evidence-skill/chapters/ch07-fdw.md))

## Connects To

- **sql-skill ch01**:SQL 执行顺序(`FROM` 是 JOIN 阶段,详 [ch01 §1](ch01-grammar.md))
- **sql-skill ch07**:PG 特有(`LATERAL JOIN` + `unnest` 数组展开场景)
- **sql-skill ch08**:索引与性能(JOO 算法 EXPLAIN 视角详 [ch08 §3](ch08-indexes-perf.md);大 OFFSET keyset pagination 详 [ch08 §5](ch08-indexes-perf.md))
- **sql-skill ch09**:反模式综合(隐式 JOIN 详 [ch09 §2](ch09-antipatterns.md);N+1 详 [ch09 §6](ch09-antipatterns.md))
- **evidence-skill ch05**:中文 schema 业务侧雷区(JOO 列名假名清单,本 chapter 不重写)
- **evidence-skill ch07**:postgres_fdw 跨 DB JOIN 性能差,高频 JOIN 预聚合本地表
```