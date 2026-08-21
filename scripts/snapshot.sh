#!/bin/bash
# Day-N baseline snapshot: RPC view of the cluster (API half of the instrument).
# Usage: ./snapshot.sh [RPC_URL]
# Writes timestamped JSON snapshots under data/YYYY-MM-DD/.
set -euo pipefail
RPC="${1:-https://api.mainnet-beta.solana.com}"
DAY="$(date -u +%Y-%m-%d)"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="data/$DAY"
mkdir -p "$OUT"
curl -s "$RPC" -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"getClusterNodes"}' \
  > "$OUT/cluster-nodes-$TS.json"
curl -s "$RPC" -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"getVoteAccounts"}' \
  > "$OUT/vote-accounts-$TS.json"
SOLANA_BIN="${SOLANA_BIN:-$HOME/.local/share/solana/install/active_release/bin/solana}"
"$SOLANA_BIN" gossip -u "$RPC" --output json-compact \
  > "$OUT/cli-gossip-$TS.json" 2>/dev/null || true
echo "snapshot written to $OUT at $TS"
