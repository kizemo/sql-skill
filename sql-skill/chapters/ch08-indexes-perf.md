# Chapter 8: SQL 索引与性能优化 — PostgreSQL 通用视角

## Core Idea

PostgreSQL 索引是 query planner 的隐形指挥棒:B-Tree 默认 + GIN/BRIN/Hash 走数据类型;WHERE/JOIN/ORDER BY/GROUP BY 上的函数 / 类型转换 / 隐式 cast 都可能让 Seq Scan 顶替 Index Scan;**EXPLAIN ANALYZE 是唯一真相**。本章专注 PG 通用索引与性能优化,**BI 场景适配**(Core 28 page + nginx immutable + pgbouncer)归 [evidence-skill ch14](../../evidence/evidence-skill/chapters/ch14-performance.md)。

## Frameworks Introduced

### §1 索引结构(4 条)

- **B-Tree 是 PG 默认索引** — 等值 + 范围 + 前缀匹配都适用;`CREATE INDEX` 不指定 type 时默认 B-Tree。深度 4-5 可覆盖百万级记录(luke `the-tree`)。
- **Hash 索引只支持等值** — PG 10+ WAL-logged crash-safe,但 B-Tree 已能覆盖等值,Hash 几乎无优势,实际场景极少用。
- **GIN (Generalized Inverted Index) 用于多值列** — JSONB / array / tsvector,倒排索引,`@>` / `?` / 全文检索都走 GIN。
- **BRIN (Block Range Index) 用于大表时序范围** — 空间仅 B-Tree 的 0.1-1%,适合 append-only 时序表(物理顺序与逻辑顺序一致时)。

### §2 WHERE 子句索引(5 条)

- **WHERE 上函数破坏索引**:`WHERE UPPER(col) = 'X'` 走 Seq Scan;要 `WHERE col = LOWER('X')` 或建表达式索引 `CREATE INDEX ... ON t (LOWER(col))`。
- **隐式类型转换破坏索引**:`WHERE int_col = '123'` (string literal) → PG 强制 cast → Seq Scan;改 `WHERE int_col = 123`。
- **`IS NULL` / `IS NOT NULL` 在 B-Tree 上走索引**,但 PG 默认 NULL 不入索引,需 `CREATE INDEX ... WHERE col IS NOT NULL` partial index 才生效。
- **`LIKE 'prefix%'` 走 B-Tree**;`LIKE '%suffix'` / `LIKE '%mid%'` 不走,需 pg_trgm GIN 或全文检索。
- **范围查询(BETWEEN / `>` `<`)走索引**,但要求 ORDER BY 列与范围列一致或 covering index。

### §3 JOIN 算法(3 条)

- **Nested Loop**:适合"小数据集 + 索引"场景,outer 1万行 × inner 索引查 1 行 → 总 1万次 index lookup。N+1 问题根因。
- **Hash Join**:适合大表等值 JOIN,PG 8.3+ 默认选项;内存建 hash 表,内存不足 spill 到磁盘 temp file。
- **Sort Merge Join**:两边都已排序的场景;多见于显式 ORDER BY 后 JOIN 或索引已排序列的 JOIN。

### §4 排序与分组索引(3 条)

- **ORDER BY 列建索引可避免 sort**:PG 看到索引顺序就直接顺序扫,无需 Sort 算子。
- **NULLS LAST / NULLS FIRST 必须与索引排序一致**才能走索引,默认 NULLS LAST(ASC) / NULLS FIRST(DESC)。
- **GROUP BY 列建索引可避免 HashAggregate**:planner 改用 Index scan + GroupAggregate,内存占用大幅下降。

### §5 分页与窗口函数索引(3 条)

- **Top-N (`ORDER BY ... LIMIT N`) 走索引** — 扫 N 条索引 entry 就停,O(N) 而非 O(M)。
- **大 OFFSET (`OFFSET 100000 LIMIT 20`) 禁用** — PG 仍扫前 100020 条再丢弃;改 keyset pagination(`WHERE id > last_id LIMIT N`)。
- **窗口函数 `OVER (PARTITION BY ... ORDER BY ...)` 不直接用索引**,但 `PARTITION BY` + `ORDER BY` 都建索引可让 planner 选 Index Scan 替代 Sort。

### §6 EXPLAIN 与执行计划(3 条)

