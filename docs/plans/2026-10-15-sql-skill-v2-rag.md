# sql-skill v2.0 — gbrain RAG 集成 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (本会话 Native). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** sql-skill v2.0 集成 gbrain RAG,跨整个 Obsidian SQL vault 1GB+ 沉淀。4 层 lookup:gbrain semantic recall → cheatsheet → chapter → evidence-skill。新增知识 3 通道同步:Cron + Claude Code hook + Manual。

**Tech Stack:** gbrain v0.60.214.0 (PGLite + pgvector + keyless) / Bash / PowerShell / Python hook / Markdown

**Spec:** `F:/soft/00selfmade/sql-skill/docs/superpowers/specs/2026-10-15-sql-skill-v2-rag-design.md`

## Global Constraints

- **gbrain 引擎**:PGLite local(`C:\Users\Duanyi\.gbrain\brain.pglite`),版本 0.60.214.0(不升级 0.60.232.0)
- **Live serve**:pid 177804(MCP 锁),一次性 setup 需 kill serve;运行时只走 MCP
- **ingest 范围**:`E:/obsidian/SQL/` 7 目录(优先级 1-3,跳过 199M 的 nl2sql-handbook)
- **top_k**:5(用户确认)
- **CLAUDE.md 红线**:禁 rm/Remove-Item;禁 git reset --hard;禁 DROP/TRUNCATE/DELETE 不带 WHERE
- **临时文件**:`C:\Temp\`(不写 `~/.tmp/`)
- **单次 Write ≤ 400 行 / 8000 tokens**(避 120s abort)
- **执行方式**:Native(用户预选)

## Review Focus

5 个 spec 涉及但无 task 测试的潜在失误面:

1. **gbrain pglite_busy 锁**:补救 — 一次性 ingest 在 kill serve 后跑;运行时只走 MCP 工具;Manual 脚本先 stop-serve-import-restart-serve。
2. **ingest 199M nl2sql-handbook 慢**:补救 — 跳过 199M 全部,留 v3.0 按需 sub-ingest。
3. **PostToolUse hook 频繁触发慢**:补救 — `--newer-than 1h` 增量 + 5min debounce + `if ".md" in file_path` 过滤。
4. **semantic 召回质量差**:补救 — 5 条 test query 验证 + 反馈调优;fallback Read/Grep 兜底。
5. **跨平台 cron 兼容性**:补救 — Windows Task Scheduler 优先,Linux cron 作 fallback,文档说明双方案。

---

## Task 1: 一次性 ingest 整个 Obsidian SQL vault(优先级 1-3)

**Files:**
- Create: `F:/soft/00selfmade/sql-skill/tools/ingest-sql-vault.sh`
- Bash: kill gbrain serve → gbrain import → restart serve

**Interfaces:**
- ingest 完成 5 目录(优先级 1-2 全 ingest,3 部分)
- gbrain doctor 报告 green

- [ ] **Step 1: 写 `tools/ingest-sql-vault.sh` 一键脚本(优先级 1-3)**
- [ ] **Step 2: 备份 live serve 状态 + kill serve(pid 177804)**
- [ ] **Step 3: 跑优先级 1 ingest(sql-skill + luke)**
- [ ] **Step 4: 跑优先级 2 ingest(civilian7 + awesome-postgres)**
- [ ] **Step 5: 跑优先级 3 ingest(sql-style-guide)**
- [ ] **Step 6: 跳过 199M nl2sql-handbook(留 v3.0)**
- [ ] **Step 7: 重启 gbrain serve**
- [ ] **Step 8: 跑 `gbrain doctor` 验证 ingest 完整性**
- [ ] **Step 9: invocation `superpowers:verification-before-completion`**

## Task 2: 5 条 test query 验证召回质量

**Files:**
- Create: `F:/soft/00selfmade/sql-skill/docs/superpowers/v2-eval-queries.md`(test query + 期望召回 + 实际召回对比)

**Interfaces:**
- 5 条 query 跨目录 / 同义词 / 实战覆盖
- top-5 召回质量 OK

- [ ] **Step 1: 写 5 条 test query 文档(v2-eval-queries.md)**
- [ ] **Step 2: 跑 query 1: "如何优化大 OFFSET 性能"**
- [ ] **Step 3: 跑 query 2: "中文 schema 假名修复"**
- [ ] **Step 4: 跑 query 3: "递归 CTE 取前 N 个斐波那契"**
- [ ] **Step 5: 跑 query 4: "JSONB 字段 GIN 索引大小"**
- [ ] **Step 6: 跑 query 5: "postgres_fdw 跨 DB JOIN 性能"**
- [ ] **Step 7: 人工检查 top-5 召回,记录命中率**
- [ ] **Step 8: 召回质量 < 80% 触发调优(改 conservative mode / chunk_size)**
- [ ] **Step 9: invocation `superpowers:verification-before-completion`**

## Task 3: sql-skill SKILL.md v2.0 集成 Layer 0

**Files:**
- Edit: `E:/obsidian/SQL/08-sql-skill/SKILL.md` "How to Use" 段

**Interfaces:**
- Layer 0: gbrain semantic recall(NEW)
- Layer 1: cheatsheet
- Layer 2: chapter
- Layer 3: evidence-skill

- [ ] **Step 1: Read SKILL.md 当前 "How to Use" 段**
- [ ] **Step 2: Edit SKILL.md 加 Layer 0 gbrain recall 段**
- [ ] **Step 3: Edit SKILL.md 调整三层 → 四层 lookup 描述**
- [ ] **Step 4: Edit SKILL.md "调研入口" 段标注 gbrain 已 ingest**
- [ ] **Step 5: Edit SKILL.md "已知边界" 段加 v2.0 进展行**
- [ ] **Step 6: verification — SKILL.md grep gbrain / Layer 0 ≥ 3 处**

## Task 4: 新增知识同步 - 通道 A(Cron 周期同步)

**Files:**
- Create: `F:/soft/00selfmade/sql-skill/tools/register-cron-sync.ps1`
- Bash: 注册 Windows Task Scheduler

**Interfaces:**
- 每周日 02:00 自动跑 `gbrain sync --repo "E:/obsidian/SQL/"`
- 日志可查

- [ ] **Step 1: 写 `register-cron-sync.ps1` 创建 Windows Task Scheduler 任务**
- [ ] **Step 2: 跑 `register-cron-sync.ps1` 注册任务**
- [ ] **Step 3: 验证任务已注册(ScheduledTasks cmdlet)**
- [ ] **Step 4: (可选)写 Linux cron fallback `register-cron-sync.sh`**

## Task 5: 新增知识同步 - 通道 B(Claude Code PostToolUse hook)

**Files:**
- Create: `~/.claude/hooks/post-write-auto-ingest.py`
- Edit: `~/.claude/settings.json` 注册 hook

**Interfaces:**
- Claude 写 .md 落到 Obsidian SQL vault → 自动 `gbrain sync --newer-than 1h`
- 5min debounce 防频繁触发
- 不影响主流程(timeout 5min 兜底)

- [ ] **Step 1: 写 `~/.claude/hooks/post-write-auto-ingest.py`(Python hook)**
- [ ] **Step 2: 验证 hook 语法(python -m py_compile)**
- [ ] **Step 3: Read `~/.claude/settings.json` 现有 hooks 配置**
- [ ] **Step 4: Edit `~/.claude/settings.json` 注册 PostToolUse hook**
- [ ] **Step 5: 验证 hook 触发(测试写一个 .md 模拟)**

## Task 6: 新增知识同步 - 通道 C(Manual 一键脚本)

**Files:**
- Create: `F:/soft/00selfmade/sql-skill/tools/ingest-sql-vault.sh`(已在 Task 1 Step 1 写)

**Interfaces:**
- 一键 ingest 整个 Obsidian SQL vault
- 进度可见
- 失败回滚

- [ ] **Step 1: 验证 `ingest-sql-vault.sh` 可执行**
- [ ] **Step 2: 文档化在 v2.0 handoff "新增知识" 段**

## Task 7: v2.0 验证 + handoff

**Files:**
- Create: `F:/soft/00selfmade/sql-skill/handoff-sql-skill-v2-rag-2026-10-15.md`
- Edit: `E:/obsidian/SQL/08-sql-skill/cheatsheet.md`(Layer 0 决策表)

**Interfaces:**
- 10 题 civilian7 答案质量验证(至少 7/10 答对)
- handoff v2.0 完整版交付

- [ ] **Step 1: 跑 10 题 civilian7 验证(Layer 0 gbrain + Layer 1-3 兜底)**
- [ ] **Step 2: 记录答案质量 + 召回命中率**
- [ ] **Step 3: Edit `cheatsheet.md` 加 "Layer 0 gbrain" 决策表条目**
- [ ] **Step 4: 写 `handoff-sql-skill-v2-rag-2026-10-15.md`**
  - v1.0 → v2.0 演进
  - gbrain ingest 状态
  - 4 层 lookup 详细
  - 3 通道同步机制
  - 验证结果
  - 已知限制 + v3.0 演进方向
- [ ] **Step 5: Phase v2.0 ledger 更新**

---

## Execution Handoff

Plan 完成,保存到 `F:/soft/00selfmade/sql-skill/docs/superpowers/plans/2026-10-15-sql-skill-v2-rag.md`。

执行方式:用户已选 **Native**(本会话内顺序完成)。7 任务跨 6 文件 + 1 handoff。任务 1 (ingest) 在 kill gbrain serve 状态下执行,任务 2-7 在 MCP 通道下执行。

Native 顺序:Task 1 ingest → Task 2 验证 → Task 3 SKILL.md → Task 4 Cron → Task 5 hook → Task 6 manual(已含 Task 1)→ Task 7 handoff。