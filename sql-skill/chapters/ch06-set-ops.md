# Chapter 6: SQL 集合操作 — UNION / INTERSECT / EXCEPT

## Core Idea

集合操作(Set Operations)把两个或多个 `SELECT` 结果集按行级合并,分 4 种:① **UNION** 合并并去重;② **UNION ALL** 合并保留重复;③ **INTERSECT** 交集(两表共有行);④ **EXCEPT** 差集(左表有右表无)。与 JOIN 的根本区别:JOIN 是**列级扩展**(横向加列),集合操作是**行级扩展**(纵向加行)。**列数 + 类型必须匹配**是集合操作第一铁律;**ORDER BY / LIMIT 必须放最后**是第二铁律。**集合操作与 JOIN 在很多场景可等价**(详 §4),按场景选。

## Frameworks Introduced

### §1 UNION / UNION ALL(合并去重 / 保留重复)— 2 条铁律

- **UNION 合并并自动去重**:`A UNION B` 返回 A + B 的所有行,重复行只保留一份(去重代价是内部 sort/hash);`UNION ALL` 保留重复行,无去重开销,性能更好。
- **UNION vs UNION ALL 决策**:能容忍重复 + 性能优先 → `UNION ALL`;必须去重 → `UNION`(但考虑先用 `UNION ALL` + 外部 `SELECT DISTINCT` 控制范围)。

### §2 INTERSECT(交集,自动去重)— 1 条铁律

- **INTERSECT 返回两表共有行**:`A INTERSECT B` 等价 `A ∩ B`;自动去重,等同 `INTERSECT ALL` + 外部去重。**INTERSECT vs INNER JOIN**:INTERSECT 是行级集合(整行匹配),INNER JOIN 是列级(ON 条件匹配);详 §4 等价场景。

### §3 EXCEPT(差集,自动去重)— 1 条铁律

- **EXCEPT 返回左表有但右表无的行**:`A EXCEPT B` 等价 `A - B`;**注意顺序**,`B EXCEPT A` 是反向差集。PG 也支持 `EXCEPT ALL` 保留重复。

### §4 集合操作与 JOIN 转换(等价表达)— 1 条铁律

- **INTERSECT 常用 `INNER JOIN + DISTINCT` 替代**:`A INTERSECT B` 等价 `SELECT DISTINCT a.* FROM A a INNER JOIN B b ON a.id = b.id`(列匹配时);`EXCEPT` 常用 `LEFT JOIN ... WHERE right.id IS NULL` 替代(详 [ch02 §2](ch02-joins.md))。**集合操作可读性更好但失去谓词下推**。

### §5 集合操作 + ORDER BY / LIMIT(顶层 vs 子查询)— 2 条铁律

- **`ORDER BY` / `LIMIT` 必须放整个集合操作最后**:`(SELECT ... UNION SELECT ...) ORDER BY col LIMIT 10`;不能放每个子查询里。子查询内 `ORDER BY` + `LIMIT` 仅在该子查询是顶层时才生效。
- **多个子查询列数 + 类型必须匹配**:`SELECT a, b FROM t1 UNION SELECT c, d FROM t2` — 两子查询列数必须相同,对应列类型兼容(自动 cast)。

### §6 集合操作反模式(列数类型不匹配 / ORDER BY 误用)— 3 条铁律

- **列数不匹配 → 报 syntax error**:`SELECT a, b FROM t1 UNION SELECT c FROM t2`(2 列 vs 1 列);改 `UNION SELECT c, NULL FROM t2` 补齐。
- **列类型严重不兼容**:`SELECT '1' UNION SELECT 2` — `'1'` 文本和 `2` 整数,PG 强类型拒绝;改 `SELECT '1'::int UNION SELECT 2`。
- **`SELECT *` + 集合操作**:列变化时 silently 改语义;改 explicit columns(详 [ch09 §2](ch09-antipatterns.md))。

## Key Concepts

### §1 UNION / UNION ALL

- **`UNION`**:合并两表 + 去重(内部 sort/hash 去重)
- **`UNION ALL`**:合并两表 + 保留所有行(无去重开销)
- **`UNION` vs `UNION ALL` 决策**:能容忍重复 + 性能优先 → `UNION ALL`

### §2 INTERSECT

- **`INTERSECT`**:两表共有行(自动去重)
- **`INTERSECT ALL`**:两表共有行(保留重复)
- **vs INNER JOIN**:INTERSECT 行级整行匹配;INNER JOIN 列级 ON 条件匹配