- **EXPLAIN 显示 planner 估算成本**(cost / rows / width),**EXPLAIN ANALYZE 真正执行**并对比真实 vs 估算。
- **4 大核心算子必认**:`Seq Scan`(全表扫) / `Index Scan`(索引点查) / `Bitmap Index Scan + Bitmap Heap Scan`(索引多行 + 回表批量) / `Hash Join` / `Nested Loop` / `Sort`。
- **pg_stat_statements 查慢 query top-N**:`SELECT query, calls, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 20` — 一次看到所有 hot path。

## Key Concepts

### §1 索引结构

- **B-Tree (Balanced Tree)**:平衡搜索树,PG 默认,深度对数增长,深度 4-5 覆盖百万级记录。叶子节点通过 doubly linked list 串联,支持顺序扫描
- **Hash Index**:只支持等值 `=`,PG 10+ WAL-logged crash-safe
- **GIN (Generalized Inverted Index)**:多值倒排索引,JSONB `?` / `@>` / array `@>` / tsvector `@@` 都走 GIN
- **BRIN (Block Range Index)**:块范围摘要,记录每块 min/max,适合 append-only 时序大表
- **GiST**:通用搜索树,几何 / 全文 / 范围类型
- **`USING <method>`**:`CREATE INDEX ... USING btree|hash|gin|brin|gist`
- **`INCLUDE (col1, col2)`**:PG 11+,B-Tree 索引可附加非键列形成 covering index,免回表

### §2 WHERE 子句索引

- **`operator class`**:`CREATE INDEX ... USING btree (col varchar_pattern_ops)` 让 LIKE 前缀匹配不走 collation 转换
- **表达式索引**:`CREATE INDEX ... ON t (LOWER(col))`,WHERE `LOWER(col) = X` 才走索引
- **partial index**:`CREATE INDEX ... WHERE col IS NOT NULL`,只为满足条件的行建索引,体积小
- **隐式类型转换**:PG 严格类型系统,`int_col = '123'` 让 PG cast `'123'` 为 int,如该列未建索引且 cast 不一致 → Seq Scan
- **LIKE 模式**:前缀通配 `'abc%'` 走索引;前后通配 `'%abc'` 或 `'%abc%'` 不走

### §3 JOIN 算法

- **Nested Loop**:outer 顺序扫,每行在 inner 表用索引查 1 行
- **Hash Join**:outer 内存建 hash,inner 用 hash probe 找匹配
- **Sort Merge Join**:两边先 sort,再 merge 配对
- **N+1 problem**:应用层 for 循环 N 次单条 query,应改 1 次批量 query + JOIN

### §4 排序与分组

- **Index Scan vs Sort 算子**:有索引 → planner 选 Index Scan,无 → Sort 算子 + 内存 / 磁盘排序
- **GroupAggregate vs HashAggregate**:Index + GroupAggregate 用流式聚合;无 → HashAggregate 内存聚合或 spill
- **`NULLS FIRST` / `NULLS LAST`**:ORDER BY 子句,默认 PG 是 `NULLS LAST`(ASC) / `NULLS FIRST`(DESC),与 PG 默认 B-Tree 行为一致

### §5 分页与窗口

- **Top-N optimization**:planner 遇到 `ORDER BY ... LIMIT N` 且 N 远小于表大小时,自动改 plan 提前终止扫描
- **keyset pagination**:`WHERE (created_at, id) > (last_ts, last_id) ORDER BY created_at, id LIMIT N`,比 OFFSET 快几个数量级
- **`OVER (PARTITION BY ...)`**:窗口函数,默认 planner 用 Sort + WindowAgg;PARTITION BY 列有索引可避免 Sort

### §6 EXPLAIN 与执行计划

- **cost**:planner 估算成本,单位 abstract;`0.00..100.00` 表示 startup cost..total cost
- **rows**:planner 估算返回行数;真实行数从 EXPLAIN ANALYZE `actual rows=...` 看
- **width**:估算每行字节数
- **Seq Scan / Index Scan / Index Only Scan / Bitmap Heap Scan**:4 大表扫算子
- **Hash Join / Nested Loop / Merge Join**:3 大 JOIN 算子
- **Sort / GroupAggregate / HashAggregate**:排序与聚合算子
- **pg_stat_statements**:PG extension,记录每条 query 的统计信息(calls / total_exec_time / mean_exec_time)

## Mental Models

### §1 索引结构

