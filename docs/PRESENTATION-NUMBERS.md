# S-NodeFinder presentation numbers sheet

**Captured 2026-09-02, they advance.** Every row below is a reading taken at a
stated instant, not a fixed property of the cluster. Gossip has no archive, so
a number without a capture date is not a number. Refresh with
`./scripts/refresh-numbers.sh` the day before the meeting and re-date any row
that moves.

Sheet generated: 2026-09-03T01:41:48Z. Series spans 2026-08-21 through
2026-09-02.

---

## 1. Headline numbers for the slides

### Slide 4: what was built

| Fact | Value | Capture date |
| --- | --- | --- |
| rpcview series start (first dated snapshot on disk) | 2026-08-21 | 2026-08-21 |
| spy first successful wire capture | 2026-08-22T00:27:05Z | 2026-08-22 |
| UTC days with data on disk | 13 (2026-08-21 to 2026-09-02) | 2026-09-02 |
| Snapshot cadence | roughly 6 hours, RPC and spy | 2026-09-02 |

### Slide 5: results so far

| Claim | Value | Source instant |
| --- | --- | --- |
| Freshest full 120 s spy window, final peer count | **3,070** | 2026-09-02, run 14:36:42Z, final tick 14:38:42Z |
| Discovery curve for that window (4 ticks, 30 s apart) | 754 / 1,792 / 2,571 / **3,070** | 2026-09-02 14:37:12Z to 14:38:42Z |
| Curve still rising at the final tick | +499 on the last tick | 2026-09-02 14:38:42Z |
| Nearest RPC view to that window (+48 min) | 3,705 nodes | 2026-09-02T15:26:46Z |
| Coverage of that window against the nearest RPC view | 3,070 / 3,705 = **82.9 %** | 2026-09-02 |
| Closing RPC view for the day | 3,685 nodes, 3,658 unique gossip IPs | 2026-09-02T23:20:08Z |
| Coverage against the day's closing RPC view | 3,070 / 3,685 = 83.3 % | 2026-09-02 |
| Wire/RPC gap, last four days, full windows only | **17.1 % to 25.1 %** | 2026-08-30 to 2026-09-02 |
| Wire/RPC gap, first paired window | 4.6 % | 2026-08-22 |
| Stake-weighted identified fraction, W1 | **0.984203 (98.42 %)** | 2026-08-22 00:27:05Z capture, 00:30:52Z stake snapshot |
| Stake-weighted identified fraction, W2 | 0.996054 (99.61 %) | 2026-08-22 21:30:16Z capture, 18:44:43Z stake snapshot |
| Vote accounts, current / delinquent | **677 / 18** | 2026-09-02T23:20:08Z |
| Client census leader | 4.2.1, 1,880 of 3,685 nodes = **51.0 %** | 2026-09-02T23:20:08Z |
| Client census, previous reading | 4.2.1, 2,036 of 3,751 nodes = 54.3 % | 2026-08-31T11:13:59Z |
| Day over day gossip IP churn, latest pair | entered 33, left 34, stable 3,722 | 2026-09-01 to 2026-09-02 |

Client census, full top six at the 2026-09-02T23:20:08Z snapshot (n = 3,685):

| Version | Nodes | Share |
| --- | ---: | ---: |
| 4.2.1 | 1,880 | 51.0 % |
| 4.2.0 | 557 | 15.1 % |
| 4.2.2 | 449 | 12.2 % |
| 2.3.8 | 191 | 5.2 % |
| 4.1.2 | 174 | 4.7 % |
| 4.2.0-rc.1 | 100 | 2.7 % |

The 4.2.2 row did not exist in the 2026-08-31 census. An upgrade wave is in
flight, which is why the 4.2.1 share fell from 54.3 % to 51.0 % in two days.

### Wire versus RPC, every full 120 s window in the series

Each spy window is paired to the nearest parseable cluster-nodes snapshot in
time. Gap is (RPC nodes minus wire pubkeys) divided by RPC nodes.

