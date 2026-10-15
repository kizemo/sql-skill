# Chapter 7: PostgreSQL 特有 — JSONB / array / GIN / FDW / 中文 schema

## Core Idea

PostgreSQL 相比标准 SQL 提供 5 大特有能力:① **JSONB**(二进制存储 + `?` `@>` 操作符 + GIN 索引);② **array**(`@>` `ANY` `unnest` + GIN);③ **GIN / GIST 索引决策**;④ **postgres_fdw 跨 DB**(`taobao.mart_X` 2-segment path);⑤ **中文 schema 雷区**(双引号 / 假名 / date SUBSTR)。**postgres_fdw 5 步建表 SQL 细节**归 [evidence-skill ch07](../../evidence/evidence-skill/chapters/ch07-fdw-cross-db.md),**中文列双引号与假名映射**归 [evidence-skill ch05](../../evidence/evidence-skill/chapters/ch05-sql-antipatterns.md),本章讲通用 PG 特有 + 与 evidence-skill 协作模式。

## Frameworks Introduced

### §1 JSONB(3 条)

- **JSONB 比 JSON 好**:`jsonb_col` 自动去重 + 二进制存储 + 支持 GIN;`json_col` 保留原文本顺序 + 无索引,几乎不用
- **`@>` / `?` / `?|` `?&` 操作符走 GIN**:`jsonb @> '{"key": "val"}'` / `jsonb ? 'key'` / `jsonb ?| array['k1','k2']` 全部走索引;`->>` / `->` 文本提取**不走索引**
- **嵌套查询 `jsonb_path_query`**:用于复杂 JSONB 路径查询,但**不走 GIN**,需大数据集时建表达式索引

### §2 array(3 条)

- **array 列类型**:`integer[]` / `text[]` / `varchar(50)[]` 等,适合低基数多值列(如 user.tags)
- **`@>` `&&` 操作符走 GIN**:`tags @> ARRAY['taobao']` / `tags && ARRAY['a','b']`(任一元素存在)
- **`unnest(array_col)` 转行**:与 `LATERAL JOIN` 配合行级展开,适合"数组转多行聚合"

### §3 GIN / GIST 索引决策(2 条)

- **JSONB 用 `jsonb_path_ops` GIN**:只支持 `@>` 但索引体积小一半;`jsonb_ops` 支持所有操作符但体积大
- **GIN update cost 高**:适合**读多写少**;高频 update 列建 GIN 会拖慢写入

### §4 postgres_fdw 跨 DB(2 条)

- **2-segment path `taobao.mart_X`**:erp DB 内建 foreign table 代理 taobao DB;`taobao.mart_X` ✓,`taobao.bi.mart_X` ✗ 触发 `cross-database references are not implemented`(PG 看到 taobao 当 database 名,跨 DB ref 不支持)
- **pgbouncer 必 `pool_mode = session`**:transaction-mode 破坏 5 项(`search_path` / `statement_timeout` / FDW 事务 / prepared statements / advisory locks)

### §5 中文 schema 雷区(3 条)

- **中文列名必双引号**:`SELECT SUM("销售金额")` ✓;`SELECT SUM(销售金额)` ✗ PG 把"销售金额"当 string literal
- **`ds` `shop_name` `stat_date` 是假名**:真名 `"订单日期"` / `"店铺"` / `source_year_month`,要查 `information_schema.columns` 确认(详见 [evidence-skill ch05](../../evidence/evidence-skill/chapters/ch05-sql-antipatterns.md))
- **`date` 类型不能 `SUBSTR`**:改 `TO_CHAR("订单日期", 'YYYY-MM')` 或 `"订单日期"::text` cast(详见 [evidence-skill ch05](../../evidence/evidence-skill/chapters/ch05-sql-antipatterns.md))

## Key Concepts

### §1 JSONB

- **JSONB**:二进制 JSON,自动去重、压缩、支持 GIN
- **JSON**:文本 JSON,保留原序、不支持 GIN、几乎不用
- **`->` / `->>`**:`->` 返回 JSONB / JSON,`->>` 返回 text;**都不走索引**
- **`@>`**:"包含"操作符,`jsonb @> '{"key": "val"}'`,走 GIN
- **`?` / `?|` / `?&`**:key 存在 / 任一存在 / 全部存在;走 GIN
- **`jsonb_path_query`**:JSONPath 表达式,`$.key.nested`,**不走 GIN**
- **`jsonb_path_ops`**:GIN 索引 operator class,只支持 `@>`,索引小一半
- **`jsonb_ops`**:GIN 默认,支持所有操作符,索引大

