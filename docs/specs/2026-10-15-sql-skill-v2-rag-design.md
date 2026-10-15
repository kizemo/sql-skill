# sql-skill v2.0 — gbrain RAG 集成设计 spec

**Date**: 2026-10-15
**Phase**: v1.0 完成(2026-10-14)→ v2.0 设计阶段
**Owner**: claude (this session)
**Status**: 用户已对齐(2026-10-15 确认 4 项)
**核心**: 把 sql-skill 从"自闭 10 章"升级到"跨整个 Obsidian SQL vault 1GB+ 沉淀 RAG 增强"

---

## 一、设计背景

### 1.1 v1.0 完成状态

sql-skill v1.0 = 10 章 + 4 辅助 / ~5161 行(详 handoff-sql-skill-v1-2026-10-14.md)
- 局限:沉淀在 `E:/obsidian/SQL/08-sql-skill/`,自闭
- 同一 vault 7 目录 / 1GB+ 实战沉淀(luke / civilian7 / pg-docs / nl2sql-handbook / SQLBolt / awesome-postgres / sql-style-guide)**未被 sql-skill 引用**
- 调研入口只列路径,agent 不主动读

### 1.2 用户已确认 4 项(2026-10-15)

1. ✅ gbrain MCP 已 connected(见 MCP 服务列表截图)
2. ✅ ingest 范围 = **整个 Obsidian SQL 子数据库** + 新增知识处理
3. ✅ top_k = **默认 5**
4. ✅ **混合策略**(gbrain 为主,Read/Grep 兜底)

### 1.3 关键约束(CLAUDE.md 红线,沿用 Phase 2-3c)

- ❌ 禁 rm / Remove-Item / del 任何文件
- ❌ 禁 git reset --hard / git clean -fd / git checkout --
- ❌ 禁 DROP / TRUNCATE / DELETE FROM 不带 WHERE
- ❌ 禁文件名用 \ / : * ? " < > |
- ✅ 临时文件写 C:\Temp\,不写 ~/.tmp/
- ✅ 单次 Write ≤ 400 行 / 8000 tokens(避 120s abort)
- ✅ Edit 用锚定 old_string 追加

### 1.4 gbrain 现状(2026-10-15 验证)

- 版本:gbrain v0.60.214.0(PGLite + pgvector + keyless + conservative)
- 引擎:PGLite local,路径 `C:\Users\Duanyi\.gbrain\brain.pglite`
- Live serve:pid 177804 (MCP,Connected)
- 升级提示:0.60.232.0 available(本次不升级,避免兼容性问题)
- 可用命令:`import` / `sync` / `query` / `search` / `recall` / `remember` / `get` / `list`
- MCP 通道:用户 session 中应有 `mcp__plugin_gbrain_gbrain__*` 系列工具

---

## 二、v2.0 目标

把 sql-skill 从"自闭 10 章"升级到"跨 1GB+ Obsidian SQL vault RAG 增强":

| 维度 | v1.0 | v2.0 |
|---|---|---|
| 知识范围 | sql-skill 10 章 / 5161 行 | 整个 Obsidian SQL vault / 1GB+ |
| 召回方式 | 手动 Read(agent 选文件) | gbrain semantic recall 自动 top-5 |
| 同义词 | ❌(文件名/标题严格匹配) | ✅(向量语义召回) |
| 新增知识 | 手动复制粘贴到 chapter | gbrain sync 自动 ingest |
| 跨目录 | 手动 Read 多个文件 | 一次性 semantic 召回 |

---

## 三、v2.0 必交付清单

### 3.1 ingest 整个 Obsidian SQL vault

| 路径 | 范围 | 优先级 |
|---|---|---|
| `E:/obsidian/SQL/00-索引.md` | 资源总索引 | 1 |
| `E:/obsidian/SQL/08-sql-skill/` | sql-skill 10 章 + 4 辅助 | 1 |
| `E:/obsidian/SQL/03-use-the-index-luke/` | luke 48 章 + pg-docs 5 章 + SQLBolt 17 课 | 1 |
| `E:/obsidian/SQL/02-sql-tutorial-civilian7/` | 1065 题评测 | 2 |
| `E:/obsidian/SQL/04-awesome-postgres/` | PG 资源汇总 | 2 |
| `E:/obsidian/SQL/05-sql-style-guide/` | SQL 风格 | 3 |
| `E:/obsidian/SQL/01-nl2sql-handbook/` | NL2SQL 综述 199M | 3(按需) |