### §3 EXCEPT

- **`EXCEPT`**:左表有但右表无(自动去重)
- **`EXCEPT ALL`**:左表有但右表无(保留重复)
- **注意顺序**:`A EXCEPT B` ≠ `B EXCEPT A`

### §4 集合 vs JOIN 转换

- **INTERSECT → INNER JOIN + DISTINCT**:行级集合 → 列级 JOIN
- **EXCEPT → LEFT JOIN + IS NULL**:差集 → anti-join(详 [ch02 §2](ch02-joins.md))

### §5 ORDER BY / LIMIT

- **顶层 `ORDER BY` / `LIMIT`**:作用整个集合操作结果
- **子查询内 `ORDER BY` / `LIMIT`**:仅该子查询生效(子查询为顶层时)
- **列数 + 类型匹配**:集合操作硬性要求

## Mental Models

### §1 UNION / UNION ALL

- **UNION 是"集合合并"**:数学上的"并集",自动去重;`UNION ALL` 是"多集合合并",保留重复。
- **UNION 性能差在去重**:数据量大时内部 sort 慢;优先 `UNION ALL` + 外部 DISTINCT。

### §2 INTERSECT

- **INTERSECT 是"集合交集"**:数学上的"交集",找两表共有行。

### §3 EXCEPT

- **EXCEPT 是"集合差集"**:数学上的"差集",找左表有右表无;**顺序敏感**。

### §4 集合 vs JOIN

- **集合操作是行级,JOIN 是列级**:这是根本区别;场景能转换但语义不同。
- **INTERSECT 用集合操作可读性高**:SQL 一眼看穿"找共有";INNER JOIN 需 ON 条件对应关系。

### §5 ORDER BY / LIMIT

- **集合操作是"行级流水线"**:先各子查询计算,再合并去重,最后 ORDER BY / LIMIT。

### §6 集合操作反模式

- **列数不匹配是"硬错"**:语法错直接拒绝,debug 易;类型不匹配是"软错",cast 后能跑但语义可能错。

## Anti-patterns

### §1

- ❌ 能用 `UNION ALL` 的场景用 `UNION` → 改 `UNION ALL` + 外部 `SELECT DISTINCT` 控制范围

### §2

- ❌ INTERSECT 重复用 `INNER JOIN + DISTINCT` → 看场景,INTERSECT 整行匹配可读性更好

### §3

- ❌ EXCEPT 顺序搞错 → 明确 `A EXCEPT B` 语义,反向写 `B EXCEPT A`

### §4

- ❌ 集合操作与 JOIN 混用不知等价场景 → INTERSECT → `INNER JOIN + DISTINCT`;EXCEPT → `LEFT JOIN + IS NULL`

### §5

- ❌ `ORDER BY` / `LIMIT` 放每个子查询内 → 改放整个集合操作后
- ❌ 列数不匹配 → 改补齐(NULL 占位或重写 SQL)

### §6

- ❌ `SELECT *` + 集合操作 → explicit columns(详 [ch09 §2](ch09-antipatterns.md))
- ❌ 列类型严重不兼容 → 改 cast 统一类型

## Code Examples

### §1 UNION / UNION ALL

```sql
-- UNION 合并并去重
SELECT user_id FROM orders WHERE status = 'completed'
UNION
SELECT user_id FROM refunds WHERE status = 'processed';
-- 所有"完成订单"或"已处理退款"的用户,重复 user_id 只保留一份

-- UNION ALL 保留重复(性能更好)
SELECT user_id FROM orders WHERE status = 'completed'
UNION ALL
SELECT user_id FROM refunds WHERE status = 'processed';
-- 含重复,用于"统计总数"等场景

-- UNION ALL + DISTINCT(可读性 + 性能兼顾)
SELECT DISTINCT user_id FROM (
  SELECT user_id FROM orders WHERE status = 'completed'
  UNION ALL
  SELECT user_id FROM refunds WHERE status = 'processed'
) sub;
-- 先合并(无去重开销)再去重,planner 可能优化
```

### §2 INTERSECT

