# Chapter 9: SQL 反模式综合 — 25+ 模式从 civilian7 + evidence-skill 实战

## Core Idea

SQL 反模式是"看似正确但长期踩坑"的写法,分 7 类:① **数据建模反模式**(EAV 实体属性值);② **查询编写反模式**(SELECT * / 隐式 JOIN);③ **索引使用反模式**(过度索引 / 无用索引);④ **NULL 处理反模式**(NULL 拼接 / NULL 聚合);⑤ **字符串 / 日期反模式**(隐式 cast / date SUBSTR);⑥ **性能反模式**(N+1 / 大 OFFSET / 函数索引失效);⑦ **安全反模式**(SQL 注入 / 字符串拼接)。**业务侧雷区**(中文列假名清单 / Evidence BI / nginx / FDW)归 [evidence-skill](../../evidence/evidence-skill/SKILL.md) 业务章节。本章是通用反模式综合。

## Frameworks Introduced

### §1 数据建模反模式(3 条)

- **EAV (Entity-Attribute-Value) 反模式**:`entity`/`attribute`/`value` 三列动态属性表 → 每行一次 JOIN,N+1 × M,扩展性差、查询复杂、约束缺失。修法:关系表 + 业务字段显式化;非要动态属性用 JSONB + GIN。
- **宽表反模式**:50数无上限(几百列),更新频繁时 TOAST + 行迁移开销巨大。修法:按业务域拆表,1:N 关联。
- **过度范式 / 不范式**:`users(id, name)` + `user_addresses(user_id, address)` + `user_phones(user_id, phone)` 5+ 张表,JOIN 链 4-5 层。修法:按查询模式适度冗余,物化视图聚合高频 JOIN 链。

### §2 查询编写反模式(3 条)

- **`SELECT *` 反模式**:拉全列,大表 TOAST 开销 + 网络 IO 浪费 + 隐式依赖列顺序。修法:`SELECT col1, col2` explicit columns。
- **隐式 JOIN (逗号 FROM)**:`FROM orders, users WHERE orders.user_id = users.id` → 易遗漏 WHERE 条件 → 笛卡尔积炸表。修法:`FROM orders o INNER JOIN users u ON o.user_id = u.id` 显式 JOIN。
- **子查询滥用 WHERE col IN (subquery)**:子查询返回 10000 行 → 性能差;改 `WHERE col IN (SELECT col FROM t LIMIT 100)` 控制规模,或改 `EXISTS`。

### §3 索引使用反模式(3 条)

- **过度索引**:10 列全建 B-Tree 索引,update 时 10 个索引都要更新 → 写入性能下降 50%+。修法:只建必要的索引(高频 WHERE / JOIN / ORDER BY 列),用 `pg_stat_user_indexes` 找无用索引。
- **无用索引**:建了但 query 从不用(选择性差 / 重复索引 / 函数索引)。修法:`SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0` 找出从未使用的索引,`DROP INDEX`。
- **重复索引**:`CREATE INDEX (col)` + `CREATE INDEX (col DESC)` 同时存在,后者覆盖前者(除 ORDER BY DESC)。修法:`SELECT indexname FROM pg_indexes WHERE tablename = 't'` 查重,合并。

### §4 NULL 处理反模式(3 条)

- **`NULL = NULL` 反模式**:认为 `NULL = NULL` 是 TRUE,实际是 NULL。修法:始终用 `IS NULL` / `IS NOT NULL`(详 [ch01 §3](ch01-grammar.md))。
- **NULL 拼接反模式**:`col1 || col2` 当任一为 NULL 时结果 NULL,而非空字符串。修法:`COALESCE(col1, '') || COALESCE(col2, '')`。
- **NULL 聚合反模式**:`SUM(col)` NULL 跳过;`COUNT(*)` 含 NULL,`COUNT(col)` 不含 NULL。修法:`SUM(COALESCE(col, 0))` 显式归 0。

