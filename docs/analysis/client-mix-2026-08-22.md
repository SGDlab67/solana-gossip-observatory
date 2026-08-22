# Client Mix Census from Gossip, 2026-08-22

## Overview

Two gossip-spy snapshots were collected on 2026-08-22. This analysis classifies every
observed identity into a client family: Agave, Jito, Firedancer, or Other.

## Data Sources

| Window | JSONL file | Identities |
|--------|-----------|------------|
| W1 (00:27 UTC) | spy-2026-08-22-002705.jsonl | 3,543 |
| W2 (21:30 UTC) | spy-2026-08-22-213016.jsonl | 3,592 |

Counts are unique pubkeys in each JSONL, verified with an independent recount
on 2026-08-22. Note: the W2 spy-summary file's final tick reports total_peers
3,490, which lags the JSONL count by 102 identities. Treat the JSONL as
authoritative for identity counts; the summary tick reflects table size at a
tick boundary, not cumulative observed identities.

Supplementary RPC snapshots used for `clientId` lookup:
- cluster-nodes-20260822T003052Z.json (W1)
- cluster-nodes-20260822T184443Z.json (W2)

## Method

### Step 1: Join spy data with cluster-nodes

Each spy record is keyed by `pubkey`. The `getClusterNodes` RPC response includes a
`clientId` field introduced in Agave 2.x. For the 97-99% of pubkeys present in both
sources, the `clientId` from the RPC is used directly.

### Step 2: Version-string fallback

A small number of pubkeys appear in the spy JSONL but not in the RPC response (24 in W1,
34 in W2). These are classified from the `version` field in the gossip ContactInfo record
using these rules, applied in order:

1. `clientId` present: use the table below.
2. Version starts with `0.1` and length > 4 (e.g. `0.1005.40100`): Firedancer.
3. Version starts with `1.100.`: Firedancer.
4. Version starts with `26.`: Jito (Jito uses calendar versioning in some builds).
5. Major version 2, 3, or 4 (e.g. `4.2.1`): Agave.
6. All other version strings: Other.

### Step 3: clientId family mapping

| clientId from RPC | Family |
|-------------------|--------|
| Agave | Agave |
| AgaveBam | Agave |
| JitoLabs | Jito |
| Firedancer | Firedancer |
| Frankendancer | Firedancer |
| Unknown(N) | Other |

`AgaveBam` is a Jito-patched Agave build that still self-identifies as an Agave fork at
the protocol level. It is counted under Agave here, consistent with the upstream client
identity it reports. See the Caveats section.

## Results

### Window 1 (002705 UTC, 3,543 identities)

| Family | Count | Share |
|--------|-------|-------|
| Agave | 2,290 | 64.6% |
| Jito | 973 | 27.5% |
| Firedancer | 140 | 4.0% |
| Other | 140 | 4.0% |
| **Total** | **3,543** | **100%** |

Firedancer breakdown: 110 Frankendancer + 30 Firedancer (from cluster-nodes clientId).

Other breakdown: all nodes with Unknown(N) clientId from the RPC (Unknown(10)=73,
Unknown(8)=30, Unknown(11)=22, Unknown(12)=8, Unknown(13)=3, Unknown(9)=2,
Unknown(30928)=1, Unknown(19785)=1).

### Window 2 (213016 UTC, 3,592 identities)

| Family | Count | Share |
|--------|-------|-------|
| Agave | 2,321 | 64.6% |
| Jito | 995 | 27.7% |
| Other | 141 | 3.9% |
| Firedancer | 135 | 3.8% |
| **Total** | **3,592** | **100%** |

Firedancer breakdown: 111 Frankendancer + 24 Firedancer (from cluster-nodes clientId).

### Shift between windows

Agave and Jito shares held steady at 64.6% and ~27.5-27.7%. Firedancer edged down by
5 nodes (140 to 135). Total peer count grew by 49 (3,543 to 3,592), consistent with
normal churn and online validators ramping up in the evening UTC window.

## Caveats

### AgaveBam ambiguity

AgaveBam is maintained by Jito Labs and includes Jito-specific modifications (block
engine integration, MEV relayer). Operators may consider it a Jito client. This analysis
classifies it under Agave because its `clientId` explicitly says `AgaveBam`, not
`JitoLabs`, and it shares the Agave codebase. If AgaveBam is reclassified as Jito:

- W1: Jito rises to 27.5% + (373/3543=10.5%) = 38%, Agave falls to 54%.
- W2: Jito rises to approximately 38%, Agave falls to approximately 54%.

### Unknown(N) clientIds

Nodes reporting `Unknown(N)` are peers whose client integer code is not in the current
Agave enum. These could be custom forks, pre-release Firedancer builds, or testnet
tooling. Without a mapping table from integer to name, they cannot be classified further.

### Gossip vs. consensus set

The spy JSONL captures all reachable gossip peers, including non-voting RPC nodes,
explorers, and tooling. The cluster-nodes RPC covers a narrower set: only nodes the
leader knows about. The 24-34 pubkeys with version-string fallback are likely edge nodes
not in the active cluster set.

### Version-string parsing limits

Version strings in gossip are self-reported and unverified. A node can advertise any
string. The fallback heuristics are best-effort. They affected only 24 nodes in W1 and
34 in W2, so the overall classification accuracy is high (99.3% and 99.1% covered by
authoritative clientId).
