# Chapter 10: SQL Agent 范式 / 与 evidence-skill 协作 / 评测

## Core Idea

sql-skill v1.0 沉淀 10 章通用 SQL 知识(语法 / 索引 / JOIN / 窗口 / CTE / 聚合 / 集合 / 反模式),与 [evidence-skill](../../evidence/evidence-skill/SKILL.md) 业务侧(BI / 中文 PG schema / nginx / FDW / MCP)严格互补。**ch10 不重写 evidence-skill 18 章**,只讲三件事:① **SQL Agent 范式**(MCP + 4 道防线);② **评测集**(civilian7 1065 题筛选);③ **v1.0 沉淀清单**(ch01-ch10 + 4 supporting 文件)。**核心铁律**:写 SQL / 排错 / 调性能,先查 cheatsheet,再翻对应 chapter,最后查 evidence-skill 业务侧 — **三层 lookup 顺序固定**。

## Frameworks Introduced

### §1 sql-skill 与 evidence-skill 边界(已固化)— 1 条铁律

- **sql-skill 讲通用,evidence-skill 讲业务侧**:sql-skill ch01-ch10 是 PostgreSQL 通用视角;evidence-skill 18 章是 Evidence BI / 中文 PG schema / nginx / FDW / MCP 业务落地。**ch10 边界**:不重写 evidence-skill 18 章内容,只引 + 协作范式。

### §2 SQL Agent 范式(MCP + 4 道防线,引用 evidence-skill ch16)— 2 条铁律

- **AI agent 跑 SQL 必 4 道防线**:`readonly role` + `sqlglot AST` 白名单 + `statement_timeout` + `LIMIT clamp`;任一被攻破其他兜底(纵深防御,详 [ch09 §7](ch09-antipatterns.md) + [evidence-skill ch16](../../evidence/evidence-skill/chapters/ch16-mcp-selfhost.md))。
- **schema 路由 + 中文 schema 自动 wrap**:多数据库场景用 schema 选择 + 权限治理(详 [evidence-skill ch01](../../evidence/evidence-skill/chapters/ch01-quickstart.md) connection.yaml);中文列双引号 wrap 防 `column "ds" does not exist`(详 [evidence-skill ch05](../../evidence/evidence-skill/chapters/ch05-sql-antipatterns.md))。

### §3 中文 schema 假名修复流程(引用 evidence-skill ch05)— 1 条铁律

- **13+ page 待修列名清单**:`ds` → `"订单日期"`、`shop_name` → `"店铺"`、`stat_date` → `"订单日期"` 或 `source_year_month`;evidence-skill ch05 是业务侧权威,sql-skill ch07 §5 只引不重写(详 [ch07 §5](ch07-pg-specific.md))。

### §4 BI 场景性能与 Core 28 page(引用 evidence-skill ch14)— 1 条铁律

- **BI 性能铁律归 evidence-skill ch14**:Core 28 page + nginx immutable + pgbouncer session-mode + FDW 跨 DB;sql-skill ch08 §3 / §6 讲通用 EXPLAIN,不重写 BI 适配(详 [evidence-skill ch14](../../evidence/evidence-skill/chapters/ch14-performance.md))。

### §5 评测集(引用 civilian7 1065 题)— 1 条铁律

- **评测源沿用 civilian7**:1065 题覆盖 beginner / intermediate / advanced;sql-skill 不重写题库筛选机制,ch09 §1-§7 / ch02 §7 / ch03 §7 反模式引用具体路径,Phase 4+ 自动化评测用。

### §6 sql-skill v1.0 沉淀清单— 1 条铁律

- **三层 lookup 顺序固定**:① cheatsheet(13 决策表 + 18 关键经验)→ ② 对应 chapter(ch01-ch10)→ ③ evidence-skill 业务侧(ch05/ch07/ch14/ch16);reviewer 5 秒判断走哪一层。

## Key Concepts

### §1 边界

- **sql-skill**:10 章通用 SQL 知识
- **evidence-skill**:18 章业务落地知识
- **联动**:sql-skill ch02-09 + evidence-skill ch05/ch07/ch14/ch16 互补

