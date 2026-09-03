# S-NodeFinder: 10-minute research update

**For:** Dr. Zane Ma, ASTRO Lab, Oregon State University
**By:** Huu Tai Le (Stephen)
**Prepared:** 2026-09-02
**Numbers:** all figures below are sourced in `docs/PRESENTATION-NUMBERS.md`,
captured 2026-09-02. Re-run `./scripts/refresh-numbers.sh` the day before and
re-date anything that moved.

Budget: 7 slides, 10 minutes. Slides 1 to 4 are setup and should take about 4
minutes. Slide 5 is the payload, about 2 minutes. Slide 6 is the honesty slide
and deserves a full 2 minutes because Q&A lives there. Slide 7 closes in 1
minute, leaving 1 minute of slack.

---

## Opening line (verbatim)

> "Thanks for the time. I have been listening to Solana's gossip layer for two
> weeks, and I want to show you what it gives up and what I still cannot
> measure."

---

## Slide 1: How anonymous is a Solana validator?

**Title:** S-NodeFinder: measuring validator anonymity decay at the Solana
gossip layer

**What Stephen says:**
"The question is: how anonymous is a Solana validator at the gossip layer, and
how fast does that anonymity decay under passive observation? I have two
instruments running against mainnet and a dated series going back to
2026-08-21. Today is a status report, not a result."

**Visual:** Title, name, date, and the research question set on its own line in
large type. Nothing else on the slide.

**Numbers:** Series start 2026-08-21, 13 UTC days of data on disk as of
2026-09-02.

**Honesty note:** Say "status report, not a result" in the first fifteen
seconds. It sets the contract for slide 6.

---

## Slide 2: Three sub-questions

**Title:** The question breaks into three

**What Stephen says:**
"First, linking speed and accuracy: how much of the validator set resolves to an
advertised IP as a function of how long a passive observer listens. Second,
stake-weighted exposure: what fraction of activated stake sits behind an IP the
protocol already advertises. Third, concentration: how far those IPs collapse
into a small number of autonomous systems or hosting providers. The first two
are instrumented and producing data. The third is planned work, and I have
measured none of it."

**Visual:** Three rows. Rows one and two tagged INSTRUMENTED in one colour, row
three tagged PLANNED in grey. The grey should be visibly different, not subtle.

**Numbers:**
- Sub-question 1, instrumented: freshest full window recovered 3,070 identities
  in 120 seconds (2026-09-02, run 14:36:42Z).
- Sub-question 2, instrumented: stake-weighted identified fraction 0.984203
  (2026-08-22 W1 capture).
- Sub-question 3: no measurement exists.

**Honesty note:** Do not let the third row look like a result with a pending
number. It is a research plan. Say "planned" out loud, do not rely on the slide
colour to carry it.

---

## Slide 3: Why gossip, and why the Ethereum mapping does not port

**Title:** Gossip publishes identity by design

**What Stephen says:**
"Every participating node advertises a ContactInfo record to anyone who
listens: identity pubkey, gossip socket, TPU and TVU sockets, shred version,
client version. So the question is not whether identity leaks. It is how
completely and how fast. This is the NodeFinder question, from Kim, Ma and
colleagues at IMC 2018, asked against a different overlay. The mapping does not
port directly: Ethereum's discovery is Kademlia-style, so a crawler can walk the
ID space, whereas Solana's CRDS is a push and pull anti-entropy table. Coverage
is a function of dwell time, not scan breadth. That is why my main variable is
how long I listen."

**Visual:** Left half, a ContactInfo record with the six advertised fields
listed. Right half, two small diagrams side by side: an ID-space walk labelled
Kademlia, and a dwell-time curve labelled CRDS.

**Numbers:** No new numbers on this slide. Reference: Kim, Ma, Murali, Mason,
Miller, Bailey, "Measuring Ethereum Network Peers", IMC 2018.

**Honesty note:** The "does not port directly" sentence is the most important
one on the slide. It shows the lineage is understood rather than borrowed.
Deliver it as a design constraint, not as a caveat.

---

## Slide 4: Two instruments, deliberately redundant

**Title:** What is built and running

