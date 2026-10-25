# Channel A 排查计划 · 2026-10-17

## 现象

- Claude Code 自动 PostToolUse 在当前 session 未触发
- 手动模拟 hook payload 完美工作(hook 脚本 + queue 写入 + debounce 全部正常)
- 实测 3 次 Write,3 秒延迟后查 queue 仍空
- debounce 文件仅含手动 2 条,无任何自动触发

## 已排除

- ❌ Python 命令路径(`C:\Python314\python.exe` 存在,手动调用 OK)
- ❌ Python 脚本逻辑(模拟 payload 工作完美)
- ❌ vault 路径匹配(regex 测试通过)
- ❌ debounce(新文件无前次记录)
- ❌ gbrain MCP / brain filesystem(hook 不依赖)

## 候选假设(优先级排序)

### H1: matcher 格式不兼容当前 Claude Code 版本

**症状**:settings.json line 129 `matcher: "Write|Edit|MultiEdit"` 用了 `|` 分隔符
**现代 Claude Code** 期望数组格式:`matcher: ["Write", "Edit", "MultiEdit"]`
**验证**:对比 gbrain 工作的 hooks(均无 matcher)vs 本 hook(有 matcher)
**修复**:改 matcher 为数组格式

### H2: settings.json 在 session 启动后修改不生效

**症状**:hook 配置正确但 Claude Code 已缓存 settings 不重读
**验证**:本次 session 启动时 settings.json 已是当前状态(line 126-137 在 v2.2 handoff 中确认存在),所以应该被加载
**修复**:可能需重启 session

### H3: PreToolUse 阻断 → PostToolUse 不 fire

**症状**:no-delete-gate.py(PreToolUse,timeout 5s)若 hang/return non-zero → Write 被拒 → PostToolUse 不 fire
**验证**:实际 Write 都成功了(文件创建),说明 PreToolUse 未阻断
**修复**:N/A(已排除)

### H4: 子进程 stdin pipe 异常

**症状**:Claude Code PostToolUse 用 pipe 传 payload,Python 脚本 `sys.stdin.read()` 可能 timeout
**验证**:手动模拟正常,但 Claude Code 传的实际 payload 可能略有不同
**修复**:脚本加 `sys.stdin = open(sys.stdin.fileno(), 'r', buffering=1)` 行缓冲

### H5: hook 输出 stderr 被吞

**症状**:hook 抛 exception 但 stderr 写入失败
**验证**:加 try/except + 写文件日志(`/c/Users/Duanyi/.claude/.cache/hook-debug.log`)

### H6: tool_name 实际值不是 "Write"

**症状**:Claude Code 内部 tool_name 可能不同(如 `"wriite"` 或 `"WriteFile"`)
**验证**:在 hook 入口加 `print(payload, file=open(log, 'a'))` 看实际 payload

## 排查步骤

### Step 1:确认 hook 在外部触发成功(5min)

手动从 PowerShell 调 Claude Code 风格的 hook 调用,确认 Claude Code 路径 OK:

```powershell
$payload = '{"tool_name":"Write","tool_input":{"file_path":"E:/obsidian/SQL/08-sql-skill/chapters/test-hook-trigger.md"}}'
$payload | & "C:\Python314\python.exe" "F:\soft\00selfmade\sql-skill\tools\post-write-auto-sync.py"
```

### Step 2:加 hook stderr 文件日志(5min)

改 `post-write-auto-sync.py`,加:
```python
LOG = Path.home() / ".claude" / ".cache" / "post-write-auto-sync.log"
def log(msg):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
```

记录:hook 入口 / payload 解析 / 路径匹配 / debounce 决策 / queue 写入。

### Step 3:再写 1 个 vault .md + 立即查 stderr log(2min)

如果 log 仍空,说明 hook 没被 Claude Code 调用 → H1/H2 路径
如果 log 有 "Invalid hook payload",说明 H6(tool_name 不匹配)

### Step 4:验证 H1(改 matcher 格式)

settings.json:
```json
"matcher": ["Write", "Edit", "MultiEdit"]
```

vs 原 `"matcher": "Write|Edit|MultiEdit"`

**注意**:改动后**必须重启 Claude Code session**(否则 settings.json 缓存不刷新)。

### Step 5:验证 H6(tool_name 不匹配)

在 hook 入口加:
```python
log(f"tool_name={payload.get('tool_name', '<missing>')}")
log(f"keys={list(payload.keys())}")
```

看实际 tool_name 值。

## 修复路径(假设排查结果)

| 结果 | 修复 |
|---|---|
| H1 命中 | matcher 改数组格式 + 写新版 settings.json |
| H2 命中 | 用户手动重启 Claude Code session |
| H4 命中 | hook 脚本加行缓冲 |
| H6 命中 | matcher 改用实际 tool_name 值 |
| 其它 | 写 issue 升级 Claude Code / 改 hook 设计 |

## 不依赖 Channel A 的备选方案

即使 auto-trigger 修不好,Channel C(下次 session 启动 queue consumer)仍能消费已写入的 queue 条目。**但 hook 不自动 fire 就没 queue 条目可消费**,所以 Channel A 仍是关键。

Channel D(手动)始终可用:`python tools/sync_to_brain.py <path>`(待写)。
