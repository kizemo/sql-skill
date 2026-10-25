# Chapter 11: 多方言 MySQL / Oracle / SQL Server — 语义差异、反模式、跨库协作

## Core Idea

会写 SQL 的人都会 SQL;被多方言咬人的从来不是语法,是**语义默认值不同**。同一个 `WHERE col = 123`,PG 把**数字**转成文本、MySQL 把**文本**转成数字、SQL Server 又把**文本**转成数字 —— 三种方言把索引失效的方向分成两派。同一个 `''`,Oracle 等于 NULL,MySQL / SQL Server 不等于。`LIMIT` 在 Oracle / SQL Server 根本不存在。**ch11 不教三种方言入门**,只讲三件事:① **每方言的语义地雷**(§1-§3);② **一张跨方言对照表**(§4);③ **跨库协作的现实边界**(§5)。**核心铁律:写任何 SQL 前先确认目标方言** —— SQL 语法 99% 通用,而那 1% 的语义差异恰好落在 **NULL 和索引** 上,也就是最贵的两个地方。

## Frameworks Introduced

### §1 MySQL 8.0 — 方言要点 — 3 条铁律

- **铁律 1 · 隐式转换方向是"文本 → 数字"**:MySQL 里 `varchar_col = 123` 会把 `varchar_col` 转成数字再比,转换掉的那一侧**走不了索引**。PG 方向相反(数字 → 文本),SQL Server 与 MySQL 同向但转换发生在 varchar 一侧。**这是 MySQL 最常见的慢查询根因**,修法:`WHERE CAST(col AS UNSIGNED) = 123` 反而更慢(显式转换照样断索引),正确解法是**把比较值转成列的类型** 或 **建函数索引**(8.0.13+)。
- **铁律 2 · 字符串拼接必须 `CONCAT()`**:`||` 在 MySQL 默认是**逻辑或**(不是拼接),除非 sql_mode 含 `PIPES_AS_CONCAT`。MySQL 的拼接语义是 SQL 标准里的"隐式转换优先",`CONCAT()` 遇 NULL 返回 NULL,`CONCAT_WS()` 遇 NULL 才跳过。
- **铁律 3 · DDL 不是事务性的**:MySQL 的 `CREATE TABLE` / `ALTER TABLE` / `DROP TABLE` 都会**隐式 commit**,不能像 PG 那样 `BEGIN; ALTER; ROLLBACK;` 回滚。schema 变更脚本必须**先备份再改**,不能靠事务兜底。

### §2 Oracle — 方言要点 — 3 条铁律

- **铁律 1 · 空字符串 = NULL**:Oracle 把 `''` 存成 NULL,`WHERE x = ''` **永远不匹配任何行**(`x IS NULL` 才是它)。从 PG 迁过去的 ETL 脚本里,任何 `= ''` 的过滤条件在 Oracle 上**会静默丢掉整批数据**。MySQL / SQL Server / PG 保留 `''`,Oracle 是唯一的例外。
- **铁律 2 · 隐式转换依赖会话 NLS 变量**:`NLS_DATE_FORMAT` / `NLS_NUMERIC_CHARACTERS` / `NLS_LANGUAGE` 决定了 `WHERE date_col = '2026-01-01'` 的解析结果和 `'1234.56'` 是不是数字。**同一个 SQL 在两个会话里语义不同**,这是 Oracle 排查"同样的查询别人跑得过我跑得慢"的头号原因。生产连接必须显式设 NLS。
- **铁律 3 · 分页必须带 ORDER BY**:`OFFSET n ROWS FETCH NEXT m ROWS ONLY`(12c+)在**没有 ORDER BY** 时返回哪 m 行是**未定义的**,且优化器可能给不同计划。旧版 `ROWNUM` 只能"先取前 N 再排",与"先排再取"语义不同 —— `ROWNUM < n` **在 ORDER BY 之前**生效,这是 Oracle 最经典的翻页 bug。

### §3 SQL Server — 方言要点 — 3 条铁律

