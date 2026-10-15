# Glossary — sql-skill v0.1 关键术语

> 按字母顺序排列。每条:term — 定义(chapter 来源)
> 覆盖: ch01 语法铁律 + ch07 PG 特有 + ch08 索引与性能

## A

- **`ANY(array)`** — array 操作符,数组中任一元素匹配(`tags = ANY(ARRAY['a','b'])`)。(ch07 §2)
- **anti-pattern** — 反模式,常见错误做法;每 chapter "Anti-patterns" 段固定列出。(ch01/ch07/ch08)

## B

- **B-Tree (Balanced Tree)** — PG 默认索引,平衡搜索树,深度 4-5 覆盖百万级;等值 / 范围 / 前缀匹配都走。(ch08 §1)
- **Bitmap Heap Scan** — 索引多行批量回表;WHERE 返回多行但无需 ORDER BY 索引顺序时使用。(ch08 §6)
- **BRIN (Block Range Index)** — 块范围摘要,记录每块 min/max;append-only 时序大表空间省 99%。(ch08 §1)

## C

- **`CAST(col AS int)`** — 标准 SQL 类型转换,等价 `col::int`。(ch01 §2)
- **covering index** — 包含 INCLUDE 列的 B-Tree 索引,`Index Only Scan` 免回表。(ch08 §1)
- **`COALESCE(a, b, c)`** — 取第一个非 NULL 参数,优于 CASE WHEN。(ch01 §3)
- **`COUNT(*)` / `COUNT(col)` / `COUNT(DISTINCT col)`** — 行数 / 非 NULL 数 / 去重数,NULL 处理不同。(ch05 §1)
- **CTE (Common Table Expression)** — `WITH name AS (SELECT ...)` 命名临时结果集,query 级。(ch04 §1)
- **`CROSS JOIN`** — 笛卡尔积,m × n 行,无匹配条件;`FROM a, b` 隐式等价。(ch02 §3)

## D

- **`date` type (PG)** — PG date 类型,**不能直接 `SUBSTR`**,需 `TO_CHAR` 或 `::text` cast。(ch07 §5)
- **doubly linked list** — 索引叶子节点串联方式,支持顺序扫描。(ch08 §1)
- **`DENSE_RANK()`** — 窗口排序函数,1, 1, 2(并列后不跳号)。(ch03 §2)

## E

- **`EXCEPT`** — 集合差集,左表有但右表无(自动去重);顺序敏感。(ch06 §3)
- **`EXCEPT ALL`** — 集合差集,保留重复。(ch06 §3)
- **evidence-skill** — 业务侧 skill,18 章(BI / 中文 PG schema / nginx / FDW / MCP),与 sql-skill 互补。(ch10 §1)

## F

- **`FROM` clause** — SQL 执行第 1 阶段,决定数据源;表别名在 FROM 阶段生成。(ch01 §1)
- **`frameworks introduced`** — 每 chapter 固定段,列出 N 条铁律(When/How)。(ch01/ch07/ch08)
- **`FILTER (WHERE ...)`** — PG 9.4+ 聚合内条件过滤,优于 `SUM(CASE WHEN ...)`。(ch05 §4)
- **`FIRST_VALUE(col)` / `LAST_VALUE(col)` / `NTH_VALUE(col, n)`** — 窗口分析函数,拿窗口边界值;LAST_VALUE 需显式 frame。(ch03 §3)
- **`FULL [OUTER] JOIN`** — 保留两侧所有行,两边无匹配都填 NULL。(ch02 §2)

## E

- **`EXPLAIN`** — 显示 planner 估算成本 / rows / width,无实际执行。(ch08 §6)
- **`EXPLAIN ANALYZE`** — 真正执行并对比真实 vs 估算,看 `actual rows` / `actual time`。(ch08 §6)
- **expression index** — 表达式索引,`CREATE INDEX ... ON t (LOWER(col))`,WHERE `LOWER(col)=X` 才走索引。(ch08 §2)

## F

- **`FROM` clause** — SQL 执行第 1 阶段,决定数据源;表别名在 FROM 阶段生成。(ch01 §1)
- **`frameworks introduced`** — 每 chapter 固定段,列出 N 条铁律(When/How)。(ch01/ch07/ch08)

