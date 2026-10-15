# Chapter 4: SQL CTE / 递归 CTE / 物化 — PostgreSQL 通用视角

## Core Idea

CTE(Common Table Expression,`WITH` 子句)是 SQL 的"临时命名结果集",分两类:① **非递归 CTE** — 简单的命名子查询,提升可读性和复用性;② **递归 CTE** (`WITH RECURSIVE`)— 反复执行直到空集,适用层次结构(员工-经理树)、图遍历、数字序列生成。PG 12+ 支持 `AS MATERIALIZED` / `AS NOT MATERIALIZED` 控制是否内联。CTE vs 子查询 vs 临时表的性能对比关键看**是否复用 + 复杂度**:**CTE 提升可读性,临时表适合多步复杂 ETL**。**postgres_fdw 跨 DB CTE** 走 local scope(详 [evidence-skill ch07](../../evidence/evidence-skill/chapters/ch07-fdw.md))。

## Frameworks Introduced

### §1 WITH clause 基础(非递归 CTE)— 2 条铁律

- **CTE 是 WITH 子句定义的命名临时结果集**:`WITH cte_name AS (SELECT ...) SELECT * FROM cte_name`;只在紧随其后的单条 query 有效。
- **CTE 提升可读性 + 复用性**:把复杂子查询提取为命名 CTE,主查询读起来像"业务描述";同一 CTE 可在主查询中被引用多次(SELECT / FROM / JOIN)。

### §2 WITH RECURSIVE(递归 CTE + UNION / UNION ALL)— 2 条铁律

- **递归 CTE 由 anchor + recursive part 组成**:`WITH RECURSIVE cte AS (anchor UNION recursive_part)`;anchor 是初始查询,recursive part 引用自身产生下一层,直到空集停止。
- **UNION 去重 / UNION ALL 保留重复**:递归中常用 `UNION ALL` 保留中间结果(性能更好),最终 `UNION` 用于去重。

### §3 MATERIALIZED CTE 决策(PG 12+ AS MATERIALIZED / NOT MATERIALIZED)— 1 条铁律

- **PG 12+ 默认 MATERIALIZED(物化)**:CTE 被计算一次并存储为临时结果,主查询多次引用共享结果;**性能好但失去谓词下推**(主查询的 WHERE 不能 push 到 CTE 内)。
- **`AS NOT MATERIALIZED` 内联**:PG 11- 默认行为;CTE 当子查询内联到主查询,**支持谓词下推但多次引用会重复计算**;按场景选。

### §4 CTE vs 子查询 vs 临时表(性能对比)— 2 条铁律

- **CTE vs 子查询**:CTE 主要是可读性,性能差异 PG 12+ 几乎无(MATERIALIZED 一次计算);子查询内联谓词下推好。
- **CTE vs 临时表**:临时表是会话级实体,有统计信息可建索引;CTE 是 query 级,**CTE 不能建索引**;复杂多步 ETL + 大中间结果用临时表。

### §5 CTE 可读性 + 维护性

- **CTE 是"业务逻辑分段"**:每段 CTE 描述一个业务步骤,主查询是组合;vs 一坨嵌套子查询,debug 时一头雾水。
- **多 CTE 链式**:`WITH a AS (...), b AS (SELECT FROM a) SELECT FROM b`,每步命名 + 注释让 reviewer 5 秒看懂。

### §6 递归 CTE 应用场景(层次结构 / 图遍历 / 数字序列)

- **层次结构**:员工-经理树(详 §2 demo)、目录树、评论回复链。
- **图遍历**:从某节点出发找所有可达节点(BFS / DFS)。
- **数字序列生成**:`generate_series` + 递归生成斐波那契 / 等差 / 等比。

### §7 CTE 反模式(过度嵌套 / 物化滥用)— 3 条铁律

- **CTE 过度嵌套**:5+ 层 CTE 嵌套可读性反而下降,改子查询或临时表。
- **物化滥用**:`AS MATERIALIZED` 失去谓词下推,大 CTE 多次引用内存 spike;按场景选 MATERIALIZED vs NOT MATERIALIZED。
- **CTE 不能建索引**:大结果集 + 高频 JOIN → 临时表 + 索引。

## Key Concepts

### §1 WITH clause

- **CTE (Common Table Expression)**:`WITH name AS (SELECT ...) SELECT ...`,query 级命名临时结果集
- **`AS (SELECT ...)`**:CTE 定义子句,可以是 SELECT / VALUES / INSERT/UPDATE/DELETE(PG 12+)
- **作用域**:仅在紧随其后的单条 query 有效