- **索引 = 数据的有序副本**:索引按 key 排序,表本身堆存储无序。索引让 planner 用"二分查找"(B-Tree 路径)替代"全表扫"。
- **索引选择是 cost-based**:PG planner 根据统计信息 + I/O cost 估算选择 plan,**有索引不一定用**(小表 Seq Scan 更快)。
- **多值列不能用 B-Tree**:`[1,2,3]` / `{"a":1}` 这类数据无法表达"一个 key 对应多 value"的关系,需 GIN 倒排索引。

### §2 WHERE 子句索引

- **索引列上的函数让索引"看不见"**:`UPPER(col)` 计算后已不是索引列本身,planner 看到的是表达式结果。要么建表达式索引,要么改写法。
- **类型一致性是索引生效前提**:`int_col = '123'` 让 PG 把 string cast 到 int,这个 cast 不一定与索引存储一致(字符集 / collation / 精度都可能影响)。

### §3 JOIN 算法

- **小数据 + 索引 = Nested Loop,大数据 + 等值 = Hash Join,大表已排序 = Sort Merge** — 三种 JOIN 各有最佳场景。
- **JOIN 顺序由 planner 决定**:`FROM a JOIN b JOIN c` 实际执行顺序可能不同,planner 按 cost 选最优;显式控制用 `JOIN_ORDER` hint(PG 不支持,只能重写 SQL)。

### §4 排序与分组

- **索引顺序就是 query 顺序**:索引 `ORDER BY col ASC` 就能避免 sort,`DESC` 索引才能避免 DESC sort。
- **GROUP BY 索引要前置列匹配**:`GROUP BY a, b` 要建 `(a, b)` 索引,`(b, a)` 索引不能避免 HashAggregate。

### §5 分页与窗口

- **OFFSET 是反模式**:`OFFSET N` 让 PG 扫前 N+limit 行再丢弃,大 N 时 I/O 巨大。
- **窗口函数不是真"分组"**:`OVER (PARTITION BY ...)` 保留所有行,只是计算每行所属分组的聚合;PARTITION BY 列有索引可避免 Sort。

### §6 EXPLAIN

- **EXPLAIN 是估算,EXPLAIN ANALYZE 是真相**:估算与真实可能差几个数量级(尤其统计信息过期)。
- **rows mismatch 是性能问题的第一信号**:估算 rows=10 实际 rows=10000 → 统计信息过期,跑 `ANALYZE table_name`。
- **慢 query 的 80% 问题在 20% plan**:`pg_stat_statements` 找 top-N 慢 query,逐条 EXPLAIN ANALYZE 看 plan。

## Anti-patterns

### §1

- ❌ 大表时序列用 B-Tree → BRIN 空间省 99%,查询性能可接受
- ❌ JSONB 字段不建 GIN → 全表扫描(SELECT jsonb_col->>'key' = 'X' 必扫)
- ❌ 默认用 Hash 索引 → B-Tree 已能覆盖等值,Hash 几乎无优势
- ❌ 高频 update 列建 GIN → update cost 高,适合读多写少
- ❌ 索引列存长字符串 → B-Tree 索引 entry 大,IO 浪费

### §2

- ❌ WHERE 上函数 → 表达式索引或改写法(`WHERE UPPER(col) = X` → `WHERE col = LOWER(X)` 或表达式索引)
- ❌ 不指定范围时间 → 必加 WHERE 时间窗,否则全表扫
- ❌ `WHERE int_col = '123'` (string literal) → 隐式 cast 破坏索引
- ❌ `LIKE '%abc%'` 中间通配 → 不走 B-Tree,改 pg_trgm GIN
- ❌ 不跑 ANALYZE → 统计信息过期,planner 选错 plan

### §3

- ❌ 应用层 N+1 for 循环 → 改单次批量 query + JOIN
- ❌ 大表 JOIN 不分析数据量分布 → Nested Loop 误用导致指数级 lookup
- ❌ JOIN 顺序不写 explicit → 让 planner 选,但 EXPLAIN 验证 plan 合理
- ❌ 不建索引就 JOIN → Nested Loop 必须有索引

### §4

- ❌ ORDER BY 不建索引 → Sort 算子耗内存 / spill 磁盘
- ❌ GROUP BY 列不建索引 → HashAggregate 内存 spike
- ❌ NULLS LAST/FIRST 与索引顺序不一致 → 仍要走 Sort

