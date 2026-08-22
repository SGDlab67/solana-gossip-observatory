# RPC versus wire gap, 2026-08-22

## Summary

For both capture windows on 2026-08-22, the set of identities reported by an
RPC `getClusterNodes` snapshot and the set of identities observed directly on
the gossip wire by the spy overlap heavily but do not match. RPC consistently
sees more identities than the wire capture does, in raw count. The gap is
roughly stable in relative terms between the two windows.

| Window | RPC identities | Wire identities | Intersection | Wire-only (on wire, absent from RPC) | RPC-only (in RPC, absent from wire) |
|---|---|---|---|---|---|
| W1 | 3,712 | 3,543 | 3,519 | 24 (0.68% of wire) | 193 (5.20% of RPC) |
| W2 | 3,729 | 3,592 | 3,558 | 34 (0.95% of wire) | 171 (4.59% of RPC) |

W1: RPC snapshot `cluster-nodes-20260822T003052Z.json` (taken 2026-08-22
00:30:52 UTC) versus spy capture `spy-2026-08-22-002705.jsonl` (observed
window 00:27:35 - 00:29:05 UTC). The snapshot trails the capture by roughly
1.75 to 3.25 minutes, a tight pairing.

W2: RPC snapshot `cluster-nodes-20260822T184443Z.json` (taken 2026-08-22
18:44:43 UTC) versus spy capture `spy-2026-08-22-213016.jsonl` (observed
window 21:30:46 - 21:32:16 UTC). The snapshot precedes the capture by about
2 hours 46 minutes. This is not a tight pairing; the two W2 files are the only
RPC and spy files present for the day, so they are compared as given, but the
gap numbers for W2 should be read with that ~2h46m offset in mind rather than
treated as a true instantaneous cross-section.

## Method

**RPC side.** Each `cluster-nodes-*.json` file is a raw `getClusterNodes`
JSON-RPC response. Identities are the `pubkey` field of each entry in
`result` (a flat list, one entry per node the responding RPC node's gossip
table currently holds).

**Wire side.** Each `spy-*.jsonl` file is a newline-delimited capture of
gossip `ContactInfo` records, one JSON object per line, keyed by `pubkey`.
Verified that every line in both spy files carries a distinct `pubkey`
(3,543 lines / 3,543 unique pubkeys for W1; 3,592 lines / 3,592 unique
pubkeys for W2), so no per-window deduplication was needed beyond a set
build.

**Matching.** Identities are joined by exact `pubkey` string equality
(RPC's `pubkey` field against spy's `pubkey` field). No normalization was
needed; both sides use the same base58 identity string.

**Delta definitions.**
- Wire-only = identities present in the spy capture set but absent from the
  RPC snapshot set for that window.
- RPC-only = identities present in the RPC snapshot set but absent from the
  spy capture set for that window.

All counts are raw set differences/intersections computed directly from the
two source files per window; none are estimated.

## Shred-version check

Every identity in the wire-only, RPC-only, and intersection sets in both
windows carries `shred_version` / `shredVersion` 50093, the same value seen
across the intersection. The gap is not explained by identities belonging to
a different shred version (e.g. a testnet or forked cluster leaking into one
side's view); all deltas are within the same cluster.

## Drift between windows

The gap moved in opposite directions on the two sides between W1 and W2:

- Wire-only count rose from 24 to 34 (0.68% -> 0.95% of that window's wire
  set), and the share of wire-only identities that self-report as
  `validator: true` rose from 4/24 (16.7%) to 19/34 (55.9%).
- RPC-only count fell from 193 to 171 (5.20% -> 4.59% of that window's RPC
  set).

In relative terms the RPC-only share (the dominant side of the gap in both
windows) is stable at roughly 4.6-5.2%. The wire-only share is small in both
windows (under 1%) but nearly doubled in raw count and share between W1 and
W2, driven mostly by validator-flagged identities rather than non-validator
peers. Given the ~2h46m offset on the W2 RPC snapshot noted above, part of
this movement may reflect elapsed time between the RPC and wire observations
rather than a same-instant RPC/wire discrepancy; a same-instant W2 re-capture
would be needed to separate the two effects.

## Raw counts (for verification)

```
W1 RPC total (result array length):        3712
W1 wire total (unique pubkeys):             3543
W1 intersection:                            3519
W1 wire-only:                                 24
W1 rpc-only:                                 193

W2 RPC total (result array length):        3729
W2 wire total (unique pubkeys):             3592
W2 intersection:                            3558
W2 wire-only:                                 34
W2 rpc-only:                                 171
```

## Sources

- `data/2026-08-22/cluster-nodes-20260822T003052Z.json`
- `data/2026-08-22/cluster-nodes-20260822T184443Z.json`
- `data/2026-08-22/spy-2026-08-22-002705.jsonl`
- `data/2026-08-22/spy-2026-08-22-213016.jsonl`
