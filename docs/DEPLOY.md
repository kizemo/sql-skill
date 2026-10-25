# 部署指南

三种部署形态,按需选一。

---

## 方式 A:只装 Claude Code(推荐,零依赖)

### 1. 克隆并安装

```bash
git clone https://github.com/kizemo/sql-skill.git
cd sql-skill

mkdir -p ~/.claude/skills/sql-skill
cp -r sql-skill/* ~/.claude/skills/sql-skill/
```

Claude Code 会自动发现 `~/.claude/skills/sql-skill/SKILL.md`,按 frontmatter 的 `description` + `triggers` 路由。

### 2. 验证

问 Claude:

> 大 OFFSET 分页怎么优化?

预期:查 `cheatsheet.md` → 命中 `chapters/ch08-indexes-perf.md` §5 → 给 keyset 分页方案。

### 3. 项目级安装(可选)

```bash
mkdir -p <your-project>/.claude/skills/sql-skill
cp -r sql-skill/* <your-project>/.claude/skills/sql-skill/
```

---

## 方式 B:接 Obsidian vault(Read + Grep 检索)

把 skill 复制到 Obsidian SQL 子 vault,便于人工查阅 + agent 用 Grep 定位。

```bash
# 推荐目录结构
cp -r sql-skill/ E:/obsidian/SQL/08-sql-skill/
```

vault 路径不是硬编码在逻辑里的 —— `references/retrieval.md` 记录了检索路径与 fallback 顺序,换路径只需改那一个文件。

---

## 方式 C:接 gbrain(semantic recall + 自动同步)

### 前提

- 已装 [gbrain](https://github.com/garrytan/gbrain) 0.60+
- `~/.claude/settings.json` 里启用了 `gbrain@gbrain` 插件
- `default` 是唯一 source(多 source 会触发 source-guard 锁)

```bash
gbrain sources list          # 应该只看到 default
gbrain doctor --json         # 看 embedding_key_source / 引擎状态
```

### 知识同步(4 通道)

| 通道 | 触发 | 何时用 |
|---|---|---|
| A. PostToolUse hook | Claude 写 `.md` 到 vault | 主通道,写完即同步(≈1s) |
| B. Cron 每日 02:00 | 计划任务 | 同步 Obsidian app 的外部编辑 |
| C. SessionStart | 每次 Claude 启动 | 消费 A 遗留的 queue(兜底) |
| D. Manual | 你手动 | 应急 / 批量 ingest |

#### 注册通道 A(PostToolUse hook)

编辑 `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "C:/Python314/python.exe \"F:/path/to/sql-skill/tools/post-write-auto-sync.py\"",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

> ⚠️ **Windows 关键点**:hook 命令必须用**正斜杠**路径。
> Claude Code 用 `/usr/bin/bash -c "<cmd>"` 执行 hook,未加引号的 `C:\Python314\python.exe`
> 会被 bash 当转义符吃掉反斜杠 → `command not found` → hook **静默不执行**。
> 这是 2026-10-26 排查出来的根因,当时 11 条 hook 里有 10 条是死的。

#### 注册通道 B(Cron)

```powershell
PowerShell -ExecutionPolicy Bypass -File F:/path/to/sql-skill/tools/register-cron-sync.ps1
Get-ScheduledTask -TaskName "gbrain-sql-skill-sync"
```

#### 注册通道 C(SessionStart 消费 queue)

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "C:/Python314/python.exe \"F:/path/to/sql-skill/tools/sync-queue-consumer.py\"",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

### 启用 embedding(可选,让 recall 变准)

```bash
gbrain embeddings enable --embedding-model <provider:model>
```

需要对应的 API key 环境变量(默认 `VOYAGE_API_KEY`)。未启用时 gbrain 走 keyword 召回。

### 验证

```bash
# hook 是否被调用
tail -20 ~/.claude/.cache/post-write-auto-sync.log
# 期望看到:[auto-sync HH:MM:SS] OK synced sql-skill/xxx via cli
```

---

## 三处副本要手动同步

仓库源和两处部署目录**不是 junction**,改完必须三份都更新:

| 位置 | 作用 |
|---|---|
| `<repo>/sql-skill/` | 仓库源(git 管理) |
| `~/.claude/skills/sql-skill/` | Claude Code 实际加载 |
| `<vault>/08-sql-skill/` | Obsidian vault(4 通道同步源) |

```bash
SRC=<repo>/sql-skill
for DST in ~/.claude/skills/sql-skill <vault>/08-sql-skill; do
  cp "$SRC/SKILL.md" "$DST/SKILL.md"
  cp "$SRC"/chapters/*.md "$DST/chapters/"
  cp "$SRC"/supporting/*.md "$DST/supporting/"
  cp "$SRC"/references/*.md "$DST/references/"
done

# 校验
md5sum <repo>/sql-skill/SKILL.md ~/.claude/skills/sql-skill/SKILL.md <vault>/08-sql-skill/SKILL.md
```

---

## 排障

| 症状 | 原因 | 处理 |
|---|---|---|
| hook 日志空 | Claude Code 没调 hook | 重启 session(它会重读 settings.json) |
| `command not found` | hook 路径用了反斜杠 | 全部改正斜杠 |
| `Invalid hook payload` | payload 被截断 / 编码不对 | 看 `~/.claude/.cache/post-write-auto-sync.payload.err` 的原始字节 |
| brain 里查不到新页 | gbrain serve 持锁 | `gbrain status` 看锁状态;CLI 走 filesystem persistence 通常不受影响 |
| `embedding_state: disabled` | 缺 `VOYAGE_API_KEY` | 配环境变量后 `gbrain embeddings enable` |

更多排查记录见 [`docs/handoffs/`](handoffs/)。
