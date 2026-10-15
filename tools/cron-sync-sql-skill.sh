#!/bin/bash
# cron-sync-sql-skill.sh — 通道 B Cron 周期同步
# 每日 02:00 跑(Windows Task Scheduler)
# 1. 扫 vault .md 文件 mtime
# 2. 对变化的文件调 gbrain sweep(--once 推进 mention_links + git_state)
# 3. 跑 sync-queue-consumer.py 消费 queue
#
# 注册(Task Scheduler):
#   schtasks /create /tn "gbrain-sql-skill-sync" /tr "daily 02:00" \
#     /sc daily /ru "$USER" \
#     /cmd "C:\Program Files\Git\usr\bin\bash.exe F:/soft/00selfmade/sql-skill/tools/cron-sync-sql-skill.sh"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GBRAIN="/c/Users/Duanyi/.claude/Cache/.bun/bin/gbrain"
VAULT="E:/obsidian/SQL/08-sql-skill"
LOG_FILE="F:/soft/00selfmade/sql-skill/logs/sync-cron.log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Cron sync start ===" | tee -a "$LOG_FILE"

# 1. 扫 vault,记 mtime 变化的文件
CHANGED_FILES=$(find "$VAULT" -name "*.md" -newer "$LOG_FILE.snap" 2>/dev/null || true)
touch "$LOG_FILE.snap"

if [ -n "$CHANGED_FILES" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] changed files:" | tee -a "$LOG_FILE"
    echo "$CHANGED_FILES" | tee -a "$LOG_FILE"
    echo "$CHANGED_FILES" | wc -l | tee -a "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] no files changed since last sync" | tee -a "$LOG_FILE"
fi

# 2. 跑 gbrain sweep(--once 推进 mention_links + git_state)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] running gbrain sweep --once" | tee -a "$LOG_FILE"
"$GBRAIN" sweep --once 2>&1 | tee -a "$LOG_FILE" || echo "[WARN] sweep failed" | tee -a "$LOG_FILE"

# 3. 消费 sync queue
echo "[$(date '+%Y-%m-%d %H:%M:%S')] consuming sync queue" | tee -a "$LOG_FILE"
python "$SCRIPT_DIR/sync-queue-consumer.py" 2>&1 | tee -a "$LOG_FILE" || echo "[WARN] queue consumer failed" | tee -a "$LOG_FILE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Cron sync done ===" | tee -a "$LOG_FILE"
