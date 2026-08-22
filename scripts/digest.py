#!/usr/bin/env python3
"""S-NodeFinder weekly digest.

Reads the raw snapshot tree under data/ (RPC view: cluster-nodes-*.json and
vote-accounts-*.json; gossip view: spy-*.jsonl) and emits a markdown brief to
snapshots/digests/YYYY-Www.md comparing the latest UTC day against the previous
one, plus a 5-line summary on stdout.

Python 3 standard library only. Always exits 0: problems are reported as
"health: ATTENTION" inside the brief, not as a non-zero status.
"""

import glob
import json
import os
import sys
import traceback
from collections import Counter
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")
OUT_DIR = os.path.join(REPO_ROOT, "snapshots", "digests")

# File types the snapshot pipeline is expected to produce every day.
REQUIRED_TYPES = ("cluster-nodes", "vote-accounts")
# Types that are nice to have but whose absence is not a health failure.
OPTIONAL_TYPES = ("cli-gossip", "spy", "spy-summary")
# A day whose snapshots are further apart than this is flagged.
MAX_GAP_HOURS_OK = 12.0

STAMP_LEN = len("20260821T034230Z")


# ---------------------------------------------------------------- file naming

def parse_stamp(basename):
    """Return the UTC datetime encoded in a YYYYmmddTHHMMSSZ filename token."""
    for chunk in basename.replace(".", "-").split("-"):
        if len(chunk) != STAMP_LEN or chunk[8] != "T" or chunk[-1] != "Z":
            continue
        digits = chunk[:8] + chunk[9:-1]
        if not digits.isdigit():
            continue
        try:
            return datetime(
                int(chunk[0:4]), int(chunk[4:6]), int(chunk[6:8]),
                int(chunk[9:11]), int(chunk[11:13]), int(chunk[13:15]),
                tzinfo=timezone.utc,
            )
        except ValueError:
            return None
    return None


def file_type(basename):
    """Strip the timestamp and extension: cluster-nodes-<stamp>.json -> cluster-nodes."""
    stem = basename.split(".")[0]
    parts = stem.split("-")
    while parts and len(parts[-1]) == STAMP_LEN and parts[-1].endswith("Z"):
        parts.pop()
    return "-".join(parts) if parts else stem


def looks_like_day(name):
    return (
        len(name) == 10
        and name[4] == "-"
        and name[7] == "-"
        and name.replace("-", "").isdigit()
    )


def describe(path):
    """(day, datetime, type) for a data file, falling back to mtime when unstamped."""
    basename = os.path.basename(path)
    stamp = parse_stamp(basename)
    if stamp is None:
        stamp = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)
        parent = os.path.basename(os.path.dirname(path))
        day = parent if looks_like_day(parent) else stamp.strftime("%Y-%m-%d")
    else:
        day = stamp.strftime("%Y-%m-%d")
    return day, stamp, file_type(basename)


def rel(path):
    return os.path.relpath(path, REPO_ROOT)


# ------------------------------------------------------------------- loading

def collect_files():
    """day -> list of {path, dt, type}, sorted by timestamp."""
    by_day = {}
    for path in glob.glob(os.path.join(DATA_DIR, "**", "*"), recursive=True):
        if not os.path.isfile(path):
            continue
        day, dt, ftype = describe(path)
        by_day.setdefault(day, []).append({"path": path, "dt": dt, "type": ftype})
    for entries in by_day.values():
        entries.sort(key=lambda e: e["dt"])
    return by_day


def load_json(path, errors):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read().strip()
        if not text:
            errors.append("%s: empty file" % rel(path))
            return None
        return json.loads(text)
    except (OSError, ValueError) as exc:
        errors.append("%s: %s" % (rel(path), exc))
        return None


def split_host(addr):
    """'1.2.3.4:8001' or '[::1]:8001' -> host without port."""
    if not isinstance(addr, str) or not addr:
        return None
    if addr.startswith("["):
        end = addr.find("]")
        return addr[1:end] if end > 0 else addr
    return addr.rsplit(":", 1)[0] if ":" in addr else addr