### §5

- ❌ `OFFSET 100000 LIMIT 20` → keyset pagination (`WHERE id > last_id`)
- ❌ Top-N 不建 ORDER BY 列索引 → O(M) 扫表
- ❌ 窗口函数 PARTITION BY 列不建索引 → Sort 算子

### §6

- ❌ 只看 EXPLAIN 不看 EXPLAIN ANALYZE → 估算 ≠ 真实
- ❌ 不查 pg_stat_statements → 漏掉真慢 query
- ❌ rows mismatch 不 ANALYZE → 统计信息过期,plan 错
- ❌ 监控只看 pg_stat_user_tables.seq_scan / idx_scan → 不看具体 query

## Code Examples

### §1 B-Tree 默认索引 + GIN + BRIN

```sql
-- B-Tree 默认(等值 + 范围 + 前缀匹配都走)
CREATE INDEX idx_orders_date ON orders USING btree (order_date);
SELECT * FROM orders WHERE order_date BETWEEN '2026-01-01' AND '2026-12-31';

-- JSONB 字段 GIN(@> 操作符走索引)
CREATE INDEX idx_orders_meta ON orders USING gin (meta jsonb_path_ops);
SELECT * FROM orders WHERE meta @> '{"channel": "taobao"}';

-- BRIN 时序大表(1 亿行,B-Tree 2GB,BRIN 20MB)
CREATE INDEX idx_events_ts_brin ON events USING brin (event_time);
SELECT count(*) FROM events WHERE event_time BETWEEN '2026-01-01' AND '2026-01-31';
-- 范围查询仍走 BRIN(扫块范围摘要,再回表过滤)
```

### §2 WHERE 索引 + 表达式索引 + partial index

```sql
-- 函数破坏索引 → 表达式索引救场
CREATE INDEX idx_users_name_lower ON users (LOWER(name));
SELECT * FROM users WHERE LOWER(name) = 'alice';
-- 现在走索引,否则 Seq Scan

-- 隐式 cast 破坏索引 → 类型一致即可
CREATE INDEX idx_orders_qty ON orders (qty);
SELECT * FROM orders WHERE qty = 100;  -- 整数,走索引
SELECT * FROM orders WHERE qty = '100';  -- 字符串 → cast → Seq Scan

-- partial index (90% 行 col NOT NULL)
CREATE INDEX idx_orders_deleted_at_partial ON orders (deleted_at) WHERE deleted_at IS NOT NULL;
-- 索引体积仅为 10% 表大小(90% 行 deleted_at IS NULL 被排除)

-- LIKE 前缀走索引
CREATE INDEX idx_users_email ON users (email);
SELECT * FROM users WHERE email LIKE 'alice%';  -- 走索引
SELECT * FROM users WHERE email LIKE '%alice%'; -- 不走索引
```

### §3 JOIN 算法对比

```sql
-- Nested Loop:小数据集 + 索引(典型 N+1 反例)
-- SELECT * FROM orders o WHERE o.user_id = X (走 user_id 索引)
-- vs 应用层 for user in users: SELECT * FROM orders WHERE user_id = user.id
-- 应用层 N+1 必改为 1 次 JOIN:
SELECT u.id, u.name, o.*
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.created_at > NOW() - INTERVAL '7 days';

-- Hash Join:大表等值 JOIN(无显式语法,planner 选)
EXPLAIN ANALYZE
SELECT u.name, SUM(o.amount)
FROM users u
JOIN orders o ON o.user_id = u.id
GROUP BY u.name;
-- 两边都大 → planner 选 Hash Join
```

### §4 排序与分组索引

```sql
-- ORDER BY 列索引(免 Sort)
CREATE INDEX idx_orders_created_at ON orders (created_at DESC);
SELECT * FROM orders ORDER BY created_at DESC LIMIT 10;
-- EXPLAIN:Index Scan Backward using idx_orders_created_at(无 Sort)

-- GROUP BY 列索引(免 HashAggregate)
CREATE INDEX idx_orders_user_id ON orders (user_id);
SELECT user_id, count(*) FROM orders GROUP BY user_id;
-- EXPLAIN:Index Scan + GroupAggregate(无 HashAggregate)
```

### §5 Top-N + keyset pagination + 窗口函数