- **铁律 1 · SARGability 是第一性原理**:SQL Server 社区的专属术语 —— 一个谓词**能不能把索引查找转成 seek**(而不是 scan),取决于**比较的哪一侧发生了类型转换**。`WHERE varchar_col = 123` 里 varchar 的优先级低于 int,SQL Server 把 varchar 转 int → 索引断。**修法不是 CAST,是改比较值类型**:`WHERE varchar_col = '123'`(字面量加引号即修好)。`ISNULL(col, 0) = 0` 同理 → 改成 `col = 0 OR col IS NULL`。
- **铁律 2 · `FORMAT()` 是性能陷阱**:`FORMAT(date_col, 'yyyy-MM')` 走 CLR 格式化,**慢一个数量级且断索引**。正确写法是 `CONVERT(varchar(10), date_col, 23)`(style 23 = `yyyy-mm-dd`),或直接 `FORMAT` 只在展示层用。`CONVERT` 的 style code 是性能友好路径,`FORMAT` 不是。
- **铁律 3 · `OFFSET` 深分页要换 keyset**:`OFFSET 100000 ROWS FETCH NEXT 100 ROWS ONLY` 让引擎**扫掉并丢弃前 10 万行**,代价随 offset 线性增长(与 PG 的 `OFFSET` 同一个病)。keyset 分页写法与 PG 完全一致(§5 对照表给出三方言三写法)。另外 `WITH (NOLOCK)` 允许脏读、允许丢行、允许重复行,**不是"性能优化"**。

### §4 跨方言对照 — 1 条铁律

- **铁律 · 迁移前先查对照表,不要凭记忆改**:语法差异可以查文档,**语义默认值差异查不到** —— 空串、隐式转换方向、分页原子性、DDL 事务性这四项**必须**逐条对照。任何"从 PG 迁到 X 方言"的需求,第一步是产出**方言差异清单**(§6 模板),而不是直接改 SQL。

### §5 多 DB 协作 — 2 条铁律

- **铁律 1 · `postgres_fdw` 只连 PG**:`postgres_fdw` 的**远端必须是 PostgreSQL**,它走的是 PG 原生协议。**PG → MySQL / Oracle / SQL Server 无法用 `postgres_fdw`**。MySQL / Oracle / MSSQL 各有第三方 FDW 扩展(`mysql_fdw` / `orafce` / `tSql`),但**可用性、性能、支持度各不相同**,不能当作生产默认方案。**跨方言 JOIN 的正解是同步到中间层,不是联邦查询**(§5 心智模型)。
- **铁律 2 · 跨库 JOIN 默认走"查询门面"**:把异构源(MySQL 订单库 / Oracle ERP / MSSQL CRM)的需要联查的数据**同步到一个 PG 中间层**,对外只暴露 PG 一套方言 —— 应用侧、BI 侧、agent 侧全部只写一种 SQL。**代价是同步延迟**,收益是**只有一种方言需要维护**;当有 ≥2 个异构源参与同一个 JOIN 时,这个交换通常是划算的。

### §6 方言迁移检查清单 — 1 条铁律

- **铁律 · 迁移必查 12 项**:空串语义 / 隐式转换方向 / 分页写法 / DDL 事务性 / 标识符引用 / 字符串拼接 / 日期格式化 / NULL 排序位置 / 序列语法 / 标识符大小写 / JSON 类型 / 索引能力(partial / expression / 函数索引)。§6 给出逐项的三方言写法与**踩坑后果**。

## Key Concepts

### §1 MySQL 8.0

- **InnoDB 聚簇索引**:数据行本身按主键顺序存放,二级索引叶子节点存**主键值**而非行指针 → 覆盖索引(`EXPLAIN` 显示 `Using index`)比 PG 更值钱
- **前缀索引**:只能建在**字符串列前缀**(`col(10)`),不能对数字列用 → 长 varchar 全表扫描的常见原因
- **函数索引**:8.0.13+ 支持 `CREATE INDEX idx ON t ((CAST(col AS UNSIGNED)))`,可救隐式转换
- **JSON**:5.7+ 有 `JSON` 类型,但索引靠 **generated column + 二级索引**,不是 PG 的 GIN
- **无 partial index / 无 GIN / 无 BRIN**:全文走 `FULLTEXT`,空间走 `SPATIAL`
- **`EXPLAIN`**:8.0.18+ 支持 `EXPLAIN ANALYZE`(真执行),`EXPLAIN FORMAT=JSON` 给结构化计划
- **`SHOW INDEX FROM tbl`**:看 key 名 / 列序 / cardinality,PG 对应 `pg_indexes` + `pg_stat_user_indexes`

### §2 Oracle