# ------------------------------------------------------------------- metrics

def cluster_metrics(entries, errors):
    """Per-day RPC cluster view: point-in-time from the latest snapshot,
    plus the union of gossip IPs seen across the whole day (used for churn)."""
    snapshots = []
    union_ips = set()
    for entry in [e for e in entries if e["type"] == "cluster-nodes"]:
        doc = load_json(entry["path"], errors)
        if doc is None:
            continue
        nodes = doc.get("result") if isinstance(doc, dict) else doc
        if not isinstance(nodes, list):
            errors.append("%s: no result array" % rel(entry["path"]))
            continue
        ips = set()
        rpc_nodes = 0
        versions = Counter()
        for node in nodes:
            if not isinstance(node, dict):
                continue
            host = split_host(node.get("gossip"))
            if host:
                ips.add(host)
            if node.get("rpc"):
                rpc_nodes += 1
            versions[node.get("version") or "unknown"] += 1
        union_ips |= ips
        snapshots.append({
            "path": entry["path"], "dt": entry["dt"], "nodes": len(nodes),
            "ips": ips, "rpc_nodes": rpc_nodes, "versions": versions,
        })
    if not snapshots:
        return None
    latest = snapshots[-1]
    return {
        "snapshot_count": len(snapshots),
        "latest_path": latest["path"],
        "latest_dt": latest["dt"],
        "nodes": latest["nodes"],
        "unique_ips": len(latest["ips"]),
        "rpc_nodes": latest["rpc_nodes"],
        "versions": latest["versions"],
        "day_ips": union_ips,
    }


def vote_metrics(entries, errors):
    """Current and delinquent validator counts from the day's latest snapshot."""
    result = None
    for entry in [e for e in entries if e["type"] == "vote-accounts"]:
        doc = load_json(entry["path"], errors)
        if doc is None:
            continue
        payload = doc.get("result") if isinstance(doc, dict) else doc
        if not isinstance(payload, dict):
            errors.append("%s: no result object" % rel(entry["path"]))
            continue
        current = payload.get("current") or []
        delinquent = payload.get("delinquent") or []
        result = {
            "path": entry["path"], "dt": entry["dt"],
            "current": len(current), "delinquent": len(delinquent),
        }
    return result