```sql
-- INTERSECT:两表共有用户
SELECT user_id FROM orders WHERE created_at > NOW() - INTERVAL '30 days'
INTERSECT
SELECT user_id FROM logins WHERE created_at > NOW() - INTERVAL '30 days';
-- 同时有订单和登录的活跃用户

-- INTERSECT ALL:保留重复
SELECT product_id FROM inventory WHERE warehouse = 'A'
INTERSECT ALL
SELECT product_id FROM inventory WHERE warehouse = 'B';
-- A 和 B 仓库共有产品(可能有多个 product_id 重复)

-- INTERSECT vs INNER JOIN 对比
-- INTERSECT:整行匹配,所有列必须相同
SELECT user_id FROM table_a
INTERSECT
SELECT user_id FROM table_b;

-- INNER JOIN:列级匹配,只要 ON 条件列匹配
SELECT DISTINCT a.user_id FROM table_a a
INNER JOIN table_b b ON b.user_id = a.user_id;
```

### §3 EXCEPT

```sql
-- EXCEPT:左表有右表无
SELECT user_id FROM all_users
EXCEPT
SELECT user_id FROM deleted_users;
-- 活跃用户 = 所有用户 - 已删除用户

-- EXCEPT 顺序敏感
SELECT user_id FROM deleted_users
EXCEPT
SELECT user_id FROM all_users;
-- = 空(已删除用户 ⊆ 所有用户)

-- 反向场景:找出只在 table_b 不在 table_a 的
SELECT user_id FROM table_b
EXCEPT
SELECT user_id FROM table_a;
```

### §4 集合操作与 JOIN 转换

```sql
-- INTERSECT → INNER JOIN + DISTINCT
-- 集合写法
SELECT user_id FROM active_30d
INTERSECT
SELECT user_id FROM paid_30d;
-- 等价 JOIN 写法
SELECT DISTINCT a.user_id
FROM active_30d a
INNER JOIN paid_30d b ON b.user_id = a.user_id;

-- EXCEPT → LEFT JOIN + IS NULL (anti-join)
-- 集合写法
SELECT user_id FROM all_users
EXCEPT
SELECT user_id FROM blocked_users;
-- 等价 anti-join 写法(详 [ch02 §2](ch02-joins.md))
SELECT a.user_id
FROM all_users a
LEFT JOIN blocked_users b ON b.user_id = a.user_id
WHERE b.user_id IS NULL;

-- 决策:可读性优先选集合操作;需要谓词下推优化选 JOIN
```

### §5 集合操作 + ORDER BY / LIMIT

```sql
-- 顶层 ORDER BY / LIMIT 作用整个结果
(SELECT user_id, created_at FROM orders WHERE status = 'completed'
 UNION
 SELECT user_id, created_at FROM refunds WHERE status = 'processed')
ORDER BY created_at DESC
LIMIT 10;
-- 取最近 10 条事件(订单 + 退款合并)

-- ❌ 子查询内 ORDER BY + LIMIT(只限该子查询)
(SELECT user_id FROM orders WHERE status = 'completed' ORDER BY created_at DESC LIMIT 5
 UNION
 SELECT user_id FROM refunds WHERE status = 'processed' ORDER BY created_at DESC LIMIT 5);
-- LIMIT 5 限每个子查询,合并后可能 10 行,不是"top 5 整体"
```

### §6 集合操作反模式 + 修法

