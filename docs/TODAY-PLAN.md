# S-NodeFinder Task Plan 2026-08-22

Rule for every task: no em-dashes in any prose written. Verify with
grep -n '—' before finishing. Status values: pending, in_progress, done,
blocked, waiting. The loop agent runs tasks in id order, one per iteration.

## T1 stake-weighted leak table
- Model: claude-fable-5, effort high
- Task: join spy gossip identities to vote accounts and stake for both
  2026-08-22 windows; compute stake_weighted_identified_fraction (share of
  activated stake whose identity resolves to a single advertised IP).
- Deliverable: docs/analysis/stake-weighted-leak-2026-08-22.md
- Verify: numbers actually computed from data/2026-08-22/, table present
- Commit: analysis: stake-weighted identity-to-IP leak, 2026-08-22
- Status: done (verified by Hermes: recomputed fraction 0.984203 exactly)

## T2 client mix census
- Model: claude-sonnet-4-6, effort high
- Task: classify gossip ContactInfo client/version fields into Agave, Jito,
  Firedancer families per window; histogram plus shares.
- Deliverable: docs/analysis/client-mix-2026-08-22.md
- Verify: histogram counts sum near 3,543 and 3,592
- Commit: analysis: client mix census from gossip, 2026-08-22
- Status: done (verified by Hermes: counts match JSONL, em-dash clean)

## T3 RPC versus wire gap, both windows
- Model: claude-sonnet-4-6, effort high
- Task: diff rpcview cluster-nodes snapshots against the two spy windows;
  produce the delta table and note whether the gap is stable or drifting.
- Deliverable: docs/analysis/rpc-wire-gap-2026-08-22.md
- Verify: delta numbers match raw file counts
- Commit: analysis: RPC versus wire gap for 2026-08-22
- Status: pending

## T4 AS and cloud concentration
- Model: claude-sonnet-4-6, effort high
- Task: check for an offline ASN/cloud enrichment source (GeoLite2 ASN db,
  existing cache in repo); if available, enrich unique gossip IPs and report
  stake share by top AS and cloud. If no source is available, do not
  fabricate: mark blocked with the exact missing piece.
- Deliverable: docs/analysis/as-cloud-concentration-2026-08-22.md
- Verify: counts of unique IPs enriched, no invented mappings
- Commit: analysis: AS and cloud concentration, 2026-08-22
- Status: pending

## T5 degree of anonymity d scaffold
- Model: claude-fable-5, effort high
- Task: implement the Diaz 2002 entropy computation over a candidate set N
  for the 2026-08-22 windows. Be explicit that choosing N is research
  design, not settled; document the choice made and the honest limitations.
- Deliverable: analysis/d-anonymity/ with code plus docs/analysis/d-notes.md
- Verify: script runs and prints d and stake-weighted variant, with caveats
- Commit: analysis: degree of anonymity scaffold, Diaz 2002
- Status: pending

## T6 AFTER_PAPER self-test completion
- Model: claude-sonnet-4-6, effort high
- Task: read docs/AFTER_PAPER.md; complete any unanswered self-test items
  from the IMC 2018 reading, and the one permanent note if missing.
- Deliverable: updated docs/AFTER_PAPER.md
- Verify: no empty answer stubs remain
- Commit: docs: complete AFTER_PAPER self-test
- Status: pending

## T7 digest dry-run
- Model: claude-haiku-4-5, effort high
- Task: run scripts/digest.py against current data; confirm it produces a
  valid weekly digest without errors. Fix obvious breakage only.
- Deliverable: a dry-run digest file plus notes
- Verify: script exits 0 and writes output
- Commit: chore: verify digest pipeline dry run
- Status: pending

## T8 OSU CS 5XX candidates
- Model: claude-sonnet-4-6, effort high, WebSearch allowed
- Task: research OSU CS 5XX graduate courses relevant to networking,
  distributed systems, and security; list candidates for winter (one course)
  and Spring 2027 (two courses). Cite catalog sources.
- Deliverable: docs/CS5XX-CANDIDATES.md
- Verify: every listed course has a source URL
- Commit: docs: CS 5XX candidate courses for winter and spring
- Status: pending

## T9 repo docs refresh
- Model: claude-haiku-4-5, effort high
- Task: update README and ROADMAP to current reality: spy crawl on Hermes
  cron every 6h, two captures 2026-08-22, cron script path fix.
- Deliverable: updated README.md and docs/ROADMAP.md
- Verify: no stale claims about scheduling remain
- Commit: docs: refresh to post-fix crawl reality
- Status: pending

## T10 third data point fold-in
- Model: claude-sonnet-4-6, effort high
- Task: only if data/2026-08-22/ contains a spy capture newer than 21:30 UTC:
  fold it into the digest and note the three-window trend. If not yet
  present, mark waiting and do nothing else.
- Deliverable: updated snapshots/digests/2026-W34.md or a trend note
- Verify: the new capture's counts appear in the note
- Commit: analysis: fold third capture into weekly digest
- Status: waiting

## End condition
When all tasks are done, blocked, or waiting: report plan complete with a
one-line summary per task and stop. Do not invent tasks beyond this list.
