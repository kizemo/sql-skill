# Chapter 1: SQL 语法铁律 — 通用 PostgreSQL 视角

## Core Idea

SQL 语法铁律三层:① **执行顺序 ≠ 书写顺序**(FROM→WHERE→GROUP BY→HAVING→SELECT→DISTINCT→ORDER BY→LIMIT);② **表达式与别名作用域**(列别名只能在 SELECT 后用,WHERE/GROUP BY 不能引用);③ **NULL 是三值逻辑**(`NULL = NULL` 是 NULL 不是 TRUE);④ **风格统一**(关键字大写 / 表名 snake_case / 缩进 2 空格)。**中文列名双引号 / `ds` `shop_name` 假名**等业务侧雷区归 [evidence-skill ch05](../../evidence/evidence-skill/chapters/ch05-sql-antipatterns.md),本章只讲通用语法。

## Frameworks Introduced

### §1 SQL 执行顺序(1 条铁律)

- **真实执行顺序**:`FROM` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `DISTINCT` → `ORDER BY` → `LIMIT` / `OFFSET`。
  - 含义:WHERE 不能用 SELECT 定义的列别名(别名还没生成);GROUP BY 在 WHERE 后(过滤后聚合);ORDER BY 在 SELECT 后(可引用别名);LIMIT 最后。

### §2 表达式与别名(3 条)

- **列别名仅在 SELECT 之后可用**:`SELECT col + 1 AS new_col FROM t WHERE new_col > 5` ❌ — 报 `column "new_col" does not exist`;改 `WHERE col + 1 > 5` 或子查询。
- **ORDER BY 可引用列别名**:`SELECT col + 1 AS new_col FROM t ORDER BY new_col` ✓ — 因为 ORDER BY 在 SELECT 之后。
- **类型转换 cast**:`'123'::int` / `CAST('123' AS int)` / `int '123'` — PG 三种 cast 语法等价,推荐 `::` 简洁。

### §3 NULL 三值逻辑(3 条)

- **`NULL = NULL` 是 NULL 不是 TRUE**:WHERE `col = NULL` 永远 0 行;必须用 `WHERE col IS NULL` 或 `WHERE col IS NOT NULL`。
- **`COALESCE(a, b, c)` 取第一个非 NULL**:优于 `CASE WHEN a IS NOT NULL THEN a WHEN b IS NOT NULL THEN b ELSE c END`,可读性强。
- **`NULLIF(a, b)`:a=b 时返回 NULL,否则返回 a**:用于"等于某值时返回空"的场景,如 `NULLIF(col, '')` 把空字符串归 NULL。

### §4 风格铁律(2 条)