### §2 array

- **`integer[]` / `text[]`**:数组类型,适合低基数多值
- **`ARRAY[1, 2, 3]`**:数组字面量
- **`@>`**:"包含所有元素" → `tags @> ARRAY['taobao']`
- **`&&`**:"任一元素重叠" → `tags && ARRAY['a','b']`
- **`ANY(array)`**:数组中任一元素匹配 → `tags = ANY(ARRAY['a','b'])`
- **`unnest(array_col)`**:数组转行,常与 LATERAL JOIN 配合

### §3 GIN / GIST

- **GIN (Generalized Inverted Index)**:多值倒排,JSONB / array / tsvector
- **GiST (Generalized Search Tree)**:几何 / 全文 / 范围类型
- **`jsonb_path_ops` vs `jsonb_ops`**:GIN operator class,前者体积小一半但只支持 `@>`

### §4 postgres_fdw

- **`CREATE EXTENSION postgres_fdw`**:启用 FDW 扩展
- **`CREATE SERVER`**:定义远程 PG server 连接(host/port/dbname)
- **`CREATE USER MAPPING`**:本地 user → 远程 user 映射
- **`CREATE FOREIGN TABLE`**:本地 schema 装 foreign table,数据在远程 server
- **`IMPORT FOREIGN SCHEMA`**:PG 9.5+,自动从远程 schema 导入所有表定义
- **2-segment path**:`taobao.mart_X` (erp DB 内 taobao schema 装 foreign tables)
- **3-segment path 错**:`taobao.bi.mart_X` (PG 看到 taobao 当 database 名)

### §5 中文 schema

- **PG identifier quote**:`"中文"` 双引号;SQL 标准是 `"identifier"`,但中文列名几乎必用
- **`ds` / `shop_name` / `stat_date`**:常见英文假列名,**真名在 PG 不存在**
- **`information_schema.columns`**:PG 系统视图,查表真实列名
- **`TO_CHAR(date, 'YYYY-MM')`**:标准 SQL 格式化 date → string
- **`::text` cast**:`col::text` 把任意类型转 text

## Mental Models

### §1

- **JSONB 是数据库内的 KV 存储**:把半结构化数据存进 PG,免去建 10 个稀疏列
- **`@>` / `?` 是"包含"语义**:与 SQL `=` 不同,适合 JSON 嵌套结构
- **`->>` 不走索引**:JSONB 字段不能直接 SELECT 提取后比较,要走 `@>` 操作符

### §2

- **array 列 vs 关联表**:低基数(< 100)、无 join 需求 → array 列;高频 join → 建关联表
- **GIN 让 array 等值查询 O(log N)**:`tags @> ARRAY['x']` 走索引;无 GIN 时 Seq Scan

### §3

- **GIN 是读优化索引**:update cost 高,适合"插入一次查多次"的数据(如商品标签、日志字段)
- **jsonb_path_ops 是性价比选择**:只支持 `@>` 但索引小一半,大多数 JSONB 查询用 `@>` 就够

### §4

- **FDW = 数据库代理**:本地 query 透明代理到远程 server,适合"少表 + 简单查询"场景
- **高频跨 DB JOIN 性能差**:每个 query 走网络,大批聚合需本地物化 view

### §5

- **中文列 = 数据契约**:spec 写的逻辑名 ≠ 真 PG 列名,要 `information_schema.columns` 查
- **`date` ≠ `text`**:PG 严格类型,SQL 函数不自动 cast

## Anti-patterns

### §1

- ❌ `json_col` 用文本 JSON → 改 `jsonb_col`
- ❌ `SELECT jsonb_col->>'key' = 'X'` → 文本提取不走索引,改 `WHERE jsonb_col @> '{"key": "X"}'`
- ❌ `jsonb_path_query` 大数据集 → 不走 GIN,改表达式索引或物化

### §2

- ❌ array 列高频 join → 改关联表(array 列无 PK,join 慢)
- ❌ array 列不建 GIN → `@>` 操作 Seq Scan

### §3

- ❌ 高频 update 列建 GIN → update cost 高,拖慢写入
- ❌ 默认 `jsonb_ops` 不知有 `jsonb_path_ops` 更省空间

