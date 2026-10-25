#!/usr/bin/env python3
"""eval_civilian7.py — Civilian7 SQL 题评测脚本(1090 题,~1065)

用法:
  python eval_civilian7.py --mode count                       # 只数题 + 分布统计
  python eval_civilian7.py --mode skill-aware                 # 题目标签 → sql-skill 章匹配覆盖率
  python eval_civilian7.py --mode baseline --db PATH          # 跑 reference SQL 自检(需测试 DB)
  python eval_civilian7.py --mode claude-api --db PATH        # 模型答 SQL → 执行结果对拍 reference(需 API key)
  python eval_civilian7.py --mode claude-api --db PATH --context skill   # 同上,但把 sql-skill 章节塞进 prompt
  python eval_civilian7.py --mode all --db PATH               # 全跑(推荐)

测试 DB(现成,32 张电商表):
  E:/obsidian/SQL/02-sql-tutorial-civilian7/docs/en/playground/ecommerce-playground.db
  或自建:python E:/obsidian/SQL/02-sql-tutorial-civilian7/src/cli/generate.py --db out.db

API:走 anthropic SDK,读环境变量 ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN / ANTHROPIC_BASE_URL;
    模型名用 --model 或 EVAL_MODEL(默认 MiniMax-M3.1-Flash)。

输出:
  eval_civilian7_report.json  — 完整机器可读
  eval_civilian7_report.md    — markdown 摘要

退出码:
  0 全部通过 / 1 部分失败 / 2 关键错误
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[FAIL] PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# ============================================================================
# 路径配置
# ============================================================================
ROOT = Path("E:/obsidian/SQL/02-sql-tutorial-civilian7")
EXERCISES_DIR = ROOT / "exercises"
SQL_SKILL_DIR = Path("F:/soft/00selfmade/sql-skill/sql-skill")

DEFAULT_OUT_JSON = Path("F:/soft/00selfmade/sql-skill/eval_civilian7_report.json")
DEFAULT_OUT_MD = Path("F:/soft/00selfmade/sql-skill/eval_civilian7_report.md")


# ============================================================================
# 1. 加载器
# ============================================================================
def load_all_problems() -> list[dict]:
    """加载所有 YAML,展平为 problems[] 列表,带 source file"""
    if not EXERCISES_DIR.exists():
        print(f"[FAIL] exercises dir not found: {EXERCISES_DIR}", file=sys.stderr)
        sys.exit(2)

    out = []
    for yaml_file in sorted(EXERCISES_DIR.rglob("*.yaml")):
        try:
            with yaml_file.open(encoding="utf-8") as f:
                doc = yaml.safe_load(f)
        except Exception as e:
            print(f"[WARN] YAML parse fail {yaml_file}: {e}", file=sys.stderr)
            continue

        if not isinstance(doc, dict):
            continue
        meta = doc.get("metadata", {})
        problems = doc.get("problems", []) or []
        difficulty = meta.get("difficulty", "unknown")
        for p in problems:
            p["_source_file"] = str(yaml_file.relative_to(ROOT))
            p["_difficulty"] = difficulty
            p["_metadata_concepts"] = meta.get("concepts", []) or []
            p["_metadata_tables"] = meta.get("tables", []) or []
            out.append(p)
    return out


# ============================================================================
# 2. 标签 → sql-skill 章 matcher
# ============================================================================
# Tag → chapter mapping(基于 sql-skill/INDEX.md + 10 章主题归纳)
TAG_TO_CHAPTER: dict[str, list[str]] = {
    # ch01-grammar + ch05-aggregates(基础查询/聚合)
    "SELECT": ["ch01-grammar", "ch05-aggregates"],
    "WHERE": ["ch01-grammar"],
    "ORDER BY": ["ch01-grammar"],
    "LIMIT": ["ch01-grammar"],
    "LIKE": ["ch01-grammar"],
    "IS NULL": ["ch01-grammar"],
    "IS NOT NULL": ["ch01-grammar"],
    "DISTINCT": ["ch01-grammar"],
    "COUNT": ["ch05-aggregates"],
    "SUM": ["ch05-aggregates"],
    "AVG": ["ch05-aggregates"],
    "MIN": ["ch05-aggregates"],
    "MAX": ["ch05-aggregates"],
    "GROUP BY": ["ch05-aggregates"],
    "HAVING": ["ch05-aggregates"],
    "products": ["ch05-aggregates"],  # tag 标注的表名也算 ch05(商品聚合常见场景)
    # ch02-joins
    "JOIN": ["ch02-joins"],
    "INNER JOIN": ["ch02-joins"],
    "LEFT JOIN": ["ch02-joins"],
    "RIGHT JOIN": ["ch02-joins"],
    "FULL JOIN": ["ch02-joins"],
    "SELF JOIN": ["ch02-joins"],
    "CROSS JOIN": ["ch02-joins"],
    # ch03-window-functions
    "Window": ["ch03-window-functions"],
    "ROW_NUMBER": ["ch03-window-functions"],
    "RANK": ["ch03-window-functions"],
    "DENSE_RANK": ["ch03-window-functions"],
    "LEAD": ["ch03-window-functions"],
    "LAG": ["ch03-window-functions"],
    "PARTITION BY": ["ch03-window-functions"],
    # ch04-cte-recursion
    "CTE": ["ch04-cte-recursion"],
    "WITH": ["ch04-cte-recursion"],
    "RECURSIVE": ["ch04-cte-recursion"],
    # ch06-set-ops
    "UNION": ["ch06-set-ops"],
    "INTERSECT": ["ch06-set-ops"],
    "EXCEPT": ["ch06-set-ops"],
    # ch07-pg-specific
    "JSONB": ["ch07-pg-specific"],
    "JSON": ["ch07-pg-specific"],
    "JSON_EXTRACT": ["ch07-pg-specific"],
    "JSON_EACH": ["ch07-pg-specific"],
    "JSON_GROUP_ARRAY": ["ch07-pg-specific"],
    "JSON_GROUP_OBJECT": ["ch07-pg-specific"],
    "JSON Path": ["ch07-pg-specific"],
    "ARRAY": ["ch07-pg-specific"],
    "GIN": ["ch07-pg-specific"],
    "BRIN": ["ch07-pg-specific"],
    # ch08-indexes-perf
    "Index": ["ch08-indexes-perf"],
    "INDEX": ["ch08-indexes-perf"],
    "EXPLAIN": ["ch08-indexes-perf"],
    # ch09-antipatterns
    "NOT IN": ["ch09-antipatterns"],
    "EXISTS": ["ch09-antipatterns", "ch04-cte-recursion"],
    "IN": ["ch09-antipatterns"],
    # ch10-evidence-bridge(Text2SQL/evidence)
    "Text2SQL": ["ch10-evidence-bridge"],
}

# 概念关键词 → 章(matcher 兜底,题目 concepts 字段用)
CONCEPT_TO_CHAPTER: dict[str, list[str]] = {
    "select": ["ch01-grammar"],
    "where": ["ch01-grammar"],
    "order by": ["ch01-grammar"],
    "limit": ["ch01-grammar"],
    "like": ["ch01-grammar"],
    "null": ["ch01-grammar"],
    "case": ["ch01-grammar"],
    "join": ["ch02-joins"],
    "inner join": ["ch02-joins"],
    "left join": ["ch02-joins"],
    "right join": ["ch02-joins"],
    "self join": ["ch02-joins"],
    "window": ["ch03-window-functions"],
    "row_number": ["ch03-window-functions"],
    "rank": ["ch03-window-functions"],
    "lead": ["ch03-window-functions"],
    "lag": ["ch03-window-functions"],
    "cte": ["ch04-cte-recursion"],
    "recursive": ["ch04-cte-recursion"],
    "union": ["ch06-set-ops"],
    "intersect": ["ch06-set-ops"],
    "except": ["ch06-set-ops"],
    "jsonb": ["ch07-pg-specific"],
    "gin": ["ch07-pg-specific"],
    "brin": ["ch07-pg-specific"],
    "index": ["ch08-indexes-perf"],
    "explain": ["ch08-indexes-perf"],
    "antipattern": ["ch09-antipatterns"],
    "exists": ["ch04-cte-recursion"],
    "not in": ["ch09-antipatterns"],
    "evidence": ["ch10-evidence-bridge"],
}


def match_problem_to_chapters(p: dict) -> set[str]:
    """用 tags + concepts + title 三路匹配 sql-skill 章,返回去重集合"""
    chapters: set[str] = set()

    # 1. tags 匹配
    for tag in p.get("tags", []) or []:
        for ch in TAG_TO_CHAPTER.get(tag, []):
            chapters.add(ch)

    # 2. metadata.concepts 匹配
    for concept in p.get("_metadata_concepts", []) or []:
        c_lower = concept.lower().strip()
        for kw, chs in CONCEPT_TO_CHAPTER.items():
            if kw in c_lower:
                for ch in chs:
                    chapters.add(ch)

    # 3. type 字段(SELECT/Aggregate/Join/...)兜底
    ptype = (p.get("type", "") or "").lower()
    type_map = {
        "select": ["ch01-grammar"],
        "aggregate": ["ch05-aggregates"],
        "join": ["ch02-joins"],
        "window": ["ch03-window-functions"],
        "cte": ["ch04-cte-recursion"],
        "subquery": ["ch04-cte-recursion"],
        "set": ["ch06-set-ops"],
        "ddl": ["ch07-pg-specific"],
        "dml": ["ch07-pg-specific"],
        "json": ["ch07-pg-specific"],
        "analytics": ["ch05-aggregates", "ch01-grammar"],
        "patterns": ["ch09-antipatterns", "ch01-grammar"],
        "comprehensive": ["ch01-grammar"],
        "debug": ["ch09-antipatterns"],
        "explain": ["ch08-indexes-perf"],
    }
    for ch in type_map.get(ptype, []):
        chapters.add(ch)

    # 4. title_en / body_en 文本兜底扫描
    text = " ".join([
        str(p.get("title_en", "") or ""),
        str(p.get("body_en", "") or ""),
    ]).lower()
    text_keywords = {
        "json": ["ch07-pg-specific"],
        "window": ["ch03-window-functions"],
        "cte": ["ch04-cte-recursion"],
        "recursive": ["ch04-cte-recursion"],
        "join": ["ch02-joins"],
        "aggregate": ["ch05-aggregates"],
        "group by": ["ch05-aggregates"],
        "having": ["ch05-aggregates"],
        "index": ["ch08-indexes-perf"],
        "explain": ["ch08-indexes-perf"],
        "union": ["ch06-set-ops"],
        "except": ["ch06-set-ops"],
        "intersect": ["ch06-set-ops"],
        "exists": ["ch04-cte-recursion"],
        "case": ["ch01-grammar"],
        "null": ["ch01-grammar"],
        "trigger": ["ch07-pg-specific"],
        "view": ["ch07-pg-specific"],
        "stored procedure": ["ch07-pg-specific"],
        "function": ["ch07-pg-specific"],
        "constraint": ["ch07-pg-specific"],
        "transaction": ["ch07-pg-specific"],
        "isolation": ["ch07-pg-specific"],
    }
    for kw, chs in text_keywords.items():
        if kw in text:
            for ch in chs:
                chapters.add(ch)

    return chapters


def mode_skill_aware(problems: list[dict]) -> dict:
    """覆盖率统计:每题 → sql-skill 章集合"""
    chapter_problems: dict[str, list[str]] = defaultdict(list)
    unmatched_problems: list[dict] = []
    for p in problems:
        chs = match_problem_to_chapters(p)
        if not chs:
            unmatched_problems.append({
                "id": p["id"],
                "source_file": p["_source_file"],
                "difficulty": p["_difficulty"],
                "tags": p.get("tags", []),
                "type": p.get("type", ""),
            })
        for ch in chs:
            chapter_problems[ch].append(p["id"])

    by_difficulty: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for p in problems:
        chs = match_problem_to_chapters(p)
        for ch in chs:
            by_difficulty[p["_difficulty"]][ch] += 1
        if not chs:
            by_difficulty[p["_difficulty"]]["__unmatched__"] += 1

    coverage = {
        "total_problems": len(problems),
        "matched_problems": len(problems) - len(unmatched_problems),
        "unmatched_problems": len(unmatched_problems),
        "coverage_pct": round(100.0 * (len(problems) - len(unmatched_problems)) / max(len(problems), 1), 1),
        "chapters_covered": len(chapter_problems),
        "per_chapter_count": {ch: len(ids) for ch, ids in sorted(chapter_problems.items())},
        "per_difficulty_per_chapter": {
            diff: dict(counter) for diff, counter in by_difficulty.items()
        },
        "unmatched_samples": unmatched_problems[:20],  # 前 20 例
    }
    return coverage


# ============================================================================
# 3. Baseline mode — 跑 reference SQL 自检
# ============================================================================
def resolve_sql(problem: dict, dialect: str = "sqlite") -> str:
    """从 reference_sql 里取指定方言的 SQL。

    两种数据形态(实测 1090 题):
    - str(238 题):直接就是 SQL
    - dict(852 题):按方言分键 —— 'common' 822 / 'sqlite' 30 /
      'postgresql' 18 / 'mysql' 18 / 'oracle' 30 / 'sqlserver' 30
      (同一题可能同时有 5 个方言键)
    取值优先级:指定方言 > common > 任意非空值。
    """
    rs = problem.get("reference_sql")
    if isinstance(rs, str):
        return rs
    if isinstance(rs, dict):
        if rs.get(dialect):
            return rs[dialect]
        if rs.get("common"):
            return rs["common"]
        for v in rs.values():
            if v:
                return v
    return ""


def split_statements(sql: str) -> list[str]:
    """把多语句 SQL 拆成单条语句。

    sqlite3.execute() 一次只能跑一条("You can only execute one statement at a time"),
    而 reference SQL 里 16% 是 `CREATE TEMP TABLE ...; SELECT ...` 这种多语句脚本。
    """
    stmts = []
    buf = ""
    for line in sql.splitlines(keepends=True):
        buf += line
        if sqlite3.complete_statement(buf):
            s = buf.strip()
            if s:
                stmts.append(s)
            buf = ""
    tail = buf.strip()
    if tail:
        stmts.append(tail)
    return stmts


def normalize_sql_for_sqlite(sql: str) -> str:
    """剥掉 SQLite 不认的客户端指令 / 事务控制语句。

    - `DELIMITER $$` 是 MySQL 客户端指令(不是 SQL)→ 整行删
    - `BEGIN / COMMIT / ROLLBACK / START TRANSACTION / END TRANSACTION`
      与 Python sqlite3 的隐式事务管理冲突
      ("cannot start a transaction within a transaction")→ 整行删,交给驱动管
    """
    out = []
    for line in sql.splitlines():
        st = line.strip().upper()
        if st.startswith("DELIMITER"):
            continue
        if re.match(r"^(BEGIN|COMMIT|ROLLBACK)\b", st):
            continue
        if re.match(r"^(START|END)\s+TRANSACTION\b", st):
            continue
        out.append(line)
    return "\n".join(out)


# SQLite 跑不起来的方言专属构造 —— 不该算"题出错",算"不适用"
NOT_APPLICABLE_MARKERS = (
    "PROCEDURE", "FUNCTION", "TRIGGER", "DELIMITER",
    "INFORMATION_SCHEMA", "SYS.", "PG_", "STUFF(", "NVL(",
    "TOP ", "ROWNUM", "CONNECT BY", "SYSDATE", "GETDATE(",
    "DISTINCT AGGREGATES MUST HAVE EXACTLY ONE ARGUMENT",
)

# 约束违例: civilian7 里有一批练习**故意**插重复主键 / 空 NOT NULL,
# 目的就是演示报错("-- PRIMARY KEY 중복 → 에러 발생")。这类不是"题坏了"。
CONSTRAINT_MARKERS = (
    "UNIQUE CONSTRAINT FAILED",
    "NOT NULL CONSTRAINT FAILED",
    "CHECK CONSTRAINT FAILED",
    "FOREIGN KEY CONSTRAINT FAILED",
)


def classify_error(err: str) -> str:
    """把错误分成 dialect_not_applicable / expected_error / 真错误。"""
    up = err.upper()
    if any(m in up for m in NOT_APPLICABLE_MARKERS):
        return "dialect_not_applicable"
    if any(m in up for m in CONSTRAINT_MARKERS):
        return "expected_error"
    return "error"


_DROP_RE = re.compile(
    r"^\s*CREATE\s+(?:TEMP\s+|TEMPORARY\s+)?(VIEW|TABLE)\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w\".\[\]]+)",
    re.I,
)


def exec_sql(conn: sqlite3.Connection, sql: str) -> tuple[list, list]:
    """执行(可能多语句的)SQL,返回 (最后结果集的行, 列名)。

    CREATE VIEW / TEMP TABLE 之前先 DROP —— reference SQL 里建视图/临时表的脚本
    重复跑会撞 "already exists"。
    """
    rows: list = []
    cols: list = []
    conn.commit()
    for s in split_statements(normalize_sql_for_sqlite(sql)):
        m = _DROP_RE.match(s)
        if m:
            kind = "VIEW" if m.group(1).upper() == "VIEW" else "TABLE"
            try:
                conn.execute(f"DROP {kind} IF EXISTS {m.group(2)}")
            except Exception:
                pass
        cur = conn.execute(s)
        if cur.description is not None:
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
    return rows, cols


def run_reference_sql(problem: dict, conn: sqlite3.Connection) -> dict:
    """在测试 DB 上跑 reference SQL,返回执行结果(行数/列/hash)

    多语句脚本:逐条执行,取**最后一个返回结果集**的语句作为结果
    (脚本通常以 SELECT 结尾;若 SELECT 在中间也能取到)。
    """
    sql = resolve_sql(problem, "sqlite")
    if not sql:
        return {"status": "no_sql", "row_count": 0, "col_count": 0, "result_hash": None}

    try:
        # 走 exec_sql:统一做 SQLite 方言归一化(去 DELIMITER / 事务控制)
        # + CREATE VIEW/TABLE 前先 DROP + 多语句拆分
        rows, cols = exec_sql(conn, sql)
        if not cols and not rows:
            return {"status": "no_result", "row_count": 0, "col_count": 0, "result_hash": None}

        sorted_rows = sorted(str(r) for r in rows)
        result_hash = hashlib.sha256("\n".join(sorted_rows).encode()).hexdigest()[:16]
        return {
            "status": "ok",
            "row_count": len(rows),
            "col_count": len(cols),
            "result_hash": result_hash,
            "_sorted_rows": sorted_rows,
        }
    except Exception as e:
        err = str(e)[:200]
        return {
            "status": classify_error(err),
            "error": err,
            "row_count": 0,
            "col_count": 0,
            "result_hash": None,
        }


def mode_baseline(problems: list[dict], db_path: Path, sample: int = 50) -> dict:
    """跑 reference SQL 在测试 DB 上,采样自检"""
    if not db_path.exists():
        return {"error": f"DB not found: {db_path}"}

    conn = sqlite3.connect(str(db_path))
    try:
        # 抽样
        import random
        sample_problems = random.sample(problems, min(sample, len(problems)))
        results = []
        ok_count = 0
        err_count = 0
        na_count = 0
        exp_count = 0
        for p in sample_problems:
            r = run_reference_sql(p, conn)
            r["id"] = p["id"]
            r["difficulty"] = p["_difficulty"]
            results.append(r)
            if r["status"] == "ok":
                ok_count += 1
            elif r["status"] == "dialect_not_applicable":
                na_count += 1
            elif r["status"] == "expected_error":
                exp_count += 1
            else:
                err_count += 1
        applicable = len(sample_problems) - na_count - exp_count
        return {
            "sampled": len(sample_problems),
            "ok_count": ok_count,
            "error_count": err_count,
            "dialect_not_applicable": na_count,
            "expected_error": exp_count,
            "ok_pct": round(100.0 * ok_count / max(applicable, 1), 1),
            "samples": results,
        }
    finally:
        conn.close()


# ============================================================================
# 4. Claude API mode — 模型答 SQL,执行结果对拍 reference SQL
# ============================================================================
SQL_PROMPT_TEMPLATE = """You are a SQLite SQL expert. Write ONE SQLite query that answers the question.