## G

- **GIN (Generalized Inverted Index)** — 多值倒排索引,JSONB / array / tsvector;`jsonb_path_ops` 只支持 `@>` 索引小一半。(ch07 §1/§3)
- **`GROUP BY`** — SQL 执行第 3 阶段,聚合前分组;列有索引可免 HashAggregate。(ch01 §1, ch05 §2, ch08 §4)
- **`GROUP BY ROLLUP(a, b)`** — 层级小计,(a, b) → (a) → ()。(ch05 §2)
- **`GROUP BY CUBE(a, b)`** — 所有维度组合,笛卡尔积聚合。(ch05 §2)
- **`GROUPING SETS ((a), (b), ())`** — 显式维度组合,比 ROLLUP / CUBE 灵活。(ch05 §5)
- **`GROUPING(col)` / `GROUPING_ID(...)`** — 多维报表中区分真实 NULL vs 聚合 NULL,0/1 bit mask。(ch05 §5)
- **GiST (Generalized Search Tree)** — 通用搜索树,几何 / 全文 / 范围类型。(ch07 §3)

## H

- **`HAVING`** — SQL 执行第 4 阶段,聚合后过滤(`COUNT(*) > 5`);**不能用列别名**;WHERE 不能用聚合函数。(ch01 §1, ch05 §3)

## I

- **`INTERSECT`** — 集合交集,两表共有行(自动去重)。(ch06 §2)
- **`INTERSECT ALL`** — 集合交集,保留重复。(ch06 §2)

## I

- **`INCLUDE (col1, col2)`** — PG 11+,B-Tree 索引附加非键列,免回表形成 covering index。(ch08 §1)
- **`INNER JOIN`** — 返回两表 ON 条件匹配的交集行;`JOIN` 默认就是 INNER JOIN。(ch02 §1)
- **`IS DISTINCT FROM`** — NULL-safe 等值,`NULL IS DISTINCT FROM NULL` 是 FALSE(等价)。(ch01 §3)
- **`IS NULL` / `IS NOT NULL`** — 唯一判断 NULL 的方法;`col = NULL` 永远 0 行。(ch01 §3, ch08 §2)
- **Index Only Scan** — covering index 命中,免回表;`EXPLAIN` 看 `Heap Fetches: 0`。(ch08 §6)

## J

- **JSONB** — 二进制 JSON,自动去重 + 压缩 + 支持 GIN;`@>` / `?` 操作符走索引。(ch07 §1)
- **JSON (vs JSONB)** — 文本 JSON,保留原序,不支持 GIN,几乎不用。(ch07 §1)
- **JOIN 7 种** — INNER / OUTER (LEFT/RIGHT/FULL) / CROSS / SELF / NATURAL / USING,JOIN 是多表查询核心。(ch02)

## K

- **key concepts** — 每 chapter 固定段,关键术语定义。(ch01/ch07/ch08)
- **keyset pagination** — `WHERE id > last_id LIMIT N`,比 `OFFSET M LIMIT N` 快几个数量级。(ch08 §5)

## L

- **leaf node** — 索引最底层节点,按 key 排序,通过 doubly linked list 串联。(ch08 §1)
- **LAG(col, n, default) / LEAD(col, n, default)** — 窗口分析函数,拿前/后第 n 行的 col 值。(ch03 §3)
- **`LEFT [OUTER] JOIN`** — 保留左表所有行,右表无匹配填 NULL;`OUTER` 关键字可省略。(ch02 §2)
- **LIKE** — 模式匹配,`'prefix%'` 走 B-Tree,`'%suffix'` / `'%mid%'` 不走。(ch08 §2)
- **`LIMIT` / `OFFSET`** — SQL 执行第 8 阶段裁剪结果;大 OFFSET 禁用,改 keyset pagination。(ch01 §1, ch08 §5)

## H

