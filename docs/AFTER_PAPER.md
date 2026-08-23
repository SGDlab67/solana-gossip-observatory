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

**Permanent note (2026-08-22).**

Protocol layering as a measurement surface: what you can observe without being a validator is exactly what the protocol already broadcasts to anyone who listens. On Solana that is gossip `ContactInfo` (pull-only CRDS listen, no vote, no stake required) and public RPC (`getClusterNodes`, `getVoteAccounts`). NodeFinder's insight was that Ethereum's RLPx/DEVp2p discovery layer is a similarly public surface; the Solana equivalent is the gossip plane, not Turbine (data plane, downstream of leader selection) or Gulf Stream (transaction forwarding, requires being in the forwarding path). A measurement surface is defined by what a passive, unprivileged listener sees, not by what the protocol is "for."

P2P network health metrics NodeFinder used, and the Solana analogs actually instrumented in this repo:

| NodeFinder metric | Solana analog | Where measured here |
| --- | --- | --- |
| Peer count | Distinct identity pubkeys with `ContactInfo` on the wire, per tick | `spy/` (3,543 pubkeys, 120 s window, 2026-08-22) |
| Client mix (Geth/Parity) | Agave / Firedancer / Jito version census | `docs/analysis/client-mix-2026-08-22.md` |
| Churn | Node arrival/departure rate, identity persistence across repeated captures | Planned, not yet run (docs/ROADMAP.md Phase 2) |
| AS/geography concentration | IP to AS/cloud enrichment of gossip IPs | Planned, not yet run (docs/ROADMAP.md Phase 4) |
| Unreachable advertised addresses | Advertised `ContactInfo` sockets with no confirmed reachability, or RPC/wire view gap (RPC 3,712 nodes vs wire 3,543 pubkeys, same-day) | `docs/analysis/rpc-wire-gap-2026-08-22.md` |

The RPC/wire gap is the one metric this repo treats as a first-class finding rather than measurement noise: it is the Solana-specific version of NodeFinder's observation that the discovered overlay and the consensus-relevant set disagree.

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

**Date finished paper:** 2026-08-21 (per docs/ONE-PAGER.md date; paper reading preceded the first 1-pager draft).

**Q1. What would a Solana NodeFinder measure?**

Same three sub-claims the 1-pager (docs/ONE-PAGER.md, section 1) already commits to:

1. Speed and accuracy of identity-to-IP linking: how much of the validator set resolves to an advertised IP, as a function of how long a pull-only observer (`spy/`) listens. Message type: gossip `ContactInfo` (identity pubkey, gossip socket, TPU/TVU sockets, shred version, client version), harvested via CRDS pull and cross-checked against `getClusterNodes`.
2. Stake-weighted leak: what fraction of activated stake sits behind an IP the protocol already advertises, by joining gossip identities to `getVoteAccounts`.
3. AS and cloud concentration: how far those advertised IPs collapse into a small number of autonomous systems or hosting providers.

The identity that leaks is the pubkey to IP binding itself, published to anyone who listens, not extracted through any new exploit.

**Q2. Which Solana layers analogize to RLPx / DEVp2p / eth subprotocol?**

Per the methodology mapping (this file, section "Methodology mapping", and docs/ONE-PAGER.md section 3):

| NodeFinder (Ethereum) | Solana analog |
| --- | --- |
| RLPx discovery scan | Gossip CRDS pull (`spy/`), `getClusterNodes` (`rpcview/`) |
| DEVp2p HELLO harvest | Gossip `ContactInfo` |
| Ethereum STATUS (network / genesis) | Shred version |
| Client / version census (Geth / Parity) | Agave / Firedancer / Jito version census |
| Geography / AS + latency | IP to AS/cloud enrichment of gossip IPs |

Turbine and Gulf Stream are not part of this mapping: they are data-plane and transaction-forwarding paths downstream of gossip, not discovery or handshake layers, so they have no NodeFinder analog. QUIC is Solana's transport for TPU traffic, comparable to RLPx's transport role but not to RLPx's discovery function, which is the piece NodeFinder measured. Gossip is the layer that actually corresponds to what NodeFinder harvested.

**Primary operational mode chosen (RPC census / gossip spy / custom crawler):** Both, deliberately redundant, per docs/ONE-PAGER.md section 4: `rpcview/` (RPC census, operational since 2026-08-19) is the backstop series since gossip has no archive; `spy/` (custom pull-only CRDS listener, first successful wire capture 2026-08-22) is the closer NodeFinder analog. Per this file's section 4, RPC census is the same-day default for the 1-pager; the spy is stronger evidence layered on top, not a same-day requirement.
