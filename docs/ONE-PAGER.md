# S-NodeFinder: Measuring the Degree of Anonymity of Solana Validators at the Gossip Layer

**For:** Dr. Zane Ma, ASTRO Lab, Oregon State University
**Author:** Stebit
**Date:** 2026-08-21 (due 2026-08-31)
**Repo:** `solana-gossip-observatory` (two instruments: `rpcview/`, `spy/`)

## 1. Research question

What is the degree of anonymity of a Solana validator at the gossip layer, and how fast does it decay under passive observation?

Three measurable sub-claims:

1. **Speed and accuracy of identity to IP linking.** How much of the validator set resolves to an advertised IP, as a function of how long a pull-only observer listens?
2. **Stake-weighted leak.** What fraction of activated stake sits behind an IP the protocol already advertises?
3. **AS and cloud concentration.** How far do those IPs collapse into a small number of autonomous systems or hosting providers?

## 2. Motivation

Solana's gossip layer is not designed to hide operators: every participating node advertises a `ContactInfo` record (identity pubkey, gossip socket, TPU/TVU sockets, shred version, client version). Public RPC re-exports much of the same through `getClusterNodes`. The interesting question is therefore not *whether* identity leaks, but *how completely and how quickly*, and *how much economic weight* sits behind the leak. A validator whose IP is a 120-second lookup has a different threat surface (targeted DoS, traffic analysis, leader-slot-timed pressure) than one that requires an active crawl.

Measured on mainnet (single 120 s pull-only gossip window, 2026-08-22T00:27:05Z to 00:29:05Z):

| Observation | Value |
| --- | ---: |
| Distinct identity pubkeys with a `ContactInfo` observed on the wire | **3,543** |
| of which advertised a TVU (shred-receiving) socket, final tick | **3,452** |
| CRDS peer-table size at each of four 30 s ticks | **1,540 -> 2,642 -> 3,321 -> 3,543** |
| RPC view, captured 00:30:52Z: cluster nodes | **3,712** |
| RPC view, captured 00:30:52Z: unique gossip IPs | **3,685** |

Two minutes of passive listening recovered ~95% of the node count the cluster's own RPC advertised two minutes later, from a listener that contributes nothing to the mesh. Both counts are one entry per identity pubkey, so they are directly comparable; neither is ground truth. Note that the 3,452 figure is the shred-receiving node population, not the staked validator set: the same-day RPC capture shows 682 current vote accounts.

**The view gap is itself a finding.** The RPC view (3,712 nodes / 3,685 unique gossip IPs) exceeds the wire view (3,543 pubkeys) by 169 nodes, roughly 4.6%. That delta is what the cluster *advertises* through a curated endpoint but the mesh did not *show* a single observer in 120 s. It has at least three candidate explanations that the longitudinal series is designed to separate: (a) the window was too short, since the curve had not flattened (+222 on the final tick); (b) CRDS propagation and pruning give any single vantage point a partial table; (c) the RPC endpoint's view is stale or retains nodes that have already left. NodeFinder reported the same class of disagreement on Ethereum, between the overlay a crawler discovers and the consensus-relevant set; we treat cross-view disagreement as a signal about observability, not as noise to be averaged away.

## 3. Related work