- **Hash Index** — 仅支持等值,PG 10+ WAL-logged crash-safe;B-Tree 已能覆盖等值,几乎无优势。(ch08 §1)
- **Hash Join** — 大表等值 JOIN;PG 8.3+ 默认;内存建 hash 表,内存不足 spill 磁盘 temp file。(ch08 §3)
- **`HAVING`** — SQL 执行第 4 阶段,聚合后过滤(`COUNT(*) > 5`)。(ch01 §1)

## I

- **`INCLUDE (col1, col2)`** — PG 11+,B-Tree 索引附加非键列,免回表形成 covering index。(ch08 §1)
- **`IS DISTINCT FROM`** — NULL-safe 等值,`NULL IS DISTINCT FROM NULL` 是 FALSE(等价)。(ch01 §3)
- **`IS NULL` / `IS NOT NULL`** — 唯一判断 NULL 的方法;`col = NULL` 永远 0 行。(ch01 §3, ch08 §2)
- **Index Only Scan** — covering index 命中,免回表;`EXPLAIN` 看 `Heap Fetches: 0`。(ch08 §6)

## J

- **JSONB** — 二进制 JSON,自动去重 + 压缩 + 支持 GIN;`@>` / `?` 操作符走索引。(ch07 §1)
- **JSON (vs JSONB)** — 文本 JSON,保留原序,不支持 GIN,几乎不用。(ch07 §1)

## K

- **key concepts** — 每 chapter 固定段,关键术语定义。(ch01/ch07/ch08)
- **keyset pagination** — `WHERE id > last_id LIMIT N`,比 `OFFSET M LIMIT N` 快几个数量级。(ch08 §5)

## L

- **leaf node** — 索引最底层节点,按 key 排序,通过 doubly linked list 串联。(ch08 §1)
- **LIKE** — 模式匹配,`'prefix%'` 走 B-Tree,`'%suffix'` / `'%mid%'` 不走。(ch08 §2)
- **`LIMIT` / `OFFSET`** — SQL 执行第 8 阶段裁剪结果;大 OFFSET 禁用,改 keyset pagination。(ch01 §1, ch08 §5)

## M

- **mental models** — 每 chapter 固定段,抽象心智模型。(ch01/ch07/ch08)
- **MATERIALIZED (CTE)** — PG 12+ 默认行为,CTE 一次计算多次用,失去谓词下推。(ch04 §3)
- **`MATERIALIZED` / `NOT MATERIALIZED` (CTE)** — PG 12+ 显式控制 CTE 物化行为。(ch04 §3)
- **Merge Join** — Sort Merge Join,两边都已排序场景,merge 两边排序流。(ch08 §3)

## N

- **NATURAL JOIN** — 自动按同名列匹配,无 ON 条件;**生产禁用**(加列 silently 改语义)。(ch02 §5)
- **Nested Loop** — 小数据集 + 索引 JOIN 场景;outer 顺序扫 + inner 索引 lookup 1 行。(ch08 §3)
- **N+1 problem** — 应用层 for 循环 N 次单条 query,应改 1 次批量 query + JOIN。(ch08 §3, ch02 §7, ch09 §6)
- **NULL** — "未知值",**`NULL = NULL` 是 NULL 不是 TRUE**;三值逻辑。(ch01 §3)
- **`NULLIF(a, b)`** — `a=b` 时返回 NULL,否则返回 a;用于"等于某值归 NULL"。(ch01 §3)
- **`NTILE(n)`** — 窗口分桶函数,把数据均分成 n 桶,返回桶号 1..n。(ch03 §2)

## O

- **`OVER` clause** — 窗口函数标志,`OVER (PARTITION BY ... ORDER BY ...)`;没有 OVER 的聚合是 GROUP BY。(ch03 §1)
- **operator class**:`CREATE INDEX ... USING btree (col varchar_pattern_ops)` 让 LIKE 前缀不走 collation 转换。(ch08 §2)
- **`ORDER BY`** — SQL 执行第 7 阶段,可引用列别名;列有索引可免 Sort。(ch01 §1, ch08 §4)

## P

