# handoff — sql-skill v0.3 · 2026-10-26

> **本会话完成**:多方言 ch11 + hook 内嵌 MCP 客户端(即写即同步)+ eval 新模式 + README 重写 + **已 commit 并 push GitHub**
> **GitHub**:https://github.com/kizemo/sql-skill · main @ `2cd9291`(本地 = 远端,工作区 clean)
> **新会话任务**:见 § 六

---

## 一、必读顺序

| # | 路径 | 用途 |
|---|---|---|
| 1 | 本文件 | 当前状态 + 下一步 |
| 2 | [CHANGELOG](../CHANGELOG.md) | v0.1→v0.3 全部变更 / 修复 / 指标 |
| 3 | [README](../../README.md) | 项目全貌 + 价值主张 + 部署 + 评测证据 |
| 4 | [DEPLOY](../DEPLOY.md) | 三种部署形态 + Windows hook 路径坑 |
| 5 | [eval-ab-2026-10-26](../audit/eval-ab-2026-10-26.md) | 执行准确率 A/B 负结果分析 |

---

## 二、本会话最重要的发现(不在原 handoff 预期内)

### 🔴 全局性根因:Claude Code 的 hook 在 Windows 上必须是正斜杠路径

**症状**:所有 hook 静默不执行。Channel A 写文件 → vault 里的文件 → brain 里永远查不到。

**根因**:Claude Code 用 `/usr/bin/bash -c "<cmd>"` 执行 hook。settings.json 里

```json
"command": "C:\\Python314\\python.exe \"F:\\...\\post-write-auto-sync.py\""
```

反斜杠**未被引号包裹的可执行路径**被 bash 当转义符吃掉 → `C:Python314python.exe` → `command not found`。

**证据**:今天早前 session 的 transcript 里 `hookInfos`/`hookErrors` 记录了
`C:Python314python.exe: command not found` 和
`C:UsersDuanyi.claudehooksstop-auto-handoff: command not found`。

**影响面**:`~/.claude/settings.json` 11 条 hook 里 **10 条是死的**,其中包括
`no-delete-gate.py` —— 也就是 CLAUDE.md 里那条**删除护栏一直是关的**。
唯一活着的 `guard-secret-files.js` 只因 `node` 走 PATH + 脚本路径带双引号。

**修复**:全部改成正斜杠(`C:/Python314/python.exe "F:/..."`)。
备份在 `~/.claude/backups/settings.json.recovery-pre-paths-2026-10-25.bak`。

**推论(已证伪的两条旧假设)**:
- ❌ handoff v0.2 的 H1「matcher 数组格式」—— matcher 没问题
- ❌ handoff v0.2 的 H2「settings.json 未被本 session 加载」—— **settings 被加载了**
  (gbrain 那几条 hook 正常执行了 11s),只是命令本身跑不起来
- ✅ 顺带证伪:**Claude Code 会热重载 settings.json** —— 改完当次就生效,不用重启

### 🟡 hook payload 解析(已加固,原 bug 未复现)

观测到一次 `Invalid hook payload: Expecting ',' delimiter: line 1 column 984`。
6 种 payload 形态(短中文 / 60KB 超长 / 转义反斜杠 / 引号括号 / 换行tab / emoji)
+ 真实 Write/Edit payload 全部复现不出。

**加固**:改成单次二进制读 + 显式 UTF-8 解码(不依赖 locale 编码);
解析失败时把原始字节落盘到 `~/.claude/.cache/post-write-auto-sync.payload.err`
(4096 字节上限),下次复现可直接看原始数据。

---

## 三、本会话交付

### 3.1 skill 内容(v0.3)

| 项 | v0.2 | v0.3 |
|---|---:|---:|
| index(每会话都付) | 98 tok | **100 tok**(预算 ~100 ✅) |
| load(触发时) | 1,908 tok | **2,005 tok**(预算 ~5,000 ✅) |
| 单次触发合计 | 2,006 tok | **2,105 tok** |
| validator 警告 | 0 | **0** |
| 章节 | 10 | **11** |
| 章节正文行数 | 3,918 | **4,375** |
| 术语索引 | 84 | **99** |

