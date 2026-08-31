# Email: One-Pager Follow-Up to Dr. Ma

**Subject:** Solana Gossip Observatory (S-NodeFinder): one-pager and one scope question

---

Dear Dr. Ma,

Attached is a one-pager on the Solana Gossip Observatory (S-NodeFinder), the gossip-layer measurement work I have been building. The short version: a pull-only CRDS listener recovered roughly 95 percent of the cluster's node count from a single 120-second window, and the gap between what the wire shows and what RPC advertises looks like a finding rather than noise. The series now runs unattended on a six-hour schedule.

Two things I would value from you.

First, the one decision: is a sustained pull-only gossip spy in scope at this stage, and at what duty cycle? Continuous or near-continuous capture is what turns this from a snapshot into a churn dataset, and it is the one methodological step where I want your ethics judgment before I run it. If sustained capture is in scope, I would also value your view on whether a second vantage point, a differently located spy, is worth the added footprint.

Second, on working arrangement: I plan to work independently and check in by email as results accumulate. That independence is deliberate, and worth naming why: I want to own the research process end to end, from framing the question to running the capture to defending the numbers, rather than consuming finished results someone else earned. This field is learned from papers, not textbooks, so the close reading is part of the training itself; a measurement method only becomes mine once I have reproduced it against a live cluster and watched where it bends. I also want the hours inside the Solana ecosystem, not adjacent to it: running captures, comparing what the wire says to what the tooling claims, getting to know how operators actually run their nodes. I enjoy being a participant in this network far more than a spectator of it, and I think Solana deserves honest measurement from someone who cares enough to sit with the raw wire data. Next up on my side are the churn analysis and the stake-weighted exposure table, with AS and cloud concentration to follow. I will propose an in-person meeting once there is something concrete that benefits from it, and if a call would ever be more useful than email, I am glad to make time.

Thank you for your time!

Sincerely,
Huu Tai Le
#934768741
www.linkedin.com/in/stephenforcrypto