| Window final tick (UTC) | Wire pubkeys | Nearest RPC | Offset (h) | Gap |
| --- | ---: | ---: | ---: | ---: |
| 2026-08-22 00:29:05Z | 3,543 | 3,712 | 0.03 | 4.6 % |
| 2026-08-22 21:32:16Z | 3,592 | 3,729 | 2.79 | 3.7 % |
| 2026-08-23 03:34:17Z | 3,250 | 3,746 | 2.70 | 13.2 % |
| 2026-08-23 17:12:42Z | 3,356 | 3,736 | 2.72 | 10.2 % |
| 2026-08-23 23:15:18Z | 3,442 | 3,740 | 2.68 | 8.0 % |
| 2026-08-24 05:17:27Z | 3,301 | 3,740 | 3.36 | 11.7 % |
| 2026-08-24 17:14:52Z | 3,425 | 3,751 | 0.03 | 8.7 % |
| 2026-08-25 16:33:51Z | 3,229 | 3,737 | 2.08 | 13.6 % |
| 2026-08-26 04:54:40Z | 3,200 | 3,740 | 2.30 | 14.4 % |
| 2026-08-26 17:27:13Z | 3,152 | 3,723 | 2.51 | 15.3 % |
| 2026-08-26 23:38:51Z | 3,124 | 3,736 | 2.60 | 16.4 % |
| 2026-08-27 05:41:17Z | 3,170 | 3,736 | 2.18 | 15.1 % |
| 2026-08-28 19:02:50Z | 3,159 | 3,742 | 0.32 | 15.6 % |
| 2026-08-30 01:27:39Z | 2,814 | 3,758 | 2.71 | 25.1 % |
| 2026-08-31 01:36:15Z | 3,041 | 3,754 | 3.62 | 19.0 % |
| 2026-09-01 04:23:34Z | 2,978 | 3,744 | 3.11 | 20.5 % |
| 2026-09-02 00:55:24Z | 3,057 | 3,723 | 0.99 | 17.9 % |
| 2026-09-02 06:57:40Z | 3,054 | 3,723 | 5.05 | 18.0 % |
| 2026-09-02 14:38:42Z | 3,070 | 3,705 | 0.80 | 17.1 % |

The gap is not flat. It sat at 3.7 % to 4.6 % on 2026-08-22, ran 8 % to 16.4 %
from 2026-08-23 to 2026-08-28, and has held between 17.1 % and 25.1 % on every
full window since 2026-08-30. That is a widening, not a constant offset, and it
is the shape a short window plus a partial CRDS table would produce if the
window is the binding constraint. It is not yet separated from RPC staleness.

### Slide 6: the limits, with their numbers

| Limit | Number that shows it | Capture date |
| --- | --- | --- |
| d is not computed on any fresh window | last computed d: 0.001688 unweighted, 0.000000 stake-weighted | 2026-08-22 W1 |
| d at the endpoint only | about 98.9 % of W1 identities sat alone on their IP, so d_t = 0 | 2026-08-22 W1 |
| Shared-IP residual is tiny | 11 IPs carried more than one identity in W1 (36 identities) | 2026-08-22 W1 |
| 120 s windows undercount | every full window ends on a rising tick, +499 on the freshest | 2026-09-02 |
| Duty cycle is mid migration | 23 spy runs in the last 7 days, 8 full 4-tick windows, 15 truncated | 2026-08-27 to 2026-09-02 |
| Snapshot pipeline has gaps | 4 unparseable cluster-nodes files in the series | 2026-08-23 to 2026-09-02 |
| AS and cloud enrichment | no measurement exists, planned work | n/a |
| Stake table not refreshed | freshest stake-weighted figure is 11 days old | 2026-08-22 |

Unparseable cluster-nodes files, named so they are not a surprise in Q&A:

| File | Size | Failure |
| --- | ---: | --- |
| data/2026-08-23/cluster-nodes-20260823T073758Z.json | 23,675 B | truncated JSON |
| data/2026-08-25/cluster-nodes-20260825T003914Z.json | 0 B | empty |
| data/2026-08-30/cluster-nodes-20260830T231313Z.json | 0 B | empty |
| data/2026-09-02/cluster-nodes-20260902T090817Z.json | 790,236 B | truncated JSON |

