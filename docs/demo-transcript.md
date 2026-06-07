# Demo Transcript

Roughly 12 minutes of spoken delivery. This is the *natural-sounding* version of `demo-script.md` — what you'd actually say in the room, in your voice, not what the slides say.

Stage directions are in brackets `[like this]`. Things you'd say out loud are not in brackets. Read it through once, then put it down — the goal is to internalize the arc, not memorize the words.

---

## [Slide 1 — Title]

> Thanks for the time today. So what I want to walk you through is a project I built that's structured like a Sales Engineering conversation about observability. Customer pain at the top, the architecture in the middle, a live incident triage in the middle-to-end, and a clean implementation path at the close.

> The reason I built it this way is — I spent two years on backend systems where the answer to "why is this slow" was almost always "go ask three people across three Slack channels." That hurts. So I wanted to build the version where the dashboards answer that question without anybody having to ask.

> Anything I should know about your team or what you're dealing with right now before I get into it? [pause — let them answer if they want, or just nod and move on]

> Okay, let's start with the customer.

---

## [Slide 2 — The Customer]

> So the customer here is Acme Trading Platform. They're a Series C fintech, about 400 people. They run a high-traffic backend that talks to maybe six downstream dependencies — pricing feeds, clearing partners, KYC providers, internal risk services. The kind of setup where any one of those going slow is felt by their end customers immediately.

> The thing I want to land is — they're not asking for "more monitoring." They have monitoring. What they're asking for is *less time spent triaging*. The on-call rotation is burnt out. Incidents are being detected by customers, not by engineering. And when a page does fire, the first 15 to 30 minutes is people arguing about which service to look at.

---

## [Slide 3 — What "Broken" Looks Like Today]

> Here's how I'd break the pain down. [gesture to slide]

> Customer-detected incidents — that's the first one and the most embarrassing. The team finds out from a support ticket. Long mean time to triage — somebody is paged, but they spend 20 minutes figuring out which downstream to point at. Alert fatigue — too many pages per shift, most are noise, the real signal gets ignored because it looks like more noise. No shared view of an incident — engineering, support, and leadership all looking at different tabs.

> And then the quiet one — recurring root causes. The same patterns of incident keep happening because the post-incident data doesn't surface them clearly enough to prioritize a fix. Same incident, six months later, surprise.

---

## [Slide 4 — Discovery]

> Before I'd build anything, here are the questions I'd want to walk through. Pick four to six in a real call.

> On current state — what tooling do you use today? Who owns the dashboards? How many places does someone have to look during an incident?

> On the on-call experience — how many alerts per shift? What percentage are real? Has the team ever spent more than 30 minutes deciding *which* service is the cause?

> On cross-team — does support get information during an active incident, or do they have to page engineering for status?

> And on investment — what was the last incident that materially affected revenue, and what would justify funding observability work this quarter? That last one isn't bait — it's the actual conversation that lets the SRE lead get budget.

> Six questions. Real conversation, not a checklist.

---

## [Slide 5 — Architecture]

> Okay, here's the stack. [gesture to diagram]

> Two services. The api on port 8000 — that's the customer-facing trading API. The downstream on port 8001 — that's standing in for a real third-party. In a real engagement, that's where your actual vendor would plug in.

> Both services have the same observability surface — structured JSON logs and a Prometheus metrics endpoint. Prometheus scrapes both every 10 seconds. Grafana queries Prometheus and shows your team the dashboards.

> The thing I want to highlight — both services emit the same metric *names*. So when we query, we filter by the `job` label to pick api or downstream. That makes the dashboards reusable and gives us comparison panels for free.

---

## [Slide 6 — The Four Dashboards]

> Four dashboards, each designed to answer one specific question. [open Grafana]

> Overview — is the platform healthy? Three stat panels up top: request rate, 5xx percentage, p95 latency. Plus the request-rate time series at the bottom. This is the dashboard your on-call opens first. If everything's green, the rest of the day is yours.

> Latency — where is the slowness? p50, p95, p99 over time. Then the same breakdown per endpoint. Then a table of the slowest endpoints right now.

> Errors — what's failing and how often? Per-endpoint 5xx rate, the status-code pie, and an all-responses stacked view. The pie matters because intermittent issues are subtle — they shift the mix, they don't spike the rate.

> And dependencies — is it us or them? Downstream call rate by target. Outcome breakdown — success versus timeout versus server error versus connect error. p95 latency for downstream calls. And the panel I'm most proud of — "Is It Us Or Them?" — that compares api success rate to downstream success rate in one view. When those two lines diverge, you know exactly where the problem is.

---

## [Slide 7 — Healthy Baseline]

> Right now we're sending about 12 requests per second across a mix of endpoints. That's the steady-state weekday profile. p95 latency around 80 milliseconds. Error rate is zero. This is the baseline. [point to Overview]

> The mental model I want to land — any drift from this picture is a signal. You're not training your on-call to memorize thresholds. You're training them to notice when the shape changes.

---

## [Slide 8 — Live Demo: Latency Spike]

> Okay, let me break something on purpose. [switch to terminal]

> I'm going to inject 800 milliseconds of latency on every downstream call.

```bash
./scripts/incident.sh latency 800
```