```sql
-- Top-N 走索引
CREATE INDEX idx_orders_amount ON orders (amount DESC);
SELECT * FROM orders ORDER BY amount DESC LIMIT 10;
-- EXPLAIN:Index Scan,扫 10 条即停

-- OFFSET 反模式 vs keyset pagination
-- ❌ OFFSET 100000 LIMIT 20 → 扫前 100020 行
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 100000;

-- ✅ keyset pagination → 扫 20 行
SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20;

-- 窗口函数 PARTITION BY 索引
CREATE INDEX idx_orders_user_amount ON orders (user_id, amount DESC);
SELECT user_id, amount, rank() OVER (PARTITION BY user_id ORDER BY amount DESC)
FROM orders;
-- EXPLAIN:Index Scan + WindowAgg(无 Sort)
```

### §6 EXPLAIN ANALYZE 完整解读

```sql
EXPLAIN ANALYZE
SELECT u.name, count(*) AS order_count
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE u.created_at > NOW() - INTERVAL '30 days'
GROUP BY u.name
ORDER BY order_count DESC
LIMIT 100;
```

典型输出(luke `sql-explain-plan` + pg-docs `performance-tips`):

```
Limit  (cost=... rows=100) (actual time=12.345..12.350 rows=100 loops=1)
  ->  Sort  (cost=... rows=...) (actual time=12.300..12.340 rows=100 loops=1)
        Sort Key: (count(*)) DESC
        ->  HashAggregate  (cost=... rows=...) (actual time=10.000..12.000 rows=5000 loops=1)
              Group Key: u.name
              ->  Hash Join  (cost=... rows=...) (actual time=2.000..8.000 rows=50000 loops=1)
                    Hash Cond: (o.user_id = u.id)
                    ->  Seq Scan on orders o  (cost=... rows=...) (actual time=0.100..5.000 rows=200000 loops=1)
                          Filter: ...
                    ->  Hash  (cost=... rows=...) (actual time=1.500..1.500 rows=10000 loops=1)
                          ->  Index Scan on users u  (cost=... rows=...) (actual time=0.050..1.000 rows=10000 loops=1)
                                Index Cond: (created_at > ...)
Planning Time: 0.5 ms
Execution Time: 12.5 ms
```

**4 大必读算子**:

| 算子 | 含义 | 何时该出现 |
|---|---|---|
| `Seq Scan` | 全表扫 | 小表(< 10000 行)或无索引可用 |
| `Index Scan` | 索引点查 + 回表 | 索引列过滤 + 少量结果 |
| `Index Only Scan` | 索引覆盖,免回表 | INCLUDE covering index + heap fetch 可省 |
| `Bitmap Heap Scan` | 索引多行批量 + 回表 | WHERE 返回多行但不需 ORDER BY 索引顺序 |
| `Hash Join` | 大表等值 JOIN | 两边都大 + 等值条件 |
| `Nested Loop` | 小表 JOIN | outer 小 + inner 有索引 |
| `Sort` | 排序 | 无 ORDER BY 列索引 |
| `HashAggregate` | 哈希聚合 | 无 GROUP BY 列索引 |

**rows mismatch 是性能第一信号**:`(cost=... rows=100) (actual rows=10000)` → 跑 `ANALYZE users;` 更新统计信息。

## Reference Tables

### §1 索引类型决策表

| 场景 | 推荐索引 | 原因 |
|---|---|---|
| 等值 / 范围 / 前缀匹配 | B-Tree | PG 默认,通用 |
| 仅等值 | Hash(几乎不用) | B-Tree 已能覆盖 |
| JSONB / array / tsvector | GIN | 倒排索引,多值匹配 |
| 时序大表(append-only) | BRIN | 空间省 99%,范围扫 |
| 几何 / 全文 / 范围类型 | GiST | R-tree 等 |
| 复合条件 | partial index | 只索引 subset,体积小 |
| 避免回表 | B-Tree INCLUDE (col1, col2) | covering index,Index Only Scan |

### §2 WHERE 子句索引决策表

| WHERE 写法 | 是否走索引 | 修法 |
|---|---|---|
| `col = X` | ✓ | — |
| `col LIKE 'abc%'` | ✓ | — |
| `UPPER(col) = X` | ❌ | 表达式索引 `LOWER(col)` 或 `col = LOWER(X)` |
| `col BETWEEN X AND Y` | ✓ | — |
| `col IS NULL` | ❌(默认 NULL 不入索引) | partial index `WHERE col IS NOT NULL` 或 `INCLUDE NULL` |
| `int_col = '123'` | ❌ | 改 `int_col = 123` |
| `col LIKE '%abc'` | ❌ | 改 pg_trgm GIN |
| `col IN (subquery)` | ✓ (如子查询结果少) | 子查询结果大 → Hash Join |

