# prompt — sql-skill v2.2 部署完成 · 新会话接力 Phase 4+

承接 `F:/soft/00selfmade/sql-skill/handoff-sql-skill-v2-2-deployed-2026-10-15.md`(必读 7 文件清单在 § 一)。

**当前状态**:sql-skill v2.2 已沉淀 10 章 + 4 辅助(~5161 行)+ 已部署到 `E:/Users/Duanyi/.claude/skills/sql-skill/` + GitHub 推送到 https://github.com/kizemo/sql-skill + 4 通道动态同步机制(通道 A/C 已注册,B 工具已写等用户跑 register-cron-sync.ps1,D manual 可用)+ gbrain brain 已有 18 pages(6 evidence-skill + 12 sql-skill)。

**下阶段任务**(优先级排序):① 注册 Cron 通道 B(用户跑 `register-cron-sync.ps1`)+ 测试 Channel A hook 实际触发 ② enable gbrain embedding(跑 `gbrain doctor --json`)+ ingest 优先级 2 目录(awesome-postgres / style-guide) ③ Phase 5:评测集自动化(civilian7 1065 题)+ 多 DB 支持(MySQL/Oracle/SQL Server)+ hook 升级内嵌 MCP 客户端。

**禁止事项**:禁 rm 用户文件 / 禁 git reset --hard / 禁 DROP / 禁禁 "skip permissions" 绕过 / 临时文件 `C:\Temp\` / 单次 Write ≤ 400 行;不重做 Phase 2-3c + v2.0-v2.2(所有沉淀已 git 化)。

**Rulings**(踩坑沉淀):sql-skill 部署成功路径 = evidence-skill 6 页 `mcp:put_page` 走 default source(避免 source-guard)+ bash 不可用假设走 PowerShell/全路径 bash.exe+ Claude Code skill 必须 SKILL.md 在根目录。

**加速模式**:无;严格按 handoff 路径顺序执行,不急不糙。