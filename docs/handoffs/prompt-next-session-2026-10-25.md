# prompt — sql-skill v0.2 token 优化完成 · 新会话接力 Phase 4/5 剩余

承接 `F:\soft\00selfmade\sql-skill\handoff-sql-skill-v0-2-token-optimization-2026-10-25.md`
(必读顺序在 § 一;背景/实测/改动清单/避坑全在里面,此处不重复)

**先读这 5 个文件建立全貌**:
1. `F:\soft\00selfmade\sql-skill\handoff-sql-skill-v0-2-token-optimization-2026-10-25.md`
2. `F:\soft\00selfmade\skill-optimizer\handover\sql-skill-token-efficiency.md`
3. `F:\soft\00selfmade\sql-skill\docs\audit\sql-skill-audit-2026-10-25.md`
4. `F:\soft\00selfmade\sql-skill\sql-skill\SKILL.md`
5. `F:\soft\00selfmade\sql-skill\handoff-phase-4-verify-2026-10-17.md`

**当前状态**:sql-skill v0.2 token 优化已交付(index 231→98 / load 5503→1908 tok,validator 0 警告,三处副本 md5 一致);Phase 4 验证完成;Phase 5 评测 MVP 完成(1090 题 100% 覆盖)。**全部改动未 commit**。

**分支/基线**:`main` @ `5825eac`,工作区有未 commit 改动(清单见 handoff § 四)。

**必交付(按优先级)**:
1. 重启 Claude Code session 后验证 Channel A 自动 PostToolUse 是否触发(查 `~/.claude/.cache/post-write-auto-sync.log` 有无 `HOOK ENTRY`);不触发则按 `F:\soft\00selfmade\sql-skill\docs\handoffs\channel-a-debug-plan-2026-10-17.md` 走 H1(matcher 数组格式)
2. Phase 5 续:多 DB(MySQL/Oracle/SQL Server anti-pattern + ch10 multi-db)+ hook 内嵌 MCP 客户端
3. eval_civilian7 扩展:`--mode claude-api`(需 API key)、`--mode baseline`(需先用 `E:\obsidian\SQL\02-sql-tutorial-civilian7\src\cli\generate.py` 生成 SQLite 测试 DB)
4. 询问用户是否 commit / push GitHub(仓库 https://github.com/kizemo/sql-skill)

**等用户动作(不可代劳)**:Cron 通道 B 注册(`PowerShell -ExecutionPolicy Bypass -File F:\soft\00selfmade\sql-skill\tools\register-cron-sync.ps1`)+ gbrain embedding(`VOYAGE_API_KEY` 环境变量)

**禁止事项**:禁 rm 用户文件 / 禁 git reset --hard / 禁 DROP / 禁 "skip permissions" 绕过 / 临时文件写 `C:\Temp\` / 单次 Write ≤ 400 行;**不重做 v0.1 沉淀与本次 v0.2 优化**(已 git 化 + 已部署);改 skill 前先跑 `python -m scripts.run --skill <dir> --scope audit-only` 取基线,改后复跑对比

**加速模式**:无;严格按 handoff 路径顺序执行,不急不糙。
