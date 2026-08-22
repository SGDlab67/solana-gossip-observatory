# ONE-PAGER WALKTHROUGH

Mentor explanation of the 1-pager structure in [ONE-PAGER.md](ONE-PAGER.md).
Written for Stephen as a first-time researcher learning what a 1-pager is and
why each section exists. Read this alongside the 1-pager itself.

---

## What a 1-pager actually is

It is not a paper. It is a persuasion document with a deadline. The goal is to
make Dr. Ma think "this student knows what they are doing, this is worth my
time, here is exactly what I can do to help." It has to survive a 2-minute
skim by someone who has read 10,000 of these. Every sentence either advances
the argument or gets cut.

The six sections form a funnel: question, motivation, related work, method,
contribution, ask.

## 1. Research question

One sentence, then three measurable sub-claims. The trick here is that the
question is scoped to something you can actually measure this semester: "how
fast does anonymity decay under passive observation." Not "is Solana
anonymous" (unanswerable), but "how long must a listener wait before
identities resolve to IPs" (answerable with your instruments). The three
sub-claims map directly to your three phases: linking speed, stake-weighted
leak, AS concentration. Every roadmap phase is visible in the question.

## 2. Motivation

This section does the heavy lifting. It starts by conceding the obvious
objection: gossip is not designed to hide operators, everything is already
public. That concession is what makes the section honest and therefore
credible. Then it reframes: the question is not whether identity leaks, it is
how completely, how fast, and how much economic weight sits behind the leak.
That is the intellectual pivot of the whole document. Then the numbers table
lands as evidence, not assertion. Then the punchline: "Two minutes recovers
~96% of what the cluster's own RPC advertises, from a passive listener that
contributes nothing." That single sentence is the entire motivation in
miniature.

## 3. Related work

Two moves here. First, the mapping table to NodeFinder (IMC 2018). This is
the single most important page in your career right now, because it is the
paper your direction is named after. The table does something subtle: it
shows what ports over and what does not. Ethereum uses Kademlia-style
discovery where you can walk the ID space. Solana uses CRDS push/pull
anti-entropy where coverage depends on dwell time and peer selection. That
difference is your methodological justification for why a Solana measurement
is not just "NodeFinder again but on Solana." Second, the SIGMETRICS census.
Positioning against it is the sharpest move in the document: they measured 36
chains from the API vantage, we measure one chain from the wire vantage, and
the delta between those views is the object of study. That is a defensible
novelty claim. You are not claiming nobody measured Solana. You are claiming
nobody measured the wire layer, and the gap is itself the finding.

## 4. Method

Two instruments, deliberately redundant. The honest engineering story: the
custom crate was not a preference, it was the only path, because no shipped
binary can join the 4.2.x mesh. That sentence builds more credibility than
any amount of technical detail. Then the pipeline: join to vote accounts,
enrich to AS, compute d, diff the views. Then the longitudinal churn plan,
which is the part that makes this a research program instead of a one-off
scrape. Then ethics, which is not a footnote: it is a first-class section.
For a measurement paper, ethics is part of the method, and reviewers and
advisors check it first.

## 5. Expected contribution

Four numbered items, each one a real artifact: a quantified decay curve, a
stake-weighted visibility table, a methodological result on vantage
disagreement, a reusable instrument. Then the closer: "This is a measurement,
not a paper promise." That sentence is doing three jobs at once. It manages
expectations (no paper claim yet), it signals honesty, and it is the exact
tone Dr. Ma's framing wants: independent work, monthly meetings, 1-pager as
next artifact.

## 6. One ask

This is the part most first-timers get wrong. They write "please advise"
which is empty. The document instead asks one concrete question with a real
decision in it: is sustained capture in scope, and at what duty cycle? And it
flags the exact place where you want his ethics judgment rather than your
own. That is how you get a useful answer from an advisor: give them a
decision, not a status report. It also sets up the next meeting: you will
walk in with a specific methodological question already asked.

## The three meta-skills

First, the numbers are the skeleton. Every claim traces to an observed
figure. The ~96% is computed from the table (3543/3657). The 3.8% gap is
computed from the table (140/3683). Nothing is asserted that is not in that
table. That is the habit that separates research from blogging.

Second, the honest-limitations line: "the curve had not flattened (+222 on
the final tick), so 120s undercounts." A first-timer hides that. The document
states it. Why is that good? Because Dr. Ma will find it anyway, and finding
it himself destroys trust. Finding it stated openly builds trust. Also it is
scientifically correct: the number is a lower bound and the document says so.

Third, the ask is what makes it a 1-pager rather than a report. A report
summarizes. A 1-pager asks for something. The whole document is built to make
that one ask land.

## Diaz metric caveat

The document says we adopt d = H/H_max, but we have not actually computed d
yet, only the d=0 endpoint from rpcview. The metric is adopted as the target,
not claimed as measured. If a rigorous review flags it, that is correct
behavior, not an error: claiming a computed value you have not computed is
exactly the kind of thing that would embarrass a first-time researcher.

Review status (2026-08-21): the review already handled this correctly, the
1-pager frames d as an adopted target, not a measured value.