**What Stephen says:**
"rpcview is a typed Rust CLI over public RPC getClusterNodes and
getVoteAccounts, writing dated JSON snapshots on a fixed roughly six-hour
schedule. It is the backstop, because gossip has no archive and the clock is the
dataset. spy is a hand-built pull-only CRDS listener against the current Agave
4.2.x protocol, first successful wire capture on 2026-08-22. I want to be plain
about one thing: there is no shipped gossip binary for Agave 4.x. The 4.x line
ships gossip as a library only, and the one binary that does exist, solana
1.18.26, announces gossip port 0 against the 4.2.x mesh and stays at zero nodes.
So I wrote the protocol client. On ethics: passive, pull-only, one persistent
identifiable identity so operators can recognise and filter me, conservative
rates, and the full bind is in ETHICS.md."

**Visual:** Two boxes side by side, rpcview and spy, with a shared timeline bar
underneath marked 2026-08-21 (series start) and 2026-08-22 (first wire
capture). Arrow from each box into the same dated store.

**Numbers:**
- rpcview: dated series begins 2026-08-21, 13 UTC days on disk as of 2026-09-02.
- spy: first successful wire capture 2026-08-22T00:27:05Z.
- Cadence: roughly 6 hours for both.

**Honesty note:** The one-pager says rpcview has been operational since
2026-08-19, but `data/` holds nothing before 2026-08-21. Say 2026-08-21 unless
the two missing days are recovered before the meeting.

---

## Slide 5: What two minutes of listening buys

**Title:** Results so far

**What Stephen says:**
"One 120-second passive window on 2026-09-02 recovered 3,070 identities against
3,705 the cluster's own RPC advertised 48 minutes later. That is about 83
percent, from a listener that contributes nothing to the mesh. The discovery
curve was still rising at the final tick: 754, 1,792, 2,571, 3,070, so the last
30 seconds added 499. The gap between the wire view and the RPC view was 4 to 5
percent in my first week and has sat between 17 and 25 percent on every full
window since 2026-08-30. That widening is starting to look systematic rather
than a short-window artifact, and I am not yet able to say which. Stake-weighted
identified fraction is 0.984, from the 2026-08-22 capture. Client census is led
by 4.2.1 at 51 percent. Day over day churn is small: 33 IPs in, 34 out, 3,722
stable between 2026-09-01 and 2026-09-02."

**Visual:** One chart, the discovery curve for the 2026-09-02 14:36 window, with
a dashed horizontal line at the paired RPC count of 3,705. The rising final tick
should be visually obvious.

**Numbers (all captured 2026-09-02 unless stated):**
- Wire: 3,070 identities, run 14:36:42Z, final tick 14:38:42Z, 4 ticks at 30 s.
- Curve: 754 / 1,792 / 2,571 / 3,070, final tick +499.
- Paired RPC: 3,705 nodes at 15:26:46Z, offset +48 min. Coverage 82.9 percent.
- Day's closing RPC view: 3,685 nodes, 3,658 unique gossip IPs, 23:20:08Z.
- Wire/RPC gap, full windows, 2026-08-30 to 2026-09-02: 17.1 to 25.1 percent.
- Wire/RPC gap, first paired window 2026-08-22: 4.6 percent.
- Stake-weighted identified fraction: 0.984203, captured 2026-08-22.
- Client census: 4.2.1 at 1,880 of 3,685, 51.0 percent, captured 2026-09-02.
- Churn: entered 33, left 34, stable 3,722, 2026-09-01 to 2026-09-02.

**Honesty note (three, all of them said out loud):**
1. The gap sentence stops at "starting to look systematic rather than a
   short-window artifact". Do not extend it into a cause. Short window, partial
   CRDS table, and RPC staleness are all still live, and none is separated.
2. The 0.984 figure is 11 days old. State the date when you state the number.
3. The client census moved: 54.3 percent on 2026-08-31, 51.0 percent on
   2026-09-02, with a new 4.2.2 build taking 12.2 percent. Quote the fresh one.
   If asked why it moved, the answer is an upgrade wave in flight, visible in
   the census itself.

**Optional strengthener if time allows (5 seconds):** 2026-09-02 produced three
complete windows, at 00:53, 06:55 and 14:36, finishing at 3,057, 3,054 and
3,070. Three same-day windows within 16 peers of each other is a better result
than one window.

---

## Slide 6: What I cannot yet claim

**Title:** Honest limits

**What Stephen says:**
"Four limits, and I would rather state them than have you find them. One: the
anonymity metric d is not computed on any fresh window. What I have is the d = 0
endpoint, the share of identities that sit alone on their IP, which was about
98.9 percent in the August 22 capture. Choosing the candidate set for identities
that are not at that endpoint is unfinished work. Two: AS and cloud enrichment is
planned, not measured. There is no number. Three: 120-second windows undercount,
and I know that because the curve was still rising at every final tick. Four: the
spy duty cycle is mid-migration. Of 23 runs in the last seven days, 8 completed
four ticks and 15 were truncated. Everything I showed you comes from the full
windows only."

