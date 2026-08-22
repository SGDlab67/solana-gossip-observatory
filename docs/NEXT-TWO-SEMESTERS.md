# Next Two Semesters (draft email to Dr. Ma)

Subject: S-NodeFinder: the next two semesters, plus one ethics question

---

Dr. Ma,

The 1-pager laid out what S-NodeFinder measures. This note is the other half:
what I intend to do with the coming year, written as a commitment rather than
a status report.

Where the instruments stand. rpcview has been snapshotting the public RPC
view on a timer for days. The spy, the pull-only CRDS listener that
contributes nothing to the mesh and runs under one fixed, identifiable
identity per our ethics bind, completed two full captures in a single day:
3,543 identities in the first 120 second window, 3,490 in the second. On the
final tick of the second capture the saturation curve was still climbing,
which tells me the bounded window undercounts and the interesting curve is
longer than two minutes.

I want to be precise about what is and is not done. The instruments work and
those counts are observed, not extrapolated. But the degree of anonymity d
from Diaz 2002, the number the research question is built around, is not
computed yet. The stake-weighted leak table comes first, then the anonymity
decay curve, then d. I would rather hand you an unfinished pipeline with
honest numbers than a finished-sounding claim.

The coursework is arranged to serve this. I have one more semester at Oregon
State before CS 5XX registration opens to me, so the plan is one course in
the winter and two in Spring 2027, chosen so the reading feeds the
measurement work instead of running beside it. My research time goes to the
overlap between your interests and my Solana work, in this order: the
anonymity measure of the network, then churn, client mix, and the gap between
what RPC advertises and what the wire actually shows.

One question needs your judgment, not mine. A sustained pull-only spy,
continuous rather than bounded 120 second windows, is what turns these
snapshots into a churn dataset. Is that within the ethics we agreed on, and
if so, at what duty cycle? The spy would stay pull-only, on its single
identifiable identity; only the duration changes. I will not run it
continuously before you have weighed in.

Everything above should improve with time; that is the point of building
instruments instead of one-off scrapes. This is what the project can become,
and I am committing the year to it.

Stebit
