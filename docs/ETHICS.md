# Ethics

S-NodeFinder is benign measurement of a public peer-to-peer network. The bar is the same spirit as NodeFinder (Kim, Ma et al., IMC 2018): Menlo Report principles, public data, minimal footprint, no abuse of the system under study.

This is not a pentest of validators. It is not a deanonymization-for-harm project. Snapshots exist so we can measure how much identity the protocol already leaks.

## Principles

- **Beneficence / non-maleficence.** Collect only what is needed to answer the research question. Do not degrade cluster liveness, leader schedules, or other operators' machines.
- **Respect for persons.** Validator pubkeys and gossip IPs are already public on the wire. Do not treat operators as targets. Do not contact them with "we found your IP" unless Dr. Ma agrees that disclosure is warranted.
- **Justice.** Do not single out a small operator for extra probing. Census the public set. Report aggregates (stake-weighted leak, AS concentration) before naming hosts.
- **Respect for law and public interest.** Stay inside documented RPC and gossip-spy interfaces. No exploits, no credential use, no access to private RPC.

## Allowed

- Public RPC methods that the cluster already exposes, including `getClusterNodes` and `getVoteAccounts`.
- Documented gossip-spy / pull-only participation (`solana-gossip spy` or an equivalent pull-only listener), if and when that phase starts.
- Offline enrichment of IPs already present in those public dumps (AS, cloud, geo), using public datasets.

## Not allowed

- Eclipse attacks, or any attempt to isolate a validator from honest peers.
- Sybil identity flooding (many gossip identities to occupy tables or crowd out peers).
- Voting, stake, or any consensus participation.
- Gossip spam, shred spam, or inflated pull/push rates.
- Connecting in a way that impersonates a validator or advertises false ContactInfo at scale.
- Republishing raw IP lists casually (blog posts, public gists, unreviewed appendices). Dumps stay in the research store.

## Snapshot handling

RPC and gossip dumps may contain public pubkeys and IPs that gossip already publishes. That does not make the dump a press release.

- Store snapshots as research data.
- Prefer aggregates in notes and in the 1-pager (counts, stake fractions, AS rankings).
- If an example row is needed, use a well-known public RPC node or a self-owned address, not a random validator IP.
- Do not commit large IP dumps to a public remote without an explicit decision.

## If a gossip spy is added later

When (not before) a live spy is justified:

1. Bind **pull-only**. Never vote. Never push ContactInfo except the minimum the client requires to stay in the table, if any.
2. **Identify** the measurement node (user-agent / gossip client string, or a documented pubkey) so operators can filter it.
3. Keep **occupancy tiny**: one spy process, one identity, conservative peer and CRDS pull rates.
4. Log enough to prove the spy did not vote and did not spam.
5. Re-read this file before first live run. If the client cannot be constrained to pull-only, do not run it.

## When in doubt

Do not run it. Email Dr. Ma with the proposed method and the expected load. Independent work does not mean silent aggressive measurement.