### §2 SQL Agent 范式

- **MCP self-host**:AI agent 跑 SQL 的标准协议,详 [evidence-skill ch16](../../evidence/evidence-skill/chapters/ch16-mcp-selfhost.md)
- **4 道防线**:readonly + sqlglot + statement_timeout + LIMIT,详 [ch09 §7](ch09-antipatterns.md)
- **schema 路由**:多 DB 场景选 schema,详 [evidence-skill ch01](../../evidence/evidence-skill/chapters/ch01-quickstart.md)

### §3 中文 schema

- **`ds` 假名**:真实列名 `"订单日期"`,7+ page 待修
- **`shop_name` 假名**:真实列名 `"店铺"`,13+ page 待修
- **`stat_date` 假名**:mart vs raw 表列名差异

### §4 BI 场景性能

- **Core 28 page**:Evidence BI 性能监控点
- **nginx immutable**:静态资源 `/_app/immutable/` 缓存
- **pgbouncer session-mode**:连接池,详 [ch07 §4](ch07-pg-specific.md)

### §5 评测集

- **civilian7 1065 题**:beginner / intermediate / advanced
- **评测源**:沿用,不重写题库筛选

### §6 v1.0 沉淀

- **三层 lookup**:cheatsheet → chapter → evidence-skill
- **9 段结构**:每 chapter 9 段固定
- **v1.0 完整版**:10 章 + 4 辅助文件

## Mental Models

### §1 边界

- **sql-skill 是"语法 + 性能 + 反模式"通用层**:跨 DB 通用,PostgreSQL 视角。
- **evidence-skill 是"业务落地"层**:Evidence BI 工具链 + 中文 schema 业务侧权威。

### §2 SQL Agent 范式

- **4 道防线是"纵深防御"**:readonly 防破坏;sqlglot 防注入;timeout 防慢 query;LIMIT 防 OOM。
- **schema 路由是"权限治理"**:BM25 75-97% 减 token 借鉴(详 [evidence-skill ch01](../../evidence/evidence-skill/chapters/ch01-quickstart.md))。

### §3 中文 schema

- **假名是"认知错位"**:业务 spec 用 `ds`,PG 列是 `"订单日期"`,agent 写 SQL 必须翻译。
- **修复流程**:查 `information_schema.columns` → 找真列名 → 替换假名 → 加双引号。

### §4 BI 场景性能

- **Core 28 page 是"BI 性能基线"**:超过 28 page 触发慢 query 告警。
- **nginx immutable 是"静态资源优化"**:immutable assets 强缓存。

### §5 评测集

- **civilian7 是"实战题库"**:1065 题覆盖 SQL 各场景;评测 SQL 生成质量。

### §6 v1.0 沉淀

- **三层 lookup 是"快速决策"**:不要逐章翻,先 cheatsheet 决策表,再针对性 chapter。
- **v1.0 是"完整 10 章"**:Phase 2 + 3a + 3b + 3c 4 阶段沉淀。

## Anti-patterns

### §1

- ❌ 重复 evidence-skill 18 章内容 → 只引 + 协作范式

### §2

- ❌ AI agent 跑 SQL 漏 4 道防线 → readonly + sqlglot + timeout + LIMIT 必齐
- ❌ 4 道防线任一缺失 → 纵深防御,任一攻破其他兜底

### §3

- ❌ 中文 schema 假名未修复 → 查 `information_schema.columns` 拿真列名
- ❌ 中文列无双引号 → `"店铺"` `"订单日期"` 双引号

### §4

- ❌ BI 性能问题套用通用 EXPLAIN → 走 evidence-skill ch14 BI 场景适配
- ❌ FDW 跨 DB 高频 JOIN → 预聚合本地表

### §5

- ❌ 自建题库不沿用 civilian7 → 沿用 1065 题,Phase 4+ 自动化

### §6

- ❌ 写 SQL 不查 cheatsheet → 13 决策表先查,再翻 chapter
- ❌ 业务侧雷区查 sql-skill 通用层 → 走 evidence-skill ch05/ch07/ch14/ch16