> Watch the Overview p95 panel. [wait ~15 seconds] There. Yellow now red. Took us about 15 seconds from injection to alert-worthy. In a normal world, your customer would not have noticed yet.

> Now let's triage. Switch to Latency. [point to the per-endpoint panel] See how `/accounts/{id}/positions` is at the top? That endpoint makes N downstream calls — one per position the account holds. So an 800ms downstream latency turns into 1.6 seconds for a 2-position account, 4 seconds for a 5-position account. Cascade.

> Now switch to Dependencies. The "Is It Us Or Them?" panel. Downstream p95 is tracking the api p95 1-to-1. That's the answer — it's the downstream, not us.

> Recover.

```bash
./scripts/incident.sh recover
```

> [wait 10 seconds] Back to baseline. No restart. The dashboards just reflect the new reality.

---

## [Slide 9 — Live Demo: Outage]

> Okay, what about a real outage. The downstream is going to start returning 503 for everything.

```bash
./scripts/incident.sh outage
```

> [switch to Errors dashboard] 5xx rate spikes. The status-code pie shifts. Clear visual signal.

> But here's the slide I really want to show you. [switch to Dependencies] The "Is It Us Or Them?" panel. Look — downstream success rate is at zero. API success rate is still elevated, around 40%, because endpoints like `/health` and the local account-lookup endpoints don't touch the downstream.

> One panel. Two lines. Two seconds. You know it's the downstream. Your support team can post a banner immediately.

> Recover.

```bash
./scripts/incident.sh recover
```

---

## [Slide 10 — Live Demo: Fan-Out Cascade]

> Okay, one more. This is the tricky one — the one most platforms miss.

```bash
./scripts/incident.sh latency 600
```

> 600 milliseconds. Not dramatic. [switch to Overview] p95 is elevated but not red. In a noisy room, easy to miss.

> [switch to Latency dashboard, point to the per-endpoint panel] But here — the positions endpoint is dramatically worse than the others. That's the fan-out. Customers with many positions feel it. Customers with few positions don't.

> This is the scenario that gets you in trouble in real life. Your biggest customers — the ones with the most data — feel it worst. Your smallest customers don't notice. The aggregate "p95 latency" stat doesn't scream loud enough to wake anyone up. But your strategic accounts are calling their account manager.

> The fix here is to surface per-endpoint latency separately. Which we do. [recover]

```bash
./scripts/incident.sh recover
```

---

## [Slide 11 — End-to-End Tracing]

> One more thing I want to show, because it ties everything together.

> [switch to terminal] I'm going to hit the api with a custom request ID. [run curl with X-Request-Id]

> Now I'm going to grep both services' logs for that ID. [run docker logs | grep on both]

> Same ID, both services. When a customer says "my position lookup failed at 3:47am," you give that ID to your on-call. They grep both services. End-to-end trace, no distributed tracing system required, no extra cost.

> If you want to add OpenTelemetry on top of this later, you've already got the foundation. But you don't need it to start.

---

## [Slide 12 — Implementation Path]

> So what's the path. [gesture to slide]

> First: a 30-minute review with your SRE lead. Walk through the metric model, the dashboard opinions, the request-ID propagation pattern. Most of that conversation is "yes, we already do that" or "we tried that and it didn't stick." Both useful.

> Second: pick three customer-facing endpoints. Wrap them in this instrumentation. Get a week of real traffic.

> Third: one failure drill against staging. Pick one scenario from the playbook. Run it during business hours with your on-call rotation watching. Time-to-detect. Time-to-triage. Quantify.

> After that, the rollout is self-evident. The question stops being "should we" and starts being "where next."

---

## [Slide 13 — Recommended Next Steps]

> So the concrete next step is — can we get a 30-minute call with your SRE lead and one engineer who's on-call this week? That's enough to validate whether this pattern fits, or whether there's something specific to your environment I'd need to adjust.

> Does that work, or would you sequence it differently?

> [actually ask, then shut up and listen]

---

## [Slide 14 — Q&A]

> Cool. Happy to take questions. The repo is at github.com slash my username slash observability-incident-triage. All the walkthrough docs are in the `docs` folder if anyone wants to dig in after the call.

---

## Notes for Yourself Before Going Live

- **Speak slower than feels natural.** SE demos go better at 110 words/min than 150. You sound more confident at the slower pace.
- **The "Is It Us Or Them?" panel is your closer.** It's the visual that lands hardest. Make sure you give it room to breathe.
- **The fan-out scenario is the depth-flex.** Most SE candidates show latency and outage. Showing the cascade scenario tells the interviewer you've thought about real-world incident patterns, not just textbook ones.
- **Don't run all five scenarios.** Three is the cap. The other two are pocket aces for Q&A.
- **The recovery is part of the story.** Don't rush past it. Customers remember recoveries because that's the experience you're really selling — "nothing dramatic, the system just resumes."
- **If Docker dies mid-demo, stay calm.** Screenshots in the demo-script repo as a fallback. "Looks like the container restarted — here's the response shape from earlier" is a totally fine recovery. Panicking is not.
- **It's okay to say "I don't know."** "That's a great question, the honest answer is it depends on your Prometheus retention budget — let me follow up by EOD" beats guessing.
