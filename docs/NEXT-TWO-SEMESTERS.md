# Next Two Semesters (draft email to Dr. Ma)

Subject: S-NodeFinder, one semester out, and the courses ahead

---

Dr. Ma,

The 1-pager described what S-NodeFinder measures. This note is about what I
will do with the coming year, and it is meant as a commitment, not a status
update.

The project has a shape now. Two instruments, one clock. The RPC snapshot
series has been running for days. The gossip spy, which listens at the wire
without contributing to the mesh, completed its second full capture today:
3,490 identities in two minutes, close to the 3,543 it saw in the first
window, and the saturation curve was still climbing on the final tick. What
that means in practice: the degree of anonymity of a Solana validator is
becoming a number we can watch change, instead of a thing we argue about.
The stake-weighted leak table comes next, then the decay curve.

The coursework lines up behind it. I have one semester left before I can
register for CS 5XX. In the winter I will take one course, and two in Spring
2027, so the reading there feeds the measurement work instead of running
parallel to it. My research time goes to the intersection of your interests
and mine: anonymity measurement first, then churn, client mix, and the gap
between what RPC advertises and what the wire actually shows.

I will be honest about the state of things. The instruments work and the
first numbers are real, but the anonymity measure itself, the degree of
anonymity d from Diaz 2002, is not computed yet. That is the next milestone,
not a promise. I would rather show you a number than a claim.

The one thing I need from you is the judgment I cannot make alone: whether a
sustained pull-only spy, running continuously instead of in bounded windows,
is within the ethics we agreed on, and at what duty cycle. With that answer,
the snapshots become a churn dataset by the time I am taking those courses.

Stebit
