# S-NodeFinder: Measuring the Degree of Anonymity of Solana Validators at the Gossip Layer

**Prepared for:** Dr. Zane Ma, ASTRO Lab, Oregon State University
**Prepared by:** Stephen Le
**Date:** 2026-08-26 (draft; final date at send)
**Repository:** solana-gossip-observatory

## 1. Research question

What is the degree of anonymity of a Solana validator at the gossip layer, and how quickly does that anonymity decay under passive observation?

Three measurable sub-questions follow. First, linking speed and accuracy: how much of the validator set resolves to an advertised IP, as a function of how long a pull-only observer listens. Second, stake-weighted exposure: what fraction of activated stake sits behind an IP the protocol already advertises. Third, concentration: how far those advertised IPs collapse into a small number of autonomous systems or hosting providers. The third sub-question is planned work; the first two are instrumented and producing data.

## 2. Motivation

Solana's gossip layer is not designed to hide operators. Every participating node advertises a ContactInfo record: identity pubkey, gossip socket, TPU/TVU sockets, shred version, and client version. Public RPC re-exports much of the same through getClusterNodes. The interesting question is therefore not whether identity leaks, but how completely, how quickly, and how much economic weight sits behind the leak. A validator whose IP is a 120-second lookup has a different threat surface, such as targeted denial of service, than one that requires an active crawl.

Measured on mainnet in a single 120-second pull-only gossip window (2026-08-22T00:27:05Z to 00:29:05Z):

| Observation | Value |
| --- | ---: |
| Distinct identity pubkeys with a ContactInfo on the wire | 3,543 |
| of which advertised a TVU (shred-receiving) socket, final tick | 3,452 |
| CRDS peer table at each of four 30-second ticks | 1,540 / 2,642 / 3,321 / 3,543 |
| RPC view at 00:30:52Z: cluster nodes | 3,712 |
| RPC view at 00:30:52Z: unique gossip IPs | 3,685 |

Two minutes of passive listening recovered roughly 95 percent of the node count the cluster's own RPC advertised two minutes later, from a listener that contributes nothing to the mesh. Both counts are one entry per identity pubkey, so they are directly comparable; neither is ground truth. The 3,452 figure is the shred-receiving node population, not the staked validator set: the same-day RPC capture shows 682 current vote accounts.

The gap between views is itself a finding. The RPC view (3,712 nodes, 3,685 unique gossip IPs) exceeds the wire view (3,543 pubkeys) by 169 nodes, roughly 4.6 percent. That delta is what the cluster advertises through a curated endpoint but the mesh did not show a single observer in 120 seconds. Three candidate explanations remain to be separated by the longitudinal series: the window was too short, since the curve had not flattened (+222 on the final tick); CRDS propagation and pruning give any single vantage point a partial table; or the RPC endpoint's view is stale. NodeFinder reported the same class of disagreement on Ethereum. We treat cross-view disagreement as a signal about observability, not as noise to be averaged away.

## 3. Related work

Kim, Ma, Murali, Mason, Miller, Bailey. Measuring Ethereum Network Peers. IMC 2018. NodeFinder harvested Ethereum's overlay via RLPx discovery and DEVp2p HELLO/STATUS, reporting peer counts, client mix, and AS and geography concentration. It also showed that the discovered overlay is far larger and messier than the consensus-relevant set. The mapping does not port directly: Ethereum's Kademlia-style discovery lets a crawler walk the ID space, whereas Solana's CRDS is a push/pull anti-entropy table, so coverage is a function of dwell time and peer selection, not scan breadth.

| NodeFinder (Ethereum) | S-NodeFinder (Solana) |
| --- | --- |
| RLPx discovery scan | Gossip CRDS pull (spy), getClusterNodes (rpcview) |
| DEVp2p HELLO harvest | Gossip ContactInfo |
| STATUS (network, genesis) | Shred version |
| Geth/Parity client census | Agave/Firedancer/Jito version census |
| Geography and AS | IP to AS/cloud enrichment of gossip IPs |

Kiffer et al. Multiple Sides of 36 Coins. ACM SIGMETRICS 2026. Reports a Solana node population of roughly 3,693 from an API-level vantage, which falls between our wire view (3,543) and our same-window RPC view (3,712), an independently collected anchor for the order of magnitude. Its contribution is breadth across chains at an API vantage; ours is depth at one chain's wire vantage, with the API/wire delta as the object of study.

