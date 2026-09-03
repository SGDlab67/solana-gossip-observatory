#!/bin/bash
# refresh-numbers.sh: one-command numbers refresh for the day before a meeting.
#
# Reads only the raw files already on disk under data/. Computes nothing it
# cannot source. Prints a clean block that pastes straight into
# docs/PRESENTATION-NUMBERS.md.
#
# Covers the 7 most recent UTC day directories present under data/:
#   1. each day's latest cluster-nodes snapshot: node count, unique gossip IPs
#   2. every spy run in those days: file name, tick count, final peer count
#   3. the latest vote-accounts snapshot: current and delinquent counts
#
# Empty or truncated JSON prints EMPTY rather than crashing. At least one
# 0-byte cluster-nodes file is known to exist in the series.
#
# Usage: ./scripts/refresh-numbers.sh
set -euo pipefail
cd "$(dirname "$0")/.."   # repo root, wherever the script is invoked from

DAYS="${DAYS:-7}" python3 - <<'PY'
import datetime as dt
import glob
import json
import os
import re
import sys

DAYS = int(os.environ.get("DAYS", "7"))
DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STAMP = "%Y%m%dT%H%M%SZ"


def load(path):
    """Return the parsed 'result' payload, or None if the file is unusable."""
    try:
        if os.path.getsize(path) == 0:
            return None
        with open(path) as fh:
            return json.load(fh)["result"]
    except (OSError, ValueError, KeyError, TypeError):
        return None


def cluster_counts(path):
    """(node count, unique gossip IPs) for a getClusterNodes snapshot."""
    result = load(path)
    if result is None:
        return None
    ips = {n["gossip"].rsplit(":", 1)[0] for n in result if n.get("gossip")}
    return len(result), len(ips)


def stamp_of(path, prefix):
    """UTC timestamp embedded in a snapshot file name, for sorting."""
    base = os.path.basename(path)
    return dt.datetime.strptime(base[len(prefix):-len(".json")], STAMP)


days = sorted(d for d in glob.glob("data/*") if DAY_RE.match(os.path.basename(d)))
if not days:
    sys.exit("no data/YYYY-MM-DD directories found")
days = days[-DAYS:]

generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
print("S-NodeFinder numbers refresh")
print("generated: %s" % generated)
print("window:    %s to %s (%d UTC days on disk)"
      % (os.path.basename(days[0]), os.path.basename(days[-1]), len(days)))
print()

# 1. RPC cluster view, latest snapshot per UTC day.
print("## RPC cluster view (latest cluster-nodes snapshot per UTC day)")
print()
print("| UTC day | snapshot | nodes | unique gossip IPs |")
print("| --- | --- | ---: | ---: |")
for day in days:
    files = sorted(glob.glob(os.path.join(day, "cluster-nodes-*.json")),
                   key=lambda p: stamp_of(p, "cluster-nodes-"))
    label = os.path.basename(day)
    if not files:
        print("| %s | none | EMPTY | EMPTY |" % label)
        continue
    latest = files[-1]
    counts = cluster_counts(latest)
    if counts is None:
        print("| %s | %s | EMPTY | EMPTY |" % (label, os.path.basename(latest)))
        # Fall back to the freshest snapshot of that day that does parse.
        for candidate in reversed(files[:-1]):
            counts = cluster_counts(candidate)
            if counts is not None:
                print("| %s | %s (latest readable) | %d | %d |"
                      % (label, os.path.basename(candidate), counts[0], counts[1]))
                break
    else:
        print("| %s | %s | %d | %d |"
              % (label, os.path.basename(latest), counts[0], counts[1]))
print()

# 2. Spy runs. A full window is 4 ticks at 30 seconds, so 120 seconds.
print("## Spy runs (spy-summary files, one row per run)")
print()
print("| UTC day | summary file | ticks | final peers | curve |")
print("| --- | --- | ---: | ---: | --- |")
for day in days:
    for path in sorted(glob.glob(os.path.join(day, "spy-summary-*.jsonl"))):
        rows = []
        try:
            with open(path) as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        rows.append(json.loads(line))
        except (OSError, ValueError):
            rows = []
        label = os.path.basename(day)
        name = os.path.basename(path)
        if not rows:
            print("| %s | %s | EMPTY | EMPTY | EMPTY |" % (label, name))
            continue
        peers = [r.get("total_peers") for r in rows]
        final = peers[-1]
        curve = " / ".join(str(p) for p in peers)
        flag = "" if len(rows) == 4 else "  (truncated)"
        print("| %s | %s | %d%s | %d | %s |"
              % (label, name, len(rows), flag, final, curve))
print()

# 3. Stake view, freshest vote-accounts snapshot in the window.
print("## Vote accounts (freshest snapshot in window)")
print()
vote_files = []
for day in days:
    vote_files.extend(glob.glob(os.path.join(day, "vote-accounts-*.json")))
vote_files.sort(key=lambda p: stamp_of(p, "vote-accounts-"))
printed = False
for path in reversed(vote_files):
    result = load(path)
    if result is None:
        continue
    current = len(result.get("current", []))
    delinquent = len(result.get("delinquent", []))
    print("| snapshot | current | delinquent |")
    print("| --- | ---: | ---: |")
    print("| %s | %d | %d |" % (os.path.basename(path), current, delinquent))
    printed = True
    break
if not printed:
    print("| snapshot | current | delinquent |")
    print("| --- | ---: | ---: |")
    print("| none readable | EMPTY | EMPTY |")
print()
print("All values read directly from data/. Nothing above is estimated.")
PY
