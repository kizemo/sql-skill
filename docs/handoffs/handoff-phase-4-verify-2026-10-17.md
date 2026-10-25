# sql-skill Phase 4 验证 · 2026-10-17

## 完成项

### Channel A 实测(部分通过 + 关键发现)

**通过**:
- ✅ 手动 PostToolUse hook 模拟 payload → 队列写入正常
  - queue 文件:`1792216966_sql-skill_chapters-test-channel-a-trigger-2026-10-17.json`
  - slug:`sql-skill/chapters-test-channel-a-trigger-2026-10-17`
  - debounce:`{"E:/obsidian/SQL/08-sql-skill/chapters/test-channel-a-trigger-2026-10-17.md": 1792216966.18651}`
- ✅ sync-queue-consumer.py 真实消费 → brain filesystem 写入正常
  - 输出:`C:\Users\Duanyi\.gbrain\content\cf1c1488-...\default\sql-skill\chapters-test-channel-a-real-2026-10-17.md`
- ✅ debounce 5min 窗口生效(只处理新文件/超窗口文件)

**未通过**:
- ❌ **Claude Code 自动 PostToolUse 在本 session 未触发**
  - 实测 3 次 Write(同 session,3 秒延迟后查队列)
  - queue 始终空,debounce 仅含手动触发的 2 条
  - 路径匹配、Python 命令、文件 payload 全部正确
  - 可能原因:Claude Code 当前 session-level hook 触发异常 / 设置加载问题

### Channel C 实测

- ✅ SessionStart hook 已注册(settings.json line 75-86)
- ✅ consumer 脚本验证可跑(dry-run + 真实执行)
- 注:本 session 启动未触发 Channel C(可能同上原因)

### Channel D(manual)

- ✅ `sync_to_brain()` 函数在 post-write-auto-sync.py 中可手动调

### Cron Channel B

- ❌ **未注册**(Get-ScheduledTask 返回空)
- ✅ 工具已就绪:`register-cron-sync.ps1` + `cron-sync-sql-skill.sh`
- **等用户 PowerShell 跑**:`PowerShell -ExecutionPolicy Bypass -File F:\soft\00selfmade\sql-skill\tools\register-cron-sync.ps1`

### gbrain 状态(PID 46940 已消亡,自动恢复)

- `gbrain_status` 显示 `recovered`(lock_held → recovered)
- 新 live serve PID 254540 持有脑锁(占 stdio)
- `gbrain doctor --json` 已可跑(filesystem-only fallback,DB 检查被 live serve 阻塞)
- `embedding_key_source` 缺 `VOYAGE_API_KEY` — embedding 未启用
- 全套 gbrain MCP 工具已可用(MCP HTTP 端点 127.0.0.1:3131)

### Phase 5 评测集自动化(eval_civilian7.py)— 完成 MVP

**结果**:
- 题数:**1090**(INDEX 写 1065,实测 1090)
- 75 YAML 文件,分布:beginner 342(含 lectures)+ intermediate 366 + advanced 382
- 覆盖率:**100.0%**(1090/1090)
- 每章覆盖题数:
  - ch01-grammar 918(含基础查询/case/null)+ ch02-joins 280 + ch03-window 245
  - ch04-cte 267 + ch05-aggregates 468 + ch06-set-ops 101
  - ch07-pg-specific 139(JSON/数组/DDL)+ ch08-indexes-perf 44 + ch09-antipatterns 59
- ch10-evidence-bridge 0 题(civilian7 不含 Text2SQL 题)

**实现要点**:
- 4 路匹配:tags + metadata.concepts + type 字段 + title/body_en 文本兜底
- 报告输出:JSON(机器可读)+ Markdown(摘要)
- 3 模式:`--mode count / skill-aware / baseline`(`--db PATH` 跑 reference SQL 自检)
- 不需 API key,纯本地匹配