- **标识符**:不加引号 → **强制转大写**;加双引号 → **大小写敏感**。跨库迁移时 PG 的小写表名到 Oracle 变成大写对象名,应用侧 SQL 不加引号正好对上,加了引号就全错
- **空串即 NULL**:`'' IS NULL` 为真;`NVL(a, b)`(Oracle)≈ `COALESCE(a, b)`(标准)
- **`DECODE`**:Oracle 专有的 `CASE` 简写
- **`ROWNUM` vs `ROW_NUMBER()`**:前者是伪列(过滤先于排序),后者是窗口函数(排序后编号)—— **语义完全不同**,迁移时不能直接替换
- **`CONNECT BY PRIOR`**:Oracle 专有层级查询,PG / MySQL / MSSQL 都要用递归 CTE 改写
- **索引**:B-Tree + **位图索引**(低基数列,如状态码)+ **反向索引** + **函数索引**;`ANALYZE` 收集统计信息,**统计信息陈旧是"计划突然变慢"的头号原因**
- **`MERGE INTO`**:Oracle / SQL Server 都有 upsert,MySQL 用 `INSERT ... ON DUPLICATE KEY UPDATE`

### §3 SQL Server

- **标识符**:`[col]` 方括号;`SET QUOTED_IDENTIFIER ON` 后也支持 `"col"`
- **分页**:`OFFSET n ROWS FETCH NEXT m ROWS ONLY`(2012+);旧版 `SELECT TOP n`
- **拼接**:`+` 或 `CONCAT()`(2012+);`+` 遇 NULL 返回 NULL
- **空串保留**:`''` 不等于 NULL(与 Oracle 相反)
- **序列**:`IDENTITY(1,1)` 或 `SEQUENCE`(2012+)
- **索引**:聚簇 / 非聚簇 + `INCLUDE` 覆盖列 + **filtered index**(`WHERE status = 1`)—— filtered index 是 PG partial index 的等价物
- **`CROSS APPLY` / `OUTER APPLY`**:等价于 PG 的 `LATERAL`,MySQL 8.0 有 `LATERAL`(8.0.14+)
- **递归 CTE**:默认最多 **100 层**,超限报错,需 `OPTION (MAXRECURSION 0)` —— PG 无此限制
- **诊断**:`SET STATISTICS IO, TIME ON` + `sys.dm_exec_query_stats` / `sys.dm_db_index_usage_stats`
- **`GETDATE()`** 返回 `datetime`(精度 3.33ms),`SYSDATETIME()` 返回 `datetime2`(100ns 精度)

### §4 跨方言对照

- **语义地雷四项**:空串、隐式转换方向、分页原子性、DDL 事务性
- **语法差异可查,语义差异不可查**:迁移前必须逐条对照(§6)
- **索引能力不对等**:PG 独有 GIN / BRIN / partial / expression;MySQL 无;Oracle 靠函数索引 + 位图;MSSQL 靠 computed column + filtered index

### §5 多 DB 协作

- **`postgres_fdw` 的远端必须是 PG**:跨方言走不了这条路
- **第三方 FDW 扩展**:`mysql_fdw` / `orafce` / `tSql`,可用性与性能各异,不做生产默认
- **四种协作模式**:查询门面(同步到 PG 中间层)/ ETL 落 ODS-DWD-DWS / CDC(Kafka + Debezium / Canal / GoldenGate)/ 应用层 fan-out
- **联邦查询的真实代价**:谓词下推不全 → 远端全表扫 + 本地 join;网络往返放大;类型跨方言转换;无统一事务
- **决策口诀**:**异构源 ≥ 2 且要 JOIN → 同步门面;异构源 = 1 且只做报表 → 联邦查询可接受**

### §6 方言迁移检查清单

- **12 项**:空串 / 隐式转换 / 分页 / DDL 事务 / 标识符 / 拼接 / 日期 / NULL 排序 / 序列 / 大小写 / JSON / 索引能力
- **空串与隐式转换是必查项**:这两项各自都能让"迁移后跑得通但结果不对 / 跑得慢"同时发生

## Mental Models

### §1 MySQL

- **MySQL 的隐式转换是"字符串优先被吃掉"**:SQL 引擎遇到类型不匹配,按"把弱类型方转成强类型方"处理;MySQL / SQL Server 的弱类型方是**字符串**,PG 的弱类型方是**数字**。**记住"谁转谁"比记住规则更重要** —— 因为它直接决定索引断在哪一侧。
- **前缀索引是字符串列的第二种病**:PG 的 btree 对长文本也能建索引,MySQL 的前缀索引只覆盖前 N 字符 → **LIKE 命中不了后缀**,排序也不准。

