# lookup-sql-vault — Layer 0 检索规范(Read + Grep,无外部依赖)

## 目的

让 agent 接到 SQL 问题时,**不依赖 gbrain / 不需要 ingest / 不需要重启 Claude Code**,直接检索 `E:/obsidian/SQL/` 整个 vault 1GB+ 沉淀。

## 检索顺序(4 层)

### Layer 0: Read + Grep + Glob 跨 vault

**触发**:任何 SQL 问题(包括但不限于"如何写 JOIN" / "为什么 query 慢" / "中文 schema 怎么配")

**算法**:

```python
def lookup_sql_vault(question: str, top_k: int = 5) -> list:
    """跨 Obsidian SQL vault 全文检索,返回 top-k 命中段落"""
    # 1. 关键词提取
    keywords = extract_sql_keywords(question)  # 中文 + 英文混合
    
    # 2. 优先级目录(本 skill 沉淀 + 实战 + 索引圣经)
    priority_paths = [
        "E:/obsidian/SQL/08-sql-skill/",         # 本 skill 10 章 + 4 辅助
        "E:/obsidian/SQL/03-use-the-index-luke/", # luke 48 章 + pg-docs + SQLBolt
        "E:/obsidian/SQL/02-sql-tutorial-civilian7/",  # 1065 题
        "E:/obsidian/SQL/04-awesome-postgres/",  # PG 资源
        "E:/obsidian/SQL/05-sql-style-guide/",   # 风格
        # 跳过 199M 的 01-nl2sql-handbook
    ]
    
    # 3. 跨目录 Grep 关键词
    hits = []
    for path in priority_paths:
        for keyword in keywords:
            try:
                results = Grep(
                    path=f"{path}**/*.md",
                    pattern=keyword,
                    output_mode="content",
                    context=3,
                )
                for r in results:
                    hits.append({
                        "path": r.file_path,
                        "keyword": keyword,
                        "context": r.context,
                        "score": 1.0,  # 关键词命中
                    })
            except Exception:
                continue
    
    # 4. 去重 + 排序(优先本 skill 章节)
    deduped = dedup_by_path(hits)
    return deduped[:top_k]
```

### Layer 1: cheatsheet.md

详见 `E:/obsidian/SQL/08-sql-skill/cheatsheet.md`,13 决策表 + 18 关键经验。

### Layer 2: 对应 chapter

```python
def lookup_chapter(topic: str) -> str:
    """根据 topic 路由到对应 chapter"""
    chapter_map = {
        "ch01": "SQL 语法铁律 / NULL / 别名",
        "ch02": "JOIN 7 种 / OUTER / CROSS / SELF",
        "ch03": "窗口函数 / OVER / RANK / LAG-LEAD",
        "ch04": "CTE / 递归 CTE / 物化",
        "ch05": "聚合 / GROUP BY / HAVING / FILTER",
        "ch06": "集合操作 / UNION / INTERSECT / EXCEPT",
        "ch07": "JSONB / array / GIN / FDW / 中文 schema",
        "ch08": "索引 / JOIN 算法 / EXPLAIN / 性能",
        "ch09": "反模式 / EAV / SELECT * / N+1 / SQL 注入",
        "ch10": "evidence-skill 协作 / 4 道防线 / 三层 lookup",
    }
    for key, desc in chapter_map.items():
        if topic_matches(topic, desc):
            return f"E:/obsidian/SQL/08-sql-skill/chapters/{key}-*.md"
```

### Layer 3: evidence-skill 业务侧

```python
# 业务侧雷区(中文 schema / FDW / BI 性能 / MCP)
# 详 E:/Users/Duanyi/.claude/skills/evidence-skill/
# 关键词命中时直接 Read:
evidence_keywords = ["ds", "shop_name", "stat_date", "nginx", "pgbouncer", "FDW", "MCP"]
```

## 关键词提取规则

```python
def extract_sql_keywords(question: str) -> list[str]:
    """从问题提取 SQL 关键词"""
    # SQL 关键词(JOIN / WHERE / INDEX ...)
    sql_kw = ["join", "where", "group by", "having", "order by", "limit", 
              "index", "explain", "jsonb", "array", "cte", "window",
              "union", "intersect", "except", "transaction", "lock"]
    
    # 中文关键词(中文 schema / 中文术语)
    zh_kw = ["中文", "假名", "schema", "性能", "慢", "优化", "索引", 
             "窗口", "递归", "物化", "聚合", "集合", "反模式"]
    
    # 实体(luke 章节 / civilian7 题号 / chapter 编号)
    entity_kw = extract_entities(question)  # ch01, ch08, R6, ...
    
    return [k for k in sql_kw + zh_kw if k in question.lower()] + entity_kw
```

## 工具说明

| 工具 | 用途 | 优势 |
|---|---|---|
| `Grep` | 关键词全文搜索 | 跨目录,快,精准 |
| `Glob` | 文件名模式 | 找特定类型文件 |
| `Read` | 读单个文件 | 精读,带行号 |
| `mcp__plugin_gbrain_gbrain__query` | gbrain 语义召回(可选) | 同义词,需 env 配置 |

## 已知限制

1. **Grep 不懂同义词**:"keyset pagination" vs "大 OFFSET 优化" 不会自动匹配
2. **跨 1GB vault 慢**:每次查询 Grep 全 vault 可能 1-3s
3. **无向量召回**:语义理解需 future gbrain stage 3(v2.2)
4. **Read 上下文有限**:大文件 Read 默认 2000 行,长内容需用 offset/limit

## 性能优化

1. **优先 Layer 0 → Layer 1 → Layer 2 → Layer 3**:先 cheatsheet 看是否有现成决策
2. **关键词精确**:多关键词交集,不要模糊匹配
3. **Glob 限定范围**:先用 Glob 找到文件再 Read,不要盲读
4. **缓存结果**:同一查询在 session 内复用

## 升级路径(v2.2 gbrain stage 3)

当用户设置 `GBRAIN_SOURCE=sql-vault` + 重启 Claude Code 后:
1. `gbrain ingest` 把 vault 全部 ingest
2. Layer 0 优先用 `mcp__plugin_gbrain_gbrain__query` semantic recall
3. Grep/Read 作为 fallback

详见 `handoff-sql-skill-v2-rag-2026-10-15.md`。