**Visual:** Four lines, plain text, no icons, no red. Each line is a limit
followed by the number that proves it. Restraint on this slide reads as
confidence.

**Numbers:**
- Last computed d: 0.001688 unweighted, 0.000000 stake-weighted, 2026-08-22 W1.
- d = 0 endpoint: about 98.9 percent of W1 identities alone on their IP; 11 IPs
  carried more than one identity, 36 identities total.
- Undercount evidence: every full window ends on a rising tick, +499 on the
  freshest.
- Duty cycle: 23 runs, 8 full, 15 truncated, 2026-08-27 to 2026-09-02.
- Pipeline gaps: 4 unparseable cluster-nodes files in the series, no UTC day
  lost.

**Honesty note:** This is the slide, not an appendix to slide 5. Do not
compress it, do not soften it, do not apologise for it. The one-pager states
these as unfinished rather than claimed and this deck matches it exactly. If
Stephen is running long, cut slide 3, not this one.

---

## Slide 7: Next

**Title:** What comes next

**What Stephen says:**
"Four things in order. Churn over the full accumulated series rather than one
day pair. Longer windows with a saturation fit, so I can report a time to
coverage instead of a single-window count. A refresh of the stake-weighted
table on a current capture. Then the thing the whole question is built around:
the anonymity decay curve, d as a function of passive observation time. That is
the headline result, and everything before it is instrumentation."

**Visual:** Four items on a short horizontal timeline, with d(t) at the end,
visually heaviest. An empty axis labelled d against observation time, with no
curve drawn on it, is the right image: it shows the shape of the answer without
pretending to have it.

**Numbers:** No new numbers. Current series length 13 UTC days, 2026-08-21 to
2026-09-02, which is the input to the churn analysis.

**Honesty note:** The empty axis is deliberate. If a curve is drawn on it, even
a sketch, it will be read as a preliminary result.

---

## Closing line (verbatim)

> "Two weeks in, the instruments work and the series is running. The number I
> came here for is not measured yet. I would rather show you that honestly now
> than a clean curve later that I cannot defend."

---

## Q&A: three most likely questions

**1. "Why is the wire view so much smaller than the RPC view, and why is the gap
growing?"**
Three candidates are still live, short window, partial CRDS table at a single
vantage, and RPC staleness, and I have not separated them; a second differently
located spy plus longer windows is how I would separate the first two.

**2. "Is d = 0 not just restating that gossip is public? Where is the finding?"**
Correct, and I say so in the write-up: near-zero d confirms the protocol is
non-anonymous by design, so the contribution is the decay curve and the
stake-weighted magnitude, not the endpoint value.

**3. "Is running a spy on mainnet ethically acceptable, and at what duty
cycle?"**
It is passive and pull-only under one persistent identifiable identity at
conservative rates, which is the Menlo Report posture NodeFinder used, and the
duty cycle for sustained capture is exactly the judgment call I want from you.

**Likely follow-ups, one line each, if they come up:**
- *"Why did you write your own client?"* Agave 4.x ships gossip as a library
  only, and solana 1.18.26 announces gossip port 0 against the 4.2.x mesh.
- *"How does this compare to published Solana node counts?"* Kiffer et al.,
  SIGMETRICS 2026, report roughly 3,693 from an API vantage, which sits between
  my wire view and my RPC view.
- *"What if the RPC endpoint is just wrong?"* That is one of the three
  candidates, and it is why the cross-view delta is reported as a first-class
  metric rather than averaged away.
- *"How much stake is behind a single IP?"* 98.42 percent of activated stake as
  of 2026-08-22, and that table needs a refresh before I quote it again.

---

## Pre-meeting checklist

1. Run `./scripts/refresh-numbers.sh` and re-date every figure in
   `docs/PRESENTATION-NUMBERS.md` that moved.
2. If a fresh full window exists after 2026-09-02 14:36Z, use it on slide 5 and
   redraw the discovery curve.
3. Re-read `docs/ETHICS.md` before saying anything about the spy's posture.
4. Check whether the 4.2.2 upgrade wave has moved the census again. It moved 3.3
   points in two days.
