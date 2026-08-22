# Stake-weighted identity-to-IP leak, 2026-08-22

## Summary

For both gossip capture windows on 2026-08-22, nearly all activated stake on
the cluster maps to a validator identity that already advertises a single
gossip IP on the wire. The stake-weighted identified fraction is:

- Window 1 (spy started 2026-08-22 00:27:05 UTC): **0.9842 (98.42%)**
- Window 2 (spy started 2026-08-22 21:30:16 UTC): **0.9961 (99.61%)**

This is a restatement of public gossip data, not a new exploit. Validator
identities and their advertised gossip endpoints are broadcast by design so
that peers can reach each other. What this note quantifies is how much of the
economic weight of the cluster is trivially attributable to a single network
address at capture time.

## Method

The leak metric joins two independent observations for a single day:

1. **Gossip observation (the wire).** Each spy capture is a 120-second listen
   on the gossip network, deduplicated to one ContactInfo record per node
   identity (`pubkey`). Each record carries the advertised `gossip` endpoint as
   `IP:port`. We reduce the endpoint to its host (IP) and group by identity.
2. **Stake observation (RPC).** The `getVoteAccounts` RPC snapshot lists every
   vote account with its `nodePubkey` (the validator identity) and
   `activatedStake` in lamports. We sum `activatedStake` per `nodePubkey`
   across both `current` and `delinquent` sets, so a node with more than one
   vote account is counted once with its combined stake.

We then join the two on validator identity. A staked identity is counted as
"identified" when it appears in the gossip capture with exactly one advertised,
non-loopback IP. Loopback (127.0.0.0/8, ::1) is excluded from the advertised-IP
count because it does not identify a reachable host.

```
stake_weighted_identified_fraction
  = sum(activatedStake of identities seen in gossip with a single advertised IP)
  / sum(activatedStake of all vote-account identities)
```

Window-to-snapshot pairing:

- Window 1: `spy-2026-08-22-002705.jsonl` joined to
  `vote-accounts-20260822T003052Z.json` (RPC taken 00:30:52 UTC, roughly 4
  minutes after the capture).
- Window 2: `spy-2026-08-22-213016.jsonl` joined to
  `vote-accounts-20260822T184443Z.json` (RPC taken 18:44:43 UTC, roughly 2.75
  hours before the capture). This is the closest vote-accounts snapshot
  available for the day; see caveats.

Both `getVoteAccounts` snapshots report the same total activated stake
(433,485,334,041,286,798 lamports, about 433,485,334 SOL) because
`activatedStake` is fixed within an epoch and both snapshots fall in the same
epoch.

## Join counts at each step

### Window 1 (00:27 capture, 00:30 vote snapshot)

| Step | Count |
| --- | --- |
| Gossip: unique node identities in capture | 3,543 |
| Vote accounts: current | 682 |
| Vote accounts: delinquent | 12 |
| Vote accounts: unique node identities | 694 |
| Identities matched (staked and seen in gossip) | 678 |
| of which single advertised IP | 678 |
| of which multiple advertised IPs | 0 |
| of which loopback only | 0 |
| Staked identities NOT seen in gossip | 16 |

Total activated stake: 433,485,334,041,286,798 lamports (about 433,485,334 SOL).
Identified stake: 426,637,595,719,486,208 lamports (about 426,637,596 SOL).
Unmatched stake (16 identities not in this capture): about 6,847,738 SOL.

**stake_weighted_identified_fraction = 0.984203 (98.42%)**

### Window 2 (21:30 capture, 18:44 vote snapshot)

| Step | Count |
| --- | --- |
| Gossip: unique node identities in capture | 3,592 |
| Vote accounts: current | 686 |
| Vote accounts: delinquent | 8 |
| Vote accounts: unique node identities | 694 |
| Identities matched (staked and seen in gossip) | 682 |
| of which single advertised IP | 682 |
| of which multiple advertised IPs | 0 |
| of which loopback only | 0 |
| Staked identities NOT seen in gossip | 12 |

Total activated stake: 433,485,334,041,286,798 lamports (about 433,485,334 SOL).
Identified stake: 431,774,683,619,728,625 lamports (about 431,774,684 SOL).
Unmatched stake (12 identities not in this capture): about 1,710,650 SOL.

**stake_weighted_identified_fraction = 0.996054 (99.61%)**

## Largest staked validators and IP visibility

The top staked identities of the day, with the gossip IP each advertised in
each window. Every one of the top 15 was IP-visible in both windows. Stake is
shown in SOL, rounded.

