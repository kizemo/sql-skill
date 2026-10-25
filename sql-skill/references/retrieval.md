# Retrieval — 跨 vault 检索策略

> SKILL.md 只留一行指引,细节在此。**读条件**:需要查 skill 之外的资料(luke 48 章、civilian7 题、PG 资源、风格指南)时读本文件。

---

## 1. Layer 0:Read + Grep 直接检索 Obsidian SQL vault

**为什么不用 gbrain ingest**:无需 ingest、无需重启 Claude Code、无需 user 操作 —— agent 直接 Read + Grep 即可,立即生效,跨 1GB+ 沉淀,关键词精准。

### 已纳入检索的目录(按优先级)

| 目录 | 范围 | 优先级 |
|---|---|---|
| `E:/obsidian/SQL/00-索引.md` | 资源总索引 | 1 |
| `E:/obsidian/SQL/08-sql-skill/` | sql-skill 自身 10 章 + supporting | 1 |
| `E:/obsidian/SQL/03-use-the-index-luke/` | luke 48 章 + pg-docs 5 章 + SQLBolt 17 课 | 1 |
| `E:/obsidian/SQL/02-sql-tutorial-civilian7/` | 1090 题 SQL 实战评测集 | 2 |
| `E:/obsidian/SQL/04-awesome-postgres/` | PG 资源汇总 | 2 |
| `E:/obsidian/SQL/05-sql-style-guide/` | SQL 风格指南 | 3 |
| `E:/obsidian/SQL/01-nl2sql-handbook/` | NL2SQL 综述 199M(跳过) | 3 |

### 检索流程

```python
# 1. 从 question 提取关键词
keywords = extract_sql_keywords(question)   # JOIN / B-Tree / 中文 schema ...

# 2. 跨 vault 全文搜索(按上表优先级顺序)
hits = []
for path in PRIORITY_1_DIRS:                # 08-sql-skill / 03-use-the-index-luke
    hits += Grep(path, keywords, context=3)

# 3. top-5 排序去重
return top_k(hits, k=5)
```

**fallback**:命中太多或太少 → Read 单个文件精读:
```python
content = Read("E:/obsidian/SQL/08-sql-skill/chapters/ch08-indexes-perf.md")
```

### 可选升级:gbrain semantic recall

用户设置 `GBRAIN_SOURCE=sql-vault` + 重启 Claude Code 后可用同义词召回(优于纯关键词)。
**当前限制**:MCP source binding + serve PGLite 锁 —— 详见
`F:/soft/00selfmade/sql-skill/handoff-sql-skill-v2-rag-2026-10-15.md` § 三。

---

## 2. 分层 lookup 顺序

| Layer | 内容 | 适用 |
|---|---|---|
| **0** | 跨 vault Read + Grep(见上) | 找资料、找出处 |
| **1** | [supporting/cheatsheet.md](../supporting/cheatsheet.md) — 13 决策表 + 18 关键经验 | 快速决策(**优先级最高**) |
| **2** | [chapters/ch01-ch10](../INDEX.md) — ~5161 行 | deep dive |
| **3** | [evidence-skill](E:/Users/Duanyi/.claude/skills/evidence-skill/) | 业务侧雷区(中文 schema / FDW / BI 性能 / MCP / nginx) |

---

## 3. 入口速查

| 意图 | 去哪 |
|---|---|
| 无参数 | 12 大框架速查(SKILL.md)+ chapter index |
| 指定章节 | `ch01`…`ch10` / `glossary` / `patterns` / `cheatsheet` → 读对应文件 |
| 决策快查 | `supporting/cheatsheet.md` 13 决策表 + 18 关键经验 |
| 模式匹配 | `supporting/patterns.md` 8 大模式 + 反模式总表 |
| 术语查询 | `supporting/glossary.md`(166 条定义) |
| 术语定位 | `references/topic-index.md`(84 条 → 章节) |

---

## 4. 本地资源速查

| 资源 | 路径 |
|---|---|
| 资源总索引 | `E:/obsidian/SQL/00-索引.md` |
| luke 48 章 | `E:/obsidian/SQL/03-use-the-index-luke/luke/` |
| pg-docs 5 章 | `E:/obsidian/SQL/03-use-the-index-luke/pg-docs/` |
| SQLBolt 17 课 | `E:/obsidian/SQL/03-use-the-index-luke/sqlbolt/` |
| civilian7 1090 题 | `E:/obsidian/SQL/02-sql-tutorial-civilian7/exercises/` |
| nl2sql-handbook 综述 | `E:/obsidian/SQL/01-nl2sql-handbook/`(199M) |
| 评测脚本 | `F:/soft/00selfmade/sql-skill/tools/eval_civilian7.py` |

---

## 5. 联动 skill / 项目文档

| 文档 | 路径 |
|---|---|
| evidence-skill(BI / 中文 PG 业务侧 / nginx / FDW / MCP) | `E:/Users/Duanyi/.claude/skills/evidence-skill/` |
| sql-skill GitHub 仓库 | https://github.com/kizemo/sql-skill |
| v2.2 部署 handoff | `F:/soft/00selfmade/sql-skill/handoff-sql-skill-v2-2-deployed-2026-10-15.md` |
| v2.1 RAG 设计 handoff | `F:/soft/00selfmade/sql-skill/handoff-sql-skill-v2-rag-2026-10-15.md` |
| v1.0 完整版 handoff | `F:/soft/00selfmade/sql-skill/docs/handoffs/handoff-sql-skill-v1-2026-10-14.md` |
| spec / plan 全集 | `F:/soft/00selfmade/sql-skill/docs/specs/` · `docs/plans/` |
| token 效率优化分析 | `F:/soft/00selfmade/skill-optimizer/handover/sql-skill-token-efficiency.md` |

---

## 6. 升级频率建议

- **PG 大版本升级时** → re-read luke `sql-anatomy-*` + pg-docs `indexes.html` + `performance-tips.html`
- **每月** → 跑 `ANALYZE` + 看 `pg_stat_statements` top-20 慢 query
- **每季** → review 索引决策(B-Tree / GIN / BRIN / Hash 是否仍最优)
- **半年** → review 与 evidence-skill 边界(避免重叠)
