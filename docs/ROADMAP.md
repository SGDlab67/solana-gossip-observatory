# Roadmap

Small phases. The next external artifact is a **1-pager for Dr. Ma by 2026-08-31**. This roadmap does not promise a paper.

## Phase 0 (now): RPC snapshot CLI

`s-nodefinder snapshot` against public RPC: `getClusterNodes` + `getVoteAccounts`. Write JSON under `snapshots/`. This is the census NodeFinder would have called "who is in the overlay right now," using Solana's already-public RPC instead of a discovery scan.

Done when: one command produces a dated dump you can open and count nodes, gossip IPs, and vote pubkeys.

## Phase 1 (after the paper): 1-pager + self-test

Finish IMC 2018. Same day, run [AFTER_PAPER.md](AFTER_PAPER.md): self-test answers, one permanent note, 1-pager skeleton, explicit choice of RPC vs spy vs crawler.

Done when: the 1-pager is sendable (question, motivation, related work, method, expected contribution, one ask) and the self-test is written down.

## Phase 2: gossip spy, longitudinal crawl (churn)

Pull-only, identified, tiny occupancy. Repeat ContactInfo harvest on a timer. Measure who appears, who leaves, how advertised IPs change.

Status (as of 2026-08-22): hand-built spy is running. Captures logged for 2026-08-21 and 2026-08-22. RPC-view crawl runs every 6 h via Hermes cron with 2 h watchdog. Prerequisite satisfied: the UDP spy speaks the current (4.2.x) protocol and is harvesting ContactInfo into the longitudinal series.

Done when: more than one dated gossip view exists and churn can be stated as a number (not a vibe). Ethics bind in [ETHICS.md](ETHICS.md) still holds.

## Phase 3: stake-weighted deanonymization table + AS enrichment

Join gossip/RPC IPs to vote accounts and stake. Enrich IPs with AS and cloud. Report fraction of stake that is IP-visible, and concentration in the top ASes.

Done when: one table suitable for the 1-pager or a follow-up email: stake share by AS/cloud, plus a caveat that this is public gossip, not a new exploit.

## Phase 4: client mix (Agave vs Firedancer vs Jito)

Version and client census from gossip, analogous to NodeFinder's Geth/Parity (and XOR-distance) client-friction finding. Look for systematic differences in advertised versions, ports, or reachability. Do not overfit a story until the counts exist.

Done when: a client-mix histogram over the same snapshots as Phase 2-3.

## Out of scope until someone asks

- A conference paper.
- A custom crawler that is not pull-only.
- Tor / IPFS / other anonymity systems (broader framing, not this repo's near term).
- Any method in the [ETHICS.md](ETHICS.md) "Not allowed" list.