### §4

- ❌ `taobao.bi.mart_X` 3-segment path → PG 报 cross-database references not implemented
- ❌ `pgbouncer transaction_mode` + FDW → 破坏 FDW 事务
- ❌ 高频跨 DB JOIN 不预聚合本地 → 每次 query 走网络

### §5

- ❌ 中文列无双引号 → `SUM(销售金额)` 报 type error,改 `"销售金额"`
- ❌ 用 `ds` / `shop_name` 假名 → PG 报 column does not exist,查真名
- ❌ `SUBSTR(date_col, 1, 7)` → PG 报 `function substr(date, integer, integer) does not exist`,改 `TO_CHAR` / `::text`

## Code Examples

### §1 JSONB + GIN

```sql
-- 表 + JSONB 字段 + GIN 索引
CREATE TABLE orders (
  id bigserial PRIMARY KEY,
  user_id bigint,
  meta jsonb NOT NULL
);

-- 推荐:jsonb_path_ops 索引(只支持 @>,体积小一半)
CREATE INDEX idx_orders_meta ON orders USING gin (meta jsonb_path_ops);

-- ✅ 走 GIN 的查询
SELECT * FROM orders WHERE meta @> '{"channel": "taobao"}';
SELECT * FROM orders WHERE meta ? 'coupon';
SELECT * FROM orders WHERE meta ?| ARRAY['refund', 'exchange'];

-- ❌ 不走 GIN 的查询
SELECT * FROM orders WHERE meta->>'channel' = 'taobao';  -- 文本提取,Seq Scan

-- 嵌套 JSONB 查询(jsonb_path_query,不走 GIN)
SELECT * FROM jsonb_path_query(meta, '$.items[*]') AS item
FROM orders WHERE id = 1;
```

### §2 array + GIN

```sql
-- array 列 + GIN
CREATE TABLE users (
  id bigserial PRIMARY KEY,
  name text,
  tags text[]
);

CREATE INDEX idx_users_tags ON users USING gin (tags);

-- ✅ 走 GIN
SELECT * FROM users WHERE tags @> ARRAY['vip'];        -- 包含
SELECT * FROM users WHERE tags && ARRAY['a', 'b'];     -- 任一重叠

-- unnest 数组转行(LATERAL JOIN)
SELECT u.id, u.name, tag
FROM users u,
LATERAL unnest(u.tags) AS tag;
-- 1 个用户 3 个 tag → 3 行

-- array ANY 等值
SELECT * FROM users WHERE tags = ANY(ARRAY['vip', 'gold']);
```

### §3 GIN 决策

```sql
-- jsonb_path_ops:只支持 @>,索引小一半,推荐默认
CREATE INDEX idx_orders_meta_lean ON orders USING gin (meta jsonb_path_ops);

-- jsonb_ops:支持所有操作符(@> ? ?| ?&),索引大
CREATE INDEX idx_orders_meta_full ON orders USING gin (meta);

-- 选择:业务只用 @> 选 jsonb_path_ops;需要 ?/?? 等用 jsonb_ops
```

### §4 postgres_fdw(摘要)

```sql
-- 完整 5 步建表 SQL 见 evidence-skill ch07,这里只列决策要点

-- 1. 创建 extension
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- 2. 创建 server(本机 erp DB 连远程 taobao DB)
CREATE SERVER taobao_pg FOREIGN DATA WRAPPER postgres_fdw OPTIONS (
    host '124.223.115.201', port '5432', dbname 'taobao'
);

-- 3. user mapping
CREATE USER MAPPING FOR kizemo SERVER taobao_pg OPTIONS (user 'kizemo', password '...');

-- 4. 创建本地 schema 装 foreign tables
CREATE SCHEMA IF NOT EXISTS taobao;

-- 5. 创建 foreign table(注意 2-segment path)
CREATE FOREIGN TABLE taobao.mart_shop_kpi_daily (
    shop_name text,
    stat_date date,
    -- ...
) SERVER taobao_pg OPTIONS (schema_name 'bi', table_name 'mart_shop_kpi_daily');

-- ✅ 正确查询
SELECT * FROM taobao.mart_shop_kpi_daily WHERE stat_date > '2026-09-01';

-- ❌ 错误 3-segment path
SELECT * FROM taobao.bi.mart_shop_kpi_daily;  -- cross-database references not implemented
```