```sql
-- ❌ 列数不匹配
SELECT user_id, amount FROM orders
UNION
SELECT user_id FROM refunds;
-- ERROR: each UNION query must have the same number of columns

-- ✅ 补齐 NULL
SELECT user_id, amount FROM orders
UNION
SELECT user_id, NULL FROM refunds;

-- ❌ 列类型严重不兼容
SELECT '1' AS x UNION SELECT 2 AS x;
-- ERROR: UNION types text and integer cannot be matched

-- ✅ 显式 cast
SELECT '1'::int AS x UNION SELECT 2 AS x;
-- 统一为 int 类型

-- ❌ SELECT * + 集合操作
SELECT * FROM orders_2025
UNION
SELECT * FROM orders_2026;
-- 列变化时 silently 改语义

-- ✅ explicit columns
SELECT id, user_id, amount, created_at FROM orders_2025
UNION
SELECT id, user_id, amount, created_at FROM orders_2026;

-- ✅ 或用 UNION ALL 包装 view
CREATE VIEW orders_all AS
  SELECT id, user_id, amount, created_at FROM orders_2025
  UNION ALL
  SELECT id, user_id, amount, created_at FROM orders_2026;

## Reference Tables

### §1 UNION 决策表

| 场景 | 选 | 原因 |
|---|---|---|
| 必须去重 | `UNION` | 自动去重 |
| 能容忍重复 + 性能优先 | `UNION ALL` | 无去重开销 |
| 数据量大 + 必须去重 | `UNION ALL` + 外部 `DISTINCT` | 可控去重范围 |

### §2 INTERSECT vs INNER JOIN 决策

| 场景 | 选 | 原因 |
|---|---|---|
| 整行匹配 + 列数少 | `INTERSECT` | 可读性高 |
| 列级 ON 条件 | `INNER JOIN + DISTINCT` | 灵活 |
| 需谓词下推优化 | `INNER JOIN + DISTINCT` | planner 可优化 |

### §3 EXCEPT 决策表

| 场景 | 选 |
|---|---|
| 找左表无右表有(顺序敏感) | `A EXCEPT B` |
| 反向 | `B EXCEPT A` |
| 大数据 + 性能 | `LEFT JOIN + IS NULL` (anti-join) |

### §4 集合 vs JOIN 转换

| 集合操作 | JOIN 等价 | 备注 |
|---|---|---|
| `A INTERSECT B` | `SELECT DISTINCT a.* FROM A a INNER JOIN B b ON ...` | 列匹配时 |
| `A EXCEPT B` | `SELECT a.* FROM A a LEFT JOIN B b ON ... WHERE b.id IS NULL` | anti-join |
| `A UNION B` | 无直接 JOIN 等价 | 必须集合操作 |

### §5 集合操作 + ORDER BY/LIMIT

| 写法 | 作用范围 |
|---|---|
| 顶层 `ORDER BY ... LIMIT N` | 整个集合操作结果 |
| 子查询内 `ORDER BY ... LIMIT N` | 仅该子查询(子查询为顶层) |
| 列数 / 类型不匹配 | 报 syntax / type error |

### §6 集合操作反模式决策表

| 反模式 | 替代 |
|---|---|
| 能用 `UNION ALL` 用 `UNION` | `UNION ALL` + 外部 `DISTINCT` |
| INTERSECT 重复 `INNER JOIN + DISTINCT` | 看场景,可读性 vs 灵活性 |
| EXCEPT 顺序错 | 明确 `A EXCEPT B` 语义 |
| 列数不匹配 | 补 `NULL` 占位 |
| 列类型不兼容 | 显式 `::int` cast |
| `SELECT *` + 集合操作 | explicit columns(详 [ch09 §2](ch09-antipatterns.md)) |

## Key Takeaways

1. **集合操作是行级扩展,JOIN 是列级扩展**:UNION 加行,JOIN 加列;场景能等价但语义不同(详 §4)
2. **UNION 去重 / UNION ALL 保留**:能容忍重复用 `UNION ALL` 性能更好,大数据 + 必须去重用 `UNION ALL` + 外部 `DISTINCT` 控制范围
3. **INTERSECT = 集合交集**:两表共有行,自动去重;`INTERSECT ALL` 保留重复
4. **EXCEPT = 集合差集**:左表有右表无,顺序敏感;`A EXCEPT B` ≠ `B EXCEPT A`
5. **列数 + 类型必须匹配**:列数不匹配报 syntax error,类型不兼容报 type error;`NULL` 占位补齐,显式 cast 统一类型
6. **ORDER BY / LIMIT 放整个集合操作最后**:`(A UNION B) ORDER BY col LIMIT N`;子查询内 `LIMIT` 只限该子查询
7. **INTERSECT → INNER JOIN + DISTINCT**;**EXCEPT → LEFT JOIN + IS NULL**(anti-join,详 [ch02 §2](ch02-joins.md))
8. **`SELECT *` + 集合操作**:列变化 silently 改语义,改 explicit columns(详 [ch09 §2](ch09-antipatterns.md))
9. **集合操作可读性高但失去谓词下推**:可读优先集合;优化优先 JOIN
10. **`UNION ALL` 包装 view 是常见模式**:`CREATE VIEW AS A UNION ALL B`,整合多源数据为单视图

## Connects To

- **sql-skill ch02**:JOIN 7 种(EXCEPT 转换 LEFT JOIN + IS NULL 详 [ch02 §2](ch02-joins.md);JOIN 是列级扩展)
- **sql-skill ch05**:聚合 / GROUP BY(INTERSECT 与 `INNER JOIN + DISTINCT` 区分;详 [ch05 §1](ch05-aggregates.md))
- **sql-skill ch09**:反模式综合(`SELECT *` + 集合操作详 [ch09 §2](ch09-antipatterns.md);列歧义详 [ch09 §6](ch09-antipatterns.md))
- **evidence-skill ch05**:中文 schema 业务侧雷区(集合操作中 `ds` / `shop_name` 假名)
```