- **`PARTITION BY`** — OVER 内子句,把数据分成多个窗口分区;省略时整表单窗口。(ch03 §1)
- **partial index** — `CREATE INDEX ... WHERE col IS NOT NULL`,只索引满足条件的行,体积小。(ch08 §2)
- **pgbouncer** — PG 连接池;**必 `pool_mode = session`**,transaction-mode 破坏 5 项(search_path / statement_timeout / FDW 事务 / prepared statements / advisory locks)。(ch07 §4)
- **`pg_stat_statements`** — PG extension,记录每条 query 统计信息(calls / total_exec_time / mean_exec_time),查慢 query top-N。(ch08 §6)
- **`percentile_cont(0.5) WITHIN GROUP (ORDER BY x)`** — PG 中位数计算,连续分布。(ch05 §1)
- **planner** — PG query planner,根据 cost-based 估算选择 plan;统计信息过期会选错。(ch08 §6)
- **postgres_fdw** — PG Foreign Data Wrapper,把另一个 PG server 的表映射成本地表。(ch07 §4)
- **`partial index`** — 同 "partial index"(重复收录)。

## N

- **Nested Loop** — 小数据集 + 索引 JOIN 场景;outer 顺序扫 + inner 索引 lookup 1 行。(ch08 §3)
- **N+1 problem** — 应用层 for 循环 N 次单条 query,应改 1 次批量 query + JOIN。(ch08 §3)
- **NULL** — "未知值",**`NULL = NULL` 是 NULL 不是 TRUE**;三值逻辑。(ch01 §3)
- **`NULLIF(a, b)`** — `a=b` 时返回 NULL,否则返回 a;用于"等于某值归 NULL"。(ch01 §3)

## O

- **operator class**:`CREATE INDEX ... USING btree (col varchar_pattern_ops)` 让 LIKE 前缀不走 collation 转换。(ch08 §2)
- **`ORDER BY`** — SQL 执行第 7 阶段,可引用列别名;列有索引可免 Sort。(ch01 §1, ch08 §4)

## P

- **partial index** — `CREATE INDEX ... WHERE col IS NOT NULL`,只索引满足条件的行,体积小。(ch08 §2)
- **pgbouncer** — PG 连接池;**必 `pool_mode = session`**,transaction-mode 破坏 5 项(search_path / statement_timeout / FDW 事务 / prepared statements / advisory locks)。(ch07 §4)
- **`pg_stat_statements`** — PG extension,记录每条 query 统计信息(calls / total_exec_time / mean_exec_time),查慢 query top-N。(ch08 §6)
- **planner** — PG query planner,根据 cost-based 估算选择 plan;统计信息过期会选错。(ch08 §6)
- **postgres_fdw** — PG Foreign Data Wrapper,把另一个 PG server 的表映射成本地表。(ch07 §4)
- **`partial index`** — 同 "partial index"(重复收录)。

## R

- **`RANK()`** — 窗口排序函数,1, 1, 3(并列跳号);区别于 `DENSE_RANK()`。(ch03 §2)
- **`RANGE BETWEEN ...`** — 帧子句,逻辑值边界(同值同行);适合时间范围滚动。(ch03 §6)
- **reference tables** — 每 chapter 固定段,决策表 / 映射表。(ch01/ch07/ch08)
- **Recursion (递归 CTE)** — `WITH RECURSIVE` + anchor + recursive part 组成,层层下钻。(ch04 §2)
- **`RIGHT [OUTER] JOIN`** — 保留右表所有行,左表无匹配填 NULL;几乎不用,改 LEFT。(ch02 §2)
- **`ROLLUP (a, b)`** — 层级小计,(a, b) → (a) → ()。(ch05 §2)
- **rows (EXPLAIN)** — planner 估算返回行数;实际行数从 EXPLAIN ANALYZE `actual rows` 看。(ch08 §6)
- **`ROWS BETWEEN ...`** — 帧子句,物理行边界(行数);适合固定行数滚动。(ch03 §6)
- **`ROW_NUMBER()`** — 窗口排序函数,1, 2, 3 唯一连续编号(无并列)。(ch03 §2)
- **ROWID** — 表行物理地址,索引 entry 引用 ROWID 找到对应表行。(ch08 §1)

## S