### §2 WITH RECURSIVE

- **`WITH RECURSIVE`**:递归 CTE 关键字
- **anchor**:递归 CTE 的初始查询,产生第一层结果
- **recursive part**:引用 CTE 自身的查询,产生下一层
- **终止条件**:recursive part 返回空集时停止
- **`UNION` / `UNION ALL`**:anchor 和 recursive part 之间用 UNION 去重或 UNION ALL 保留

### §3 MATERIALIZED

- **`AS MATERIALIZED`**:PG 12+ 显式物化,CTE 计算一次存临时结果(默认行为)
- **`AS NOT MATERIALIZED`**:PG 12+ 显式内联,CTE 当子查询内联,支持谓词下推
- **PG 11- 行为**:默认 NOT MATERIALIZED
- **PG 12+ 行为**:默认 MATERIALIZED

### §4 CTE vs 子查询 vs 临时表

- **子查询**:内联,谓词下推好,不可复用
- **CTE (PG 12+ 默认 MATERIALIZED)**:命名 + 复用 + 一次计算,失去谓词下推
- **CTE (NOT MATERIALIZED)**:命名 + 复用 + 谓词下推,多次引用重复计算
- **临时表**:会话级,可建索引;多步 ETL 用

### §5 可读性

- **业务逻辑分段**:每段 CTE 一个语义,主查询是组合
- **链式 CTE**:W1 → W2 → W3 → 主查询,逐步累加

### §6 递归 CTE 应用

- **层次结构**:员工-经理、组织树、BOM
- **图遍历**:BFS / DFS 找连通分量
- **数字序列**:斐波那契、等差、等比

## Mental Models

### §1 WITH clause

- **CTE 是"虚拟 view"**:与 view 类似但只在 query 级,不持久化;每次 query 重新计算。
- **CTE 是"query 内的命名"**:让 reviewer 一眼看穿"这段子查询是什么"。

### §2 WITH RECURSIVE

- **递归是"层层下钻"**:anchor 是顶层,recursive part 是下一层;PG 自动迭代直到空集。
- **`UNION ALL` vs `UNION`**:递归中常用 UNION ALL 保留(性能),最终结果去重用外部 SELECT DISTINCT。

### §3 MATERIALIZED

- **MATERIALIZED 是"一次计算,多次用"**:CTE 物化成临时结果,主查询多次引用共享;代价是失去谓词下推。
- **NOT MATERIALIZED 是"内联优化"**:CTE 当子查询,可被 planner 优化下推;代价是多次引用会重复算。

### §4 CTE vs 子查询 vs 临时表

- **CTE vs 子查询**:CTE 主要赢在可读性;PG 12+ 性能差异不大。
- **CTE vs 临时表**:CTE 是一次性命名结果,临时表是会话级实体;复杂多步 ETL 用临时表(可建索引 + 跨 query 复用)。

### §5 可读性

- **CTE 是"代码 review 友好"**:reviewer 顺着 CTE 名读,不用拆嵌套子查询。

### §6 递归 CTE 应用

- **递归是"用 SQL 表达循环"**:PG 用递归 CTE 实现程序式循环;适合 SQL 难以表达"未知深度"的场景。

### §7 CTE 反模式

- **过度嵌套是"过度抽象"**:CTE 不是越多越好;5+ 层嵌套 debug 反而难。
- **MATERIALIZED 滥用**:大 CTE + NOT MATERIALIZED 失去优化,改 MATERIALIZED;但 MATERIALIZED 又失去谓词下推。

## Anti-patterns

### §1

- ❌ CTE 嵌套 5+ 层 → 改子查询或临时表
- ❌ CTE 不命名(`SELECT * FROM (SELECT ...)`)→ 用 CTE 命名

### §2

- ❌ 递归 CTE anchor 缺终止条件 → 无限递归,`statement_timeout` 兜底
- ❌ 递归 CTE 用 `UNION`(去重慢) → 用 `UNION ALL` + 外部 SELECT DISTINCT

### §3

- ❌ 默认行为不知 → PG 12+ 默认 MATERIALIZED,谓词下推丢失
- ❌ 大 CTE NOT MATERIALIZED 多次引用 → 改 MATERIALIZED(但失去下推)

### §4

- ❌ 大结果集高频 JOIN → CTE 不能建索引,改临时表 + 索引

### §5

- ❌ CTE 无注释 → 加注释说明业务语义

### §6

- ❌ 递归用循环 SQL(应用层循环) → 改递归 CTE

### §7