## Code Examples

### §1 sql-skill 与 evidence-skill 联动

```python
# 伪代码:写 SQL 前三层 lookup
def write_sql(question, db):
    # Layer 1: cheatsheet 决策快查
    decision = cheatsheet_lookup(question)
    if decision.match:
        return decision.sql_template

    # Layer 2: 对应 chapter
    chapter = chapter_lookup(question)
    if chapter:
        sql = chapter.apply(question, db)

    # Layer 3: evidence-skill 业务侧雷区
    evidence_check(sql, db.schema)
    # 中文 schema 双引号 wrap / 假名修复 / 4 道防线
    return sql
```

### §2 SQL Agent 4 道防线(详 [ch09 §7](ch09-antipatterns.md) + [evidence-skill ch16](../../evidence/evidence-skill/chapters/ch16-mcp-selfhost.md))

```python
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

### §3 中文 schema 假名修复

```sql
-- ❌ 假名未修复
SELECT ds, shop_name FROM sales_overview;
-- ERROR: column "ds" does not exist

-- ✅ 查 information_schema 拿真列名
SELECT column_name FROM information_schema.columns
WHERE table_name = 'mart_shop_kpi_daily' AND table_schema = 'taobao';
-- 找到:source_year_month, "店铺", ...

-- ✅ 改真列名 + 双引号
SELECT "source_year_month", "店铺" FROM taobao.mart_shop_kpi_daily;
```

### §4 BI 场景性能(详 [evidence-skill ch14](../../evidence/evidence-skill/chapters/ch14-performance.md))

```nginx
# nginx immutable 配置(详 evidence-skill ch14)
location /_app/immutable/ {
    add_header Cache-Control "public, max-age=31536000, immutable";
}
```

```ini
# pgbouncer session-mode(详 [ch07 §4](ch07-pg-specific.md))
[pgbouncer]
pool_mode = session  # FDW 必需
```

### §5 civilian7 评测(引用 + Phase 4+ 自动化)

```bash
# civilian7 题库路径(详 _knowledge_base 调研笔记)
ls "E:/obsidian/SQL/02-sql-tutorial-civilian7/exercises/beginner/"
# civilian7 1065 题 / 引用 ch09 §1-§7 / ch02 §7 / ch03 §7 反模式
```

### §6 v1.0 三层 lookup 顺序

```text
1. cheatsheet.md(13 决策表 + 18 关键经验)
   ↓ 不够?
2. 对应 chapter(ch01-ch10)
   ↓ 业务侧?
