#!/usr/bin/env python3
"""Degree of anonymity (Diaz et al. 2002) over Solana gossip captures.

Reference:
  C. Diaz, S. Seys, J. Claessens, B. Preneel,
  "Towards Measuring Anonymity", PET 2002.
  d = H(X) / H_M, where H(X) is the Shannon entropy of the attacker's
  probability distribution over the candidate set, H_M = log2(N) is the
  maximum entropy (uniform over N candidates). d = 1 means the attacker
  learned nothing; d = 0 means the attacker pinned the target exactly.

WHAT THIS MEASURES HERE (a research-design choice, not a settled metric).
  We instantiate the Diaz model for a concrete deanonymization scenario:
  an adversary observes the gossip network, picks a target node, sees the
  IP that target advertises, and asks which validator identity is behind
  that IP. The target's anonymity set A(t) is the set of observed
  identities that advertise the same advertised gossip IP. Inside A(t) the
  adversary is taken to be uniform, so the per-target entropy is
  H_t = log2(|A(t)|) and the per-target degree is d_t = H_t / log2(N).

  The candidate set size N is the design knob. See choose_candidate_set()
  and docs/analysis/d-notes.md for the honest discussion. The default N is
  the number of unique observed identities in the window.

  Two system-level numbers are reported:
    d_unweighted    : mean of d_t over observed identities.
    d_stake_weighted: stake-weighted mean of d_t over the subset of
                      identities that carry activated stake (via
                      getVoteAccounts), weight = activatedStake share.

  Because Solana gossip is engineered so that each identity advertises a
  reachable endpoint, almost every identity has |A(t)| = 1, i.e. d_t = 0.
  A near-zero d is the expected, honest result: gossip provides essentially
  no sender anonymity. The residual comes from the handful of IPs that host
  more than one identity in a window.
"""

import argparse
import json
import math
import os
from collections import defaultdict


def load_capture(path):
    """Return dict: pubkey -> advertised gossip IP (host part), or None."""
    ids = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            gossip = rec.get("gossip")
            ip = gossip.rsplit(":", 1)[0] if gossip else None
            ids[rec["pubkey"]] = ip
    return ids


def load_stake(path):
    """Return dict: nodePubkey -> summed activatedStake (lamports).

    Sums across current and delinquent vote accounts so a node with more
    than one vote account is counted once with combined stake.
    """
    with open(path) as fh:
        doc = json.load(fh)
    result = doc["result"]
    stake = defaultdict(int)
    for bucket in ("current", "delinquent"):
        for va in result.get(bucket, []):
            stake[va["nodePubkey"]] += int(va["activatedStake"])
    return dict(stake)


def is_routable(ip):
    """Advertised IP that identifies a reachable host (excludes loopback)."""
    if not ip:
        return False
    if ip.startswith("127.") or ip == "::1":
        return False
    return True


def choose_candidate_set(ids, mode):
    """Return N, the size of the Diaz candidate set, per the chosen mode.

    modes:
      observed  : unique identities with a routable advertised IP in this
                  window. Default. N is the full observed anonymity set.
      all_ids   : every identity in the capture, including loopback / none.
      routable_ips : number of distinct routable IPs seen (identity-per-host
                  view rather than per-identity).
    """
    if mode == "observed":
        return sum(1 for ip in ids.values() if is_routable(ip))
    if mode == "all_ids":
        return len(ids)
    if mode == "routable_ips":
        return len({ip for ip in ids.values() if is_routable(ip)})
    raise ValueError("unknown candidate-set mode: %s" % mode)


def anonymity_sets(ids):
    """Map each routable IP to the set of identities advertising it."""
    by_ip = defaultdict(set)
    for pubkey, ip in ids.items():
        if is_routable(ip):
            by_ip[ip].add(pubkey)
    return by_ip


def compute(ids, stake, candidate_mode):
    n = choose_candidate_set(ids, candidate_mode)
    if n <= 1:
        raise ValueError("candidate set N must exceed 1 for log2(N)")
    h_max = math.log2(n)

    by_ip = anonymity_sets(ids)

    # Per-target degree d_t for every identity with a routable IP.
    d_by_id = {}
    for pubkey, ip in ids.items():
        if not is_routable(ip):
            continue
        aset = len(by_ip[ip])
        d_by_id[pubkey] = math.log2(aset) / h_max

    if not d_by_id:
        raise ValueError("no routable identities to score")

    d_unweighted = sum(d_by_id.values()) / len(d_by_id)

    # Stake-weighted over staked identities that are present and routable.
    weighted_num = 0.0
    weighted_den = 0
    staked_scored = 0
    for pubkey, lamports in stake.items():
        if pubkey in d_by_id and lamports > 0:
            weighted_num += d_by_id[pubkey] * lamports
            weighted_den += lamports
            staked_scored += 1
    d_stake_weighted = (weighted_num / weighted_den) if weighted_den else float("nan")

    shared_ips = {ip: len(s) for ip, s in by_ip.items() if len(s) > 1}
    ids_on_shared = sum(shared_ips.values())
    fully_deanon = sum(1 for d in d_by_id.values() if d == 0.0)

    return {
        "N": n,
        "H_max_bits": h_max,
        "scored_identities": len(d_by_id),
        "d_unweighted": d_unweighted,
        "d_stake_weighted": d_stake_weighted,
        "staked_identities_scored": staked_scored,
        "stake_lamports_scored": weighted_den,
        "fully_deanonymized_identities": fully_deanon,
        "shared_ip_count": len(shared_ips),
        "identities_on_shared_ips": ids_on_shared,
        "top_shared_ips": sorted(shared_ips.items(), key=lambda kv: -kv[1])[:5],
    }


