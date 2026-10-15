#!/usr/bin/env python3
"""post-write-auto-sync.py — Claude Code PostToolUse hook

监听 Write/Edit 完成事件,如果是 .md 文件且路径在 sql-skill vault 内
(`E:/obsidian/SQL/08-sql-skill/`),自动调 `mcp__gbrain_gbrain__put_page` 同步到 brain。

防频繁触发:
- 5min debounce(同文件)
- 只处理 .md
- 只在 sql-skill vault 路径

注册到 ~/.claude/settings.json:
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "C:\\\\Python314\\\\python.exe \"F:\\\\soft\\\\00selfmade\\\\sql-skill\\\\tools\\\\post-write-auto-sync.py\"",
            "timeout": 60
          }
        ]
      }
    ]
  }
"""
import subprocess
import json
import os
import sys
import time
import re
from pathlib import Path

# 配置
VAULT_PATTERNS = [
    re.compile(r"^E:/obsidian/SQL/08-sql-skill/.*\.md$"),
    re.compile(r"^E:\\\\obsidian\\\\SQL\\\\08-sql-skill\\\\.*\.md$"),
    re.compile(r"^/e/obsidian/SQL/08-sql-skill/.*\.md$"),
]
DEBOUNCE_FILE = Path.home() / ".claude" / ".cache" / "post-write-auto-sync-debounce.json"
DEBOUNCE_SECONDS = 300  # 5 min
SYNC_TIMEOUT = 60  # 60s

# 路径到 slug 映射
def path_to_slug(file_path: str) -> str:
    """E:/obsidian/SQL/08-sql-skill/chapters/ch02-joins.md → sql-skill/chapters/ch02-joins"""
    # 统一路径分隔符
    p = file_path.replace("\\", "/")
    # 找 vault root 后的相对路径
    if "/08-sql-skill/" in p:
        rel = p.split("/08-sql-skill/", 1)[1]
    else:
        rel = p.split("/obsidian/SQL/08-sql-skill/", 1)[1] if "/obsidian/SQL/08-sql-skill/" in p else None
        if rel is None:
            return None
    # 去掉 .md 后缀,转 / 为 -
    if rel.endswith(".md"):
        rel = rel[:-3]
    return f"sql-skill/{rel.replace('/', '-')}"


def is_in_vault(file_path: str) -> bool:
    """检查路径是否在 sql-skill vault 内"""
    if not file_path or not file_path.endswith(".md"):
        return False
    p = file_path.replace("\\", "/")
    return any(pat.match(p) for pat in VAULT_PATTERNS)


def load_debounce() -> dict:
    """读取 debounce 状态"""
    if not DEBOUNCE_FILE.exists():
        return {}
    try:
        return json.loads(DEBOUNCE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_debounce(state: dict):
    """保存 debounce 状态"""
    DEBOUNCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    DEBOUNCE_FILE.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")


def should_debounce(file_path: str) -> bool:
    """检查是否在 debounce 窗口内"""
    state = load_debounce()
    last_time = state.get(file_path, 0)
    if time.time() - last_time < DEBOUNCE_SECONDS:
        return True
    return False


def mark_debounced(file_path: str):
    """标记该文件为已触发"""
    state = load_debounce()
    state[file_path] = time.time()
    cutoff = time.time() - 86400
    state = {k: v for k, v in state.items() if v > cutoff}
    save_debounce(state)


def sync_to_brain(file_path: str):
    """读 vault 文件 + 调 gbrain MCP put_page"""
    # 读文件
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"[auto-sync] read fail: {file_path}: {e}", file=sys.stderr)
        return

    # 生成 slug
    slug = path_to_slug(file_path)
    if not slug:
        print(f"[auto-sync] slug fail: {file_path}", file=sys.stderr)
        return

    # 提取 title (# heading)
    title = ""
    for line in content.split("\n"):
        if line.startswith("# "):
            title = line[2:].strip()
            break
    if not title:
        title = slug

    # 这里不能直接调 MCP(hook 进程无 MCP 客户端)
    # 改为调用 gbrain CLI(serve 时也锁)— 不可行
    # 实际方案:写一个 queue 文件,由下一个 Claude session 消费
    queue_dir = Path.home() / ".claude" / ".cache" / "sql-skill-sync-queue"
    queue_dir.mkdir(parents=True, exist_ok=True)

    queue_entry = {
        "slug": slug,
        "title": title,
        "content": content,
        "file_path": file_path,
        "queued_at": time.time(),
    }
    queue_file = queue_dir / f"{int(time.time())}_{slug.replace('/', '_')}.json"
    queue_file.write_text(json.dumps(queue_entry, ensure_ascii=False), encoding="utf-8")
    print(f"[auto-sync] queued: {slug} → {queue_file}", file=sys.stderr)


def main():
    """hook 入口:stdin 读 hook payload"""
    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        print(f"[auto-sync] Invalid hook payload: {e}", file=sys.stderr)
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "") or tool_input.get("filepath", "")

    # 过滤
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)
    if not is_in_vault(file_path):
        sys.exit(0)
    if should_debounce(file_path):
        print(f"[auto-sync] debounced: {file_path}", file=sys.stderr)
        sys.exit(0)

    # 同步(queue 模式,因为 hook 进程无 MCP 客户端)
    sync_to_brain(file_path)
    mark_debounced(file_path)


if __name__ == "__main__":
    main()