- **SELF JOIN** — 表与自身 JOIN,用不同别名区分;典型场景:员工-经理层次、同表序列对比。(ch02 §4)
- **Seq Scan** — 全表扫;小表(< 10000 行)或无索引可用时出现。(ch08 §6)
- **snake_case** — 命名风格 `my_table` `col_a`,与 camelCase 区分。(ch01 §4)
- **Sort (算子)** — 内存 / 磁盘排序;ORDER BY 列无索引时出现。(ch08 §6)
- **Sort Merge Join** — 两边都已排序的非等值 JOIN。(ch08 §3)

## U

- **`unnest(array_col)`** — 数组转行,与 LATERAL JOIN 配合展开。(ch07 §2)
- **`UNION`** — 集合合并,自动去重;内部 sort/hash 开销。(ch06 §1)
- **`UNION ALL`** — 集合合并,保留所有行;无去重开销,性能更好。(ch06 §1)
- **`USING(col)`** — 显式指定列名匹配,比 NATURAL 略好但仍隐式;不推荐。(ch02 §5)

## T

- **three-valued logic** — TRUE / FALSE / NULL (unknown);NULL 比较结果是 NULL。(ch01 §3)
- **`TO_CHAR(date, 'YYYY-MM')`** — 标准 SQL 格式化 date → string,替代 `SUBSTR(date, 1, 7)`。(ch07 §5)
- **Top-N optimization** — planner 遇到 `ORDER BY ... LIMIT N` 且 N 远小于表大小时,自动提前终止扫描。(ch08 §5)

## U

- **`unnest(array_col)`** — 数组转行,与 LATERAL JOIN 配合展开。(ch07 §2)

## V

- **`varchar_pattern_ops`** — operator class,让 B-Tree 索引上 LIKE 前缀匹配不走 collation 转换。(ch08 §2)

## W

- **`WHERE`** — SQL 执行第 2 阶段,行级过滤;**不能引用列别名**(别名还没生成)。(ch01 §1)
- **WHERE vs HAVING** — WHERE 行级过滤(聚合前);HAVING 聚合后过滤;WHERE 不能用聚合函数。(ch05 §3)
- **width (EXPLAIN)** — planner 估算每行字节数。(ch08 §6)
- **`WINDOW w AS (...)`** — PG 命名窗口子句,多个 OVER 共享同一窗口定义。(ch03 §5)
- **Window Function** — 窗口函数,OVER 子句定义,保留所有行 + 多一列聚合;与 GROUP BY 不替代。(ch03)

## X / Y / Z

- *无*

## 数字

- **2-segment path** — `taobao.mart_X`,正确跨 DB 路径。(ch07 §4)
- **3-segment path (错误)** — `taobao.bi.mart_X`,PG 看到 taobao 当 database 名,触发 `cross-database references are not implemented`。(ch07 §4)

## 中文

- **"店铺"** — PG 中文列名,raw + mart 表都有;SQL 写法 `"店铺"` 双引号。(ch07 §5)
- **"订单日期"** — PG 中文 date 类型列,需 `TO_CHAR` 或 `::text` cast 才能 SUBSTR。(ch07 §5)
- **"销售金额"** — PG 中文列名,numeric 类型,聚合 SUM 时双引号。(ch07 §5)
- **中文列名** — PG identifier quote 必须双引号包(`"店铺"`),无双引号 PG 当 string literal。(ch07 §5)
- **`ds` (假名)** — 真实列名是 `"订单日期"`,出现在 sales-overview 等 7+ page。(ch07 §5)
- **`shop_name` (假名)** — 真实列名是 `"店铺"`,13+ page 待修。(ch07 §5)
- **`stat_date` (假名)** — 真实列名 `"订单日期"` 或 `source_year_month`,视 mart 而定。(ch07 §5)

## ch09 反模式新增词条

### E

- **EAV (Entity-Attribute-Value)** — 反模式,三列动态属性表;长期维护成本高;改 JSONB + GIN。(ch09 §1)

---

## ch06 / ch10 新增词条(Phase 3c 完成)

### C

- **civilian7 1065 题** — SQL 评测题库,beginner / intermediate / advanced 三档。(ch10 §5)
- **Core 28 page** — Evidence BI 性能基线,详 [evidence-skill ch14](../../evidence/evidence-skill/chapters/ch14-performance.md)。(ch10 §4)