Rules:
- Output ONLY the SQL query. No explanation, no markdown fences.
- Use only tables and columns listed in "Schema".
- The query must be executable on SQLite.

Schema:
{schema}

Question:
{question}
"""


def describe_tables(conn: sqlite3.Connection, tables: list[str]) -> str:
    """列出题目涉及的表 + 列(不给 schema 的话模型只能瞎猜列名)。"""
    lines = []
    for t in tables:
        try:
            cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{t}")')]
        except Exception:
            cols = []
        if cols:
            lines.append(f"- {t}({', '.join(cols)})")
        else:
            lines.append(f"- {t}")
    return "\n".join(lines) if lines else "(unknown)"


def extract_sql(text: str) -> str:
    """从模型回复里抽出 SQL(优先 ``` 代码块,否则取第一个 SELECT/WITH 段)。"""
    if not text:
        return ""
    fenced = re.search(r"```(?:sql)?\s*(.*?)```", text, re.S | re.I)
    if fenced:
        return fenced.group(1).strip()
    stmt = re.search(r"\b(WITH|SELECT)\b.*", text, re.S | re.I)
    return stmt.group(0).strip() if stmt else text.strip()


def load_skill_context(problem: dict, max_chars: int) -> str:
    """按题目匹配到的章节,取章节正文作为 prompt 上下文(测 skill 是否真的帮上忙)。"""
    try:
        chapters = match_problem_to_chapters(problem)
    except Exception:
        return ""
    if not chapters:
        return ""
    chunks = []
    for ch in sorted(chapters):
        f = SQL_SKILL_DIR / "chapters" / f"{ch}.md"
        if not f.is_file():
            continue
        try:
            chunks.append(f.read_text(encoding="utf-8"))
        except Exception:
            continue
    return "\n\n".join(chunks)[:max_chars]


def mode_claude_api(
    problems: list[dict],
    db_path: Path,
    sample: int = 30,
    model: str = "MiniMax-M3.1-Flash",
    context_mode: str = "none",
    max_context_chars: int = 4000,
    temperature: float = 0.0,
    seed: int = 42,
) -> dict:
    """让模型答 SQL,在 SQLite 上执行,与 reference SQL 的结果集对拍。

    评分口径:**执行准确率**(execution accuracy)—— 生成 SQL 与 reference SQL
    的结果集(排序后逐行)完全一致才算对。SQL 文本不同但结果相同 = 对。
    """
    try:
        import anthropic
    except ImportError:
        return {"error": "anthropic SDK not installed (pip install anthropic)"}

    if not db_path.exists():
        return {"error": f"DB not found: {db_path}"}

    # SDK 默认超时 600s —— 评测里一次卡住就白等 10 分钟,必须显式收紧
    api_timeout = int(os.environ.get("EVAL_API_TIMEOUT", "60"))
    try:
        client = anthropic.Anthropic(timeout=api_timeout)
    except TypeError:
        client = anthropic.Anthropic()
    # 探测 SDK 是否支持 temperature(标准 anthropic 支持,部分中继 shim 不支持)
    try:
        import inspect

        _SUPPORTS_TEMPERATURE = "temperature" in inspect.signature(
            client.messages.create
        ).parameters
    except Exception:
        _SUPPORTS_TEMPERATURE = False
    conn = sqlite3.connect(str(db_path))
    try:
        import random

        pool = [p for p in problems if resolve_sql(p, "sqlite")]
        rng = random.Random(seed)  # 固定种子 → A/B 两轮抽到同一批题,才可比
        sampled = rng.sample(pool, min(sample, len(pool)))

        results = []
        correct = 0
        scored = 0
        api_errors = 0
        ref_errors = 0

        for p in sampled:
            t0 = time.time()
            rec = {
                "id": p["id"],
                "difficulty": p["_difficulty"],
                "status": "?",
                "gen_status": "?",
                "ref_status": "?",
                "latency_ms": 0,
            }

            # reference 先跑 —— 跑不通的题(方言专属函数)不计分
            ref = run_reference_sql(p, conn)
            rec["ref_status"] = ref["status"]
            if ref["status"] != "ok":
                ref_errors += 1
                rec["status"] = "ref_error"
                rec["latency_ms"] = int((time.time() - t0) * 1000)
                results.append(rec)
                continue

            question = (p.get("body_en") or p.get("body") or p.get("title_en") or p.get("title") or "").strip()
            tables = list(p.get("_metadata_tables") or [])
            schema = describe_tables(conn, tables)
            prompt = SQL_PROMPT_TEMPLATE.format(schema=schema, question=question)
            if context_mode == "skill":
                ctx = load_skill_context(p, max_context_chars)
                if ctx:
                    prompt = (
                        "Reference material from the sql-skill knowledge base "
                        "(may or may not be relevant):\n\n" + ctx + "\n\n" + prompt
                    )

            try:
                kwargs = {
                    "model": model,
                    "max_tokens": 1200,
                    "messages": [{"role": "user", "content": prompt}],
                }
                # 不同 SDK / 中继 shim 支持的参数不一样(标准 anthropic 有
                # temperature,某些 shim 没有)—— 按实际签名决定传不传
                if _SUPPORTS_TEMPERATURE:
                    kwargs["temperature"] = temperature
                msg = client.messages.create(**kwargs, timeout=api_timeout)
                text = "".join(getattr(b, "text", "") for b in msg.content)
            except Exception as e:
                api_errors += 1
                rec["status"] = "api_error"
                rec["error"] = f"{type(e).__name__}: {str(e)[:160]}"
                rec["latency_ms"] = int((time.time() - t0) * 1000)
                results.append(rec)
                continue

            gen_sql = extract_sql(text)
            rec["sql"] = gen_sql[:600]
            try:
                gen_raw_rows, _ = exec_sql(conn, gen_sql)
                gen_rows = sorted(str(r) for r in gen_raw_rows)
                rec["gen_status"] = "ok"
                rec["gen_row_count"] = len(gen_rows)
            except Exception as e:
                rec["gen_status"] = "error"
                rec["error"] = f"{type(e).__name__}: {str(e)[:160]}"
                gen_rows = None

            if gen_rows is not None:
                scored += 1
                if gen_rows == ref["_sorted_rows"]:
                    correct += 1
                    rec["status"] = "correct"
                else:
                    rec["status"] = "wrong"
            rec["latency_ms"] = int((time.time() - t0) * 1000)
            results.append(rec)

        return {
            "model": model,
            "context_mode": context_mode,
            "sampled": len(sampled),
            "scored": scored,
            "correct": correct,
            "accuracy_pct": round(100.0 * correct / max(scored, 1), 1),
            "api_errors": api_errors,
            "ref_errors": ref_errors,
            "samples": results,
        }
    finally:
        conn.close()


# ============================================================================
# 5. 报告输出
# ============================================================================
def write_json_report(report: dict, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def write_md_report(report: dict, out_path: Path):
    lines = ["# Civilian7 评测报告\n"]
    lines.append(f"- 评测时间:{time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 模式:`{report['mode']}`")
    lines.append(f"- 题数:**{report['total_problems']}**\n")

    if "skill_aware" in report:
        sa = report["skill_aware"]
        lines.append("## Skill-aware 覆盖率\n")
        lines.append(f"- 总题数:**{sa['total_problems']}**")
        lines.append(f"- 命中 sql-skill:**{sa['matched_problems']}** ({sa['coverage_pct']}%)")
        lines.append(f"- 未命中:**{sa['unmatched_problems']}**")
        lines.append(f"- 覆盖章数:**{sa['chapters_covered']}**\n")

        lines.append("### 每章覆盖题数\n")
        lines.append("| 章 | 题数 |")
        lines.append("|---|---|")
        for ch, n in sa["per_chapter_count"].items():
            lines.append(f"| {ch} | {n} |")
        lines.append("")

        lines.append("### 按难度 × 章交叉\n")
        diffs = sorted(sa["per_difficulty_per_chapter"].keys())
        chapters = sorted({ch for d in sa["per_difficulty_per_chapter"].values() for ch in d})
        lines.append("| 难度 \\ 章 | " + " | ".join(chapters) + " |")
        lines.append("|" + "---|" * (len(chapters) + 1))
        for diff in diffs:
            row = sa["per_difficulty_per_chapter"][diff]
            cells = [str(row.get(ch, 0)) for ch in chapters]
            lines.append(f"| {diff} | " + " | ".join(cells) + " |")
        lines.append("")

    if "baseline" in report and "error" not in report["baseline"]:
        bl = report["baseline"]
        lines.append("## Baseline 自检\n")
        lines.append(f"- 抽样:**{bl['sampled']}** 题")
        lines.append(f"- reference SQL 可执行:**{bl['ok_count']}** ({bl['ok_pct']}%)")
        lines.append(f"- 失败:**{bl['error_count']}**\n")

    if "claude_api" in report and "error" not in report["claude_api"]:
        ca = report["claude_api"]
        lines.append("## Claude API 执行准确率\n")
        lines.append(f"- 模型:`{ca['model']}`")
        lines.append(f"- 上下文:**{ca['context_mode']}**(none=裸模型 / skill=带 sql-skill 章节)")
        lines.append(f"- 抽样:**{ca['sampled']}** 题,计分 **{ca['scored']}** 题")
        lines.append(f"- 执行准确率:**{ca['accuracy_pct']}%** ({ca['correct']}/{ca['scored']})")
        lines.append(f"- reference 在 SQLite 跑不通(不计分):**{ca['ref_errors']}**")
        lines.append(f"- API 错误:**{ca['api_errors']}**\n")
        lines.append("| id | 难度 | 状态 | 生成行数 | 延迟ms |")
        lines.append("|---|---|---|---|---|")
        for s in ca["samples"]:
            lines.append(
                f"| {s['id']} | {s['difficulty']} | {s['status']} | "
                f"{s.get('gen_row_count', '-')} | {s['latency_ms']} |"
            )
        lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


# ============================================================================
# 5. Main
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description="Civilian7 SQL 题评测")
    parser.add_argument("--mode",
                        choices=["count", "skill-aware", "baseline", "claude-api", "all"],
                        default="skill-aware")
    parser.add_argument("--db", type=Path, help="baseline / claude-api 模式用的 SQLite 测试 DB 路径")
    parser.add_argument("--sample", type=int, default=50, help="baseline 抽样数")
    parser.add_argument("--api-sample", type=int, default=30, help="claude-api 抽样数(每次调用 = 一次 API 花费)")
    parser.add_argument("--model", default=os.environ.get("EVAL_MODEL", "MiniMax-M3.1-Flash"),
                        help="claude-api 模式的模型名(默认读 EVAL_MODEL)")
    parser.add_argument("--context", choices=["none", "skill"], default="none",
                        help="claude-api 模式是否把 sql-skill 章节塞进 prompt(默认 none)")
    parser.add_argument("--max-context-chars", type=int, default=4000,
                        help="claude-api 模式 skill 上下文的字符上限")
    parser.add_argument("--seed", type=int, default=42,
                        help="抽样随机种子(A/B 对比时保持一致,默认 42)")
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    args = parser.parse_args()

    t0 = time.time()
    problems = load_all_problems()
    load_time = time.time() - t0

    report = {
        "mode": args.mode,
        "total_problems": len(problems),
        "load_time_seconds": round(load_time, 2),
    }

    if args.mode in ("count", "all"):
        # 数题 + 分布
        by_diff: dict[str, int] = defaultdict(int)
        for p in problems:
            by_diff[p["_difficulty"]] += 1
        report["count"] = {
            "by_difficulty": dict(by_diff),
            "files_loaded": len({p["_source_file"] for p in problems}),
        }
        print(f"[OK] count: {len(problems)} problems across {report['count']['files_loaded']} files")
        for diff, n in sorted(by_diff.items()):
            print(f"  {diff:12s} {n:4d}")

    if args.mode in ("skill-aware", "all"):
        sa = mode_skill_aware(problems)
        report["skill_aware"] = sa
        print(f"[OK] skill-aware: {sa['coverage_pct']}% coverage ({sa['matched_problems']}/{sa['total_problems']})")
        for ch, n in sa["per_chapter_count"].items():
            print(f"  {ch:25s} {n:4d} 题")

    if args.mode in ("baseline", "all"):
        if not args.db:
            print("[WARN] baseline 模式需要 --db PATH,跳过", file=sys.stderr)
        else:
            bl = mode_baseline(problems, args.db, args.sample)
            report["baseline"] = bl
            if "error" in bl:
                print(f"[FAIL] baseline: {bl['error']}")
            else:
                print(f"[OK] baseline: {bl['ok_pct']}% SQL 可执行 ({bl['ok_count']}/{bl['sampled']})")

    if args.mode in ("claude-api", "all"):
        if not args.db:
            print("[WARN] claude-api 模式需要 --db PATH,跳过", file=sys.stderr)
        else:
            api_sample = args.api_sample
            ca = mode_claude_api(
                problems, args.db,
                sample=api_sample,
                model=args.model,
                context_mode=args.context,
                max_context_chars=args.max_context_chars,
                seed=args.seed,
            )
            report["claude_api"] = ca
            if "error" in ca:
                print(f"[FAIL] claude-api: {ca['error']}")
            else:
                print(f"[OK] claude-api: {ca['accuracy_pct']}% 执行准确率 "
                      f"({ca['correct']}/{ca['scored']}, model={ca['model']}, context={ca['context_mode']})")
                if ca["ref_errors"]:
                    print(f"  reference SQL 在 SQLite 上跑不通(方言专属函数):{ca['ref_errors']} 题,不计分")
                if ca["api_errors"]:
                    print(f"  API 错误:{ca['api_errors']} 题")

    write_json_report(report, args.out_json)
    write_md_report(report, args.out_md)
    print(f"\n[OUT] {args.out_json}")
    print(f"[OUT] {args.out_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