CAVEATS = """\
CAVEATS (read before quoting any number)
  1. Choosing N is research design, not a settled fact. d scales with
     1 / log2(N); a different candidate set shifts the ceiling, not the
     ordering. The default N = unique observed identities is one defensible
     choice among several (see docs/analysis/d-notes.md).
  2. This restates public gossip data. Solana broadcasts ContactInfo by
     design; a near-zero d confirms the protocol is non-anonymous, it does
     not defeat any access control.
  3. The adversary model is deliberately simple: uniform over identities
     sharing an IP, no correlation across TPU/TVU/RPC ports, no cross-window
     linkage, no external enrichment (ASN, ownership). A stronger adversary
     would only lower d.
  4. Single-window snapshot. A 120-second listen can miss nodes; an IP that
     looks unique here may be shared over a longer horizon, or vice versa.
  5. Stake join uses the nearest getVoteAccounts snapshot, which is not
     simultaneous with the capture. activatedStake is fixed within an epoch,
     so the timing gap affects membership, not stake amounts.
"""


def run_window(label, capture_path, stake_path, candidate_mode):
    ids = load_capture(capture_path)
    stake = load_stake(stake_path)
    res = compute(ids, stake, candidate_mode)
    print("=" * 68)
    print("Window: %s" % label)
    print("  capture: %s" % os.path.basename(capture_path))
    print("  stake:   %s" % os.path.basename(stake_path))
    print("  candidate-set mode: %s" % candidate_mode)
    print("-" * 68)
    print("  N (candidate set)                 : %d" % res["N"])
    print("  H_max = log2(N)                   : %.4f bits" % res["H_max_bits"])
    print("  scored identities                 : %d" % res["scored_identities"])
    print("  fully deanonymized (d_t = 0)      : %d (%.2f%%)" % (
        res["fully_deanonymized_identities"],
        100.0 * res["fully_deanonymized_identities"] / res["scored_identities"],
    ))
    print("  IPs hosting >1 identity           : %d (%d identities)" % (
        res["shared_ip_count"], res["identities_on_shared_ips"]))
    if res["top_shared_ips"]:
        pretty = ", ".join("%s=%d" % (ip, c) for ip, c in res["top_shared_ips"])
        print("  top shared IPs                    : %s" % pretty)
    print("  staked identities scored          : %d" % res["staked_identities_scored"])
    print("-" * 68)
    print("  d (unweighted)                    : %.6f" % res["d_unweighted"])
    print("  d (stake-weighted)                : %.6f" % res["d_stake_weighted"])
    print("=" * 68)
    return res


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    default_data = os.path.normpath(os.path.join(here, "..", "..", "data", "2026-08-22"))

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", default=default_data,
                    help="directory holding the 2026-08-22 captures and vote accounts")
    ap.add_argument("--candidate-set", default="observed",
                    choices=["observed", "all_ids", "routable_ips"],
                    help="how to size N (default: observed)")
    args = ap.parse_args()

    d = args.data_dir
    windows = [
        ("W1 2026-08-22 00:27:05 UTC",
         os.path.join(d, "spy-2026-08-22-002705.jsonl"),
         os.path.join(d, "vote-accounts-20260822T003052Z.json")),
        ("W2 2026-08-22 21:30:16 UTC",
         os.path.join(d, "spy-2026-08-22-213016.jsonl"),
         os.path.join(d, "vote-accounts-20260822T184443Z.json")),
    ]

    missing = [p for _, cap, st in windows for p in (cap, st) if not os.path.exists(p)]
    if missing:
        print("MISSING DATA, cannot compute. Absent files:")
        for p in missing:
            print("  %s" % p)
        raise SystemExit(2)

    for label, cap, st in windows:
        run_window(label, cap, st, args.candidate_set)

    print()
    print(CAVEATS)


if __name__ == "__main__":
    main()
