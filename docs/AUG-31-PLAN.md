# Aug 31 Plan: what Stephen does himself before sending to Dr. Ma

1-pager for Dr. Zane Ma due 2026-08-31. The instruments, the captures, and
the analyses are done and running unattended. This list is the part that
only Stephen can do, so the email is real and defensible from memory.
About two hours total. Written 2026-08-25 night.

## Task 1. Read the raw data yourself (tonight or tomorrow, 30-45 min)

- snapshots/digests/2026-W35.md  (this week's digest, landed Monday)
- data/2026-08-25/spy-summary-2026-08-25-223623.jsonl  (per-tick peer
  curves from the latest capture, 3 captures that day)
- head -2 data/2026-08-25/spy-2026-08-25-223623.jsonl  then read one real
  ContactInfo record field by field: pubkey, gossip address, version
  string, shred version. Touch one actual row.

Then write down three observations in your own words. Not the digest's
words, yours. These three sentences become the spine of the email.

## Task 2. Rewrite two sections of the 1-pager in your voice

Read docs/ONE-PAGER.md end to end. Rewrite section 2 (Motivation) and
section 6 (One ask) with your own sentences. Keep every number exactly as
it is, they are verified. The ask especially: a professor is going to
answer that question, so make sure it is the question you actually want
answered. If it is not the real question, change it.

## Task 3. Decide the AS item before Thursday Aug 27

The checkpoint cron (s-nodefinder-one-pager) runs Aug 27 18:25 and should
verify a current draft, not the Aug 21 one.

Two honest paths:
- Create the free MaxMind account, give Hermes the license key, Hermes
  runs the ASN enrichment (T4 unblocked, real numbers in the draft).
- Strike "AS and cloud concentration" from the 1-pager claims and leave it
  as planned work.

Do not ship the draft as is: it currently claims a contribution we have
not measured. That is the one place the draft overstates.

## Task 4. Final pass Aug 30 or morning of Aug 31

- Read docs/ONE-PAGER.md and docs/NEXT-TWO-SEMESTERS.md end to end.
- grep -n '—' on both files (standing rule: no em-dashes).
- Update the date line in ONE-PAGER.md.
- The Monday digest lands 09:00 Aug 31 if you want the freshest full-week
  number in the email body.
- Send.

## Stays delegated (not yours to do)

Enrichment code, refresh edits, diffs, any commit work. Those are
Hermes or Claude Code tasks.

## Status as of 2026-08-25

- Spy captures exist for Aug 21 through Aug 26, all cron jobs green.
- All T1-T10 analyses from the Aug 22 plan done except T4 (AS), which is
  blocked on the ASN source decision in Task 3.
- ONE-PAGER.md exists, structurally complete, dated Aug 21. Needs Tasks
  2 and 4.