- **ch11-multi-db.md(434 行)**:MySQL / Oracle / SQL Server 的语义地雷(隐式转换方向、空串语义、分页原子性、DDL 事务性)、索引模型差异、方言反模式、跨方言对照表、跨库协作选型。
- **ch10** 新增 §7「多 DB 协作」。
- **frontmatter**:description 覆盖 4 个方言;triggers 去掉与 desc 重复的 `index decision`,新增 `MySQL / Oracle / MSSQL`;version → 0.3.0。
- **references/topic-index.md** 84 → 99 术语。

### 3.2 hook 内嵌 MCP 客户端(即写即同步)

`tools/post-write-auto-sync.py` 三层降级:

1. **MCP over HTTP** —— 内嵌最小 MCP streamable-HTTP 客户端
   (`initialize` → `notifications/initialized` → `tools/call put_page`),
   JSON 与 SSE 两种响应模式都支持。**13/13 mock server 测试通过**
   (mock server 在 `C:\Temp\mock_mcp_server.py`)
2. **gbrain CLI** —— `gbrain put <slug>` 内容走 **stdin**(章节 25KB+,
   `--content` 命令行传参会撞 Windows 32KB 上限)
3. **queue 文件** —— 兜底,绝不丢内容

**实测**:Write → hook → brain 可查 **≈1 秒**(原先要等下一个 session)。
queue 目录 0 新增文件。

> ⚠️ HTTP MCP 通道目前**没机会生效**:brain 的 PGLite 被 `gbrain serve`(stdio)锁着,
> `gbrain serve --http` 起不来。CLI 通道是当前实际生效的通道。

### 3.3 eval_civilian7 扩展

- **新模式 `--mode claude-api`**:模型答 SQL → SQLite 执行 → 与 reference SQL
  **结果集**对拍(执行准确率)。`--context none|skill` 做 A/B、`--seed` 固定抽样、
  `--model` / `--api-sample`。
- **`--mode baseline` 从崩溃修好**:reference SQL 可执行率 **95.6%**(282/300)。
  修了一串口径 bug —— `reference_sql` 有 str/dict 两种形态(原代码只处理 dict)、
  多语句不能一次执行(`sqlite3.execute` 限制)、`DELIMITER` 是 MySQL 客户端指令、
  `BEGIN` 与 sqlite3 隐式事务冲突、`CREATE VIEW` 重复创建、以及
  「故意触发约束违例」的题不该算坏题。
- **评测覆盖率仍 100%**(1090/1090),无回归。

### 3.4 文档

- **README 重写**为 GitHub 展示页:TL;DR / 问题→解法→实测 / 渐进式披露结构图 /
  token 前后对比 / 11 章索引 / 评测证据 / 快速开始 / 4 通道图 / 与 evidence-skill
  边界表 / 目录结构 / 依赖 / 贡献 checklist / **已知限制 6 条** / 路线图 / 致谢。
- **CHANGELOG.md**(Keep a Changelog 格式)、**DEPLOY.md**(三种部署形态 + 排障表)、
  **docs/audit/eval-ab-2026-10-26.md**(A/B 负结果分析)。
- **.gitattributes**:防止 `.sh` 在 Windows checkout 成 CRLF → Linux 上
  `env: 'bash\r'` 崩掉。

---

## 四、一个诚实的负结果(重要)

**执行准确率 A/B(12 题,同 seed)**:

| 轮次 | 计分题 | 正确 | 准确率 |
|---|---:|---:|---:|
| `context=none` | 12 | 2 | 16.7% |
| `context=skill` | 11 | 2 | 18.2% |

**那 2 个百分点是分母假象**:0 题从 wrong 翻成 correct,唯一变化是 `a19-03`
因 prompt 变长而**超时**(`wrong → api_error`),分母 12→11。去掉那题两轮都是 2/12。

**结论**:把知识原文塞进 prompt **不是 skill 的正确用法**,只增加超时风险。
skill 的价值在**路由到正确的章** —— 而这被样本大 90 倍的指标测了:**1090 题 100% 覆盖**。