Diaz et al. Towards Measuring Anonymity. PET 2002. We adopt the normalized degree of anonymity, d = H/Hmax, where H is the entropy of the adversary's posterior over which node in a candidate set N corresponds to a given validator identity, and Hmax = log N is the entropy of a uniform posterior. This makes anonymity a number rather than an adjective. We have not yet computed d. What rpcview emits today is the stake-weighted identified fraction: the share of activated stake whose identity already resolves to a single advertised IP, the d = 0 endpoint. Choosing the candidate set for identities not at that endpoint, and estimating the posterior over it, is unfinished work, stated here as such rather than claimed.

## 4. Method

Two instruments, deliberately redundant. rpcview (operational since 2026-08-19) is a typed Rust CLI over public RPC getClusterNodes and getVoteAccounts, producing dated JSON snapshots on a fixed schedule. It is the backstop series: gossip has no archive, so the clock is the dataset. spy (first successful wire capture 2026-08-22) is a hand-built pull-only CRDS listener against the current Agave 4.2.x protocol, emitting one JSONL row per observed ContactInfo plus a per-tick summary. A custom crate was not a preference: of the releases we checked, the Agave 4.x and 2.x bundles ship no gossip binary at all (4.x gossip is library-only), and the one binary that exists, solana 1.18.26, announces gossip port 0 against the 4.2.x mesh and stays at zero nodes.

Analysis pipeline: join gossip identities to vote accounts for stake-weighted exposure; enrich IPs to AS and cloud offline, recording source and vintage because AS mappings drift; compute d and its stake-weighted variant per snapshot; and diff the RPC view against the wire view each run, reporting the delta as a first-class metric.

Longitudinal plan: both captures repeat on a fixed six-hour schedule with automated monitoring and weekly rollups, measuring node arrival and departure rates, identity persistence, IP re-advertisement and migration, and whether the RPC/wire gap is a constant offset or a time-varying artifact. Longer windows will allow a saturation fit and a time-to-coverage figure rather than a single-window count. The series currently spans 2026-08-21 through 2026-08-26 and runs unattended.

Ethics: public gossip and public RPC data only. The spy is pull-only: it does not vote, does not push beyond the minimum ContactInfo needed to remain in the table, runs under one persistent, identifiable identity across all captures so operators can recognize and filter the measurement node, at conservative rates, and logs enough to prove both. No eclipse, no Sybil, no spam, no impersonation. This is not a new exploit: we measure what the protocol already publishes to anyone who listens. Raw IP dumps stay in the research store; reporting is by aggregate. The full bind is in the repository ethics document and is re-read before each live run.

## 5. Expected contribution

1. A quantified anonymity decay curve for Solana validators: d and its stake-weighted form as a function of passive observation time, from a vantage that contributes nothing to the network.
2. A first stake-weighted IP-visibility table: what fraction of activated stake is a lookup rather than a secret. AS and cloud concentration enrichment is planned follow-on work, explicitly not yet measured, and will be added to this table when the data exists.
3. A methodological result on vantage-point disagreement: the RPC view versus the wire view, quantified and tracked over time rather than assumed away. This generalizes past Solana to any measurement that trusts a curated API as a proxy for the overlay.
4. A reusable pull-only instrument for a protocol with no shipped spy binary, plus the dated series that gossip itself does not retain.

This document reports measured results and clearly marked planned work. It is a measurement, not a paper promise.

## 6. One ask

The one decision I need from you: is a sustained pull-only gossip spy in scope before our next meeting, and at what duty cycle? Concretely, continuous or near-continuous capture, as opposed to the current bounded 120-second windows, is what turns this from a snapshot into a churn dataset. It is the one methodological step where I want your ethics judgment rather than my own before I run it. If sustained capture is in scope, I would also value your view on whether a second vantage point, a differently located spy, is worth the added footprint for separating a short window from a partial table in the RPC/wire gap.

---

*Data: mainnet, 2026-08-22T00:27:05Z to 00:29:05Z, single 120-second pull-only gossip window, plus an RPC capture two minutes after it closed. All figures are observed, not extrapolated.*