### §5 中文 schema(决策摘要)

```sql
-- ✅ 中文列双引号
SELECT SUM("销售金额") FROM erp.erp_result.daily_store_dd_2026
WHERE SUBSTR("订单日期"::text, 1, 7) = '2026-01';

-- ❌ 中文列无双引号(PG 当 string literal)
SELECT SUM(销售金额) FROM erp.erp_result.daily_store_dd_2026;

-- ✅ date 列按月聚合
SELECT TO_CHAR("订单日期", 'YYYY-MM') AS month, SUM("销售金额")
FROM erp.erp_result.daily_store_dd_2026
GROUP BY 1;

-- ❌ date 不能 SUBSTR
SELECT SUBSTR("订单日期", 1, 7) AS month, SUM("销售金额")
FROM erp.erp_result.daily_store_dd_2026;

-- 查真列名(information_schema.columns)
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'erp_result'
  AND table_name = 'daily_store_dd_2026';
-- 看到 "店铺" "订单日期" "销售金额",而非 ds / shop_name
```

## Reference Tables

### §1 JSONB 操作符与索引

| 操作符 | 含义 | 走 GIN |
|---|---|---|
| `@>` | 包含 | ✓ |
| `?` | key 存在 | ✓ |
| `?|` | 任一 key 存在 | ✓ |
| `?&` | 所有 key 存在 | ✓ |
| `->` | JSONB 提取(JSONB 返回) | ✗ |
| `->>` | JSONB 提取(text 返回) | ✗ |
| `jsonb_path_query` | JSONPath 查询 | ✗ |

### §2 array 操作符与索引

| 操作符 | 含义 | 走 GIN |
|---|---|---|
| `@>` | 包含所有元素 | ✓ |
| `&&` | 任一元素重叠 | ✓ |
| `=` | 等值(整个数组) | ✗ |
| `ANY()` | 任一元素匹配 | 部分(走 GIN) |

### §4 FDW 路径决策

| 路径 | 含义 | 正确 |
|---|---|---|
| `taobao.mart_X` | erp DB 内 taobao schema 装 foreign table | ✓ |
| `taobao.bi.mart_X` | PG 看到 taobao 当 database 名 | ✗ |
| `bi.mart_X` | 本地 bi schema 的表 | ✓ |

### §5 中文列名 vs 假名

| 假名(代码里写) | 真名(PG 列) | 备注 |
|---|---|---|
| `ds` | `"订单日期"` | raw 表 |
| `shop_name` | `"店铺"` | raw + mart 表 |
| `stat_date` | `"订单日期"` 或 `source_year_month` | 视 mart 而定 |

## Key Takeaways

1. **JSONB 比 JSON 好**:`@>` `?` 走 GIN,`->>` `->` 不走,推荐 `jsonb_path_ops` operator class
2. **array 列 `@>` `&&` 走 GIN**,高频 join 改关联表;`unnest` 与 LATERAL JOIN 配合展开
3. **GIN update cost 高,适合读多写少**;高频 update 列不建 GIN
4. **postgres_fdw 2-segment path**:`taobao.mart_X` ✓,3-segment 触发 cross-database error;**pgbouncer 必 session-mode**
5. **中文列双引号**:`"销售金额"`,否则 PG 当 string literal
6. **date 不能 SUBSTR**:改 `TO_CHAR` / `::text` cast
7. **完整 FDW 5 步 SQL + 中文列假名映射**归 [evidence-skill ch07](../../evidence/evidence-skill/chapters/ch07-fdw-cross-db.md) 与 [evidence-skill ch05](../../evidence/evidence-skill/chapters/ch05-sql-antipatterns.md)

## Connects To

- **sql-skill ch01**:SQL 语法铁律(`COALESCE` 处理 NULL 多值列)
- **sql-skill ch08**:GIN 索引决策与 ch08 §1 GIN 决策互补;`jsonb_path_ops` 与 ch08 §1 索引类型决策同步
- **evidence-skill ch05**:中文列双引号 / `ds`/`shop_name` 假名 / date SUBSTR 陷阱(业务侧雷区权威)
- **evidence-skill ch07**:postgres_fdw 完整 5 步 SQL + pgbouncer session-mode 详情 + 4 mart 表 142k 行实战
- **evidence-skill ch14**:BI 场景性能(FDW JOIN 性能差,高频 JOIN 预聚合本地表)