### E

- **evidence-skill** — 业务侧 skill,18 章;与 sql-skill 互补,不重写。(ch10 §1)

### F

- **4 道防线** — AI agent 跑 SQL:`readonly + sqlglot + statement_timeout + LIMIT` 纵深防御。(ch09 §7, ch10 §2)

### I

- **`information_schema.columns`** — PG 系统视图,查表真实列名 + 类型。(ch10 §3)

### N

- **nginx immutable** — `/_app/immutable/` 强缓存静态资源,详 [evidence-skill ch14](../../evidence/evidence-skill/chapters/ch14-performance.md)。(ch10 §4)

### S

- **sqlglot AST 解析** — 4 道防线之一,白名单 DDL/DML 防注入。(ch09 §7, ch10 §2)

### T

- **三层 lookup** — cheatsheet → chapter → evidence-skill;快速决策顺序。(ch10 §6)

### U

- **UNION ALL 包装 view** — 整合多源数据为单视图,常用模式。(ch06 §1)

### N

- **N+1 problem** — 反模式,应用层 for 循环 N 次单条 query;改批量 + JOIN。(ch02 §7, ch09 §6)

### S

- **`SELECT *`** — 反模式,拉全列;大表 IO 浪费 + schema 耦合;改 explicit columns。(ch09 §2)
- **SQL 注入** — 反模式,字符串拼 SQL 让用户输入当 code 执行;改参数化绑定。(ch09 §7)
- **superuser role** — 反模式,agent 用 superuser 跑 query;改 readonly role + 4 道防线。(ch09 §7)

### W

- **wide table (宽表)** — 反模式,200+ 列宽表更新开销巨大;拆表按业务域。(ch09 §1)

---

## ch02-ch05 新增词条(Phase 3b 完成)

### A

- **anti-join** — `LEFT JOIN ... WHERE right.id IS NULL`,找左表无关联的行。(ch02 §2)
- **anti-join (集合操作转换)** — `A EXCEPT B` 等价 `LEFT JOIN + IS NULL`。(ch06 §3)

### C

- **CTE 嵌套滥用** — 反模式,5+ 层 CTE 嵌套可读性下降;改子查询或临时表。(ch04 §7)
- **CTE 不能建索引** — 大结果集 + 高频 JOIN 改临时表 + `CREATE INDEX`。(ch04 §4)

### F

- **FILTER 子句滥用** — 反模式,复杂 `SUM(CASE WHEN ...)` 改 `SUM(...) FILTER (WHERE ...)`。(ch05 §4)

### G

- **GROUP BY 列建索引** — 免 HashAggregate,改 Index Scan + GroupAggregate 流式聚合。(ch05 §2, ch08 §4)

### M

- **MATERIALIZED CTE 决策** — 大 CTE 多次引用用 MATERIALIZED,单次引用 + 强过滤用 NOT MATERIALIZED。(ch04 §3)

### O

- **OUTER JOIN 后 WHERE 误用** — 反模式,`LEFT JOIN ... WHERE right.col = X` 把 unmatched 过滤掉,变 INNER JOIN 语义。(ch02 §7)

### R

- **ROLLUP / CUBE / GROUPING SETS** — 多维聚合,一次 query 算多个维度,省多次 GROUP BY。(ch05 §5)

### S

- **SELECT * + GROUP BY** — 反模式,PG 严格拒绝列歧义;改 explicit columns + 聚合。(ch05 §6)


---

## 沉淀入口

- **章节源**:`E:/obsidian/SQL/08-sql-skill/chapters/ch01-grammar.md` / `ch07-pg-specific.md` / `ch08-indexes-perf.md`
- **本地资料源**:`E:/obsidian/SQL/` 7 个沉淀目录(详见 `00-索引.md`)
- **luke 索引**:`E:/obsidian/SQL/03-use-the-index-luke/README.md`(48 章节映射)
- **证据 skill**:`E:/Users/Duanyi/.claude/skills/evidence-skill/`(18 章)