Each day still has at least one readable snapshot, so no UTC day in the series
is lost. `./scripts/refresh-numbers.sh` prints EMPTY for these rather than
failing, and falls back to the day's latest readable snapshot.

---

## 2. Frozen evidence: source file per claim

Every claim on the slides traces to a file in this repository. Nothing here is
estimated, and nothing is carried over from a prior deck without re-reading the
file.

### Freshest full spy window (3,070 peers, 2026-09-02)

- `data/2026-09-02/spy-summary-2026-09-02-143642.jsonl` (4 ticks, final tick `total_peers` 3,070, `validators` 3,000)
- `data/2026-09-02/spy-2026-09-02-143642.jsonl` (3,070 lines, 3,070 unique pubkeys, so the summary and the JSONL agree for this window)

### Other full windows cited

- `data/2026-09-02/spy-summary-2026-09-02-005324.jsonl` (3,057)
- `data/2026-09-02/spy-summary-2026-09-02-065540.jsonl` (3,054)
- `data/2026-09-01/spy-summary-2026-09-01-042134.jsonl` (2,978; JSONL 2,978 unique pubkeys)
- `data/2026-08-31/spy-summary-2026-08-31-013415.jsonl` (3,041; JSONL 3,041 unique pubkeys)
- `data/2026-08-30/spy-summary-2026-08-30-012539.jsonl` (2,814)
- `data/2026-08-22/spy-summary-2026-08-22-002705.jsonl` (3,543, the first capture)

### RPC cluster view

- `data/2026-09-02/cluster-nodes-20260902T232008Z.json` (3,685 nodes, 3,658 unique gossip IPs, version census)
- `data/2026-09-02/cluster-nodes-20260902T152646Z.json` (3,705 nodes, 3,679 unique gossip IPs, the tight pair for the 14:36 window)
- `data/2026-09-01/cluster-nodes-20260901T195404Z.json` (3,724 / 3,697)
- `data/2026-08-31/cluster-nodes-20260831T185800Z.json` (3,750 / 3,716)
- `data/2026-08-29/cluster-nodes-20260829T221011Z.json` (3,751 / 3,725)
- `data/2026-08-22/cluster-nodes-20260822T003052Z.json` (3,712 / 3,685, the one-pager pairing)

### Stake view

- `data/2026-09-02/vote-accounts-20260902T232008Z.json` (677 current, 18 delinquent)
- `data/2026-08-22/vote-accounts-20260822T003052Z.json` (682 current, 12 delinquent; the stake snapshot behind 0.984203)
- `docs/analysis/stake-weighted-leak-2026-08-22.md` (method, join counts, top 15 staked identities and their advertised IPs, caveats)

### Anonymity metric

- `docs/analysis/d-notes.md` (Diaz 2002 instantiation, candidate set choice, W1 d = 0.001688 unweighted and 0.000000 stake-weighted, W2 d = 0.001869 and 0.000243)
- `analysis/d-anonymity/` (the runnable scaffold)

### Wire versus RPC gap

- `docs/analysis/rpc-wire-gap-2026-08-22.md` (set-level method: W1 intersection 3,519, wire-only 24, RPC-only 193; W2 intersection 3,558, wire-only 34, RPC-only 171; shred version 50093 on both sides, so the gap is not a cross-cluster artifact)
- The full-window gap table above, recomputed 2026-09-03 over every 4-tick summary in `data/`

### Client census

- `docs/analysis/client-mix-2026-08-22.md` (family classification method, AgaveBam ambiguity, version-string fallback rules)
- `snapshots/digests/2026-W36.md` (2026-08-31 census: 4.2.1 at 2,036 / 54.3 %)
- `data/2026-09-02/cluster-nodes-20260902T232008Z.json` (2026-09-02 census, recomputed for this sheet)

### Churn