### §2 Oracle

- **Oracle 把"空"和"NULL"合并成一个概念**:这是它和其他三方最大的语义分叉。ETL 里 `COALESCE(col, '')` 在 Oracle 上等于 `COALESCE(col, NULL)`,整段保护逻辑失效。
- **NLS 是隐式 schema**:会话级变量决定字面量怎么解析 → 同一份 SQL 在不同连接池节点上行为可能不同。**跨 Oracle 迁 PG 时,所有日期比较都要改成显式 `TO_DATE` / `DATE` 类型比较**,别依赖字面量。

### §3 SQL Server

- **SARGability = Search ARGumentability**:谓词能不能被"翻译"成索引查找。**能不能被翻译,只看一件事:比较的哪一侧被转换了**。修 SARG 永远从"别转换列"入手,不是从"加 CAST"入手。
- **`FORMAT()` 是展示层函数不是查询层函数**:它在执行计划里是一个不透明的标量 UDF,索引完全用不上。

### §4 跨方言

- **方言差异分两类**:**语法类**(能查文档、能机械替换)与**语义类**(查不到、只能对照表)。**工程上只有语义类值钱** —— 语法错会立刻报错,语义错会安静地给你错答案。

### §5 多 DB 协作

- **联邦查询是"运行时跨库",同步是"写入时跨库"**:联邦在查询时付跨网络 + 类型转换 + 无事务的代价;同步在写入时付延迟代价。**读多写少、数据可容忍分钟级延迟 → 同步;要实时、要事务 → 只能选一个主库,别联邦**。
- **查询门面的本质是"用一致性换简单性"**:异构源越多、联查越频繁,门面的收益越大。

### §6 迁移

- **迁移三段式**:① 出差异清单(§6 12 项);② 逐条映射(对照表);③ 回归跑同一批 SQL **比结果集而非比行数**(语义差异常常行数相同、内容不同)。

## Anti-patterns

### §1 MySQL

- ❌ `WHERE varchar_col = 123` → 隐式转换断索引 → 改成 `= '123'` 或建函数索引
- ❌ 用 `||` 拼字符串 → 那是逻辑或 → 用 `CONCAT()` / `CONCAT_WS()`
- ❌ 以为 DDL 可以事务回滚 → MySQL DDL 隐式 commit → 改 schema 前先备份
- ❌ 对长 varchar 建全列索引 → MySQL 会截断成前缀索引 → 显式指定前缀长度并确认查询能命中

### §2 Oracle

- ❌ `WHERE x = ''` → Oracle 里 `''` 是 NULL,**永远不匹配** → 改 `IS NULL`
- ❌ 依赖会话 NLS 解析日期字面量 → 生产连接必须显式设 `NLS_DATE_FORMAT` 等
- ❌ `ROWNUM < n` 当成"取前 n 行排序后的结果" → ROWNUM 在 ORDER BY **之前**生效 → 用 `ROW_NUMBER()` 或子查询先排后取
- ❌ `OFFSET ... FETCH` 不带 ORDER BY → 返回哪几行未定义 → 必须显式排序

### §3 SQL Server

- ❌ `WHERE varchar_col = 123` → varchar 优先级低于 int → 断索引 → 字面量加引号
- ❌ `WHERE ISNULL(col, 0) = 0` → 函数包裹列 → 改 `col = 0 OR col IS NULL`
- ❌ 用 `FORMAT(col, 'yyyy-MM')` 做查询过滤 → 慢一个数量级 → 用 `CONVERT(..., 23)`
- ❌ `WITH (NOLOCK)` 当性能优化 → 脏读 / 丢行 / 重复行 → 用 `READ COMMITTED SNAPSHOT`
- ❌ 深分页 `OFFSET 100000` → 扫掉并丢弃前 10 万行 → keyset 分页

### §4 跨方言

- ❌ 凭记忆迁移 → 语义默认值差异查不到 → 逐条对 §4 / §6
- ❌ 只比行数做回归 → 语义差异常常行数相同内容不同 → 比结果集

### §5 多 DB 协作