## Key Concepts

### §1

- **EAV (Entity-Attribute-Value)**:`entity_id` / `attribute_name` / `value` 三列动态属性表
- **宽表 (wide table)**:列数过多(几十到几百列)
- **过度范式 / 不范式**:JOIN 链过长 或 数据冗余过度

### §2

- **`SELECT *`**:拉全部列,大表 IO 浪费
- **隐式 JOIN (comma join)**:FROM 多表 + WHERE 关联,易笛卡尔积
- **`WHERE col IN (subquery)`**:子查询规模决定性能

### §3

- **`pg_stat_user_indexes`**:PG 系统视图,记录每个索引的扫描次数 / 行数
- **`pg_stat_user_tables`**:PG 系统视图,记录每个表的 seq_scan / idx_scan 次数
- **idx_scan = 0**:索引从未被使用,候选删除

### §4

- **`NULL = NULL`**:三值逻辑,结果 NULL
- **`||` (concatenate)**:字符串拼接,NULL 传染
- **`SUM / COUNT(*)` / `COUNT(col)`**:聚合函数对 NULL 处理不同

## Mental Models

### §1

- **EAV 是关系数据库的"反关系"**:用 3 列模拟 N 列,牺牲 schema 约束换灵活性;长期维护成本远高于初始收益。
- **宽表 = 表是 heap storage**:每行更新都涉及整行重写 + TOAST;100 列宽表频繁 update 比 20 列 × 5 表 join 慢 10x。

### §2

- **`SELECT *` 是"懒"**:看似方便,实际把 schema 耦合到调用方,加列 = 改下游;性能 + 维护双输。
- **隐式 JOIN 是"可读性陷阱"**:用 ON 显式条件,reviewer 一眼看穿语义;逗号 JOIN 需看清 WHERE 链。

### §3

- **索引不是越多越好**:每个索引在 update 时多一次 B-Tree 维护成本(写放大);3 个有用索引 > 10 个冗余索引。
- **`idx_scan = 0` 不一定是冗余**:unique 索引用于 unique constraint、PK 索引用于 FK check,这些"逻辑"用途不体现为 idx_scan;先查约束再删。

### §4

- **NULL 是"未知值"语义**:不是"空";`col || 'X'` 当 col 未知时,结果也未知。`COALESCE` 显式声明"未知即 X"。
- **`COUNT(*)` vs `COUNT(col)`**:前者是行数,后者是非 NULL 数;聚合前理解 NULL 处理规则。

## Anti-patterns

### §1

- ❌ EAV 三列动态属性 → 改为关系表 + JSONB 兜底
- ❌ 200 列宽表 → 拆表按业务域,JOIN 链 ≤ 3 层
- ❌ 过度范式 5+ JOIN → 适度冗余 / 物化视图

### §2

- ❌ `SELECT *` → explicit columns
- ❌ `FROM a, b WHERE a.id = b.id` → 显式 JOIN + ON
- ❌ `WHERE col IN (SELECT * FROM huge_table)` → 加 LIMIT / 改 EXISTS

### §3

- ❌ 全列建索引 → 只建高频 WHERE/JOIN/ORDER BY 列
- ❌ 不查 `pg_stat_user_indexes` 找无用索引 → 至少季度 review
- ❌ 重复索引 → 合并

### §4

- ❌ `WHERE col = NULL` → `IS NULL`(详 [ch01 §3](ch01-grammar.md))
- ❌ `col1 || col2` 不 COALESCE → 任一 NULL 结果 NULL
- ❌ `SUM(col)` 不显式归 0 → NULL 跳过导致结果 NULL 而非 0

## Frameworks Introduced(续)

### §5 字符串 / 日期反模式(3 条)