**执行**:
```bash
# 一次性 ingest(在用户 session / kill serve 后)
gbrain import "E:/obsidian/SQL/08-sql-skill/"
gbrain import "E:/obsidian/SQL/03-use-the-index-luke/"
gbrain import "E:/obsidian/SQL/02-sql-tutorial-civilian7/"
# 可选
gbrain import "E:/obsidian/SQL/04-awesome-postgres/"
gbrain import "E:/obsidian/SQL/05-sql-style-guide/"
# 跳过 199M 的 nl2sql-handbook(可按需 sub-ingest)
```

### 3.2 sql-skill SKILL.md v2.0 更新

把"How to Use" 改为 **4 层 lookup**(gbrain + cheatsheet + chapter + evidence-skill):

```markdown
## How to Use This Skill v2.0

写任何 SQL / 排错 / 调性能,按以下 4 层顺序 lookup:

### Layer 0: gbrain semantic recall(NEW · v2.0)
- 调用 `gbrain query(question, --limit 5)` 或 `mcp__gbrain__query`
- 跨整个 Obsidian SQL vault(1GB+) 语义召回 top-5
- 同义词 / 上下文理解(优于 Grep 关键词)
- fallback Read / Grep

### Layer 1: cheatsheet.md
- 13 决策表 + 18 关键经验(本 skill 沉淀)
- 适用于"快速决策"

### Layer 2: 对应 chapter
- ch01-ch10(本 skill 沉淀)
- 适用于"deep dive"

### Layer 3: evidence-skill 业务侧
- 业务侧雷区(中文 schema / FDW / BI 性能 / MCP)
- 详 `E:/Users/Duanyi/.claude/skills/evidence-skill/`
```

### 3.3 新增知识同步策略(3 通道)

| 通道 | 适用 | 触发 | 频率 |
|---|---|---|---|
| **A. Cron 周期同步** | Obsidian app 编辑 / 外部新增 | 操作系统 Task Scheduler / cron | 每周一次 |
| **B. Claude Code hook** | Claude 写新 chapter / 新 evidence | PostToolUse Write/Edit | 即时 |
| **C. Manual** | 大批新增 / 重大结构变化 | 用户手动 `gbrain sync` | 临时 |

**实施**:
- A:Windows Task Scheduler 周日 02:00 跑 `gbrain sync --repo "E:/obsidian/SQL/"` 
- B:加 `~/.claude/hooks/post-write-auto-ingest.py`,监听 Write/Edit 完成 → `gbrain sync --source sql-skill --newer-than 1h`
- C:写 `tools/ingest-sql-vault.sh` 一键脚本

### 3.4 验证

- 5 条 test query(覆盖跨目录 + 同义词 + 实战)
- 10 题 civilian7 验证答案质量
- 1 ingest 完整性检查(`gbrain doctor`)

---

## 四、4 层 lookup 详细设计

### 4.1 Layer 0: gbrain semantic recall

```python
# agent 接到 SQL 问题时
def lookup(question):
    # Layer 0: gbrain semantic recall
    hits = gbrain_query(
        question=question,
        limit=5,  # 用户确认
        scope=["08-sql-skill", "03-use-the-index-luke", "02-sql-tutorial-civilian7"]
    )
    # hits: [{path, snippet, score}, ...]
    return hits
```

**优势**:
- 跨 1GB+ vault
- 同义词召回("大 OFFSET 慢" → "keyset pagination")
- top-5 排序 + 摘要

**fallback**:
- gbrain 故障 → Read(chapters/chNN-*.md) 兜底
- 罕见关键词 → Grep 兜底

### 4.2 Layer 1-3: 沿用 v1.0(cheatsheet / chapter / evidence-skill)

不变,详 v1.0 handoff § 二。

---

## 五、新增知识同步机制详细设计

### 5.1 通道 A:Cron 周期同步(主)

**Windows 平台**:
```powershell
# 创建任务计划(每周日 02:00)
$action = New-ScheduledTaskAction -Execute "gbrain" -Argument "sync --repo E:/obsidian/SQL/ --json"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2am
Register-ScheduledTask -TaskName "gbrain-sql-vault-sync" -Action $action -Trigger $trigger
```

**优势**:
- 覆盖 Obsidian app 编辑(外部)
- 简单可靠
- 不需要 hook 基础设施

### 5.2 通道 B:Claude Code PostToolUse hook(辅)