**用法**:
```bash
python tools/eval_civilian7.py --mode count                 # 数题 + 分布
python tools/eval_civilian7.py --mode skill-aware           # 覆盖率(默认)
python tools/eval_civilian7.py --mode all --db PATH         # 全跑
```

**报告**:
- `eval_civilian7_report.json` — 完整机器可读
- `eval_civilian7_report.md` — markdown 摘要

## 待办(本 session 后续)

### Channel A 自动 PostToolUse 排查(用户已选"立即排查")

**已做诊断**(2026-10-17 14:50):
- 加 `debug_log()` 到 `post-write-auto-sync.py`(HOOK ENTRY + tool_name + 过滤决策)
- 写 vault 测试文件 → debug log **完全为空**
- → **Claude Code 完全没调 hook**(连 HOOK ENTRY 都没记录)

**根因收敛**:H2(settings.json 未被本 session 加载)最可能
- H3/H4/H5/H6 已排除(hook 未调用)
- H1(matcher 格式)不太可能(PreToolUse 用相同 `Edit|Write|MultiEdit` 格式,无证据显示被破坏)
- 修复路径:用户**重启 Claude Code session** → 重读 settings.json → 重测
- 详细排查计划见 `docs/handoffs/channel-a-debug-plan-2026-10-17.md`

可疑点(优先级):
1. Claude Code 当前 session 不重读 settings.json(已加载缓存)→ hook 配置不生效
2. matcher 格式 `Write|Edit|MultiEdit` 在新版 Claude Code 需改为数组 `["Write","Edit","MultiEdit"]`
3. PostToolUse 触发要求 tool_name 完全匹配某 matcher(可能不接受 `|` 分隔)

### Phase ② 续(用户选"close_owner 恢复")

- ✅ lock 已恢复
- ⏳ enable embedding:需用户配 `VOYAGE_API_KEY` 环境变量 / 或换 provider
- ⏳ ingest 优先级 2 vault(`04-awesome-postgres/` + `05-sql-style-guide/`)

### Phase 5 续

- ⏳ 多 DB 支持(MySQL/Oracle/SQL Server anti-pattern + ch10 加 multi-db 协作)
- ⏳ hook 内嵌 MCP 客户端(即写即同步)

## 测试残留(用户后续清理,非紧急)

- Vault:`E:/obsidian/SQL/08-sql-skill/chapters/test-channel-a-{trigger,real,async}-2026-10-17.md` 3 文件
- Brain filesystem:`.../default/sql-skill/chapters-test-channel-a-real-2026-10-17.md` 1 文件
- Queue processed:`.../processed/1792216966_*.json` + `1792217060_*.json` 2 文件
- 评测报告:`eval_civilian7_report.json` + `eval_civilian7_report.md`

## 当前 TaskList

- #1 [in_progress] ② enable gbrain embedding + ingest 优先级 2 vault
- #2 [completed] ① Cron 通道 B 注册 + Channel A 实测(部分)
- #3 [pending] ③ Phase 5:评测集自动化 + 多 DB + hook 升级(eval MVP 完成)

## 关键路径速查

| 用途 | 路径 |
|---|---|
| 项目根 | `F:/soft/00selfmade/sql-skill/` |
| Channel A hook | `F:/soft/00selfmade/sql-skill/tools/post-write-auto-sync.py` |
| Channel B 注册脚本 | `F:/soft/00selfmade/sql-skill/tools/register-cron-sync.ps1` |
| Channel C consumer | `F:/soft/00selfmade/sql-skill/tools/sync-queue-consumer.py` |
| eval_civilian7.py | `F:/soft/00selfmade/sql-skill/tools/eval_civilian7.py` |
| 队列目录 | `~/.claude/.cache/sql-skill-sync-queue/` |
| Debounce 状态 | `~/.claude/.cache/post-write-auto-sync-debounce.json` |
| Brain filesystem | `C:/Users/Duanyi/.gbrain/content/cf1c1488-.../default/` |
| Settings hooks | `E:/Users/Duanyi/.claude/settings.json` |

