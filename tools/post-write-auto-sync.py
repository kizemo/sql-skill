#!/usr/bin/env python3
"""post-write-auto-sync.py — Claude Code PostToolUse hook

监听 Write/Edit 完成事件,如果是 .md 文件且路径在 sql-skill vault 内
(`E:/obsidian/SQL/08-sql-skill/`),**即写即同步**到 brain(不再等下一 session)。

同步通道(按优先级,任一成功即止):

1. **MCP over HTTP**(可选):环境变量 `GBRAIN_MCP_URL` 可达时启用内嵌最小
   MCP 客户端 —— initialize → notifications/initialized → tools/call put_page。
   需要 `gbrain serve --http` 在跑(PGLite 脑被 stdio serve 锁着时启不了)。
2. **gbrain CLI**(默认通道):`gbrain put <slug> --content-origin <origin>`
   + stdin 传内容。与 MCP `put_page` 是同一套写入语义(chunk / revision /
   auto_links / persistence),且不受 DB 锁影响(走 filesystem persistence)。
3. **queue 文件**(兜底):写 ~/.claude/.cache/sql-skill-sync-queue/,
   由 SessionStart(C 通道)或 Cron(B 通道)稍后消费 —— 三条路都失败才走。

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
            "command": "C:/Python314/python.exe \"F:/soft/00selfmade/sql-skill/tools/post-write-auto-sync.py\"",
            "timeout": 60
          }
        ]
      }
    ]
  }
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# 配置
VAULT_PATTERNS = [
    re.compile(r"^E:/obsidian/SQL/08-sql-skill/.*\.md$"),
    re.compile(r"^E:\\obsidian\\SQL\\08-sql-skill\\.*\.md$"),
    re.compile(r"^/e/obsidian/SQL/08-sql-skill/.*\.md$"),
]
DEBOUNCE_FILE = Path.home() / ".claude" / ".cache" / "post-write-auto-sync-debounce.json"
DEBOUNCE_SECONDS = 300  # 5 min
SYNC_TIMEOUT = 60  # 60s
LOG_FILE = Path.home() / ".claude" / ".cache" / "post-write-auto-sync.log"
QUEUE_DIR = Path.home() / ".claude" / ".cache" / "sql-skill-sync-queue"

# MCP 端点:设了就优先走 MCP;不设/不可达则走 CLI
MCP_URL = os.environ.get("GBRAIN_MCP_URL", "").strip()
MCP_TIMEOUT = int(os.environ.get("GBRAIN_MCP_TIMEOUT", "20"))
# 内容来源标记:inferred=agent 写的知识文件;可用 GBRAIN_CONTENT_ORIGIN 覆盖
CONTENT_ORIGIN = os.environ.get("GBRAIN_CONTENT_ORIGIN", "inferred")
# gbrain 可执行文件
GBRAIN_BIN = os.environ.get(
    "GBRAIN_BIN", r"E:\Users\Duanyi\.claude\Cache\.bun\bin\gbrain.exe"
)


def debug_log(msg: str):
    """写 stderr + 文件日志(诊断用)"""
    line = f"[auto-sync {time.strftime('%H:%M:%S')}] {msg}"
    print(line, file=sys.stderr)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


# 路径到 slug 映射
def path_to_slug(file_path: str) -> str:
    """E:/obsidian/SQL/08-sql-skill/chapters/ch02-joins.md → sql-skill/chapters/ch02-joins"""
    p = file_path.replace("\\", "/")
    if "/08-sql-skill/" in p:
        rel = p.split("/08-sql-skill/", 1)[1]
    elif "/obsidian/SQL/08-sql-skill/" in p:
        rel = p.split("/obsidian/SQL/08-sql-skill/", 1)[1]
    else:
        return None
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
    return time.time() - last_time < DEBOUNCE_SECONDS


def mark_debounced(file_path: str):
    """标记该文件为已触发"""
    state = load_debounce()
    state[file_path] = time.time()
    cutoff = time.time() - 86400
    state = {k: v for k, v in state.items() if v > cutoff}
    save_debounce(state)


# ---------------------------------------------------------------- MCP client

class McpHttpClient:
    """最小 MCP streamable-HTTP 客户端(stdlib only)。

    流程:initialize → notifications/initialized → tools/call。
    响应可能是 JSON,也可能是 SSE(`event: message` + `data: {...}`),两种都解析。
    """

    def __init__(self, url: str, timeout: int = 20):
        self.url = url
        self.timeout = timeout
        self.session_id = None
        self._rpc_id = 0

    def _next_id(self) -> int:
        self._rpc_id += 1
        return self._rpc_id

    def _post(self, payload: dict) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            sid = resp.headers.get("Mcp-Session-Id") or resp.headers.get("mcp-session-id")
            if sid:
                self.session_id = sid
            body = resp.read().decode("utf-8", "replace")
        return self._parse_body(body)

    @staticmethod
    def _parse_body(body: str) -> dict:
        """JSON 或 SSE 都解成 dict;取最后一个 data: 事件(非流式响应通常只有一条)"""
        body = body.strip()
        if not body:
            return {}
        if body.startswith("{"):
            return json.loads(body)
        last = {}
        for line in body.splitlines():
            if line.startswith("data:"):
                raw = line[5:].strip()
                if raw:
                    try:
                        last = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
        return last

    def initialize(self) -> dict:
        resp = self._post({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "sql-skill-auto-sync", "version": "0.3.0"},
            },
        })
        if resp.get("error"):
            raise RuntimeError(f"mcp initialize error: {resp['error']}")
        # 通知(无 id,不期待响应)
        try:
            self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        except Exception:
            pass
        return resp.get("result", {})

    def call_tool(self, name: str, arguments: dict) -> dict:
        resp = self._post({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        })
        if resp.get("error"):
            raise RuntimeError(f"mcp tools/call error: {resp['error']}")
        result = resp.get("result", {})
        if result.get("isError"):
            raise RuntimeError(f"mcp tool returned error: {result}")
        return result


def mcp_put_page(slug: str, title: str, content: str) -> str:
    """通道 1:MCP over HTTP → tools/call put_page。返回 'mcp' 表示成功。"""
    client = McpHttpClient(MCP_URL, timeout=MCP_TIMEOUT)
    client.initialize()
    client.call_tool("put_page", {
        "slug": slug,
        "content": content,
        "content_origin": CONTENT_ORIGIN,
    })
    return "mcp"


# --------------------------------------------------------------- CLI channel

def cli_put_page(slug: str, title: str, content: str) -> str:
    """通道 2:gbrain CLI → put(与 MCP put_page 同一写入语义)。

    内容走 stdin —— 章节动辄 25KB+,`--content` 命令行传参会撞 Windows 32KB 上限。
    """
    if not Path(GBRAIN_BIN).is_file():
        raise RuntimeError(f"gbrain binary not found: {GBRAIN_BIN}")
    proc = subprocess.run(
        [GBRAIN_BIN, "put", slug, "--content-origin", CONTENT_ORIGIN],
        input=content.encode("utf-8"),
        capture_output=True,
        timeout=SYNC_TIMEOUT,
    )
    if proc.returncode != 0:
        err = (proc.stderr or b"").decode("utf-8", "replace").strip()
        raise RuntimeError(f"gbrain put failed rc={proc.returncode}: {err[-400:]}")
    return "cli"


# -------------------------------------------------------------- queue channel

def enqueue(slug: str, title: str, content: str, file_path: str) -> str:
    """通道 3:写 queue 文件,由 SessionStart(C)/Cron(B)消费。"""
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    queue_entry = {
        "slug": slug,
        "title": title,
        "content": content,
        "file_path": file_path,
        "queued_at": time.time(),
    }
    queue_file = QUEUE_DIR / f"{int(time.time())}_{slug.replace('/', '_')}.json"
    queue_file.write_text(json.dumps(queue_entry, ensure_ascii=False), encoding="utf-8")
    return f"queue:{queue_file}"


# ------------------------------------------------------------------- direct

def direct_sync(slug: str, title: str, content: str, file_path: str) -> str:
    """按优先级尝试三条通道,返回最终使用的通道名。"""
    attempts = []
    if MCP_URL:
        try:
            attempts.append(f"mcp:{mcp_put_page(slug, title, content)}")
            return "mcp"
        except Exception as e:
            debug_log(f"mcp channel failed, falling back: {type(e).__name__}: {e}")
    try:
        attempts.append(f"cli:{cli_put_page(slug, title, content)}")
        return "cli"
    except Exception as e:
        debug_log(f"cli channel failed, falling back to queue: {type(e).__name__}: {e}")
    return enqueue(slug, title, content, file_path)


def sync_to_brain(file_path: str):
    """读 vault 文件 → 直接同步到 brain(通道 D 手动入口也走这里)。"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"[auto-sync] read fail: {file_path}: {e}", file=sys.stderr)
        return

    slug = path_to_slug(file_path)
    if not slug:
        print(f"[auto-sync] slug fail: {file_path}", file=sys.stderr)
        return

    title = ""
    for line in content.split("\n"):
        if line.startswith("# "):
            title = line[2:].strip()
            break
    if not title:
        title = slug

    channel = direct_sync(slug, title, content, file_path)
    print(f"[auto-sync] synced {slug} via {channel}", file=sys.stderr)
    return channel


