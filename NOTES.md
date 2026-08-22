# Day 0 — 2026-08-20 (UTC data dir: 2026-08-21)

## RPC-view baseline (done)

`scripts/snapshot.sh` captures getClusterNodes + getVoteAccounts + `solana
gossip` JSON per run, timestamped under `data/UTC-day/`.

First snapshot numbers:
- cluster nodes (getClusterNodes): 3,798
- unique gossip IPs: 3,771
- nodes exposing RPC: 291
- validators: 690 current, 6 delinquent
- version census top: 4.2.1 (1,237), 4.2.0 (1,057), 4.2.0-rc.1 (502), 4.1.2
  (249), long tail to 2.3.8 (191) and 0.1105.40200 (100)

Cross-validation anchors: SIGMETRICS 2026 ~3,693 (API view), PoC 2026-08-18
~3,830, this baseline 3,798. View disagreement is itself a result.

## Wire-level spy attempt (finding, not failure)

Goal: one real gossip-layer count. Paths tried and closed:

1. `cargo install agave-gossip` (crates.io) -> stub package printing "Hello,
   world!". The name is not the real tool.
2. agave release bundles: v4.2.1, v2.2.3, v2.1.0, v2.0.14 do NOT ship a gossip
   binary. Agave 4.x gossip is library-only (no bin target).
3. solana 1.18.26 bundle: ships `solana-gossip` binary. Ran `spy` against
   entrypoint.mainnet-beta.solana.com:8001 for 120 s. IP echo works (public IP
   resolved), but the client announces Gossip Address with port 0 and never
   establishes a pull: table stays at Nodes: 0 for the whole window.

Conclusion: the mainnet mesh is 4.2.x-only; a 1.18 client cannot join. The
research instrument must speak the current protocol. The execution plan's
choice (solana-gossip crate at the current release, hand-built spy) is not a
preference, it is the only available path. Binary-shortcut routes are closed.

## Next

- Build the minimal crate-based spy (agave v4.2.1 solana-gossip): announce a
  valid ContactInfo (proper gossip port, current shred version), pull loop,
  CRDS ContactInfo records to Parquet/JSON.
- Keep snapshot.sh running on a schedule (cronjob or launchd): the RPC-view
  series is the backstop dataset and costs nothing.