| Rank | Node identity (nodePubkey) | Stake (SOL) | Window 1 gossip IP | Window 2 gossip IP |
| --- | --- | --- | --- | --- |
| 1 | Fd7btgySsrjuo25CJCj7oE7VPMyezDhnx7pZkj2v69Nk | 17,066,372 | 141.95.45.24 | 141.95.45.24 |
| 2 | HEL1USMZKAL2odpNBj2oCjffnFGaYwmbGmyewGv1e2TU | 16,054,078 | 64.130.57.134 | 64.130.57.134 |
| 3 | DRpbCBMxVnDK7maPM5tGv6MvB3v1sRMC86PZ8okm21hy | 12,175,413 | 67.202.63.79 | 67.202.63.79 |
| 4 | JUPiTERrZqgf1jUyR7dSkhMx4Kn2qJyekWsg3LT1h4b | 11,782,032 | 88.216.36.133 | 88.216.36.133 |
| 5 | C8Bey3LKVJHVqN6xPTeW8WJfUgFQAeGNBpT4Rp99JP1k | 9,178,661 | 189.1.171.13 | 189.1.171.13 |
| 6 | CAo1dCGYrB6NhHh5xb1cGjUiu86iyCfMTENxgHumSve4 | 8,917,577 | 67.208.234.129 | 67.208.234.129 |
| 7 | E1r4Psq84tHfQ6aPTvvDka4U3u8zPVD7gEUrH25RdxHL | 8,402,660 | 64.130.32.153 | 64.130.32.153 |
| 8 | EvnRmnMrd69kFdbLMxWkTn1icZ7DCceRhvmb2SJXqDo4 | 7,964,352 | 198.13.140.73 | 198.13.140.73 |
| 9 | 9eGrDohdNTAo61DRHyfMuqKWXqYnA3i254Wiszxe8FoY | 7,357,821 | 86.54.152.249 | 86.54.152.246 |
| 10 | Awes4Tr6TX8JDzEhCZY2QVNimT6iD1zWHzf1vNyGvpLM | 6,547,243 | 94.158.242.125 | 94.158.242.125 |
| 11 | 9jxgosAfHgHzwnxsHw4RAZYaLVokMbnYtmiZBreynGFP | 6,122,617 | 64.130.42.146 | 64.130.42.146 |
| 12 | JD549HsbJHeEKKUrKgg4Fj2iyv2RGjsV7NTZjZUrHybB | 6,003,737 | 86.54.153.246 | 86.54.153.246 |
| 13 | 5pPRHniefFjkiaArbGX3Y8NUysJmQ9tMZg3FrFGwHzSm | 5,958,065 | 188.42.129.244 | 188.42.129.244 |
| 14 | 5Cchr1XGEg7dbBXByV5NY2ad8jfxAM7HA3x8D56rq9Ux | 5,773,480 | 52.27.227.28 | 52.27.227.28 |
| 15 | 9rkJMARqK6VBkcxGfKBAwnA44gPAfGxPbPsfsggFNDSQ | 4,663,306 | 152.236.11.65 | 152.236.11.65 |

Note that rank 9 advertised a slightly different address between the two
windows (86.54.152.249 in window 1, .246 in window 2). It still resolved to a
single IP within each window, so it counts as identified in both. This is a
normal endpoint change across a roughly 21-hour gap, not a multi-homed
advertisement.

## Caveats

- **This is public gossip data, not an exploit.** Solana gossip broadcasts
  ContactInfo (identity plus advertised endpoints) so that nodes can peer.
  Anyone running a spy can observe it. Vote-account stake is equally public via
  RPC. This note only measures how much stake is easily attributable to an IP
  at capture time; it does not defeat any access control.
- **RPC snapshot timing.** The stake snapshot and the gossip capture are not
  taken at the same instant. Window 1's snapshot is about 4 minutes after the
  capture, which is tight. Window 2's snapshot is about 2.75 hours before the
  capture, the closest one available for the day, so a validator that changed
  identity or churned in that gap could be mis-joined. Because `activatedStake`
  is fixed within an epoch, the timing gap affects membership matching, not the
  stake amounts.
- **Vote accounts are not the full node population.** The gossip captures see
  around 3,543 and 3,592 total identities, while only 694 carry stake through a
  vote account. The denominator here is deliberately the staked population,
  because the question is about stake-weighted attributability. Non-voting RPC
  nodes, unstaked spies, and other participants are out of scope for the
  fraction.
- **Single advertised IP is an at-capture property.** An identity that
  advertised one IP in this 120-second window could rotate it later, sit behind
  a proxy, or run split TPU and TVU on separate hosts. We only assert that
  within the window the gossip `gossip` endpoint resolved to one host. We did
  not attempt to confirm reachability or ownership of that host.
- **Unmatched staked identities.** 16 identities in window 1 and 12 in window 2
  carried stake but were not observed in that capture. Their stake is treated
  as not identified, which makes the fraction a lower bound with respect to
  capture completeness: a longer listen might have observed some of them and
  raised the fraction. The largest single unmatched identity in window 1
  advertised no gossip record in that 120-second window despite about 2.9M SOL
  of stake, likely a capture-window miss rather than a validator that hides.

## Reproduction

The numbers above were produced by joining the raw files in
`data/2026-08-22/` with a plain Python script (identity join on `pubkey` to
`nodePubkey`, stake summed from `getVoteAccounts`). No counts were estimated;
every figure comes from a direct pass over the JSONL and JSON files.