- ❌ 拿 `postgres_fdw` 连 MySQL / Oracle / MSSQL → **协议层就不支持** → 换同步门面或对应 FDW 扩展
- ❌ 在 FDW 上跑大表全量扫 + 本地 JOIN → 谓词下推不全 → 预聚合后同步
- ❌ 跨库 JOIN 要求跨库事务 → 联邦查询没有统一事务 → 接受最终一致或改架构

### §6 迁移

- ❌ 迁移不查空串语义 → Oracle 静默丢数据 → 必查
- ❌ 迁移不查隐式转换方向 → 索引断 → 必查

## Code Examples

### §1 MySQL 隐式转换断索引

```sql
-- ❌ varchar_col 与数字比较 → MySQL 把 varchar_col 转数字 → 索引失效
SELECT * FROM orders WHERE varchar_col = 123;

-- ✅ 字面量给对类型
SELECT * FROM orders WHERE varchar_col = '123';

-- ✅ 或给列建函数索引(8.0.13+),让索引覆盖转换后的表达式
CREATE INDEX idx_orders_col_num ON orders ((CAST(varchar_col AS UNSIGNED)));
-- 查询需写成与索引定义完全一致的表达式才能命中
SELECT * FROM orders WHERE CAST(varchar_col AS UNSIGNED) = 123;
```

### §1 MySQL 拼接与 upsert

```sql
-- ❌ || 是逻辑或,不是拼接
SELECT CONCAT(first_name, ' ', last_name) FROM users;

-- ✅ MySQL upsert
INSERT INTO t (id, val) VALUES (1, 'x')
ON DUPLICATE KEY UPDATE val = VALUES(val);
```

### §2 Oracle 空串与 NLS

```sql
-- ❌ '' 在 Oracle 里是 NULL,永远不匹配
SELECT * FROM t WHERE name = '';

-- ✅
SELECT * FROM t WHERE name IS NULL;
-- 反向:PG 迁过来要把所有 = '' 改成 IS NULL

-- ✅ 日期字面量显式化,不依赖会话 NLS
SELECT * FROM orders
WHERE order_date >= TO_DATE('2026-01-01', 'YYYY-MM-DD');
```

### §2 Oracle ROWNUM vs ROW_NUMBER

```sql
-- ❌ ROWNUM 在 ORDER BY 之前生效:先任取 10 行,再排序
SELECT * FROM (SELECT * FROM emp ORDER BY sal DESC) WHERE ROWNUM <= 10;
-- 若内层无 ORDER BY,结果随机;而这里的 ORDER BY 实际在 ROWNUM 之后才生效(不同版本行为有别)

-- ✅ 用窗口函数:先排再编号,语义确定
SELECT * FROM (
  SELECT e.*, ROW_NUMBER() OVER (ORDER BY sal DESC) rn FROM emp e
) WHERE rn <= 10;
```

### §3 SQL Server SARGability

```sql
-- ❌ varchar 优先级低于 int → 列被转换 → 索引断(全表扫描)
SELECT * FROM orders WHERE varchar_col = 123;

-- ✅ 字面量类型对齐
SELECT * FROM orders WHERE varchar_col = '123';

-- ❌ 函数包裹列
SELECT * FROM orders WHERE ISNULL(amount, 0) = 0;

-- ✅ 改写成可搜索形式
SELECT * FROM orders WHERE amount = 0 OR amount IS NULL;
```

### §3 SQL Server 分页与日期

```sql
-- ✅ keyset 分页(三方言一致)
SELECT TOP 100 * FROM orders WHERE id > @last_id ORDER BY id;

-- ❌ 深分页
SELECT * FROM orders ORDER BY id OFFSET 100000 ROWS FETCH NEXT 100 ROWS ONLY;

-- ❌ FORMAT 慢且断索引
SELECT * FROM orders WHERE FORMAT(order_date, 'yyyy-MM') = '2026-01';

-- ✅ CONVERT + style code
SELECT * FROM orders WHERE CONVERT(varchar(7), order_date, 126) = '2026-01';
```

### §4 三方言 keyset 分页对照

```sql
-- PostgreSQL
SELECT * FROM orders WHERE id > $1 ORDER BY id LIMIT 100;

-- MySQL 8.0
SELECT * FROM orders WHERE id > ? ORDER BY id LIMIT 100;

-- Oracle 12c+
SELECT * FROM orders WHERE id > :1
ORDER BY id
OFFSET 0 ROWS FETCH NEXT 100 ROWS ONLY;

-- SQL Server 2012+
SELECT TOP 100 * FROM orders WHERE id > @1 ORDER BY id;
```