3. evidence-skill 业务侧(ch05 中文 schema / ch07 FDW / ch14 BI 性能 / ch16 MCP)
```

## Reference Tables

### §1 边界决策表

| 主题 | 查 sql-skill | 查 evidence-skill |
|---|---|---|
| 通用语法 / 性能 / 反模式 | ✓ ch01-ch10 | — |
| 中文 schema 业务侧 | ch07 §5 引 | ch05 权威 |
| FDW 跨 DB | ch07 §4 引 | ch07 5 步 SQL 权威 |
| BI 场景性能 | ch08 §3/§6 引 | ch14 nginx + pgbouncer 权威 |
| MCP 4 道防线 | ch09 §7 引 | ch16 部署细节权威 |

### §2 SQL Agent 4 道防线

| 防线 | 作用 | 详 |
|---|---|---|
| [1] readonly role | 防 DDL/DML 生效 | ch09 §7 + evidence-skill ch16 |
| [2] sqlglot AST | 防 SQL 注入 | ch09 §7 + evidence-skill ch16 |
| [3] statement_timeout | 防慢 query | ch08 §6 + evidence-skill ch16 |
| [4] LIMIT clamp | 防大结果集 OOM | ch09 §7 + evidence-skill ch16 |

### §3 中文 schema 假名修复

| 假名 | 真实列名 | 表 |
|---|---|---|
| `ds` | `"订单日期"` | raw 表 |
| `ds` | `source_year_month` | mart 表 |
| `shop_name` | `"店铺"` | raw + mart |
| `stat_date` | `"订单日期"` 或 `source_year_month` | 视 mart 而定 |

### §4 BI 性能铁律

| 主题 | 详 |
|---|---|
| Core 28 page | evidence-skill ch14 |
| nginx immutable | evidence-skill ch14 |
| pgbouncer session-mode | ch07 §4 + evidence-skill ch14 |
| FDW 跨 DB JOIN | ch07 §4 + evidence-skill ch07 |

### §5 评测源

| 来源 | 数量 | 详 |
|---|---|---|
| civilian7 | 1065 题 | beginner + intermediate + advanced |
| nl2sql-handbook | 综述 + slides | Phase 4+ 自动化 |
| awesome-text2sql | 论文 / 工具 | Phase 4+ 调研 |

### §6 v1.0 沉淀清单

| 文件 | 行数 | 状态 |
|---|---|---|
| SKILL.md | 入口 + 12 framework | Phase 3c 更新 |
| glossary.md | 关键术语 | Phase 3c 更新 |
| patterns.md | 8 模式 + 反模式总表 | Phase 3c 更新 |
| cheatsheet.md | 13 决策表 + 18 关键经验 | Phase 3c 更新 |
| ch01-grammar.md | 256 行 | Phase 2 |
| ch02-joins.md | 450 行 | Phase 3b |
| ch03-window-functions.md | 488 行 | Phase 3b |
| ch04-cte-recursion.md | 454 行 | Phase 3b |
| ch05-aggregates.md | 448 行 | Phase 3b |
| ch06-set-ops.md | 352 行 | Phase 3c |
| ch07-pg-specific.md | 322 行 | Phase 2 |
| ch08-indexes-perf.md | 405 行 | Phase 2 |
| ch09-antipatterns.md | 429 行 | Phase 3a |
| ch10-evidence-bridge.md | ~250 行 | Phase 3c |

## Key Takeaways

1. **sql-skill v1.0 = 10 章 + 4 辅助文件**:ch01-ch10 + SKILL/glossary/patterns/cheatsheet;与 evidence-skill 18 章严格互补
2. **三层 lookup 顺序固定**:cheatsheet → chapter → evidence-skill;不要逐章翻
3. **SQL Agent 4 道防线必齐**:readonly + sqlglot + statement_timeout + LIMIT;任一被攻破其他兜底
4. **ch10 不重写 evidence-skill 18 章内容**:只引 + 协作范式;中文 schema / FDW / BI 性能 / MCP 部署细节走 evidence-skill
5. **中文 schema 假名修复流程**:查 `information_schema.columns` → 找真列名 → 替换假名 → 加双引号
6. **BI 性能归 evidence-skill ch14**:Core 28 page + nginx immutable + pgbouncer session-mode;sql-skill ch08 §3/§6 只讲通用 EXPLAIN
7. **评测源沿用 civilian7 1065 题**:不重写题库筛选;Phase 4+ 自动化评测
8. **schema 路由 + 中文 schema 自动 wrap**:多 DB 场景 + 假名修复是 agent 跑 SQL 的标准前置
9. **v1.0 沉淀路径清晰**:Phase 2(3 章)→ Phase 3a(ch09)→ Phase 3b(ch02-ch05)→ Phase 3c(ch06/ch10);总行数 ~3700
10. **未来扩展(Phase 4+)**:自动化评测 / 多 DB 支持(MySQL/Oracle/SQL Server) / 与 evidence-skill 联动测试

## Connects To

- **sql-skill ch01-ch10**:所有 chapter(10 章完整版,详 Connects To 段)
- **evidence-skill ch01**:quickstart + connection.yaml(schema 路由)
- **evidence-skill ch05**:中文 schema 业务侧权威(13+ page 假名清单)
- **evidence-skill ch07**:postgres_fdw 跨 DB(5 步 SQL + 2-segment path)
- **evidence-skill ch14**:BI 场景性能(Core 28 page + nginx + pgbouncer)
- **evidence-skill ch16**:MCP self-host 4 道 SQL 防线部署细节
- **evidence-skill ch18**:完整 18 章索引