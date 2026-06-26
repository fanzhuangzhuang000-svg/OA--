#!/bin/bash
# B2.1-3 告警发送器 (每 5min 跑一次)
# - 读 /tmp/oa-alert-pending
# - 发邮件 (msmtp / sendmail) + 写 LOG
# - 成功发送后清空文件
set -uo pipefail

ALERT_FILE="/tmp/oa-alert-pending"
SENT_FILE="/tmp/oa-alert-sent"
LOG="${HOME}/oa-alert.log"
TO="${OA_ALERT_EMAIL:-admin@example.com}"
FROM="${OA_ALERT_FROM:-oa-monitor@afjsw.cn}"
COOLDOWN_MIN="${OA_ALERT_COOLDOWN:-15}"

touch "$LOG" 2>/dev/null || LOG="/tmp/oa-alert-$(whoami).log"

[ ! -s "$ALERT_FILE" ] && exit 0
[ ! -f "$SENT_FILE" ] && touch "$SENT_FILE"

# 15min 内已发同样内容则跳过
LAST_HASH=$(tail -1 "$SENT_FILE" 2>/dev/null | cut -d'|' -f1)
CUR_HASH=$(md5sum "$ALERT_FILE" | cut -d' ' -f1)
LAST_TS=$(tail -1 "$SENT_FILE" 2>/dev/null | cut -d'|' -f2)
NOW=$(date +%s)
if [ -n "$LAST_TS" ] && [ "$LAST_HASH" = "$CUR_HASH" ]; then
  AGE_MIN=$(( (NOW - LAST_TS) / 60 ))
  if [ "$AGE_MIN" -lt "$COOLDOWN_MIN" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] skip (cooldown ${AGE_MIN}m/${COOLDOWN_MIN}m)" >> "$LOG"
    exit 0
  fi
fi

SUBJECT="[OA-ALERT] $(hostname) - $(date '+%Y-%m-%d %H:%M')"
BODY=$(cat "$ALERT_FILE")

# 优先用 msmtp, 退回 mail
SENT=0
if command -v msmtp >/dev/null 2>&1; then
  if printf "To: %s\nFrom: %s\nSubject: %s\n\n%s\n" "$TO" "$FROM" "$SUBJECT" "$BODY" | msmtp "$TO" 2>>"$LOG"; then
    SENT=1
  fi
fi
if [ "$SENT" -eq 0 ] && command -v mail >/dev/null 2>&1; then
  if echo "$BODY" | mail -s "$SUBJECT" "$TO" 2>>"$LOG"; then
    SENT=1
  fi
fi
if [ "$SENT" -eq 0 ]; then
  # 无邮件客户端, 至少写日志
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] NO MAIL CLIENT, alert:" >> "$LOG"
  echo "$BODY" >> "$LOG"
fi

# 记录 + 清空
echo "${CUR_HASH}|${NOW}" >> "$SENT_FILE"
> "$ALERT_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] sent (hash=$CUR_HASH)" >> "$LOG"
exit 0