**Kim, Ma, Murali, Mason, Miller, Bailey. "Measuring Ethereum Network Peers." IMC 2018.** ([doi:10.1145/3278532.3278542](https://doi.org/10.1145/3278532.3278542)) NodeFinder harvested Ethereum's overlay via RLPx discovery plus DEVp2p HELLO/STATUS, and reported peer counts, client mix, and AS/geography concentration. It also showed that the discovered overlay is far larger and messier than the consensus-relevant set. What does *not* port directly: Ethereum's Kademlia-style discovery lets a crawler walk the ID space, whereas Solana's CRDS is a push/pull anti-entropy table, so coverage is a function of *dwell time and peer selection*, not of scan breadth. The mapping we use:

| NodeFinder (Ethereum) | S-NodeFinder (Solana) |
| --- | --- |
| RLPx discovery scan | Gossip CRDS pull (`spy/`), `getClusterNodes` (`rpcview/`) |
| DEVp2p HELLO harvest | Gossip `ContactInfo` |
| STATUS (network / genesis) | Shred version |
| Geth / Parity client census | Agave / Firedancer / Jito version census |
| Geography and AS | IP to AS/cloud enrichment of gossip IPs |

**Kiffer, Heimbach, Trautwein, Vonlanthen, Gasser. "Multiple Sides of 36 Coins: Measuring Peer-to-Peer Infrastructure Across Cryptocurrencies." ACM SIGMETRICS 2026.** (arXiv:2511.15388) Reports a Solana node population of ~3,693 from an API-level vantage point, which falls between our wire view (3,543) and our same-window RPC view (3,712), and gives an independently collected anchor for the order of magnitude. Its contribution is breadth across chains at an API vantage; ours is depth at *one* chain's wire vantage, with the API/wire delta as the object of study rather than an implementation detail.

**Diaz, Seys, Claessens, Preneel. "Towards Measuring Anonymity." PET 2002.** ([doi:10.1007/3-540-36467-6_5](https://doi.org/10.1007/3-540-36467-6_5)) We adopt their normalized degree of anonymity, *d* = *H*/*H*<sub>max</sub>, where *H* is the entropy of the adversary's posterior over which node in a candidate set *N* corresponds to a given validator identity, and *H*<sub>max</sub> = log|*N*| is the entropy of a uniform posterior over that set. This makes "how anonymous" a number rather than an adjective, and makes a stake-weighted variant natural: weight by activated stake instead of by node count. **We have not computed *d* yet.** What `rpcview` emits today is `stake_weighted_identified_fraction`: the share of activated stake whose identity already resolves to a single advertised IP, that is, the share sitting at the *d* = 0 endpoint. Choosing the candidate set *N* for identities that are not at that endpoint, and estimating the posterior over it, is unfinished work rather than a result.

## 4. Method

**Two instruments, deliberately redundant.**

- `rpcview/` (operational since 2026-08-19): typed Rust CLI over public RPC `getClusterNodes` + `getVoteAccounts`. Dated JSON snapshots on a timer. This is the backstop series: gossip has no archive, so the clock is the dataset.
- `spy/` (first successful wire capture 2026-08-22 UTC): a hand-built pull-only CRDS listener against the current Agave 4.2.x protocol, emitting one JSONL row per observed `ContactInfo` plus a per-tick summary. A custom crate was not a preference: of the releases we checked, the Agave 4.x/2.x bundles ship no gossip binary at all (4.x gossip is library-only), and the one that does, solana 1.18.26, announces gossip port 0 against the 4.2.x mesh and stays at Nodes: 0.

**Analysis pipeline.** (i) Join gossip identities to vote accounts to obtain stake-weighted leak. (ii) Enrich IPs to AS and cloud provider offline, recording enrichment source and vintage because AS mappings drift. (iii) Compute *d* and its stake-weighted variant per snapshot. (iv) Diff the RPC view against the wire view each run and report the delta as a first-class metric.

**Longitudinal churn plan.** Repeat both captures on a fixed schedule (`scripts/watchdog.sh`, weekly rollups via `scripts/digest.py`) and measure: node arrival and departure rates, identity persistence, IP re-advertisement and migration for a stable pubkey, and whether the RPC/wire gap is a constant offset or a time-varying artifact. Longer spy windows will also let us fit the saturation curve and report *time to X% coverage* rather than a single-window count.

**Ethics.** Public gossip and public RPC data only. The spy is **pull-only**: it does not vote, does not push beyond the minimum `ContactInfo` needed to remain in the table, runs as a single identity per capture at conservative rates, and logs enough to prove both. No eclipse, no Sybil, no spam, no impersonation. **This is not a new exploit**: we measure what the protocol already publishes to anyone who listens. Raw IP dumps stay in the research store; reporting is by aggregate. Full bind in `docs/ETHICS.md`, re-read before each live run.

## 5. Expected contribution

1. **A quantified anonymity decay curve** for Solana validators: *d* (and its stake-weighted form) as a function of passive observation time, from a vantage that contributes nothing to the network.
2. **A first stake-weighted IP-visibility table**, that is, what fraction of activated stake is a lookup rather than a secret, plus its AS and cloud concentration.
3. **A methodological result on vantage-point disagreement**: RPC view versus wire view, quantified and tracked over time rather than assumed away. This generalizes past Solana to any measurement that trusts a curated API as a proxy for the overlay.
4. **A reusable pull-only instrument** for a protocol with no shipped spy binary, plus the dated series that gossip itself does not retain.

This is a measurement, not a paper promise.

## 6. One ask

**Is a sustained pull-only gossip spy in scope before our next meeting, and at what duty cycle?** Concretely: continuous or near-continuous capture (versus the current bounded 120 s windows) is what turns this from a snapshot into a churn dataset, and it is the one methodological step where I want your ethics judgment rather than my own before I run it. If yes, I would also value a view on whether a second vantage point (a differently-located spy) is worth the added footprint for separating "short window" from "partial table" in the RPC/wire gap.

---

*Data: mainnet, 2026-08-22T00:27:05Z to 00:29:05Z, single 120 s pull-only gossip window, plus an RPC capture two minutes after it closed. All figures are observed, not extrapolated.*
