# prompt — 下一会话

承接:`F:\soft\00selfmade\sql-skill\docs\handoffs\handoff-sql-skill-v0-3-2026-10-26.md`

**当前基线**:`main` @ `2cd9291`(= origin/main,工作区 clean,已 push)

## 必交付

1. **把执行准确率 A/B 做实**(最有价值的下一步):
   - 换强模型 `--model claude-sonnet-5`(或 claude-opus-5-5)
   - 样本 ≥100 题,分层抽样保证 beginner/intermediate/advanced 各 1/3
   - 加 `--context chapter` / `--context cheatsheet` 模式(cheatsheet 决策表
     信息密度远高于章节原文 4000 字符)
   - 记录每题延迟,统计 skill 上下文的 token/延迟开销
   - 更新 `docs/audit/eval-ab-*.md` + README § 4.3
2. **ch10 / ch11 专项题库**(当前自动评测的盲区)
3. **HTTP MCP 通道真正跑通**(需 brain 从 stdio serve 切到 `--http`)

## 禁止事项

- 禁 rm 用户文件 / 禁 `git reset --hard` / 禁 DROP / 禁 "skip permissions" 绕过
- 临时文件写 `C:\Temp\` / 单次 Write ≤ 400 行
- 不重做 v0.1 沉淀、v0.2 token 优化、v0.3 多方言(ch11 已交付)
- **不要把 A/B 结果吹大** —— 当前是负结果,README 已如实写,改口径要同时改报告

## 等用户动作(不可代劳)

- Cron 通道 B 注册:
  `PowerShell -ExecutionPolicy Bypass -File F:\soft\00selfmade\sql-skill\tools\register-cron-sync.ps1`
- gbrain embedding enable(需 `VOYAGE_API_KEY`)
- vault 里 9 个测试文件的清理(需用户点头)

## 加速模式

无。严格按 handoff 路径顺序执行,不急不糙。