`~/.claude/hooks/post-write-auto-ingest.py`:
```python
#!/usr/bin/env python3
"""PostToolUse hook: 写完 .md 后触发 gbrain sync"""
import subprocess, json, os, sys

# 读 hook payload
payload = json.load(sys.stdin)
tool_name = payload.get("tool_name", "")
file_path = payload.get("tool_input", {}).get("file_path", "")

# 只对 .md 文件 + 落在 Obsidian SQL vault 内触发
if tool_name in ("Write", "Edit") and file_path.endswith(".md"):
    if "E:/obsidian/SQL/" in file_path or "E:\\obsidian\\SQL\\" in file_path:
        # 触发增量 ingest
        try:
            subprocess.run(
                ["gbrain", "sync", "--repo", "E:/obsidian/SQL/", "--newer-than", "1h"],
                timeout=300, capture_output=True
            )
        except Exception as e:
            print(f"auto-ingest failed: {e}", file=sys.stderr)
```

**优势**:
- 写新 chapter 即时 ingest
- 不需用户手动操作
- 增量同步,只处理 1h 内新文件

**风险**:
- 频繁触发可能慢(`gbrain sync` 30s-2min)
- 解决:加 `--newer-than 1h` 增量 + debounce 5min

### 5.3 通道 C:Manual 一键脚本

`F:/soft/00selfmade/sql-skill/tools/ingest-sql-vault.sh`:
```bash
#!/bin/bash
# 一键 ingest 整个 Obsidian SQL vault
set -e

echo "=== 1/3: 优先级 1 目录 ==="
gbrain import "E:/obsidian/SQL/08-sql-skill/" --workers 4
gbrain import "E:/obsidian/SQL/03-use-the-index-luke/" --workers 4

echo "=== 2/3: 优先级 2 目录 ==="
gbrain import "E:/obsidian/SQL/02-sql-tutorial-civilian7/" --workers 4
gbrain import "E:/obsidian/SQL/04-awesome-postgres/" --workers 4

echo "=== 3/3: 优先级 3 目录 ==="
gbrain import "E:/obsidian/SQL/05-sql-style-guide/" --workers 4

echo "=== 验证 ==="
gbrain doctor --json

echo "✅ 全部 ingest 完成"
```

---

## 六、5 条 test query(覆盖跨目录 + 同义词 + 实战)

| Query | 期望召回 |
|---|---|
| 1. "如何优化大 OFFSET 性能" | ch08 §5 + luke sql-explain-result-set.html + keyset pagination 实战 |
| 2. "中文 schema 假名修复" | ch07 §5 + evidence-skill ch05 + `ds` `shop_name` 实战 |
| 3. "递归 CTE 取前 N 个斐波那契" | ch04 §6 + civilian7 advanced recursive-cte.sql |
| 4. "JSONB 字段 GIN 索引大小" | ch07 §1 + luke sql-anatomy-gin.html + jsonb_path_ops |
| 5. "postgres_fdw 跨 DB JOIN 性能" | ch07 §4 + evidence-skill ch07 + 2-segment path 雷区 |

每条 query 跑 `gbrain query "<query>" --limit 5`,人工检查 top-5 是否覆盖期望。

---

## 七、验收清单

- [ ] gbrain ingest 完成 7 目录(优先级 1-3)
- [ ] 5 条 test query 召回质量 OK
- [ ] 10 题 civilian7 答案质量 OK(至少 7/10 答对)
- [ ] SKILL.md "How to Use" v2.0 更新(Layer 0 gbrain recall)
- [ ] Cron 任务注册成功
- [ ] PostToolUse hook 写完 + 注册到 settings.json
- [ ] Manual ingest 脚本可一键跑
- [ ] handoff-sql-skill-v2-rag-2026-10-15.md 已写

---

## 八、不做的事(明确边界)

- ❌ 不升级 gbrain 0.60.232.0(避免兼容性问题,留 v3.0)
- ❌ 不 ingest 199M 的 nl2sql-handbook 全部(按需)
- ❌ 不重写 v1.0 10 章 chapter(只更新 SKILL.md 集成层)
- ❌ 不修改 evidence-skill
- ❌ 不实施评测集自动化(Phase 5+)

---

## 九、风险与避坑

| 风险 | 避坑 |
|---|---|
| gbrain `pglite_busy` 锁 | 一次性 setup 在 kill serve 后跑 `gbrain import`;运行时只走 MCP |
| ingest 199M 慢 | nl2sql-handbook 跳过 / sub-ingest |
| semantic 召回不准 | 5 条 test query 验证 + 反馈调优 |
| hook 频繁触发慢 | `--newer-than 1h` 增量 + 5min debounce |
| 跨平台 cron(Windows / Linux) | Windows Task Scheduler + cron 双方案 |

---

## 十、下一步

1. ✅ 用户已对齐 4 项(2026-10-15)
2. invocation **`superpowers:writing-plans`** 写 v2.0 实施计划
3. 计划批准后:Native 执行 6 步骤
4. 每步完成前:`superpowers:verification-before-completion`