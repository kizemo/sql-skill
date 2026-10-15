# SQL 资料沉淀索引

> sql-skill 项目的原始资料沉淀目录。
> 下载时间：2026-10-13
> 来源：GitHub 仓库镜像 + 官方文档镜像
> 用途：作为沉淀 sql-skill 的证据层（evidence layer），后续由 OpenClaw memory-wiki 合成 wiki 页面

## 目录索引

```
SQL/
├── 00-索引.md                  ← 本文件
├── 01-nl2sql-handbook/         1.6k⭐ HKUST TKDE 25+VLDB 24/25 综述
├── 02-sql-tutorial-civilian7/  228⭐ 30 表/750K 行 SQL 实战教程
├── 03-use-the-index-luke/      Markus Winand 索引圣经全章节
├── 04-awesome-postgres/        12k⭐ PG 软件/工具/资源汇总
├── 05-sql-style-guide/         1.1k⭐ Matt Mazur SQL 风格指南
├── 06-awesome-text2sql/        3.7k⭐ Text2SQL 资源汇总
└── 07-awesome-llm-text2sql/    1.4k⭐ LLM-Text2SQL 论文集
```

## 资料分级与 sql-skill 章节对应

### Tier 1 — 必读（沉淀 sql-skill 核心知识源）

**01-nl2sql-handbook/**
- 来源：https://github.com/HKUSTDial/NL2SQL_Handbook
- 大小：199M
- License：见仓库 LICENSE
- 关键文件：
  - `TKDE_Survey.pdf` — TKDE 2025 综述：A Survey of Text-to-SQL in the Era of LLMs
  - `VLDB_Tutorial.pdf` — VLDB 2025 教程 PDF
  - `slides/NL2SQL_handbook.pdf` — 演讲 slides
  - `chapter/Benchmark.md` — Benchmark 综述
  - `chapter/Error_Analysis.md` — 错误分析
  - `chapter/Evaluation.md` — 评估方法
  - `chapter/Pre_Processing.md` — 预处理
  - `chapter/Post_Processing.md` — 后处理
  - `chapter/Translation_method.md` — 翻译方法
- skill 章节对应：ch10-evidence-compat + Phase 3 拓展

**02-sql-tutorial-civilian7/**
- 来源：https://github.com/civilian7/sql-tutorial
- 大小：13M
- License：见仓库 LICENSE
- 关键文件：
  - `docs/en/` — 27 课英文教程
  - `docs/ko/` — 27 课韩文教程
  - `exercises/beginner/` + `intermediate/` + `advanced/` + `lectures/` — 1065 题
  - `data/` — schema 与数据生成器
  - `src/` — Python 生成器代码
- skill 章节对应：ch01-grammar / ch02-joins / ch05-aggregates 入门素材 + 评测用例

**03-use-the-index-luke/**
- 来源：https://use-the-index-luke.com/ + https://sqlbolt.com/ + https://www.postgresql.org/docs/
- 作者：Markus Winand（SQL Performance Explained 同作者）
- 大小：约 1.9M（含 3 个在线教程）
- 包含：
  - `luke/` — 48 章节 use-the-index-luke（索引圣经）
  - `sqlbolt/` — 17 课程 SQLBolt（互动入门）
  - `pg-docs/` — 5 章节 PG 官方文档
- 关键主题：
  - `sql-anatomy-*` — B-Tree 索引结构
  - `sql-clustering-*` — 聚簇索引与覆盖索引
  - `sql-where-clause-*` — WHERE 子句索引（最丰富，20+ 章节）
  - `sql-join-*` — JOIN 算法（Hash / Nested Loop / Sort Merge）
  - `sql-sorting-grouping-*` — ORDER BY / GROUP BY 索引
  - `sql-partial-results-*` — 分页（Top-N / 窗口函数）
  - `sql-dml-*` — DML 与索引维护
  - `sql-explain-plan` — 执行计划阅读
  - `sql-glossary` — 术语表
- skill 章节对应：**ch08-indexes-perf 核心来源**

### Tier 2 — 重要补充

**04-awesome-postgres/**
- 来源：https://github.com/dhamaniasad/awesome-postgres
- 大小：164K
- License：CC0
- 内容：PostgreSQL 软件/库/工具/资源汇总
- skill 章节对应：ch07-pg-specific 引用

**05-sql-style-guide/**
- 来源：https://github.com/mattm/sql-style-guide
- 大小：102K
- License：见仓库 LICENSE
- 内容：Matt Mazur SQL 风格指南
- skill 章节对应：ch01 风格子节

**06-awesome-text2sql/**
- 来源：https://github.com/eosphoros-ai/Awesome-Text2SQL
- 大小：254K
- License：MIT
- 内容：Text2SQL 资源（含 BIRD/Spider SOTA 表格）+ Text2API/DSL/Vis 关联
- skill 章节对应：ch10-evidence-compat + Phase 3 拓展

**07-awesome-llm-text2sql/**
- 来源：https://github.com/DEEP-PolyU/Awesome-LLM-based-Text2SQL
- 大小：932K
- License：见仓库 LICENSE
- 内容：DEEP-PolyU 综述配套论文集（TKDE 2025）
- skill 章节对应：ch10 补充

## 资源统计

| 目录 | 大小 | 文件数 | 形态 |
|---|---|---|---|
| 01-nl2sql-handbook | 199M | 105 | GitHub 仓库（PDF + Markdown + slides） |
| 02-sql-tutorial-civilian7 | 13M | 428 | GitHub 仓库（教程 + 数据 + 练习） |
| 03-use-the-index-luke | 约 1.5M | 47 | HTML 章节镜像 |
| 04-awesome-postgres | 164K | 34 | GitHub 仓库（README 索引） |
| 05-sql-style-guide | 102K | 30 | GitHub 仓库（README 指南） |
| 06-awesome-text2sql | 254K | 37 | GitHub 仓库（README 索引） |
| 07-awesome-llm-text2sql | 932K | 35 | GitHub 仓库（论文列表） |

**总沉淀量**：约 214M / 716 文件

## 下一步沉淀路径

1. Phase 2 — 从这 7 个资料源手工提取 SQL 知识
2. Phase 3 — 整合形成 sql-skill 的 10 chapter 骨架
3. Phase 4 — 用 civilian7 的 1065 题作为评测集

## 命名规范

按 `E:/obsidian/AGENTS.md`：
- Windows 禁止字符 `\ / : * ? " < > |` 不用
- Emoji 不用
- 文件名 ≤150 字符；完整路径 ≤200 字符
- 编号用 `00-` `01-` 顺序