- `snapshots/digests/2026-W36.md` (2026-08-30 to 2026-08-31: entered 16, left 35, stable 3,729)
- Day over day union recomputed 2026-09-03 across `data/2026-08-21` to `data/2026-09-02`: entered stays between 20 and 58 per day, left between 27 and 99, stable never drops below 3,691

### Ethics and instrument provenance

- `docs/ETHICS.md` (the bind: public data only, pull only, one persistent identifiable identity, conservative rates, no eclipse, no Sybil, no impersonation)
- `docs/ONE-PAGER-FORMAL.md` (the no-shipped-binary finding: Agave 4.x ships gossip as a library only, and solana 1.18.26 announces gossip port 0 against the 4.2.x mesh)
- `scripts/snapshot.sh`, `scripts/watchdog.sh`, `scripts/digest.py` (the collection and rollup pipeline)

---

## 3. Refresh output, run 2026-09-03T01:41:48Z

Produced by `./scripts/refresh-numbers.sh`, pasted verbatim.

```
S-NodeFinder numbers refresh
generated: 2026-09-03T01:41:48Z
window:    2026-08-27 to 2026-09-02 (7 UTC days on disk)

## RPC cluster view (latest cluster-nodes snapshot per UTC day)

| UTC day | snapshot | nodes | unique gossip IPs |
| --- | --- | ---: | ---: |
| 2026-08-27 | cluster-nodes-20260827T180750Z.json | 3716 | 3688 |
| 2026-08-28 | cluster-nodes-20260828T192151Z.json | 3742 | 3715 |
| 2026-08-29 | cluster-nodes-20260829T221011Z.json | 3751 | 3725 |
| 2026-08-30 | cluster-nodes-20260830T231313Z.json | EMPTY | EMPTY |
| 2026-08-30 | cluster-nodes-20260830T163331Z.json (latest readable) | 3774 | 3740 |
| 2026-08-31 | cluster-nodes-20260831T185800Z.json | 3750 | 3716 |
| 2026-09-01 | cluster-nodes-20260901T195404Z.json | 3724 | 3697 |
| 2026-09-02 | cluster-nodes-20260902T232008Z.json | 3685 | 3658 |

## Spy runs (spy-summary files, one row per run)

| UTC day | summary file | ticks | final peers | curve |
| --- | --- | ---: | ---: | --- |
| 2026-08-27 | spy-summary-2026-08-27-053917.jsonl | 4 | 3170 | 890 / 1960 / 2714 / 3170 |
| 2026-08-27 | spy-summary-2026-08-27-122445.jsonl | 1  (truncated) | 399 | 399 |
| 2026-08-27 | spy-summary-2026-08-27-202636.jsonl | 1  (truncated) | 535 | 535 |
| 2026-08-28 | spy-summary-2026-08-28-035617.jsonl | 1  (truncated) | 361 | 361 |
| 2026-08-28 | spy-summary-2026-08-28-111951.jsonl | 1  (truncated) | 488 | 488 |
| 2026-08-28 | spy-summary-2026-08-28-190050.jsonl | 4 | 3159 | 877 / 1947 / 2694 / 3159 |
| 2026-08-29 | spy-summary-2026-08-29-020318.jsonl | 1  (truncated) | 494 | 494 |
| 2026-08-29 | spy-summary-2026-08-29-100911.jsonl | 1  (truncated) | 405 | 405 |
| 2026-08-29 | spy-summary-2026-08-29-183124.jsonl | 1  (truncated) | 14 | 14 |
| 2026-08-30 | spy-summary-2026-08-30-012539.jsonl | 4 | 2814 | 613 / 1451 / 2072 / 2814 |
| 2026-08-30 | spy-summary-2026-08-30-103310.jsonl | 1  (truncated) | 309 | 309 |
| 2026-08-30 | spy-summary-2026-08-30-191739.jsonl | 2  (truncated) | 1145 | 490 / 1145 |
| 2026-08-31 | spy-summary-2026-08-31-013415.jsonl | 4 | 3041 | 908 / 1787 / 2613 / 3041 |
| 2026-08-31 | spy-summary-2026-08-31-074305.jsonl | 1  (truncated) | 424 | 424 |
| 2026-08-31 | spy-summary-2026-08-31-141311.jsonl | 3  (truncated) | 2571 | 809 / 1620 / 2571 |
| 2026-08-31 | spy-summary-2026-08-31-220209.jsonl | 1  (truncated) | 605 | 605 |
| 2026-09-01 | spy-summary-2026-09-01-042134.jsonl | 4 | 2978 | 564 / 1568 / 2373 / 2978 |
| 2026-09-01 | spy-summary-2026-09-01-105657.jsonl | 1  (truncated) | 371 | 371 |
| 2026-09-01 | spy-summary-2026-09-01-175148.jsonl | 2  (truncated) | 1004 | 460 / 1004 |
| 2026-09-02 | spy-summary-2026-09-02-005324.jsonl | 4 | 3057 | 807 / 1763 / 2626 / 3057 |
| 2026-09-02 | spy-summary-2026-09-02-065540.jsonl | 4 | 3054 | 864 / 1884 / 2512 / 3054 |
| 2026-09-02 | spy-summary-2026-09-02-143642.jsonl | 4 | 3070 | 754 / 1792 / 2571 / 3070 |
| 2026-09-02 | spy-summary-2026-09-02-232008.jsonl | 1  (truncated) | 147 | 147 |

## Vote accounts (freshest snapshot in window)

| snapshot | current | delinquent |
| --- | ---: | ---: |
| vote-accounts-20260902T232008Z.json | 677 | 18 |

All values read directly from data/. Nothing above is estimated.
```