- **隐式 cast 反模式**:`WHERE int_col = '123'`(string literal)→ PG 强制 cast `'123'` 到 int,索引失效。修法:类型一致,详 [ch08 §2](ch08-indexes-perf.md)。
- **date SUBSTR 反模式**:`SUBSTR(date_col, 1, 7)` → PG 报 `function substr(date, integer, integer) does not exist`。修法:`TO_CHAR(date_col, 'YYYY-MM')` 或 `date_col::text`(详 [evidence-skill ch05](../../evidence/evidence-skill/chapters/ch05-sql-antipatterns.md) 业务侧权威)。
- **字符串拼接 SQL 反模式**:`query = "SELECT * FROM " + table_name + " WHERE col = '" + value + "'"` → SQL 注入漏洞。修法:参数化查询(prepared statement / psycopg2 parameter binding / sqlglot)。

### §6 性能反模式(3 条)

- **N+1 反模式**:应用层 for 循环 N 次单条 query → 数据库 N+1 次往返。修法:`SELECT * FROM t WHERE id IN (id_list)` 批量 + JOIN(详 [ch08 §3](ch08-indexes-perf.md))。
- **大 OFFSET 反模式**:`OFFSET 100000 LIMIT 20` → PG 扫前 100020 行再丢弃。修法:keyset pagination `WHERE id > last_id LIMIT N`(详 [ch08 §5](ch08-indexes-perf.md))。
- **函数索引失效反模式**:`WHERE UPPER(col) = 'X'` 走 Seq Scan。修法:表达式索引 `CREATE INDEX ON t (LOWER(col))` 或反函数 `WHERE col = LOWER('X'`(详 [ch08 §2](ch08-indexes-perf.md))。

### §7 安全反模式(3 条)

- **字符串拼接 SQL 注入**:`cursor.execute(f"SELECT * FROM users WHERE name = '{user_input}'")` → `user_input = "'; DROP TABLE users; --"` 注入破坏。修法:参数化 `cursor.execute("SELECT * FROM users WHERE name = %s", (user_input,))`。
- **`superuser` role 反模式**:MCP / agent 用 `postgres` superuser 跑 query → 任何破坏性 SQL 都生效。修法:`readonly` role + sqlglot AST 防线 + `statement_timeout` + `LIMIT` 4 道防线(详 [evidence-skill ch16](../../evidence/evidence-skill/chapters/ch16-mcp-selfhost.md))。
- **DDL/DML 未白名单反模式**:用户输入里允许 DROP / TRUNCATE → 破坏性操作执行。修法:AST 解析白名单,只允许 SELECT;DDL/DML 直接 DENY。

## Key Concepts(续)

### §5

- **隐式类型 cast**:PG 自动从一种类型 cast 到另一种;`int_col = '123'` cast string → int
- **`SUBSTR(date_col, n, m)`**:PG date 类型不支持,报 function does not exist
- **字符串拼接 SQL**:用 `+` / `||` / f-string 拼 SQL → SQL 注入风险

### §6

- **N+1 problem**:应用层 for 循环 N 次单条 query
- **OFFSET 性能**:`OFFSET M LIMIT N` 扫 M+N 行再丢弃 M 行
- **函数索引失效**:WHERE 上函数让索引"看不见"

### §7

- **SQL 注入**:用户输入未参数化,直接拼到 SQL 字符串
- **superuser role**:PG 默认 postgres user,无权限限制
- **DDL/DML 白名单**:AST 解析识别 DROP/TRUNCATE/DELETE 等危险语句

## Mental Models(续)

### §5

- **隐式 cast 是"自动但危险"**:PG 帮用户做类型转换看似方便,但 cast 让索引失效;显式类型一致是最稳的。
- **date ≠ text**:PG 严格类型系统,SQL 函数不自动 cast;`SUBSTR` 是 text 函数,date 类型不适用。

### §6