**因此本仓库只声称「路由覆盖率 100%」,不声称「skill 让 SQL 更准」。**
README § 4.3 和 § 十一都按这个口径写了。

要把这个指标做实的 5 条改进项在 `docs/audit/eval-ab-2026-10-26.md` § 5。

---

## 五、Git 状态

```
main @ 2cd9291  (= origin/main,工作区 clean)
```

| commit | 内容 |
|---|---|
| `4359b6b` | feat(skill): v0.3 渐进式披露 + 多方言 ch11 |
| `c5d156d` | feat(tools): hook 内嵌 MCP 客户端,Channel A 改即写即同步 |
| `073698f` | feat(eval): eval_civilian7 加 claude-api 模式并修 baseline 口径 |
| `a304d29` | docs: README 重写为 GitHub 展示页 + CHANGELOG + DEPLOY 指南 |
| `303edb2` | fix: 补 .gitattributes,防止 .sh 带 CRLF |
| `2cd9291` | docs: 补执行准确率 A/B 报告 —— 一个诚实的负结果 |

**三处副本已同步且 md5 一致**:
- `sql-skill/`(仓库源)
- `~/.claude/skills/sql-skill/`(Claude Code 加载)
- `E:/obsidian/SQL/08-sql-skill/`(vault / 4 通道同步源)

> 唯一差异:仓库源多了 `.skill-forge-baseline.json`(skill-forge 漂移检测基线,部署不需要)。

---

## 六、下一步

### ① 等用户动作(不可代劳)

- **Cron 通道 B 注册**:
  ```powershell
  PowerShell -ExecutionPolicy Bypass -File F:\soft\00selfmade\sql-skill\tools\register-cron-sync.ps1
  ```
  验证:`Get-ScheduledTask -TaskName "gbrain-sql-skill-sync"`
- **gbrain embedding enable**:需 `VOYAGE_API_KEY` 环境变量
  ```bash
  gbrain embeddings enable --embedding-model <provider:model>
  ```

### ② 待用户确认的清理

vault 里有 **9 个测试文件**(会被同步进 brain):
- 2026-10-17 遗留 4 个:`test-channel-a-{async,debug,real,trigger}-2026-10-17.md`
- 2026-10-25 本会话 4 个:`test-channel-a-{session2,hotreload,directsync,final}-2026-10-25.md`
- 另 1 个 `test-channel-a-debug-2026-10-17.md`

**删除需用户点头**(CLAUDE.md 红线)。

### ③ 建议的下一步开发

- **把 A/B 指标做实**:换强模型 + 样本 ≥100 + 分层抽样 + 加 `context=chapter`
  / `context=cheatsheet` 模式(cheatsheet 信息密度远高于章节原文)
- **ch10 / ch11 专项题库**:填自动评测盲区
- **HTTP MCP 通道真正跑通**:需要 brain 从 stdio serve 切到 `--http`,
  或接受 stdio + CLI 的现状
- **全局 hook 路径体检**:用户机器上其它 skill 的 `settings.json` 是否也有反斜杠路径

---

## 七、环境 / 避坑

- 分支:`main`,HEAD `2cd9291`(= origin/main)
- Python:`C:\Python314\python.exe`(3.14.6)· 仅标准库
- `anthropic` SDK 实为**中继 shim**(带 `inference_geo` / `thinking`,
  **没有 `temperature` 参数**)—— 按签名探测再传参
- gbrain:`E:\Users\Duanyi\.claude\Cache\.bun\bin\gbrain.exe`,
  `gbrain put` 在 serve 持锁时可用(走 filesystem persistence)
- `python -m scripts.run` 必须在 skill-forge 目录下跑
- **skill-forge 会往 skill 目录写产物**(best.md / audit-report.md /
  skillopt-benchmark.jsonl)→ 跑完要移到 `docs/audit/`
- Windows 上 Python print 中文会 GBK 崩 → 加 `PYTHONIOENCODING=utf-8`
- 临时文件一律写 `C:\Temp\`
