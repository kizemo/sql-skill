# 03-use-the-index-luke — 在线 SQL 教程镜像

> 包含 3 个核心在线教程的完整 HTML 镜像。
> 下载时间：2026-10-13

## 目录结构

```
03-use-the-index-luke/
├── README.md       ← 本文件
├── luke/           ← Use The Index, Luke (Markus Winand) — 48 章节
├── sqlbolt/        ← SQLBolt 互动教程 — 17 课程（18 中 1 个 HTTP 500）
└── pg-docs/        ← PostgreSQL 官方文档关键章节 — 5 章节
```

## luke/ (1.4M, 48 文件)

**来源**：https://use-the-index-luke.com/
**作者**：Markus Winand（SQL Performance Explained 同作者，业界 SQL 索引权威）
**License**：免费阅读

### 章节清单（按主题分组）

#### Anatomy — 索引结构
- `sql-anatomy-the-tree.html` — B-Tree 结构
- `sql-anatomy-the-leaf-nodes.html` — 叶子节点与有序性
- `sql-anatomy-slow-indexes.html` — 为什么索引会慢

#### Where Clause — WHERE 子句索引（最丰富）
- `sql-where-clause-null.html`
- `sql-where-clause-null/index.html`
- `sql-where-clause-null/not-null-constraint.html`
- `sql-where-clause-null/partial-index.html`
- `sql-where-clause-functions.html`
- `sql-where-clause-functions/case-insensitive-search.html`
- `sql-where-clause-functions/over-indexing.html`
- `sql-where-clause-functions/user-defined-functions.html`
- `sql-where-clause-obfuscation.html`
- `sql-where-clause-obfuscation/concatenation.html`
- `sql-where-clause-obfuscation/dates.html`
- `sql-where-clause-obfuscation/math.html`
- `sql-where-clause-obfuscation/numeric-strings.html`
- `sql-where-clause-obfuscation/smart-logic.html`
- `sql-where-clause-searching-for-ranges.html`
- `sql-where-clause-searching-for-ranges/greater-less-between-tuning-sql-access-filter-predicates.html`
- `sql-where-clause-searching-for-ranges/index-merge-performance.html`
- `sql-where-clause-searching-for-ranges/like-performance-tuning.html`
- `sql-where-clause-the-equals-operator.html`
- `sql-where-clause-the-equals-operator/concatenated-keys.html`
- `sql-where-clause-the-equals-operator/primary-keys.html`
- `sql-where-clause-the-equals-operator/slow-indexes-part-ii.html`
- `sql-where-clause-bind-parameters.html`
- `sql-where-clause-partial-and-filtered-indexes.html`

#### Clustering — 聚簇索引
- `sql-clustering-index-filter-predicates.html`
- `sql-clustering-index-only-scan-covering-index.html` — 覆盖索引
- `sql-clustering-index-organized-clustered-index.html`

#### Join — JOIN 算法
- `sql-join-hash-join-partial-objects.html`
- `sql-join-nested-loops-join-n1-problem.html`
- `sql-join-sort-merge-join.html`

#### Sorting & Grouping
- `sql-sorting-grouping-indexed-group-by.html`
- `sql-sorting-grouping-indexed-order-by.html`
- `sql-sorting-grouping-order-by-asc-desc-nulls-last.html`

#### Partial Results — 分页与窗口
- `sql-partial-results-fetch-next-page.html`
- `sql-partial-results-top-n-queries.html`
- `sql-partial-results-window-functions.html`

#### DML — 数据修改
- `sql-dml-delete.html`
- `sql-dml-insert.html`
- `sql-dml-update.html`

#### Performance
- `sql-explain-plan.html` — 执行计划阅读
- `sql-testing-scalability.html`
- `sql-testing-scalability-data-volume.html`
- `sql-testing-scalability-response-time-throughput-scaling-horizontal.html`
- `sql-testing-scalability-system-load.html`
- `sql-myth-directory.html`

#### Reference
- `sql-example-schema.html` — 范例 schema
- `sql-glossary.html` — 术语表
- `sql-preface.html` — 序言
- `sql-table-of-contents.html` — 目录
- `index.html` — 首页

### sql-skill 章节对应

**ch08-indexes-perf 章节的核心来源**：
- 索引结构 → ch08.1
- WHERE 子句索引 → ch08.2
- JOIN 算法 → ch08.3
- 排序/分组 → ch08.4
- 分页/窗口 → ch08.5
- EXPLAIN → ch08.6

---

## sqlbolt/ (360K, 17 文件)

**来源**：https://sqlbolt.com/
**License**：免费使用

### 课程清单
- `introduction.html` — 介绍
- `select_queries_introduction.html` — SELECT 入门
- `select_queries_with_constraints.html` — SELECT with WHERE
- `select_queries_with_constraints_pt_2.html`
- `select_queries_with_expressions.html` — 表达式
- `select_queries_with_nulls.html` — NULL 处理
- `select_queries_with_aggregates.html` — 聚合
- `select_queries_with_aggregates_pt_2.html`
- `select_queries_with_order_of_execution.html` — 执行顺序
- `select_queries_with_joins.html` — JOIN
- `select_queries_review.html` — 复习
- `filtering_sorting_query_results.html` — 过滤与排序
- `inserting_rows.html` — INSERT
- `updating_rows.html` — UPDATE
- `deleting_rows.html` — DELETE
- `creating_tables.html` — CREATE TABLE
- `altering_tables.html` — ALTER TABLE
- `dropping_tables.html` — DROP TABLE

（注：`end.html` 课程返回 HTTP 500，未能下载）

### sql-skill 章节对应
- ch01-grammar 入门
- ch02-joins
- ch05-aggregates

---

## pg-docs/ (108K, 5 文件)

**来源**：https://www.postgresql.org/docs/current/
**License**：PG 官方文档（PostgreSQL License）

### 章节清单
- `tutorial.html` — PG 入门教程
- `queries.html` — 查询
- `functions.html` — 函数与运算符
- `indexes.html` — 索引
- `performance-tips.html` — 性能调优

### sql-skill 章节对应
- ch07-pg-specific 权威引用
- ch08-indexes-perf 补充
