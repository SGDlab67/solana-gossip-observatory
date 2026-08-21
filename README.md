# S-NodeFinder

S-NodeFinder measures Solana's gossip-layer identity→IP leak the way NodeFinder
measured Ethereum's P2P network.

## What this is

A read-only measurement project. It observes Solana's public peer surface (RPC
cluster lists and a pull-only gossip spy) so we can say how easily validator
identity maps to IP, how that leak is weighted by stake, and how far it
concentrates by AS or cloud provider.

## What this is not

- Not a validator.
- Not an attack tool.
- Not a gossip spammer.
- Not an eclipse, Sybil, or vote client.

See [docs/ETHICS.md](docs/ETHICS.md) for the operational rules.

## Research question

What is the degree of anonymity of Solana validators at the gossip layer?

That splits into three measurable claims:

1. **Speed and accuracy** of validator↔IP linking from public gossip and RPC.
2. **Stake-weighted leak**: how much stake sits behind IPs that gossip already publishes.
3. **AS and cloud concentration**: whether those IPs cluster in a few providers.

Solana is the case study. The broader framing, from Dr. Zane Ma (OSU ASTRO Lab,
in-person discussion around 2026-08-18), is measuring degrees of anonymity
across systems (IP, Tor, blockchain, IPFS). Work independently, email questions
as they come, meet about monthly. The next external artifact is a 1-pager for
Dr. Ma by 2026-08-31, not a paper.

## Two instruments, two views

The project deliberately runs two observers, because the gap between them is
itself a result.

| | `rpcview/` | `spy/` |
|---|---|---|
| View | RPC (`getClusterNodes`, `getVoteAccounts`) | gossip wire (CRDS table) |
| Source | an endpoint someone else curates | the mesh itself |
| Status | working since 2026-08-19 | built 2026-08-20, smoke test pending |
| Cost | free, runs anywhere | must speak the current protocol |

`rpcview` is the backstop series: it costs nothing and must not stop, because
gossip has no archive and the clock is the dataset. `spy` is the real
instrument. `scripts/snapshot.sh` is the shell equivalent of `rpcview` kept for
one-off captures that also grab `solana gossip` output.

## Current status

**RPC view (2026-08-19T21:26:51Z, live mainnet):** 3,771 cluster nodes, 3,743
unique gossip IPs, 290 exposing RPC, 688 current validators (8 delinquent).
687/688 current identities appear in `getClusterNodes` with a gossip address,
carrying 99.95% of current activated stake. Read that as the protocol already
publishing ContactInfo through this RPC, not as a newly discovered mapping.

**Day-0 baseline (2026-08-20):** 3,798 cluster nodes, 3,771 unique gossip IPs,
291 exposing RPC, 690 current validators. Version census: 4.2.1 (1,237), 4.2.0
(1,057), 4.2.0-rc.1 (502), long tail back to 2.3.8 and 0.1105.40200. Counts
churn between runs; view disagreement across observers is a finding, not noise.

**Wire view:** the day-0 spy attempt established that mainnet is a 4.2.x-only
mesh and that no shipped binary can join it (agave 4.x gossip is library-only;
the 1.18 `solana-gossip` binary announces gossip port 0 and stays at Nodes: 0).
The hand-built crate spy is therefore the only path, not a preference. Full
trail in [NOTES.md](NOTES.md).

## How to run

```bash
# RPC view, typed CLI
cd rpcview && cargo run -- snapshot --out ../snapshots/latest.json

# RPC view, shell one-off (also captures `solana gossip`)
./scripts/snapshot.sh [RPC_URL]

# Wire view, bounded smoke test
cd spy && cargo run --release -- --seconds 120
```

Dumps land under `snapshots/` and `data/YYYY-MM-DD/` (UTC day), both
gitignored. Treat them as research data, not as a list to republish. Enrichment
source and vintage get recorded when AS enrichment lands, because AS mappings
drift.

## Related work

Kim, Ma, Murali, Mason, Miller, Bailey. Measuring Ethereum Network Peers. IMC
2018. https://doi.org/10.1145/3278532.3278542

PDF: https://faculty.cc.gatech.edu/~mbailey/publications/imc18_ethereum.pdf

## Docs

- [Ethics](docs/ETHICS.md)
- [After the paper](docs/AFTER_PAPER.md)
- [Roadmap](docs/ROADMAP.md)
- [Worklog](NOTES.md)