### §5 同步门面(查询门面)

```text
        ┌──────────────┐
        │ MySQL 订单库 │──┐
        └──────────────┘  │  CDC / 定时 ETL
        ┌──────────────┐  ├──────────────────┐
        │ Oracle ERP   │──┤                  ▼
        └──────────────┘  │        ┌────────────────────┐
        ┌──────────────┐  │        │ PG 中间层(门面)     │
        │ MSSQL CRM    │──┘        │ ods_ / dwd_ / dws_ │
        └──────────────┘         └────────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
                 应用层 SQL            BI 报表            Agent 自然语言→SQL
              (只写一种方言)        (只写一种方言)        (只写一种方言)
```

### §5 联邦查询的真实代价

```sql
-- ⚠️ postgres_fdw 的远端必须是 PostgreSQL
-- 下面这条对 MySQL 远端**不成立**
CREATE EXTENSION postgres_fdw;
CREATE SERVER mysql_srv FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host '10.0.0.5', dbname 'orders', port '3306');
-- 实际会报:could not connect to server / protocol 不兼容

-- ✅ 跨方言的可落地方案:同步到 PG 后本地 JOIN
-- ETL(外部) → PG staging → 本地表 → 本地 JOIN(走 PG 索引)
SELECT o.id, o.amount, c.name
FROM dwd_order o
JOIN dwd_customer c ON c.id = o.customer_id;
```

### §6 迁移差异清单模板

```text
方言迁移检查(源: PostgreSQL → 目标: <MySQL|Oracle|SQL Server>)

[ ] 1. 空串语义      : '' == NULL?  → Oracle 是,其余否 → 所有 = '' 改写
[ ] 2. 隐式转换方向  : 数字→文本 / 文本→数字 → 确认哪侧被转换,改比较值类型
[ ] 3. 分页写法      : LIMIT / OFFSET-FETCH / TOP → 换 keyset 更稳
[ ] 4. DDL 事务性    : MySQL 隐式 commit → schema 变更先备份
[ ] 5. 标识符引用    : "x" / `x` / "X" / [x] → 大小写行为差异
[ ] 6. 字符串拼接    : || / CONCAT() / || / + → MySQL 的 || 是逻辑或
[ ] 7. 日期格式化    : TO_CHAR / DATE_FORMAT / TO_CHAR / CONVERT → 别用 FORMAT
[ ] 8. NULL 排序位置 : PG 默认 NULLS LAST / Oracle 默认 NULLS FIRST → 显式写
[ ] 9. 序列语法      : serial / AUTO_INCREMENT / SEQUENCE / IDENTITY
[ ] 10. 标识符大小写 : PG 小写 / MySQL 依 OS / Oracle 大写 / MSSQL 依 collation
[ ] 11. JSON 类型    : JSONB / JSON / 21c JSON / nvarchar+ISJSON
[ ] 12. 索引能力     : partial? / expression? / function? → 缺则改写谓词
```

## Reference Tables

### §1 MySQL vs PG 关键差异

| 维度 | PostgreSQL | MySQL 8.0 | 影响 |
|---|---|---|---|
| 隐式转换方向 | 数字 → 文本 | 文本 → 数字 | 断索引的侧相反 |
| 字符串拼接 | `\|\|` | `CONCAT()` | `\|\|` 是逻辑或 |
| DDL 事务性 | 事务内 | 隐式 commit | 不能回滚 schema 变更 |
| 主键 | 任意唯一列 | 必须整型 + 聚簇 | 分区/分库策略受限 |
| JSON 索引 | GIN `@>` | generated column + index | 写法完全不同 |
| 部分索引 | 支持 | 不支持 | 只能靠生成列/复合索引近似 |
| 全文检索 | tsvector + GIN | FULLTEXT | 配置与打分语义不同 |
| 计划查看 | EXPLAIN (ANALYZE) | EXPLAIN ANALYZE / FORMAT=JSON | JSON 计划更结构化 |

### §2 Oracle vs PG 关键差异