- **N+1 是"应用层逻辑错配"**:数据库适合 batch IO,应用层 for 循环相当于每次 IPC;性能损失来自 IO 而非 SQL。
- **OFFSET 是"逐行扫描"**:PG 引擎没有"跳过"语义,OFFSET M 仍要扫 M 行才能丢弃;只有 keyset pagination 才能 O(1) 跳。

### §7

- **SQL 注入是"输入当代码"**:用户输入作为字符串拼到 SQL 解析器,被当 SQL 语法执行;参数化让输入当 data 不当 code。
- **多层防线是"纵深防御"**:任何 1 道防线被攻破,其他层兜底;readonly role + sqlglot + timeout + LIMIT 4 道防线互相补位。

## Anti-patterns(续)

### §5

- ❌ `WHERE int_col = '123'` → `WHERE int_col = 123`(详 [ch08 §2](ch08-indexes-perf.md))
- ❌ `SUBSTR(date_col, 1, 7)` → `TO_CHAR(date_col, 'YYYY-MM')` 或 `::text` cast
- ❌ f-string 拼 SQL → 参数化查询

### §6

- ❌ 应用层 N+1 for 循环 → 批量 query + JOIN
- ❌ `OFFSET 100000 LIMIT 20` → keyset pagination `WHERE id > last_id`
- ❌ `WHERE UPPER(col) = 'X'` → 表达式索引或反函数

### §7

- ❌ f-string / `+` 拼 SQL → 参数化绑定
- ❌ `superuser` role 跑 agent → `readonly` role + 4 道防线
- ❌ 允许 DDL/DML → AST 白名单 + DENY

## Code Examples

### §1 EAV 反模式 vs JSONB

```sql
-- ❌ EAV 反模式
CREATE TABLE entity_attrs (
  entity_id bigint,
  attr_name text,
  attr_value text
);
SELECT * FROM entity_attrs WHERE entity_id = 1;  -- 1 行 → N 属性

-- ✅ 关系表
CREATE TABLE users (
  id bigserial PRIMARY KEY,
  name text,
  email text,
  age int
);

-- ✅ 半结构化 → JSONB + GIN(详 ch07 §1)
CREATE TABLE products (
  id bigserial PRIMARY KEY,
  sku text,
  meta jsonb  -- 动态属性
);
CREATE INDEX idx_products_meta ON products USING gin (meta jsonb_path_ops);
SELECT * FROM products WHERE meta @> '{"color": "red"}';
```

### §2 SELECT * vs explicit

```sql
-- ❌ SELECT *
SELECT * FROM users WHERE created_at > NOW() - INTERVAL '7 days';

-- ✅ explicit columns
SELECT id, name, email, created_at
FROM users WHERE created_at > NOW() - INTERVAL '7 days';

-- ❌ 隐式 JOIN + WHERE
SELECT u.* FROM users u, orders o WHERE u.id = o.user_id AND o.amount > 100;

-- ✅ 显式 JOIN + ON
SELECT u.id, u.name FROM users u
INNER JOIN orders o ON o.user_id = u.id
WHERE o.amount > 100;
```

### §3 索引使用 / 删除无用索引

```sql
-- 1. 找无用索引(idx_scan = 0)
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- 2. 找重复索引(同列,不同名)
SELECT a.indexname, b.indexname, a.indexdef
FROM pg_indexes a, pg_indexes b
WHERE a.tablename = b.tablename
  AND a.indexname != b.indexname
  AND a.indexdef = b.indexdef;

-- 3. 删除无用索引(谨慎:先验证再删)
DROP INDEX CONCURRENTLY IF EXISTS idx_unused;
```

### §4 NULL 处理

```sql
-- ❌ NULL 拼接
SELECT first_name || ' ' || last_name FROM users;  -- 任一 NULL 结果 NULL

-- ✅ COALESCE
SELECT COALESCE(first_name, '') || ' ' || COALESCE(last_name, '') FROM users;

-- ❌ NULL 聚合
SELECT SUM(amount) FROM orders;  -- NULL 跳过

-- ✅ 显式归 0
SELECT SUM(COALESCE(amount, 0)) FROM orders;

-- ✅ NULL-safe 等值(详 ch01 §3)
SELECT * FROM users WHERE email IS DISTINCT FROM 'unknown@example.com';
```

