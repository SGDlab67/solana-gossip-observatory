# Degree of anonymity (Diaz 2002) over gossip, 2026-08-22

## What this is

A scaffold that instantiates the Diaz et al. degree of anonymity `d` for the
two 2026-08-22 gossip captures. Code lives in `analysis/d-anonymity/`. Run it
with:

```
python3 analysis/d-anonymity/d_anonymity.py
```

Reference: C. Diaz, S. Seys, J. Claessens, B. Preneel, "Towards Measuring
Anonymity", PET 2002. The metric is `d = H(X) / H_M`, where `H(X)` is the
Shannon entropy of the attacker's probability distribution over the candidate
set and `H_M = log2(N)` is the maximum entropy (a uniform distribution over
`N` candidates). `d = 1` means the attacker learned nothing; `d = 0` means the
attacker pinned the target exactly.

This is a scaffold, not a verdict. The point is to have an honest, runnable
`d` computation with the design choices written down, so later work can swap
the adversary model or the candidate set without re-deriving the plumbing.

## The scenario we instantiate

The Diaz model needs a target, an attacker, and a probability distribution
over candidates. We pick a concrete deanonymization scenario:

- Target: an observed gossip node.
- Attacker: someone running a spy who sees the IP a target advertises and
  wants to know which validator identity is behind that IP.
- Candidate set: the identities observed in the window.
- Anonymity set of a target `t`: the set of observed identities that advertise
  the same routable gossip IP as `t`. Inside that set the attacker is taken to
  be uniform, so the per-target entropy is `H_t = log2(|A(t)|)` and the
  per-target degree is `d_t = H_t / log2(N)`.

Two system-level numbers are reported:

- `d (unweighted)`: the mean of `d_t` over scored identities.
- `d (stake-weighted)`: the stake-weighted mean of `d_t` over the identities
  that carry activated stake, weight equal to each identity's `activatedStake`
  share. This answers "how anonymous is a unit of stake" rather than "how
  anonymous is a node".

Loopback (`127.0.0.0/8`, `::1`) is treated as not routable and excluded from
scoring, matching the convention in `stake-weighted-leak-2026-08-22.md`.

## Choosing N is research design, not settled

This is the honest core of the scaffold. `d` scales with `1 / log2(N)`, so the
candidate set size sets the ceiling. Changing `N` rescales the numbers but does
not change the ordering between windows or between nodes. There is no single
correct `N`; the script exposes three modes via `--candidate-set`:

- `observed` (default): `N` = unique identities advertising a routable IP in
  the window. Reading: the anonymity set is exactly the population the spy
  actually saw on the wire.
- `all_ids`: `N` = every identity in the capture, loopback and missing
  endpoints included. Slightly larger `N`, marginally lower `d`.
- `routable_ips`: `N` = count of distinct routable IPs. A host-centric view
  rather than an identity-centric one.

Other candidate sets are defensible and deliberately not hard-coded: the full
staked population (694 identities via `getVoteAccounts`), the RPC-visible set
from `cluster-nodes`, or the theoretical validator universe. Each answers a
different question. We default to `observed` because the attacker in the
scenario only knows what the spy captured, so the observed population is the
honest denominator for that attacker.

## Results (as computed, do not round away the point)

Default candidate set (`observed`).

| Window | N | H_max (bits) | d (unweighted) | d (stake-weighted) | IPs with >1 identity |
| --- | --- | --- | --- | --- | --- |
| W1 2026-08-22 00:27:05 UTC | 3542 | 11.7903 | 0.001688 | 0.000000 | 11 (36 identities) |
| W2 2026-08-22 21:30:16 UTC | 3591 | 11.8102 | 0.001869 | 0.000243 | 14 (43 identities) |

Reading of the numbers:

- `d` is essentially zero in both windows. That is the expected, honest
  result: Solana gossip is engineered so that each identity advertises a
  reachable endpoint, so about 98.9% of identities in W1 and 98.8% in W2 sit
  alone on their IP and are fully deanonymized (`d_t = 0`).
- The tiny residual comes entirely from the handful of IPs that host more than
  one identity in a window (11 IPs in W1, 14 in W2). The largest, 45.250.25.158,
  carries 9 identities in both windows, an operator co-locating nodes rather
  than a privacy mechanism.
- The stake-weighted `d` is 0.000000 in W1 and 0.000243 in W2. The difference
  is real, not noise: in W1 none of the scored shared-IP identities carried
  stake, while in W2 at least one staked identity sat on a shared IP, lifting
  the weighted mean off zero. This is a genuine capture-to-capture difference,
  not fabricated.

## Honest limitations

- `d` near zero here is a restatement of public gossip data, not an exploit.
  ContactInfo is broadcast by design; a near-zero `d` confirms the protocol is
  non-anonymous, it does not defeat access control. See `../ETHICS.md`.
- The adversary model is deliberately weak: uniform within a shared IP, no
  correlation across TPU / TVU / RPC ports, no cross-window linkage, no ASN or
  ownership enrichment. A stronger adversary can only lower `d`, never raise
  it, so the reported figures are an upper bound on anonymity under this
  scenario.
- Single 120-second window. A longer listen could merge or split anonymity
  sets: an IP that looks unique here may be shared over a longer horizon, or a
  shared IP may reflect a node churning identities. The `d` for a window is a
  property of that window, not a stable cluster constant.
- The stake join uses the nearest `getVoteAccounts` snapshot, which is not
  simultaneous with the capture (about 4 minutes after W1, about 2.75 hours
  before W2). `activatedStake` is fixed within an epoch, so the gap affects
  which identities match, not the stake amounts.
- Sensitivity to `N` is real but bounded: because almost every `d_t` is 0, the
  system `d` is dominated by the shared-IP count, not by `N`. Rescaling `N`
  moves `d` by well under an order of magnitude and never changes the
  qualitative finding that `d` is near zero.

## Reproduction

```
python3 analysis/d-anonymity/d_anonymity.py                 # default N = observed
python3 analysis/d-anonymity/d_anonymity.py --candidate-set all_ids
python3 analysis/d-anonymity/d_anonymity.py --candidate-set routable_ips
```

The script reads only the raw files in `data/2026-08-22/` and prints `d`, the
stake-weighted variant, and the caveats. If any required file is missing it
reports the absent paths and exits non-zero rather than inventing numbers.
