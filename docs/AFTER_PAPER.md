# After the paper

Same-day plan for when the IMC 2018 paper is finished. Execute this checklist the day reading ends. Do not skip to a live gossip spy until items 1-4 are done.

Paper: Kim, Ma, Murali, Mason, Miller, Bailey. Measuring Ethereum Network Peers. IMC 2018. https://doi.org/10.1145/3278532.3278542

PDF: https://faculty.cc.gatech.edu/~mbailey/publications/imc18_ethereum.pdf

Working arrangement (Dr. Zane Ma, OSU ASTRO Lab, in-person around 2026-08-18): work independently, email questions as they come, meet about monthly. Bring results, not just questions. This is not private gossip. The 1-pager is due 2026-08-31.

## Same-day checklist

### 1. Self-test (write answers before any new crawl)

Paste answers into this file (section at the bottom) or a dated note in this repo. Do not leave them in chat.

**Q1.** What would a Solana NodeFinder measure?

**Q2.** Which Solana layers (Turbine, Gulf Stream, QUIC, gossip) are analogous to RLPx / DEVp2p / eth subprotocol?

Aim for specific, falsifiable answers. "The P2P network" is not an answer. Name the message types and the identity that leaks (pubkey, IP, shred version, client).

### 2. One permanent note

Write one note that you would still want in six months:

- Protocol layering as a **measurement surface** (what you can observe without being a validator).
- P2P **network health** metrics that NodeFinder used and the Solana analogs (peer count, client mix, churn, AS concentration, unreachable advertised addresses).

Keep it short. This is the note the 1-pager draws from.

### 3. 1-pager skeleton for Dr. Ma (due 2026-08-31)

Fill this outline the same day. One page. Results can be thin; the question and method cannot.

| Section | What to put |
| --- | --- |
| Research question | Degree of anonymity: speed/accuracy of validator↔IP linking, stake-weighted leak, AS/cloud concentration. |
| Motivation | Gossip already advertises ContactInfo. RPC `getClusterNodes` already lists IPs. How much of the validator set is a lookup, not a secret. |
| Related work | This paper (NodeFinder / Measuring Ethereum Network Peers, IMC 2018). One sentence on what they measured and what we cannot copy blindly (RLPx discovery vs Solana gossip). |
| Proposed method | Phase 0 RPC census now. Later: pull-only gossip spy, stake join, AS enrichment. State ethics constraints in one line. |
| Expected contribution | A measurement, not a paper promise: a first table of how much stake is IP-visible from public interfaces, plus a plan for churn. |
| One ask | What Dr. Ma should decide or provide (RPC credits, whether a spy is in scope before the next meeting, meeting date). |

### 4. Confirm what "NodeFinder" means here

There is **no canonical Solana NodeFinder repo**. The name is the research analog, not a port of their crawler.

Operational choices, pick and write down one primary:

| Mode | What it is | What it is good for | What it is not |
| --- | --- | --- | --- |
| RPC census | `getClusterNodes` + `getVoteAccounts`, or `solana gossip` | Fast, public, enough for a first 1-pager table | Not a gossip-plane crawl. Misses nodes that never hit that RPC's view. No churn unless you repeat it. |
| `solana-gossip spy` | Separate Agave binary: UDP pull-only gossip listener (`solana-gossip spy --entrypoint ...`) | Closer to NodeFinder's overlay harvest (ContactInfo) | Not installed here yet (Agave CLI 3.1.10 is; `solana-gossip` is not on PATH). Must stay pull-only, identified, tiny occupancy. |
| Custom crawler | Own gossip/CRDS client | Full control of pull rate, logging, ethics bind | Highest risk of accidental spam. Last resort. |

Do not confuse `solana gossip` (JSON-RPC list) with `solana-gossip spy` (UDP). The former is Phase 0. The latter is Phase 2, after installing the binary or implementing an in-process pull-only listener.

For the 1-pager, **RPC census is the default**. Gossip spy is stronger evidence, not the same-day default.

### 5. Only then: live gossip spy and stake→IP table

After 1-4 exist:

- Re-read [ETHICS.md](ETHICS.md).
- One identified, pull-only spy, or repeated RPC snapshots if the spy is not ready.
- Join vote accounts to gossip IPs. Produce a stake-weighted leak table for the 1-pager if time allows.
- Do not block the 1-pager on a perfect spy. A dated RPC snapshot plus a method section is enough to send.

## Methodology mapping

NodeFinder Ethereum → Solana analog.

| NodeFinder (Ethereum) | Solana analog |
| --- | --- |
| RLPx discovery scan | Gossip crawl (`solana-gossip spy`, `getClusterNodes`) |
| DEVp2p HELLO harvest | Gossip ContactInfo |
| Ethereum STATUS (network / genesis) | Shred version / feature set |
| Client / version census | Agave vs Firedancer vs Jito |
| Geography / AS + latency | IP→AS/cloud enrichment of gossip IPs |

Use this table in the 1-pager related-work paragraph so the mapping is explicit, not implied.

## Working arrangement (reminder)

- Email questions when they appear. Do not save a month of confusion for the meeting.
- ~Monthly meetings. Bring a snapshot, a table, or a written 1-pager draft, not only a list of questions.
- Independent: Dr. Ma assigned the direction. Execution and first numbers are on this repo.

## Self-test answers (fill after reading)

**Date finished paper:**

**Q1. What would a Solana NodeFinder measure?**

_(paste here)_

**Q2. Which Solana layers analogize to RLPx / DEVp2p / eth subprotocol?**

_(paste here)_

**Primary operational mode chosen (RPC census / gossip spy / custom crawler):**

_(paste here)_