### §5 字符串 / 日期 / SQL 注入

```sql
-- ❌ 隐式 cast(详 ch08 §2)
SELECT * FROM orders WHERE qty = '100';  -- cast string → int,索引失效

-- ✅ 类型一致
SELECT * FROM orders WHERE qty = 100;

-- ❌ date SUBSTR
SELECT SUBSTR(created_at, 1, 7) FROM orders;  -- function does not exist

-- ✅ TO_CHAR 或 ::text
SELECT TO_CHAR(created_at, 'YYYY-MM') FROM orders;
SELECT SUBSTR(created_at::text, 1, 7) FROM orders;

-- ❌ f-string 拼 SQL(SQL 注入)
query = f"SELECT * FROM users WHERE name = '{user_input}'"

-- ✅ 参数化查询(psycopg2 / Python)
cursor.execute("SELECT * FROM users WHERE name = %s", (user_input,))

-- ✅ Go database/sql
db.Query("SELECT * FROM users WHERE name = $1", userInput)

-- ✅ Java JDBC PreparedStatement
pstmt.setString(1, userInput);
pstmt.executeQuery();
```

### §6 N+1 / 大 OFFSET / 函数索引

```sql
-- ❌ N+1(应用层 for 循环)
-- for user in users: cursor.execute("SELECT * FROM orders WHERE user_id = %s", (user.id,))

-- ✅ 批量 + JOIN(详 ch08 §3)
SELECT u.id, u.name, o.*
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.created_at > NOW() - INTERVAL '7 days';

-- ❌ 大 OFFSET
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 100000;  -- 扫 100020 行

-- ✅ keyset pagination
SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20;  -- 扫 20 行

-- ❌ 函数索引失效
SELECT * FROM users WHERE UPPER(name) = 'ALICE';  -- Seq Scan

-- ✅ 表达式索引
CREATE INDEX idx_users_name_upper ON users (UPPER(name));
-- 现在 WHERE UPPER(name) = 'ALICE' 走索引

-- ✅ 或反函数
SELECT * FROM users WHERE name = LOWER('ALICE');  -- 'alice' 走索引
```

### §7 SQL 注入 / superuser / DDL 防护

```python
# ✅ 4 道防线(详 evidence-skill ch16)
import psycopg2, sqlglot

# [1] readonly role + statement_timeout
conn = psycopg2.connect(dsn=os.environ["READONLY_DSN"])
with conn.cursor() as cur:
    cur.execute("SET LOCAL statement_timeout = '10s'")

    # [2] AST 解析白名单
    parsed = sqlglot.parse_one(sql)
    for node in parsed.walk():
        if node.key.upper() in ("DROP", "TRUNCATE", "DELETE", "INSERT", "UPDATE"):
            raise ValueError(f"Destructive SQL blocked: {node.key}")

    # [3] LIMIT clamp
    if "LIMIT" not in sql.upper():
        sql += " LIMIT 10000"

    # [4] 执行
    cur.execute(sql)
```

## Reference Tables

### §1 数据建模决策

| 数据形态 | 推荐 | 反模式 |
|---|---|---|
| 固定属性 | 关系表 | EAV |
| 动态属性低基数 | JSONB + GIN | EAV |
| 固定属性高频 | 关系表 + 适度冗余 | 过度范式 5+ JOIN |
| 大字段 (LOB) | 单独表 + FK | 宽表 200 列 |

### §2 查询编写决策

| 场景 | 推荐 | 反模式 |
|---|---|---|
| 拉全列 | explicit columns | `SELECT *` |
| 多表关联 | 显式 JOIN + ON | 逗号 FROM + WHERE |
| 子查询规模未知 | 加 LIMIT 或 EXISTS | 大 IN (subquery) |