---

## Footer: where the repository corrected the brief

These six items were written differently in the request that produced this
sheet, or differ from what an earlier document in this repository states. In
each case the raw files won.

1. **Vote accounts on 2026-09-02 are 677 current, not 675.** Both readable
   snapshots that day, 15:26:46Z and 23:20:08Z, report 677 current and 18
   delinquent. Source: `data/2026-09-02/vote-accounts-20260902T232008Z.json`.

2. **4.2.1 is at 51.0 %, not about 54 %.** The 54.3 % figure is real but it is
   the 2026-08-31 reading in `snapshots/digests/2026-W36.md`. By 2026-09-02 the
   share had fallen to 1,880 of 3,685, and a new 4.2.2 build had taken 12.2 %.
   Saying 54 % on 2026-09-04 would be quoting a stale census.

3. **The wire/RPC gap has not held at 16 to 19 percent for two weeks.** It was
   3.7 % to 4.6 % on 2026-08-22, ran 8 % to 16.4 % through 2026-08-28, and has
   sat at 17.1 % to 25.1 % on every full window since 2026-08-30. The defensible
   sentence is that the gap widened over the first week and has stayed in a 17 %
   to 25 % band for the last four days, not that it has been stable.

4. **There are four unparseable cluster-nodes files, not one.** Two are 0 bytes
   (2026-08-25 and 2026-08-30) and two are truncated mid-JSON (2026-08-23 and
   2026-09-02). The refresh script tolerates all four.

5. **2026-09-02 produced three full 120 s windows, not one.** Runs at 00:53,
   06:55 and 14:36 all completed 4 ticks, finishing at 3,057, 3,054 and 3,070.
   Three independent same-day windows landing within 16 peers of each other is a
   stronger result than a single window, and it is worth saying out loud.

6. **The oldest snapshot on disk is dated 2026-08-21, not 2026-08-19.**
   `docs/ONE-PAGER-FORMAL.md` says rpcview has been operational since
   2026-08-19, which may well be true of the tool, but `data/` holds no day
   directory before `data/2026-08-21`. The safe sentence on the slide is that
   the dated series begins 2026-08-21. If two earlier days exist somewhere off
   the repository, add them before claiming them.

One item the repository confirmed as written: the stake-weighted identified
fraction is 0.984203 for the 2026-08-22 W1 capture, exactly as
`docs/analysis/stake-weighted-leak-2026-08-22.md` reports it. It has not been
recomputed on a fresher window, and the deck says so.