| 维度 | PostgreSQL | Oracle | 影响 |
|---|---|---|---|
| 空字符串 | `''` ≠ NULL | `''` = NULL | `= ''` 静默丢数据 |
| 标识符 | `"x"` 大小写敏感 | `"x"` 大小写敏感;不加引号转大写 | 对象名映射 |
| 隐式转换 | 靠 PG 严格类型 | 依赖 NLS 会话变量 | 跨会话行为不一致 |
| 分页 | LIMIT/OFFSET | OFFSET-FETCH(12c+) / ROWNUM | ROWNUM 语义陷阱 |
| 层级查询 | 递归 CTE | CONNECT BY PRIOR | 需改写 |
| 空值函数 | COALESCE | NVL / NVL2 / DECODE | 函数名不同 |
| 分区 | declarative | partitioning + 复合分区 | 运维模型不同 |
| 统计信息 | autovacuum ANALYZE | `ANALYZE` / DBMS_STATS | 计划漂移主因 |

### §3 SQL Server vs PG 关键差异

| 维度 | PostgreSQL | SQL Server | 影响 |
|---|---|---|---|
| 隐式转换 | 数字 → 文本 | varchar → int(varchar 优先级低) | SARGability 断点 |
| 标识符 | `"x"` | `[x]` / `"x"`(QUOTED_IDENTIFIER ON) | — |
| 字符串拼接 | `\|\|` | `+` / `CONCAT()` | `+` 遇 NULL 返回 NULL |
| 空字符串 | ≠ NULL | ≠ NULL | 与 Oracle 相反 |
| 分页 | LIMIT/OFFSET | OFFSET-FETCH(2012+) / TOP | — |
| 部分索引 | 支持 | filtered index | 能力等价 |
| 表达式索引 | 支持 | computed column + index | 需多步 |
| LATERAL | LATERAL | CROSS/OUTER APPLY | 等价 |
| 递归 CTE | 无层数默认限制 | 默认 100 层,需 MAXRECURSION 0 | 长递归报错 |
| 诊断 | EXPLAIN ANALYZE | STATISTICS IO/TIME + dm_* 视图 | 需装 profiler 类工具 |

### §4 跨方言语法对照

| 需求 | PostgreSQL | MySQL 8.0 | Oracle | SQL Server |
|---|---|---|---|---|
| 标识符引用 | `"col"` | `` `col` `` | `"COL"` | `[col]` |
| 字符串拼接 | `\|\|` | `CONCAT()` | `\|\|` | `+` / `CONCAT()` |
| 条件聚合 | `FILTER (WHERE ...)` | 无(用 CASE) | 无(用 CASE) | 无(用 CASE) |
| 空值替换 | `COALESCE` | `COALESCE` / `IFNULL` | `NVL` / `NVL2` | `ISNULL` / `COALESCE` |
| 字符串聚合 | `string_agg` | `GROUP_CONCAT` | `LISTAGG` | `STRING_AGG` |
| 日期格式化 | `TO_CHAR` | `DATE_FORMAT` | `TO_CHAR` | `CONVERT(..., 23)` |
| 分页 | `LIMIT n OFFSET m` | `LIMIT n OFFSET m` | `OFFSET-FETCH` / `ROWNUM` | `OFFSET-FETCH` / `TOP` |
| 自增 | `GENERATED ... AS IDENTITY` | `AUTO_INCREMENT` | `SEQUENCE` / `IDENTITY` | `IDENTITY(1,1)` |
| upsert | `ON CONFLICT DO UPDATE` | `ON DUPLICATE KEY UPDATE` | `MERGE INTO` | `MERGE` |
| LATERAL | `LATERAL` | `LATERAL`(8.0.14+) | `CROSS APPLY` | `CROSS APPLY` |
| JSON 取值 | `->` / `->>` / `@>` | `->` / `->>` / `JSON_CONTAINS` | `JSON_VALUE` | `JSON_VALUE` |
| 分组集 | `GROUPING SETS` | `GROUPING SETS` | `GROUPING SETS` | `GROUPING SETS` |
| NULL 排序默认 | NULLS LAST | NULLS FIRST(low→high) | NULLS FIRST | NULLS FIRST(升序) |

### §5 多 DB 协作模式选型