### §3 JOIN 算法决策表

| 场景 | 算法 | 原因 |
|---|---|---|
| outer 小 + inner 索引 | Nested Loop | 每次 lookup 1 行 |
| 两边都大 + 等值 | Hash Join | 内存 hash |
| 两边都已排序 + 非等值 | Sort Merge Join | merge 两边排序流 |
| 不等值 (`<` `>` `BETWEEN`) | Nested Loop 或 Sort Merge | Hash Join 只支持等值 |

### §4 排序与分组决策表

| ORDER BY 列是否有索引 | planner 选择 |
|---|---|
| 有,且顺序一致 | Index Scan(无 Sort 算子) |
| 有,但顺序不一致 | Index Scan + Sort(部分优化) |
| 无 | Sort 算子(内存 / spill 磁盘) |

### §5 分页决策表

| 模式 | 性能 | 适用 |
|---|---|---|
| `ORDER BY idx LIMIT N` | O(N) | 第一页 / 小 N |
| `OFFSET M LIMIT N` | O(M+N) | ❌ 大 M 禁用 |
| `WHERE id > last_id LIMIT N` | O(N) | ✅ 大数据量分页 |
| cursor / keyset pagination | O(1) per page | ✅ 现代应用分页 |

### §6 EXPLAIN 速查表

| 看什么 | 找什么 | 修法 |
|---|---|---|
| `actual rows` vs `rows` | mismatch 几倍 | `ANALYZE table_name` |
| `actual time` | 慢算子 | 加索引 / 改 SQL |
| `Seq Scan` on big table | 全表扫 | 加索引 / partial index |
| `Sort` on memory | 内存排序 | ORDER BY 列建索引 |
| `Hash Join` spill to disk | 内存不足 | 增加 `work_mem` / 改 Nested Loop |
| `Bitmap Heap Scan` 回表多 | 索引不够覆盖 | INCLUDE covering index |

## Key Takeaways

1. **B-Tree 默认**,等值/范围/前缀都走;GIN 多值倒排;BRIN 时序省空间;Hash 几乎不用
2. **WHERE 上函数破坏索引**,改表达式索引或反函数(`UPPER(col)=X` → `col=LOWER(X)`)
3. **隐式类型 cast 破坏索引**(`int_col='123'` 走 Seq Scan),改类型一致
4. **LIKE 'prefix%' 走索引**,'%mid%' 不走;需 pg_trgm GIN
5. **Nested Loop** 适合小数据 + 索引,**Hash Join** 适合大表等值,**Sort Merge** 适合已排序
6. **ORDER BY 列建索引免 Sort**;**GROUP BY 列建索引免 HashAggregate**
7. **OFFSET 大值禁用**,改 keyset pagination(`WHERE id > last_id`)
8. **EXPLAIN ANALYZE 是唯一真相**;估算 rows 与 actual rows mismatch → `ANALYZE table_name`
9. **pg_stat_statements 查 top-N 慢 query**,逐条 EXPLAIN ANALYZE 看 plan
10. **BI 场景适配**(Core 28 page + nginx immutable + pgbouncer)归 [evidence-skill ch14](../../evidence/evidence-skill/chapters/ch14-performance.md),**不重复**

## Connects To

- **sql-skill ch01**:SQL 语法铁律(`SELECT *` 反模式在本章 Anti-patterns §1)
- **sql-skill ch07**:PG 特有(JSONB GIN + 中文 schema 中文列索引)与 §1 GIN 决策互补
- **sql-skill ch09**:反模式综合(本章 Anti-patterns 与 ch09 协同)
- **evidence-skill ch05**:SQL 中文列双引号(`"店铺"` `"订单日期"`)—— 中文列建索引时同样要双引号
- **evidence-skill ch07**:postgres_fdw 跨 DB JOIN 性能差,高频 JOIN 预聚合本地表
- **evidence-skill ch14**:BI 场景(Core 28 page + FDW 性能 + nginx `/_app/immutable/` immutable + pgbouncer session-mode)