def spy_metrics(entries, errors):
    """Gossip-view totals from spy JSONL, if any was recorded that day."""
    peer_pubkeys = set()
    peer_ips = set()
    summary_peaks = []
    validator_peaks = []
    paths = []
    lines_seen = 0
    for entry in entries:
        if entry["type"] not in ("spy", "spy-summary"):
            continue
        if not entry["path"].endswith(".jsonl"):
            continue
        paths.append(entry["path"])
        try:
            with open(entry["path"], "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        errors.append("%s: unparseable JSONL line" % rel(entry["path"]))
                        continue
                    if not isinstance(rec, dict):
                        continue
                    lines_seen += 1
                    if "total_peers" in rec:
                        summary_peaks.append(rec.get("total_peers") or 0)
                        validator_peaks.append(rec.get("validators") or 0)
                    elif "pubkey" in rec:
                        peer_pubkeys.add(rec["pubkey"])
                        host = split_host(rec.get("gossip"))
                        if host:
                            peer_ips.add(host)
        except OSError as exc:
            errors.append("%s: %s" % (rel(entry["path"]), exc))
    if not paths or lines_seen == 0:
        return None
    if summary_peaks:
        peers = max(summary_peaks)
        source = "spy-summary peak total_peers"
    else:
        peers = len(peer_pubkeys)
        source = "distinct pubkeys in spy records"
    return {
        "paths": paths, "peers": peers, "peers_source": source,
        "distinct_pubkeys": len(peer_pubkeys), "distinct_ips": len(peer_ips),
        "validators": max(validator_peaks) if validator_peaks else None,
    }


def health_metrics(entries):
    """File counts per type, missing required types, and the largest snapshot gap."""
    counts = Counter(e["type"] for e in entries)
    missing = [t for t in REQUIRED_TYPES if not counts.get(t)]
    stamps = sorted({e["dt"] for e in entries})
    max_gap = 0.0
    gap_between = None
    for earlier, later in zip(stamps, stamps[1:]):
        gap = (later - earlier).total_seconds() / 3600.0
        if gap > max_gap:
            max_gap = gap
            gap_between = (earlier, later)
    return {
        "total_files": len(entries),
        "counts": counts,
        "missing": missing,
        "max_gap_hours": max_gap,
        "gap_between": gap_between,
        "snapshot_times": stamps,
    }


def day_report(day, entries):
    errors = []
    return {
        "day": day,
        "entries": entries,
        "cluster": cluster_metrics(entries, errors),
        "votes": vote_metrics(entries, errors),
        "spy": spy_metrics(entries, errors),
        "health": health_metrics(entries),
        "errors": errors,
    }


# ----------------------------------------------------------------- formatting

def delta(new, old):
    if new is None or old is None:
        return "n/a"
    diff = new - old
    return "+%d" % diff if diff > 0 else str(diff)


def num(value):
    return "n/a" if value is None else str(value)


def get(report, section, key):
    if report is None:
        return None
    block = report.get(section)
    return None if block is None else block.get(key)


def version_lines(versions, total):
    if not versions:
        return ["  (no version data)"]
    out = []
    for name, count in versions.most_common(5):
        pct = (100.0 * count / total) if total else 0.0
        out.append("  %-12s %6d  %5.1f%%" % (name, count, pct))
    return out


def build_brief(latest, previous, week, generated, health_ok, health_notes, churn):
    lat_cluster = latest["cluster"] if latest else None
    prev_day = previous["day"] if previous else "n/a"
    lines = []
    add = lines.append

    add("# S-NodeFinder weekly digest %s" % week)
    add("")
    add("Generated: %s" % generated.strftime("%Y-%m-%dT%H:%M:%SZ"))
    add("Latest UTC day: %s" % (latest["day"] if latest else "n/a"))
    add("Previous UTC day: %s" % prev_day)
    add("")
    add("health: %s" % ("OK" if health_ok else "ATTENTION"))
    for note in health_notes:
        add("- %s" % note)
    if health_ok:
        add("- all required snapshot types present, gaps within %.0fh" % MAX_GAP_HOURS_OK)
    add("")

    add("## Cluster view (RPC)")
    add("")
    add("Point-in-time values come from each day's latest snapshot.")
    add("")
    add("| metric | %s | %s | delta |" % (latest["day"] if latest else "latest", prev_day))
    add("| --- | ---: | ---: | ---: |")
    rows = [
        ("cluster node count", get(latest, "cluster", "nodes"), get(previous, "cluster", "nodes")),
        ("unique gossip IPs", get(latest, "cluster", "unique_ips"), get(previous, "cluster", "unique_ips")),
        ("nodes exposing RPC", get(latest, "cluster", "rpc_nodes"), get(previous, "cluster", "rpc_nodes")),
        ("validators (current)", get(latest, "votes", "current"), get(previous, "votes", "current")),
        ("validators (delinquent)", get(latest, "votes", "delinquent"), get(previous, "votes", "delinquent")),
    ]
    for label, new, old in rows:
        add("| %s | %s | %s | %s |" % (label, num(new), num(old), delta(new, old)))
    add("")

    add("## Churn (gossip IPs, union across each day's snapshots)")
    add("")
    if churn is None:
        add("Not computable: needs a usable cluster-nodes snapshot on both days.")
    else:
        add("- entered: %d" % len(churn["entered"]))
        add("- left: %d" % len(churn["left"]))
        add("- stable: %d" % churn["stable"])
        add("- day set sizes: %s = %d, %s = %d"
            % (latest["day"], churn["latest_size"], prev_day, churn["prev_size"]))
        for label, key in (("entered", "entered"), ("left", "left")):
            sample = sorted(churn[key])[:10]
            if sample:
                add("- sample %s: %s%s"
                    % (label, ", ".join(sample), " ..." if len(churn[key]) > 10 else ""))
    add("")

    add("## Version census (top 5, latest snapshot of each day)")
    add("")
    add("### %s" % (latest["day"] if latest else "latest"))
    add("```")
    lines.extend(version_lines(
        get(latest, "cluster", "versions"), get(latest, "cluster", "nodes") or 0))
    add("```")
    if previous:
        add("### %s" % prev_day)
        add("```")
        lines.extend(version_lines(
            get(previous, "cluster", "versions"), get(previous, "cluster", "nodes") or 0))
        add("```")
    add("")

    add("## View disagreement (spy gossip view vs RPC view)")
    add("")
    any_spy = False
    for report in (latest, previous):
        if report is None:
            continue
        spy = report["spy"]
        if spy is None:
            continue
        any_spy = True
        rpc_ips = get(report, "cluster", "unique_ips")
        add("### %s" % report["day"])
        add("- spy peer total: %d (%s)" % (spy["peers"], spy["peers_source"]))
        add("- spy distinct gossip IPs: %d" % spy["distinct_ips"])
        add("- rpcview unique gossip IPs: %s" % num(rpc_ips))
        if rpc_ips:
            add("- ratio spy peers / rpcview IPs: %.3f" % (spy["peers"] / float(rpc_ips)))
            add("- raw difference: %d" % (spy["peers"] - rpc_ips))
        else:
            add("- ratio: n/a (no rpcview gossip IPs that day)")
        if spy["validators"] is not None:
            add("- spy validator peak: %d" % spy["validators"])
    if not any_spy:
        add("No spy JSONL (spy-*.jsonl) found for either day, so no gossip-view comparison.")
        add("Only the RPC view is represented in this brief.")
    add("")

    add("## Dataset health")
    add("")
    add("| day | files | max gap (h) | missing required | per-type counts |")
    add("| --- | ---: | ---: | --- | --- |")
    for report in (latest, previous):
        if report is None:
            continue
        health = report["health"]
        counts = ", ".join("%s=%d" % (t, c) for t, c in sorted(health["counts"].items()))
        add("| %s | %d | %.2f | %s | %s |" % (
            report["day"], health["total_files"], health["max_gap_hours"],
            ", ".join(health["missing"]) if health["missing"] else "none",
            counts or "none",
        ))
    add("")
    for report in (latest, previous):
        if report is None:
            continue
        gap = report["health"]["gap_between"]
        if gap:
            add("- %s largest gap: %s -> %s (%.2f h)" % (
                report["day"], gap[0].strftime("%H:%M:%SZ"),
                gap[1].strftime("%H:%M:%SZ"), report["health"]["max_gap_hours"]))
        if report["errors"]:
            for err in report["errors"]:
                add("- %s parse error: %s" % (report["day"], err))
    add("")

    add("## Source files")
    add("")
    for report in (latest, previous):
        if report is None:
            continue
        add("### %s" % report["day"])
        for entry in report["entries"]:
            add("- `%s`" % rel(entry["path"]))
        add("")

    if lat_cluster:
        add("Latest cluster-nodes snapshot used for point-in-time counts: `%s`"
            % rel(lat_cluster["latest_path"]))
        add("")
    return "\n".join(lines).rstrip() + "\n"


def build_stdout(latest, previous, week, churn, health_ok, out_path):
    lat_nodes = get(latest, "cluster", "nodes")
    lat_ips = get(latest, "cluster", "unique_ips")
    lat_rpc = get(latest, "cluster", "rpc_nodes")
    versions = get(latest, "cluster", "versions")
    top = versions.most_common(1)[0] if versions else None
    spy = latest["spy"] if latest else None
    if spy and lat_ips:
        view = "spy %d / rpc %d = %.3f" % (spy["peers"], lat_ips, spy["peers"] / float(lat_ips))
    elif spy:
        view = "spy %d / rpc n/a" % spy["peers"]
    else:
        view = "no spy jsonl"
    if churn is None:
        churn_txt = "churn n/a (needs two comparable days)"
    else:
        churn_txt = "churn +%d/-%d IPs" % (len(churn["entered"]), len(churn["left"]))
    return "\n".join([
        "S-NodeFinder %s | latest %s vs prev %s" % (
            week, latest["day"] if latest else "n/a",
            previous["day"] if previous else "n/a"),
        "nodes %s (%s) | gossip IPs %s (%s) | rpc-exposed %s (%s)" % (
            num(lat_nodes), delta(lat_nodes, get(previous, "cluster", "nodes")),
            num(lat_ips), delta(lat_ips, get(previous, "cluster", "unique_ips")),
            num(lat_rpc), delta(lat_rpc, get(previous, "cluster", "rpc_nodes"))),
        "validators %s current (%s) | %s delinquent (%s)" % (
            num(get(latest, "votes", "current")),
            delta(get(latest, "votes", "current"), get(previous, "votes", "current")),
            num(get(latest, "votes", "delinquent")),
            delta(get(latest, "votes", "delinquent"), get(previous, "votes", "delinquent"))),
        "%s | top version %s | view: %s" % (
            churn_txt,
            "%s (%d)" % (top[0], top[1]) if top else "n/a",
            view),
        "health: %s -> %s" % ("OK" if health_ok else "ATTENTION", rel(out_path)),
    ])


# ---------------------------------------------------------------------- main

def run():
    generated = datetime.now(timezone.utc)
    by_day = collect_files()
    days = sorted(by_day)

    latest = day_report(days[-1], by_day[days[-1]]) if days else None
    previous = day_report(days[-2], by_day[days[-2]]) if len(days) > 1 else None

    churn = None
    if latest and previous and latest["cluster"] and previous["cluster"]:
        new_ips = latest["cluster"]["day_ips"]
        old_ips = previous["cluster"]["day_ips"]
        churn = {
            "entered": new_ips - old_ips,
            "left": old_ips - new_ips,
            "stable": len(new_ips & old_ips),
            "latest_size": len(new_ips),
            "prev_size": len(old_ips),
        }

    notes = []
    if not days:
        notes.append("no data files found under data/")
    if latest and previous:
        gap_days = (
            datetime.strptime(latest["day"], "%Y-%m-%d")
            - datetime.strptime(previous["day"], "%Y-%m-%d")
        ).days
        if gap_days > 1:
            notes.append("previous day with data is %s, %d days before %s (calendar gap)"
                         % (previous["day"], gap_days, latest["day"]))
    elif days:
        notes.append("only one day of data (%s): no day-over-day comparison possible" % days[-1])
    for report in (latest, previous):
        if report is None:
            continue
        if report["health"]["missing"]:
            notes.append("%s missing required file types: %s"
                         % (report["day"], ", ".join(report["health"]["missing"])))
        if report["health"]["max_gap_hours"] > MAX_GAP_HOURS_OK:
            notes.append("%s snapshot gap %.2f h exceeds %.0f h"
                         % (report["day"], report["health"]["max_gap_hours"], MAX_GAP_HOURS_OK))
        if report["cluster"] is None:
            notes.append("%s has no usable cluster-nodes snapshot" % report["day"])
        elif report["cluster"]["nodes"] == 0:
            notes.append("%s latest cluster-nodes snapshot reports 0 nodes" % report["day"])
        if report["votes"] is None:
            notes.append("%s has no usable vote-accounts snapshot" % report["day"])
        for err in report["errors"]:
            notes.append("%s parse error: %s" % (report["day"], err))
    health_ok = not notes

    week_source = (
        datetime.strptime(latest["day"], "%Y-%m-%d") if latest else generated
    ).isocalendar()
    week = "%04d-W%02d" % (week_source[0], week_source[1])

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "%s.md" % week)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(build_brief(latest, previous, week, generated, health_ok, notes, churn))

    print(build_stdout(latest, previous, week, churn, health_ok, out_path))


def main():
    try:
        run()
    except Exception:
        traceback.print_exc(file=sys.stderr)
        print("S-NodeFinder digest failed, see stderr", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
