#!/usr/bin/env python3
"""sync-queue-consumer.py — 通道 C 主动消费 sync queue

读 ~/.claude/.cache/sql-skill-sync-queue/*.json,对每个 entry:
1. 解析 slug / title / content
2. 调 gbrain put_page 同步到 brain
3. 成功后删除 queue 文件
4. 失败则保留(下次重试)

用法:
  python sync-queue-consumer.py [--dry-run]
  # 或 Claude session 启动时自动跑

设计:hook 进程无 MCP 客户端,所以用 queue 文件中转。
Claude session 启动有 MCP 时,主动消费 queue。
"""
import json
import os
import sys
import time
from pathlib import Path

QUEUE_DIR = Path.home() / ".claude" / ".cache" / "sql-skill-sync-queue"
PROCESSED_DIR = QUEUE_DIR / "processed"
FAILED_DIR = QUEUE_DIR / "failed"
LOG_FILE = Path.home() / ".claude" / ".cache" / "sql-skill-sync.log"

DRY_RUN = "--dry-run" in sys.argv


def log(msg: str):
    line = f"[sync-consumer] {time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, file=sys.stderr)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def sync_via_subprocess(entry: dict) -> bool:
    """通过 gbrain CLI 同步(因为 Python 直接调 MCP 复杂)

    实际方案:写一个临时 .md 文件到 default source 目录,触发 gbrain 自动 import
    或直接调 `gbrain put` 命令(但 put 不是公开命令,只有 put_page 通过 MCP)
    """
    slug = entry["slug"]
    title = entry.get("title", slug)
    content = entry["content"]
    file_path = entry["file_path"]

    log(f"syncing: {slug} (from {file_path})")

    if DRY_RUN:
        log(f"  [DRY-RUN] would put_page: {slug}")
        return True

    # 尝试 1: 如果 gbrain serve 不可用,回退到文件系统写入
    # 写入到 brain default source 目录,等待下次 gbrain sync
    try:
        brain_dir = Path("C:/Users/Duanyi/.gbrain/content")
        # 找 default source 目录
        content_dirs = list(brain_dir.glob("*/default"))
        if not content_dirs:
            log("  [FAIL] brain default source dir not found")
            return False

        target_dir = content_dirs[0]
        slug_path = slug.replace("/", os.sep)
        target_file = target_dir / f"{slug_path}.md"
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(content, encoding="utf-8")
        log(f"  [OK] wrote to brain filesystem: {target_file}")
        return True
    except Exception as e:
        log(f"  [FAIL] {e}")
        return False


def process_queue():
    """处理所有 queue 文件"""
    if not QUEUE_DIR.exists():
        log(f"queue dir not found: {QUEUE_DIR}")
        return 0

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    FAILED_DIR.mkdir(parents=True, exist_ok=True)

    queue_files = sorted(QUEUE_DIR.glob("*.json"))
    if not queue_files:
        log("no queue files to process")
        return 0

    log(f"processing {len(queue_files)} queue file(s)")
    success = 0
    failed = 0

    for qf in queue_files:
        try:
            entry = json.loads(qf.read_text(encoding="utf-8"))
        except Exception as e:
            log(f"[FAIL] invalid json: {qf}: {e}")
            qf.rename(FAILED_DIR / qf.name)
            failed += 1
            continue

        if sync_via_subprocess(entry):
            # 成功,移到 processed
            qf.rename(PROCESSED_DIR / qf.name)
            success += 1
        else:
            # 失败,移到 failed(下次 session 检查可重试)
            qf.rename(FAILED_DIR / qf.name)
            failed += 1

    log(f"done: {success} success, {failed} failed")
    return success + failed


def retry_failed():
    """重试 failed 目录的(可手动调用)"""
    if not FAILED_DIR.exists():
        return 0
    for qf in FAILED_DIR.glob("*.json"):
        try:
            qf.rename(QUEUE_DIR / qf.name)
        except Exception:
            pass
    return process_queue()


def main():
    if "--retry" in sys.argv:
        retry_failed()
    else:
        process_queue()


if __name__ == "__main__":
    main()