- ❌ CTE 过度嵌套 → 改子查询或临时表
- ❌ 物化滥用 → 按场景选 MATERIALIZED vs NOT MATERIALIZED
- ❌ CTE 期望建索引 → 改临时表

## Code Examples

### §1 非递归 CTE

```sql
-- 基础 CTE:命名子查询
WITH active_users AS (
  SELECT id, name, email
  FROM users
  WHERE deleted_at IS NULL
    AND created_at > NOW() - INTERVAL '30 days'
)
SELECT u.id, u.name, COUNT(o.id) AS order_count
FROM active_users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name;

-- 多 CTE 链式
WITH
  step1 AS (
    SELECT user_id, SUM(amount) AS user_total
    FROM orders
    GROUP BY user_id
  ),
  step2 AS (
    SELECT user_id, user_total,
           RANK() OVER (ORDER BY user_total DESC) AS rnk
    FROM step1
  )
SELECT * FROM step2 WHERE rnk <= 10;
```

### §2 递归 CTE 层次结构

```sql
-- 员工-经理树
WITH RECURSIVE emp_tree AS (
  -- anchor:顶层员工(无经理)
  SELECT id, name, manager_id, 0 AS depth, name AS path
  FROM employees
  WHERE manager_id IS NULL
  UNION ALL
  -- recursive:下级员工
  SELECT e.id, e.name, e.manager_id, t.depth + 1, t.path || ' > ' || e.name
  FROM employees e
  INNER JOIN emp_tree t ON e.manager_id = t.id
)
SELECT id, name, manager_id, depth, path
FROM emp_tree
ORDER BY path;

-- 限制深度(防无限递归)
WITH RECURSIVE emp_tree AS (
  SELECT id, name, manager_id, 0 AS depth
  FROM employees
  WHERE manager_id IS NULL
  UNION ALL
  SELECT e.id, e.name, e.manager_id, t.depth + 1
  FROM employees e
  INNER JOIN emp_tree t ON e.manager_id = t.id
  WHERE t.depth < 10  -- 限制最大深度
)
SELECT * FROM emp_tree;
```

### §3 MATERIALIZED vs NOT MATERIALIZED

```sql
-- PG 12+ 默认 MATERIALIZED
WITH cte AS (
  SELECT user_id, SUM(amount) AS total
  FROM orders
  GROUP BY user_id
)
SELECT * FROM cte WHERE user_id = 1;
-- CTE 一次性物化,主查询 WHERE user_id = 1 无法 push 到 CTE 内
-- 即使只要 user_id = 1,CTE 仍全表聚合

-- AS NOT MATERIALIZED:内联,谓词下推
WITH cte AS NOT MATERIALIZED (
  SELECT user_id, SUM(amount) AS total
  FROM orders
  GROUP BY user_id
)
SELECT * FROM cte WHERE user_id = 1;
-- planner 把 WHERE user_id = 1 push 到 CTE 内聚合前过滤

-- 多次引用:NOT MATERIALIZED 重复算,MATERIALIZED 一次算
WITH cte AS NOT MATERIALIZED (
  SELECT user_id, SUM(amount) AS total FROM orders GROUP BY user_id
)
SELECT user_id, total FROM cte WHERE user_id = 1
UNION ALL
SELECT user_id, total FROM cte WHERE user_id = 2;
-- NOT MATERIALIZED:两次聚合
-- 改 MATERIALIZED:一次聚合,两次从临时结果拿
```

### §4 CTE vs 子查询 vs 临时表

```sql
-- CTE:可读性好,PG 12+ 默认 MATERIALIZED
WITH totals AS (
  SELECT user_id, SUM(amount) AS total FROM orders GROUP BY user_id
)
SELECT u.name, t.total
FROM users u JOIN totals t ON t.user_id = u.id;

-- 等价子查询:谓词下推好,但可读性差
SELECT u.name, t.total
FROM users u JOIN (
  SELECT user_id, SUM(amount) AS total FROM orders GROUP BY user_id
) t ON t.user_id = u.id;

-- 临时表:大结果集 + 高频 JOIN
CREATE TEMP TABLE tmp_user_totals AS
SELECT user_id, SUM(amount) AS total FROM orders GROUP BY user_id;
CREATE INDEX idx_tmp_user_totals ON tmp_user_totals (user_id);
-- 临时表可建索引,适合多步 ETL
SELECT u.name, t.total
FROM users u JOIN tmp_user_totals t ON t.user_id = u.id;
DROP TABLE tmp_user_totals;
```

### §5 多 CTE 链式 + 注释

