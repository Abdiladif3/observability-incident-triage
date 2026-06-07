# Deck Transcript — Observability & Incident Triage

Paired with `deck.pptx`. Roughly 12 minutes of spoken delivery, one section per slide. Stage directions in brackets `[like this]`. Read it through twice and put it down — the goal is to internalize the arc, not memorize the words.

---

## Slide 1 — Title

> Thanks for the time today. I'm going to walk through a project I built called Observability & Incident Triage. It's structured like a real Sales Engineering conversation about reliability — what an incident feels like today, what it could feel like, and what the rollout would look like.

> Twelve minutes if it goes smoothly, longer if you interrupt — and I'd rather you interrupt. Anything you're dealing with right now you'd want me to weave in? [pause]

---

## Slide 2 — Meet the customer

> Stand-in customer here is Acme Trading Platform. Series C fintech, about 400 people. They run a high-traffic backend that touches six or so downstream dependencies — pricing, clearing, KYC, internal risk. Latency-sensitive in a way that hurts.

> Four stakeholders matter for this conversation: SRE, engineering, support, product. They all care about reliability for different reasons.

---

## Slide 3 — What's broken today

> Six pains. [gesture across the grid]

> Customers detect incidents before engineering does. Triage takes 15 to 30 minutes — most of it spent arguing about which service is the cause. Alert fatigue — on-call ignores real signals because the noise won. No shared view — engineering, support, and leadership look at different tabs during the same incident. Same root cause comes back two quarters later because the data wasn't visible enough to fix it. And status pages lag reality.

> All of these reduce to one number: time-to-triage. Everything I'm about to show is in service of that number going down.

---

## Slide 4 — Discovery: what I'd ask first

> Three columns. [point to each]

> Current state — their tooling, and how many places someone looks during an incident. The second one usually surprises them.

> Incidents — alerts per shift, percentage that are real, whether the team has ever spent 30 minutes deciding which service to blame. That last one is the discovery question of the deck.

> Investment — what hurt revenue most recently, and what would justify funding observability this quarter. That column is where budget comes from. Don't skip it.

---

## Slide 5 — Architecture

> Two services — an API and a simulated downstream — both instrumented with structured logs and a /metrics endpoint. Same metric names on both, separated by the `job` label. That's what makes the dashboards reusable.

> Prometheus scrapes both every 10 seconds. Grafana queries Prometheus. The on-call engineer looks at four dashboards. That's the whole stack.

> [point to the X-Request-Id annotation] One detail to call out — request IDs propagate end-to-end from the API to the downstream. We come back to that.

---

## Slide 6 — Four dashboards, four questions

> Each dashboard answers exactly one thing. [point to each]

> Overview — is the platform healthy right now? Three KPIs, refreshing every 10 seconds.

> Latency — where is the slowness? Per-endpoint p50, p95, p99.

> Errors — what's failing and how often? 5xx rate by endpoint, status-code mix.

> Dependencies — is it us or them? Downstream success rate compared to our success rate. That last panel is the most important visual in the whole platform, and we'll see it in a minute.

> Each dashboard fits on one screen. None of them tries to do everything. That's the design opinion.

---

## Slide 7 — What healthy looks like

> Three numbers to memorize. [point to each tile]

> 12 requests per second — steady-state weekday traffic. Zero percent 5xx — anything else is a signal. 80 milliseconds p95 — under 100 feels instant.

> [point to the bottom callout] The mental model: any drift from this picture is a signal. On-call doesn't memorize thresholds. They notice when the shape changes.

---

## Slide 8 — Demo: 800ms latency injection

> [switch to terminal] I'll inject 800 milliseconds of latency into the downstream.

> [run ./scripts/incident.sh latency 800] Now switch to Grafana.

> [open Overview] Within about 10 seconds — one Prometheus scrape — the p95 panel goes red. [open Latency dashboard] Per-endpoint breakdown shows the positions endpoint is hit hardest. That's the fan-out — positions makes N downstream calls per request.

> [open Dependencies] And here's the verdict — downstream p95 tracks API p95 one-to-one. The conclusion writes itself: it's the downstream.

> [point to the verdict panel on the slide] In 15 seconds I went from "something feels slow" to "page the pricing vendor and update the status page." That's the SE story.

---

## Slide 9 — Demo: total outage

> [switch to terminal] Now the dramatic version.

> [run ./scripts/incident.sh outage] Open Grafana, Dependencies dashboard.

> [pause and let the audience look at the slide for five seconds]

> Downstream success rate: zero percent. API success rate: about 40 percent — the endpoints that don't touch the downstream still work. Health checks, account lookups, anything we serve from memory.

> Two lines, two seconds. You know it's the downstream. Support can post a status banner immediately. Engineering doesn't waste an hour figuring out which service is the cause.

> This is the single most useful panel in the whole platform.

---

## Slide 10 — Demo: fan-out cascade

> Last scenario — and this is the one most platforms miss. [point to the comparison]

> [run ./scripts/incident.sh latency 600] Single quote lookup takes 650 milliseconds. Acceptable. Looks fine on the Overview dashboard.

> But the positions endpoint takes 4.2 seconds — because it's making N downstream calls. Customers with many positions feel it. Customers with few don't. Your biggest customers complain; your smallest don't.

> [point to the bottom strip] The fix is per-endpoint latency in the dashboards. If you only look at overall p95, you miss this entirely. And the customers who experience it are the ones with the most data — usually the most strategic accounts.

---

## Slide 11 — End-to-end tracing

> One small thing that ties it all together. [point to the three steps]

> Client sends a request with an X-Request-Id header. The API logs it. The downstream logs the same ID — because it propagates through every internal call.

> When a customer says "my position lookup failed at 3:47am," you grep both services for one ID. That's the value of cheap tracing — you don't need OpenTelemetry on day one. You can layer it on later if you want spans and a flame graph, but the on-call story works without it.

---

## Slide 12 — From demo to production

> Five steps. Three to six weeks. [walk through]

> Week one — 30-minute review with their SRE lead. Walk the metric model and dashboard set. Surface objections early.

> Week one and two — pilot with three of their customer-facing endpoints. Wrap them in the same middleware pattern.

> Week two — port the dashboards into their Grafana. The JSON is in the repo.

> Week three — failure drill in staging during business hours, on-call watching. Quantify time-to-triage before and after. That's the data that funds the wider rollout.

> Week four onwards — endpoint by endpoint, sequenced by customer impact.

---

## Slide 13 — Questions

> [keep contact info visible]

> That's the platform. The repo is at github.com slash my username slash observability-incident-triage. Dashboards, incident playbook, troubleshooting runbook — all in the docs folder.

> Happy to take questions.

---

## Notes to self before going live

- **Let the outage slide breathe.** Five seconds of silence on slide 9. The visual sells itself.
- **Per-endpoint latency is the depth-flex.** Most candidates show latency and outage. Adding fan-out tells the interviewer you think about real incident patterns.
- **The verdict matters more than the path.** Don't narrate every Grafana click — let the dashboard tell the story and you summarize.
- **Run the scripts in advance.** Have `./scripts/generate-traffic.sh` running so the dashboards have baseline data. Otherwise you're presenting empty graphs.
- **Practice the timing.** 15 seconds from latency injection to red is your most-quoted statistic. Time it twice before the call to make sure it lands.
- **It's okay to say "I don't know."** "Let me check the Prometheus retention math and follow up by EOD" beats guessing.
- **If Grafana takes a beat to refresh, fill it.** "These are 10-second scrape windows, so the panel will update in about that time" buys you the pause.