def read_payload() -> dict:
    """读 stdin 的 hook payload。

    显式按 UTF-8 解码,不依赖 sys.stdin 的 locale 编码
    (Windows 上 locale 可能被改成 GBK / C,导致 payload 解码不一致)。
    解析失败时把原始字节落盘,便于定位 Claude Code 侧的真实问题。
    """
    raw = sys.stdin.buffer.read()
    text = raw.decode("utf-8", "replace")
    try:
        return json.loads(text)
    except Exception as e:
        try:
            err_file = Path.home() / ".claude" / ".cache" / "post-write-auto-sync.payload.err"
            err_file.write_bytes(raw[:4096])
            debug_log(f"payload dump -> {err_file} ({len(raw)} bytes)")
        except Exception:
            pass
        raise e


def main():
    """hook 入口:stdin 读 hook payload"""
    debug_log("HOOK ENTRY")
    try:
        payload = read_payload()
    except Exception as e:
        debug_log(f"Invalid hook payload: {type(e).__name__}: {e}")
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "") or tool_input.get("filepath", "")

    debug_log(f"tool_name={tool_name!r} file_path={file_path!r}")

    if tool_name not in ("Write", "Edit", "MultiEdit"):
        debug_log("skip: tool_name mismatch")
        sys.exit(0)
    if not is_in_vault(file_path):
        debug_log("skip: not in vault")
        sys.exit(0)
    if should_debounce(file_path):
        debug_log("skip: debounced")
        sys.exit(0)

    slug = path_to_slug(file_path)
    if not slug:
        debug_log("skip: slug unresolvable")
        sys.exit(0)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        debug_log(f"read fail: {e}")
        sys.exit(0)

    title = ""
    for line in content.split("\n"):
        if line.startswith("# "):
            title = line[2:].strip()
            break
    if not title:
        title = slug

    try:
        channel = direct_sync(slug, title, content, file_path)
        mark_debounced(file_path)
        debug_log(f"OK synced {slug} via {channel}")
    except Exception as e:
        # 兜底:任何未预期异常都写 queue,绝不丢内容
        debug_log(f"sync failed, enqueue fallback: {type(e).__name__}: {e}")
        try:
            enqueue(slug, title, content, file_path)
            mark_debounced(file_path)
        except Exception as e2:
            debug_log(f"enqueue failed too: {e2}")


if __name__ == "__main__":
    main()