### §3 索引决策

| 索引数 | 评估 | 反模式 |
|---|---|---|
| 0 | 慢 query,加索引 | — |
| 1-3 | ✓ 健康 | — |
| 4-7 | 评估每个,可能有冗余 | 过度索引 |
| 8+ | 高概率冗余 | 过度索引 + 写放大 |

### §5 字符串 / 日期决策

| 写法 | 走索引 | 修法 |
|---|---|---|
| `int_col = 123` | ✓ | — |
| `int_col = '123'` | ❌ | 改类型一致 |
| `SUBSTR(text_col, ...)` | ✓(如列有索引) | — |
| `SUBSTR(date_col, ...)` | ❌ function error | TO_CHAR / ::text |

### §7 安全决策

| 防护层 | 必需 | 失效后果 |
|---|---|---|
| [1] readonly role | ✓ | DDL/DML 生效 |
| [2] sqlglot AST | ✓ | 注入突破 |
| [3] statement_timeout | ✓ | 慢 query 拖死 DB |
| [4] LIMIT clamp | ✓ | 大结果集 OOM |

## Key Takeaways

1. **EAV 反模式**:三列动态属性表 → 关系表 + JSONB + GIN
2. **`SELECT *` 反模式**:explicit columns,大表 IO 浪费 + schema 耦合
3. **隐式 JOIN 反模式**:逗号 FROM → 显式 INNER JOIN + ON,防笛卡尔积
4. **过度索引反模式**:查 `pg_stat_user_indexes` 找无用索引,谨慎 DROP INDEX CONCURRENTLY
5. **`NULL = NULL` 反模式**:`IS NULL` / `IS NOT NULL`,三值逻辑
6. **NULL 拼接反模式**:`COALESCE(col1, '') || COALESCE(col2, '')`
7. **隐式 cast 反模式**:`int_col = '123'` → `int_col = 123`,索引失效
8. **date SUBSTR 反模式**:`TO_CHAR(date_col, 'YYYY-MM')` 或 `::text` cast
9. **N+1 反模式**:应用层 for 循环 → 批量 query + JOIN
10. **大 OFFSET 反模式**:keyset pagination `WHERE id > last_id LIMIT N`
11. **SQL 注入反模式**:f-string 拼 SQL → 参数化绑定
12. **superuser 反模式**:readonly role + 4 道防线(sqlglot + timeout + LIMIT)
13. **业务侧雷区**(中文列假名 / Evidence BI / FDW)归 [evidence-skill](../../evidence/evidence-skill/SKILL.md) 业务章节
14. **语法铁律与索引铁律**(NULL 三值逻辑 / 函数索引失效)详 [ch01 §3](ch01-grammar.md) / [ch08 §2](ch08-indexes-perf.md)

## Connects To

- **sql-skill ch01**:SQL 语法铁律(§4 NULL 三值逻辑详 [ch01 §3](ch01-grammar.md))
- **sql-skill ch07**:PG 特有(§5 字符串/日期反模式与 [ch07 §5](ch07-pg-specific.md) 中文 schema 雷区互补)
- **sql-skill ch08**:索引与性能(§3 索引反模式 / §6 性能反模式详 [ch08 §2/§3/§5](ch08-indexes-perf.md))
- **evidence-skill ch05**:中文 schema 业务侧雷区(中文列假名清单 / date SUBSTR 实战 / html-tags 雷区)
- **evidence-skill ch07**:postgres_fdw 跨 DB 反模式(2-segment vs 3-segment)
- **evidence-skill ch14**:BI 场景反模式(Core 28 page + nginx immutable 缺失)
- **evidence-skill ch16**:MCP self-host 4 道 SQL 防线(详 [ch09 §7](ch09-antipatterns.md) 安全反模式)