- **关键字大写,表名/列名 snake_case 小写**:`SELECT col_a, col_b FROM my_table WHERE col_c = 'X'` — 与 [Matt Mazur sql-style-guide](https://github.com/mattm/sql-style-guide) 对齐。
- **缩进 2 空格,逗号前空格后无空格,别名 `AS` 显式**:`SELECT col_a, col_b AS alias FROM my_table` — 缩进 + 显式 AS 让代码 review 容易。

## Key Concepts

### §1

- **FROM 子句**:决定数据源(表 / 子查询 / CTE / VALUES),最先执行;**CROSS JOIN / INNER JOIN / LEFT JOIN 等在 FROM 阶段合并**
- **WHERE 子句**:行级过滤,WHERE 阶段还没 SELECT 别名
- **GROUP BY**:聚合前的分组,WHERE 过滤后
- **HAVING**:聚合后的过滤(`COUNT(*) > 5` 这种要在聚合结果上过滤)
- **SELECT**:列投影 + 列别名生成(此时别名才出现)
- **DISTINCT**:SELECT 后去重
- **ORDER BY**:可引用列别名,排序输出
- **LIMIT / OFFSET**:最后裁剪结果集

### §2

- **列别名 (column alias)**:`SELECT col AS alias FROM ...`,`alias` 只在 SELECT 后可用
- **表别名 (table alias)**:`FROM long_table_name t`,`t` 在整个 query 可用,FROM 阶段就生成
- **`::` cast**:PG 特有,简洁 `col::int` / `col::text`
- **CAST() 函数**:标准 SQL 写法 `CAST(col AS int)`

### §3

- **三值逻辑 (three-valued logic)**:TRUE / FALSE / **NULL**(unknown)
- **`IS NULL` / `IS NOT NULL`**:唯一判断 NULL 的方法
- **`COALESCE(a, b, c, ...)`:variadic,取第一个非 NULL 参数**
- **`NULLIF(a, b)`**:二元,等则 NULL,否则 a
- **`IS DISTINCT FROM` / `IS NOT DISTINCT FROM`**:NULL-safe 等值,`NULL IS DISTINCT FROM NULL` 是 FALSE(等价),适合"col 与某值不等"的 NULL-safe 判断

### §4

- **关键字大写**:`SELECT` / `FROM` / `WHERE` / `JOIN` / `ON` / `GROUP BY` / `ORDER BY` / `LIMIT` 大写
- **snake_case**:表名 / 列名 / 别名用 `my_table` / `col_a` 而非 `myTable` / `colA`
- **显式 AS**:别名 `AS alias` 显式,不要省略
- **2 空格缩进**:子查询嵌套 2 空格递进,不要 tab

## Mental Models

### §1

- **SQL 是声明式**:你描述"要什么",DB 决定"怎么做";执行顺序是 DB 内部细节,写 SQL 时按书写顺序即可。
- **别名作用域**:表别名全局有效(从 FROM 起),列别名局部有效(只在 SELECT 之后);这是踩坑高发区。

### §2

- **别名引用陷阱**:WHERE 想用列别名 → 用子查询包一层(`SELECT * FROM (SELECT col + 1 AS new_col FROM t) sub WHERE new_col > 5`)。
- **类型 cast 的时机**:PG 是严格类型系统,`'123' = 123` 时 PG 自动 cast `'123'` 为 int;但 `int_col = '123'` 这种列在前时 cast 让索引失效(详见 ch08 §2)。

### §3

- **NULL 不是"空"**:它是"未知值",可能是任意值;`NULL = NULL` 不知道两个未知值是否相等 → NULL。
- **`COALESCE` 用于默认值**:聚合时 `SUM(COALESCE(amount, 0))` 把 NULL 当 0 算;非聚合 `COALESCE(col, 'default')` 给默认显示值。

### §4

- **风格是为了 review**:统一风格让 reviewer 5 秒看懂;不一致要花 10 倍精力"解码"。
- **`AS` 显式不省略**:虽然 `SELECT col alias` 也合法,但 `SELECT col AS alias` 一眼看穿;尤其多列时省略 AS 让可读性断崖下跌。

## Anti-patterns

### §1

- ❌ WHERE 引用列别名 → `WHERE new_col > 5`,WHERE 在 SELECT 前,别名未生成;改子查询或表达式复用

### §2

- ❌ 隐式类型转换破坏索引 → `WHERE int_col = '123'`,改 `WHERE int_col = 123`(详见 ch08 §2)
- ❌ 多列逗号后无空格 → `SELECT col_a,col_b,col_c`,可读性差
- ❌ 字符串用双引号 → `"hello world"`,PG 把双引号当 identifier quote,字符串用单引号 `'hello world'`

### §3

- ❌ `WHERE col = NULL` → 永远 0 行,NULL 不等于 NULL;改 `IS NULL`
- ❌ `WHERE col != NULL` → 同上,改 `IS NOT NULL`
- ❌ `IFNULL` / `ISNULL`(MySQL/SQL Server 函数) → PG 用 `COALESCE` / `NULLIF`

### §4

- ❌ 关键字小写混杂 → `select col From t WHERE col = 'x'`,不一致
- ❌ 表名 camelCase → `myTable`,跨 DB 时大小写敏感问题
- ❌ 多列共用 AS(省略) → `SELECT col_a alias_a, col_b alias_b`,易读错

## Code Examples

### §1 执行顺序示例

```sql
-- 8 个子句全演示
SELECT
  user_id,
  count(*) AS order_count  -- 阶段 5:SELECT
FROM
  orders                   -- 阶段 1:FROM
WHERE
  created_at > '2026-01-01'  -- 阶段 2:WHERE
GROUP BY
  user_id                  -- 阶段 3:GROUP BY
HAVING
  count(*) > 5             -- 阶段 4:HAVING
ORDER BY
  order_count DESC         -- 阶段 7:ORDER BY(可引用列别名!)
LIMIT 100;                 -- 阶段 8:LIMIT

-- WHERE 不能引用列别名(陷阱)
SELECT amount + 1 AS new_amount FROM orders WHERE new_amount > 100;
-- ERROR: column "new_amount" does not exist
-- 修法 1:表达式复用 WHERE amount + 1 > 100
-- 修法 2:子查询
SELECT * FROM (SELECT amount + 1 AS new_amount FROM orders) sub WHERE new_amount > 100;
```

### §2 别名与 cast

```sql
-- 表别名(全局可用)
SELECT u.id, u.name FROM users AS u WHERE u.created_at > NOW() - INTERVAL '7 days';

-- 列别名(SELECT 后可用)
SELECT id AS user_id, name AS user_name FROM users ORDER BY user_name; -- ✓ ORDER BY 可引用

-- 类型 cast 三种写法
SELECT '123'::int;           -- :: 简洁(推荐)
SELECT CAST('123' AS int);   -- 标准 SQL
SELECT int '123';            -- 类型前置(不常用)

-- 实际场景:date 不能 SUBSTR(详见 ch08),用 ::text 或 TO_CHAR
SELECT SUBSTR(created_at::text, 1, 7) AS month FROM orders; -- ✓
SELECT SUBSTR(created_at, 1, 7) FROM orders;               -- ✗ date 类型不支持
```

### §3 NULL 三值逻辑

```sql
-- ❌ NULL = NULL
SELECT * FROM users WHERE deleted_at = NULL;
-- 永远 0 行(NULL = NULL 是 NULL,WHERE 把 NULL 当 FALSE)

-- ✓ IS NULL
SELECT * FROM users WHERE deleted_at IS NULL;

-- COALESCE 默认值
SELECT COALESCE(nickname, name, 'anonymous') AS display_name FROM users;

-- NULLIF(等于某值归 NULL)
SELECT NULLIF(status, '') AS status FROM users;  -- 空字符串归 NULL
-- 等价于 CASE WHEN status = '' THEN NULL ELSE status END

-- IS DISTINCT FROM(NULL-safe 等值)
SELECT * FROM users WHERE email IS DISTINCT FROM 'unknown@example.com';
-- email = NULL 时 IS DISTINCT FROM 'unknown@example.com' 是 TRUE(而 != 是 NULL)
```

### §4 风格示例

```sql
-- 推荐风格(对齐 Matt Mazur sql-style-guide)
SELECT
  o.id AS order_id,
  u.name AS user_name,
  SUM(o.amount) AS total_amount
FROM
  orders AS o
  INNER JOIN users AS u ON u.id = o.user_id
WHERE
  o.created_at >= '2026-01-01'
  AND o.status = 'completed'
GROUP BY
  o.id, u.name
HAVING
  SUM(o.amount) > 100
ORDER BY
  total_amount DESC
LIMIT 100;
```

## Reference Tables

### §1 SQL 子句执行顺序速查

| 顺序 | 子句 | 作用 | 别名可用 |
|---|---|---|---|
| 1 | FROM | 数据源 | 表别名 ✓ |
| 2 | WHERE | 行过滤 | 表别名 ✓,列别名 ✗ |
| 3 | GROUP BY | 分组 | 表别名 ✓,列别名 ✗ |
| 4 | HAVING | 聚合后过滤 | 聚合函数别名 ✓ |
| 5 | SELECT | 列投影 + 列别名 | 列别名生成 |
| 6 | DISTINCT | 去重 | 列别名 ✓ |
| 7 | ORDER BY | 排序 | 列别名 ✓ |
| 8 | LIMIT / OFFSET | 裁剪 | 列别名 ✓ |

### §3 NULL 函数速查

| 场景 | 函数 | 等价 |
|---|---|---|
| 取第一个非 NULL | `COALESCE(a, b, c)` | CASE WHEN |
| 等于某值归 NULL | `NULLIF(a, b)` | CASE WHEN |
| 判断 NULL | `col IS NULL` / `IS NOT NULL` | — |
| NULL-safe 等值 | `col IS DISTINCT FROM X` | `col != X OR col IS NULL OR X IS NULL` |

### §4 风格速查

| 元素 | 风格 |
|---|---|
| 关键字 | 大写 |
| 表名 / 列名 | snake_case 小写 |
| 别名 | 显式 `AS` |
| 缩进 | 2 空格 |
| 逗号 | 行尾(列对齐)或行首 |
| 引号 | 字符串单引号,identifier 双引号 |
| 注释 | `-- 单行` / `/* 多行 */` |

## Key Takeaways

1. **执行顺序** = FROM → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT;列别名只在 SELECT 后可用
2. **`NULL = NULL` 是 NULL**,`WHERE col = NULL` 永远 0 行;用 `IS NULL` / `IS NOT NULL`
3. **`COALESCE(a, b)` 取第一个非 NULL**;`NULLIF(a, b)` 等值归 NULL
4. **类型 cast** 用 `col::int` 或 `CAST(col AS int)`,隐式 cast 在 WHERE 让索引失效
5. **关键字大写 + snake_case + 显式 AS + 2 空格缩进**(Matt Mazur 风格)
6. **中文列双引号 / `ds` `shop_name` 假名**归 [evidence-skill ch05](../../evidence/evidence-skill/chapters/ch05-sql-antipatterns.md),本章只讲通用语法

## Connects To

- **sql-skill ch07**:PG 特有(JSONB / array)用 `COALESCE` 处理 NULL 多值列
- **sql-skill ch08**:WHERE 类型 cast 破坏索引(`int_col = '123'`),详见 ch08 §2
- **sql-skill ch09**:反模式综合(WHERE 引用列别名、`WHERE col = NULL` 等)
- **evidence-skill ch05**:中文列双引号 / 假名 / date SUBSTR 陷阱(业务侧雷区)
- **evidence-skill ch07**:postgres_fdw CTE 用法 `WITH taobao.mart_X AS (...)`(CTE 是 local scope)