```sql
-- 业务:用户 30 天内复购率(至少 2 单)
WITH
  -- step1:活跃用户(30 天内有订单)
  active_users AS (
    SELECT DISTINCT user_id FROM orders
    WHERE created_at > NOW() - INTERVAL '30 days'
  ),
  -- step2:每用户订单数
  user_order_count AS (
    SELECT user_id, COUNT(*) AS cnt
    FROM orders
    WHERE user_id IN (SELECT user_id FROM active_users)
    GROUP BY user_id
  ),
  -- step3:复购用户(>=2 单)
  repeat_users AS (
    SELECT user_id FROM user_order_count WHERE cnt >= 2
  )
SELECT
  (SELECT COUNT(*) FROM active_users) AS active_count,
  (SELECT COUNT(*) FROM repeat_users) AS repeat_count,
  (SELECT COUNT(*) FROM repeat_users)::numeric / NULLIF((SELECT COUNT(*) FROM active_users), 0) AS repeat_rate;
```

### §6 递归 CTE 应用:数字序列 + 图遍历

```sql
-- 数字序列:前 10 个斐波那契
WITH RECURSIVE fib AS (
  SELECT 1 AS n, 0::bigint AS a, 1::bigint AS b
  UNION ALL
  SELECT n + 1, b, a + b FROM fib WHERE n < 10
)
SELECT n, a FROM fib;

-- 图遍历:从某节点出发找所有可达节点(BFS)
WITH RECURSIVE reachable AS (
  SELECT id AS node_id, 0 AS depth, ARRAY[id] AS path
  FROM nodes WHERE id = 1  -- 起始节点
  UNION ALL
  SELECT e.to_node, r.depth + 1, r.path || e.to_node
  FROM edges e
  JOIN reachable r ON e.from_node = r.node_id
  WHERE r.depth < 100  -- 防无限
    AND NOT (e.to_node = ANY(r.path))  -- 防环
)
SELECT * FROM reachable;
```

### §7 CTE 反模式 + 修法