| 模式 | 延迟 | 事务一致性 | 运维成本 | 适用 |
|---|---|---|---|---|
| 同步门面(ETL/CDC → PG) | 分钟级 | 单库内强一致 | 中 | **异构源 ≥ 2 且要 JOIN**(推荐) |
| FDW 联邦(PG→PG) | 实时 | 只读,单库内一致 | 低 | 同构 PG 集群,只读联查 |
| FDW 联邦(第三方扩展) | 实时 | 无跨库事务 | 高 | 评估后小范围试点 |
| CDC(Kafka + Debezium/Canal) | 秒级 | 最终一致 | 高 | 大流量变更捕获 |
| 应用层 fan-out + join | 实时 | 无 | 中 | 结果集小、可容忍部分失败 |

### §6 迁移 12 项检查表

| # | 检查项 | PostgreSQL | MySQL 8.0 | Oracle | SQL Server | 踩坑后果 |
|---|---|---|---|---|---|---|
| 1 | 空串语义 | ≠ NULL | ≠ NULL | **= NULL** | ≠ NULL | 静默丢数据 |
| 2 | 隐式转换方向 | 数字→文本 | **文本→数字** | 依 NLS | **文本→数字** | 索引断 |
| 3 | 分页写法 | LIMIT/OFFSET | LIMIT/OFFSET | OFFSET-FETCH/ROWNUM | OFFSET-FETCH/TOP | 结果不稳定 |
| 4 | DDL 事务性 | 事务内 | **隐式 commit** | 事务内 | 事务内 | 无法回滚 |
| 5 | 标识符引用 | `"x"` | `` `x` `` | `"X"` | `[x]` | 语法报错 |
| 6 | 拼接 | `\|\|` | `CONCAT()` | `\|\|` | `+` | 逻辑或 / NULL |
| 7 | 日期格式化 | `TO_CHAR` | `DATE_FORMAT` | `TO_CHAR` | `CONVERT(...,23)` | 慢查询 |
| 8 | NULL 排序 | NULLS LAST | NULLS FIRST | NULLS FIRST | NULLS FIRST | 顺序差异 |
| 9 | 序列 | IDENTITY | AUTO_INCREMENT | SEQUENCE | IDENTITY | 语法报错 |
| 10 | 大小写 | 小写 | 依 OS / `lower_case_table_names` | 大写 | 依 collation | 对象找不到 |
| 11 | JSON | JSONB | JSON | 21c JSON | nvarchar+ISJSON | 索引/语法差异 |
| 12 | 索引能力 | partial/expression/GIN | 前缀/函数(8.0.13+) | 函数/位图 | filtered/computed | 谓词重写 |

## Key Takeaways

1. **先确认方言,再写 SQL** —— 语法差异查文档,**语义差异查对照表**
2. **四类语义地雷**:空串(Oracle)、隐式转换方向(MySQL/MSSQL)、分页原子性、DDL 事务性(MySQL)
3. **隐式转换的规律**:MySQL / SQL Server 是"文本被转成数字",PG 是"数字被转成文本" —— 断索引的侧相反
4. **修 SARG 永远从"别转换列"入手**,不是从"加 CAST"入手 —— CAST 一样断索引
5. **Oracle `''` = NULL** 是唯一例外 → 迁移时所有 `= ''` 必须改 `IS NULL`,否则静默丢数据
6. **`postgres_fdw` 远端必须是 PG** —— 跨方言 JOIN 走同步门面,不走联邦
7. **异构源 ≥ 2 且要 JOIN → 同步门面**;查询门面的本质是"用一致性换简单性"
8. **MySQL DDL 隐式 commit** → schema 变更不能靠事务回滚
9. **SQL Server `FORMAT()` 是展示层函数** → 查询过滤用 `CONVERT(..., 23)`
10. **迁移必查 12 项**(§6),且**回归要比结果集而非比行数**

## Connects To

- **sql-skill ch01**:8 子句执行顺序 / NULL 三值逻辑 —— 跨方言不变的部分
- **sql-skill ch07**:PG 特有(JSONB / array / GIN / FDW / 中文 schema)—— 与 §4 对照表的 PG 侧
- **sql-skill ch08**:索引与性能 —— 隐式转换断索引的通用机制
- **sql-skill ch09**:25+ 反模式 —— §1-§3 的方言反模式是其跨方言映射
- **sql-skill ch10**:SQL Agent 范式 / evidence-skill 协作 —— 4 道防线在多方言下同样适用
- **supporting/cheatsheet.md**:13 决策表 —— 跨方言速查入口
- **evidence-skill ch07**:postgres_fdw 跨 DB 部署细节(PG→PG 场景)
