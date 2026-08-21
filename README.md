# Solana Gossip Observatory (S-NodeFinder)

NodeFinder-of-Solana instrument. Pull-only observation of Solana's gossip
protocol and periodic RPC snapshots, for the network measurement project under
Dr. Zane Ma (OSU, ASTRO Lab). See
`~/Github/personal-knowledge/solana-anonymity-research/` for the project plan
and `~/Note/Zero_Copy/Research/rust-solana-data-career/` for the career
strategy.

## Current state (2026-08-20)

- Day-0 baseline: RPC-view snapshots in `data/`, one per run via
  `scripts/snapshot.sh`. 3,798 cluster nodes, 3,771 unique gossip IPs, 291
  exposing RPC, 690 current validators. Version census: 4.2.1 (1,237), 4.2.0
  (1,057), 4.2.0-rc.1 (502), long tail back to 2.3.8 and 0.1105.40200.
- Wire-level gossip spy: installing `agave-gossip` (background). Once present,
  `agave-gossip spy` gives the protocol view. The crate-based instrument is the
  real target (see execution plan).

## Commands

```bash
./scripts/snapshot.sh [RPC_URL]   # RPC-view snapshot (getClusterNodes + getVoteAccounts + solana gossip)
```

## Data layout

`data/YYYY-MM-DD/` (UTC day), timestamped JSON per snapshot. Enrichment source
and vintage are recorded when enrichment is added; AS mappings drift.

## Notes

- Passive observation only. Ethics constraints from the execution plan apply:
  aggregates, never per-validator callouts.
- The clock is the dataset: gossip has no archive, so the crawl must not stop.