```sql
-- ❌ 5+ 层 CTE 嵌套可读性差
WITH a AS (...), b AS (SELECT FROM a), c AS (SELECT FROM b),
     d AS (SELECT FROM c), e AS (SELECT FROM d)
SELECT FROM e;
-- 5 层抽象,debug 难

-- ✅ 改临时表分步(复杂 ETL)
CREATE TEMP TABLE tmp_a AS ...;
CREATE TEMP TABLE tmp_b AS SELECT FROM tmp_a;
-- 每步可单独验证 + 加索引

-- ❌ 大 CTE NOT MATERIALIZED 多次引用
WITH big_cte AS NOT MATERIALIZED (
  SELECT a.id, SUM(b.amount) FROM big_a a JOIN big_b b ON ... GROUP BY a.id
)
SELECT * FROM big_cte WHERE id = 1
UNION ALL
SELECT * FROM big_cte WHERE id = 2;
-- 每次引用重算,慢

-- ✅ 改 MATERIALIZED(只算一次)或临时表
WITH big_cte AS MATERIALIZED (
  SELECT a.id, SUM(b.amount) FROM big_a a JOIN big_b b ON ... GROUP BY a.id
)
SELECT * FROM big_cte WHERE id = 1
UNION ALL
SELECT * FROM big_cte WHERE id = 2;
-- 一次聚合,主查询多次从临时结果拿

-- ❌ CTE 期望建索引
WITH big_cte AS (
  SELECT user_id, SUM(amount) FROM orders GROUP BY user_id
)
SELECT * FROM big_cte WHERE user_id BETWEEN 100 AND 200;
-- CTE 不能建索引,user_id 无索引则慢

-- ✅ 临时表 + 索引
CREATE TEMP TABLE tmp_user_totals AS
SELECT user_id, SUM(amount) AS total FROM orders GROUP BY user_id;
CREATE INDEX idx_tmp_user_totals ON tmp_user_totals (user_id);
SELECT * FROM tmp_user_totals WHERE user_id BETWEEN 100 AND 200;

## Reference Tables

### §1 CTE 基础速查

| 场景 | 写法 |
|---|---|
| 单 CTE | `WITH cte AS (SELECT ...) SELECT FROM cte` |
| 多 CTE 链 | `WITH a AS (...), b AS (SELECT FROM a) SELECT FROM b` |
| CTE 用于 JOIN | `WITH cte AS (...) SELECT FROM t JOIN cte ON ...` |

### §2 递归 CTE 决策

| 场景 | 关键点 |
|---|---|
| 员工-经理层次 | anchor = 顶层员工,recursive = `e.manager_id = t.id` |
| 限制深度 | `WHERE t.depth < N` 防无限递归 |
| 防环 | `WHERE NOT (next_node = ANY(path))` |
| UNION vs UNION ALL | 递归中用 UNION ALL 性能好,最终去重用外层 DISTINCT |

### §3 MATERIALIZED 决策表

| 场景 | 选 | 原因 |
|---|---|---|
| CTE 多次引用 + 代价高 | `AS MATERIALIZED` | 一次计算,多次用 |
| CTE 一次引用 + 主查询强过滤 | `AS NOT MATERIALIZED` | 谓词下推 |
| PG 11- 行为 | NOT MATERIALIZED | 默认内联 |
| PG 12+ 行为 | MATERIALIZED | 默认物化(版本陷阱) |

### §4 CTE vs 子查询 vs 临时表

| 场景 | 选 | 原因 |
|---|---|---|
| 简单命名 + 可读性 | CTE | 业务逻辑分段 |
| 谓词下推关键 | 子查询 | 内联优化 |
| 大结果集 + 高频 JOIN | 临时表 | 可建索引 + 跨 query 复用 |
| 复杂多步 ETL | 临时表 | 每步独立验证 |

### §6 递归 CTE 典型应用

| 场景 | 用递归 CTE | 用循环 SQL |
|---|---|---|
| 层次结构(深度未知) | ✓ | ✗ 难表达 |
| 图遍历(BFS/DFS) | ✓ | ✗ |
| 数字序列(前 N 项) | ✓ | 性能差 |
| 固定迭代次数 | ✓ | ✓ |

### §7 CTE 反模式决策表

| 反模式 | 替代 |
|---|---|
| 5+ 层 CTE 嵌套 | 子查询或临时表 |
| 大 CTE NOT MATERIALIZED 多次引用 | `AS MATERIALIZED` 或临时表 |
| CTE 期望建索引 | 临时表 + CREATE INDEX |
| 递归无终止条件 | `WHERE depth < N` 或 `statement_timeout` |

## Key Takeaways

1. **CTE 是 WITH 子句定义的命名临时结果集**,只在紧随其后的单条 query 有效
2. **CTE 主要赢在可读性 + 复用性**,PG 12+ 性能差异不大(默认 MATERIALIZED)
3. **递归 CTE 由 anchor + recursive part 组成**,用 `UNION ALL` 性能好,防无限递归用 `WHERE depth < N` 或 `statement_timeout`
4. **PG 12+ 默认 MATERIALIZED**(一次物化),失去谓词下推;`AS NOT MATERIALIZED` 内联支持优化下推
5. **多次引用 + 大结果集用 MATERIALIZED**;单次引用 + 强过滤用 NOT MATERIALIZED
6. **CTE 不能建索引**:大结果集 + 高频 JOIN 改临时表(可建索引 + 跨 query 复用)
7. **CTE vs 子查询 vs 临时表**:CTE 命名 + 可读;子查询谓词下推;临时表多步 ETL + 索引
8. **递归 CTE 适用场景**:层次结构(员工-经理)、图遍历、数字序列
9. **5+ 层 CTE 嵌套可读性下降**,改子查询或临时表(每步独立验证)
10. **postgres_fdw 跨 DB CTE local scope**:CTE 在外层 query 作用域,与 taobao.mart_X FDW 表兼容(详 [evidence-skill ch07](../../evidence/evidence-skill/chapters/ch07-fdw.md))
11. **业务逻辑分段 + 注释**:每段 CTE 一个语义,reviewer 5 秒看懂
12. **CTE 内 VALUES / INSERT/UPDATE/DELETE**(PG 12+ writable CTE,详 [PG docs](https://www.postgresql.org/docs/current/queries-with.html))

## Connects To

- **sql-skill ch01**:SQL 执行顺序(CTE 在 SELECT 前已计算,主查询引用 CTE 名)
- **sql-skill ch07**:PG 特有(postgres_fdw CTE 跨 DB 用法详 [evidence-skill ch07](../../evidence/evidence-skill/chapters/ch07-fdw.md))
- **sql-skill ch08**:索引与性能(临时表可建索引,CTE 不能,详 [ch08 §1](ch08-indexes-perf.md))
- **sql-skill ch09**:反模式综合(过度嵌套 / 物化滥用 与 ch09 §3 索引反模式互补)
- **evidence-skill ch07**:postgres_fdw CTE local scope,跨 DB 性能差(高频 CTE 必预聚合本地表)
```