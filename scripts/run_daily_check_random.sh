#!/usr/bin/env bash

set -euo pipefail

# cron 每天 1-15 点的第 30 分钟触发后，再随机延迟 0-600 秒。
sleep $((RANDOM % 601))

# 30% 概率执行，70% 概率跳过。
if (( RANDOM % 10 >= 3 )); then
  echo "$(date '+%F %T') skip airport-access" >> "$HOME/airport_access_daily_check_random.log"
  exit 0
fi

echo "$(date '+%F %T') run airport-access" >> "$HOME/airport_access_daily_check_random.log"

bash "/home/myuser/airport-access/scripts/daily_check_cron.sh" >> "$HOME/airport_access_daily_check_random.log" 2>&1
