#!/bin/bash
# S-NodeFinder snapshot watchdog: is the RPC half of the instrument still feeding?
# Usage: ./watchdog.sh   (silent = healthy; any stdout is an alert)
# Prints one alert line if the newest cluster-nodes snapshot is older than MAX_AGE_H
# hours, or if no snapshot exists at all. Always exits 0 so cron mails only alerts.
set -euo pipefail
cd "$(dirname "$0")/.."   # repo root, wherever the script is invoked from
DATA_DIR="${1:-data}"
MAX_AGE_H="${MAX_AGE_H:-8}"

# Newest cluster-nodes-*.json anywhere under data/, by mtime.
NEWEST=""
NEWEST_MTIME=0
while IFS= read -r f; do
  m="$(stat -f %m "$f")"
  if [ "$m" -gt "$NEWEST_MTIME" ]; then
    NEWEST_MTIME="$m"
    NEWEST="$f"
  fi
done < <(find "$DATA_DIR" -type f -name 'cluster-nodes-*.json' 2>/dev/null)

if [ -z "$NEWEST" ]; then
  echo "S-NODEFINDER ALERT: no RPC snapshot found under $DATA_DIR/ (snapshots today: 0)"
  exit 0
fi

NOW="$(date -u +%s)"
AGE_H=$(( (NOW - NEWEST_MTIME) / 3600 ))

if [ "$AGE_H" -gt "$MAX_AGE_H" ]; then
  # UTC day of the newest snapshot, taken from its filename stamp (YYYYMMDDTHHMMSSZ).
  BASE="$(basename "$NEWEST")"
  STAMP="${BASE#cluster-nodes-}"
  DAY="${STAMP:0:8}"
  COUNT="$(find "$DATA_DIR" -type f -name "cluster-nodes-$DAY"'*.json' 2>/dev/null | wc -l | tr -d ' ')"
  echo "S-NODEFINDER ALERT: no RPC snapshot for ${AGE_H}h (newest: $NEWEST); snapshots on newest UTC day $DAY: $COUNT"
fi

exit 0
