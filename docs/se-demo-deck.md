---
marp: true
theme: default
paginate: true
header: 'Observability & Incident Triage Demo Platform'
footer: 'Abdiladif Haibah'
style: |
  section {
    font-size: 26px;
    padding: 60px 70px;
  }
  section.lead {
    text-align: center;
  }
  section.lead h1 {
    font-size: 56px;
    margin-bottom: 8px;
  }
  section.lead h3 {
    font-weight: 400;
    color: #555;
  }
  h1 {
    color: #1a1a1a;
    border-bottom: 2px solid #1a1a1a;
    padding-bottom: 6px;
  }
  h2 {
    color: #2a2a2a;
  }
  table {
    font-size: 22px;
  }
  code {
    background: #f4f4f4;
    padding: 1px 6px;
    border-radius: 3px;
  }
  blockquote {
    border-left: 4px solid #888;
    color: #444;
    font-style: italic;
  }
---

<!-- _class: lead -->

# Observability & Incident Triage Demo Platform

### Translating dashboards into faster incident resolution

**Abdiladif Haibah**
Backend Engineer → Sales Engineering

<!--
Open with a one-line frame. Don't introduce the tech stack yet.

"What I'm walking you through today is the same flow I'd use with a customer:
start with what an incident feels like, end with what it would cost to fix."
-->

---

# The Customer

**Acme Trading Platform** — Series C fintech, ~400 employees.

High-traffic backend talking to 6+ downstream dependencies.

Today, when an incident happens:

- It's detected by customers, not engineering
- Triage takes 15–30 minutes deciding *which* service to blame
- Different teams look at different dashboards

Stakeholders we need to satisfy: **SRE**, **Engineering**, **Support**, **Product**.

<!--
Anchor on a real-sounding customer. Acme Trading Platform — financial services,
latency-sensitive, every incident shows up on a status page.

The four stakeholders matter — every observability conversation has at least
three of these in the room, and they all weigh the demo differently.
-->

---

# What "Broken" Looks Like Today

| Pain | Who feels it |
| --- | --- |
| Customer-detected incidents | Engineering, leadership |
| Long mean-time-to-triage | On-call, customers |
| Alert fatigue, low signal-to-noise | On-call |
| No shared incident view | Support, leadership |
| Recurring root causes | Engineering manager |
| No real-time customer comms | Support, CS |

> They don't need more monitoring. They need less time spent triaging.

<!--
Land the business problem before showing any tech.
This is what discovery is for — surface the pain in language the customer
already uses, before you propose anything.
-->

---

# Discovery — The Questions I'd Lead With

**Current state**
- What tooling do you use today for metrics, logs, traces?
- How many places does someone look during an incident?

**On-call experience**
- How many alerts per shift? What percentage are real?
- Has the team ever spent 30+ minutes deciding *which* service is the cause?

**Investment**
- What was the last incident that materially affected revenue?
- What would justify funding observability work this quarter?

<!--
6 questions across the 3 most important categories.
In a real call, I'd pick 4–6 questions total based on who's in the room.

The investment question is the one that lets the SRE lead get budget. Don't skip it.
-->

---

# Architecture

```
API Client
    │
    ▼
api (:8000)  ──►  downstream (:8001)
    │                 │
    ▼                 ▼
   /metrics         /metrics
    │                 │
    └─►  prometheus (:9090)  ──►  grafana (:3000)
                                      ▲
                                      │
                              On-Call Engineer
```

Both services emit the same metric *names* — `job` label distinguishes them.

<!--
Keep it simple. The customer doesn't need to see every middleware.
They need to see: instrumentation surface, scrape pipeline, query layer, human.

Same metric names is a deliberate design choice — it makes dashboards reusable.
-->

---

# Four Dashboards — One Question Each

| Dashboard | Question it answers |
| --- | --- |
| **Overview** | Is the platform healthy right now? |
| **Latency** | Where is the slowness? |
| **Errors** | What's failing and how often? |
| **Dependencies** | Is it us or them? |

Each is opinionated. None tries to do everything.

<!--
The four-dashboard set is the SE story. Hiring managers see this and recognize
the discipline — it's the same opinion that Datadog, Honeycomb, and New Relic
build their default dashboard packs around.
-->

---

# The Healthy Baseline

[Open Grafana → Overview]

- Request rate: ~12 req/s
- 5xx rate: 0%
- p95 latency: ~80ms

> Any drift from this picture is a signal.

The on-call's job isn't to memorize thresholds. It's to notice when the shape changes.

<!--
Set the baseline before breaking anything. The audience needs to see normal
so they can recognize abnormal in the next slides.

Bonus credibility: if you say "any drift is a signal," you sound like an SRE
even if you've never been one.
-->

---

# Live Demo — Latency Spike (800ms)

`./scripts/incident.sh latency 800`

1. Overview p95 → yellow → red in ~15s
2. Latency by endpoint → `/positions` worst (fan-out amplification)
3. Dependencies → downstream p95 tracking api p95 1:1
4. Verdict: it's the downstream
5. Recover → baseline restored

> "15 seconds from 'something feels slow' to 'the pricing downstream is the cause.'"

<!--
Run this live. Don't narrate every click.

The closing line is the win. SE = translate technical signal into time-to-triage.
-->

---

# Live Demo — Outage

`./scripts/incident.sh outage`

[Switch to Dependencies → "Is It Us Or Them?" panel]

- Downstream success rate: **0%**
- API success rate: **~40%** (endpoints that don't touch downstream)

> Two lines, two seconds — you know it's the downstream.

The single most useful panel in the whole platform.

<!--
This is the panel that closes interviews. The visual is unambiguous.

Don't rush it. Let the room look at it for 5 seconds.
-->

---

# Live Demo — Fan-Out Cascade (600ms)

`./scripts/incident.sh latency 600`

Overview p95: elevated, not red.

Latency by endpoint:

- `/health`, `/market/quote/{symbol}`: ~650ms — acceptable
- `/accounts/{id}/positions`: **~1300ms** — broken

> The scenario most platforms miss. Big customers feel it; small customers don't.

<!--
This slide is the depth-flex. Most SE candidates show latency and outage.
Showing the cascade tells the interviewer you've thought about real-world
incident patterns, not just textbook ones.

The line about big customers vs small customers lands because every B2B
audience has lived this.
-->

---

# End-to-End Tracing

```bash
curl -H "X-Request-Id: trace-001" \
  http://localhost:8000/market/quote/AAPL

docker logs api | grep trace-001
docker logs downstream | grep trace-001
```

Same ID, both services. **No distributed tracing system required.**

> When a customer says "my position lookup failed at 3:47am," you grep both services for one ID.

<!--
This is the slide that proves you've thought about how customers actually report bugs.

It also leaves the door open to "and you'd layer OpenTelemetry on top of this
later." Which is the natural growth path.
-->

---

# Implementation Path

1. **30-min SRE review** — walk through the metric model
2. **Pilot 3 endpoints** — wrap your top 3 customer-facing endpoints
3. **Port dashboards** — into your existing Grafana
4. **Failure drill** — one scenario against staging, on-call watching
5. **Quantify** — time-to-detect, time-to-triage, before vs after
6. **Production rollout** — endpoint by endpoint

> *"Does that cadence work for you, or would you sequence it differently?"*

<!--
Always close with a concrete next step that puts the ball in the customer's court.

For SE interview audiences, this slide proves you know how to move a deal forward
without being pushy.
-->

---

<!-- _class: lead -->

# Questions

**Repository:** `observability-incident-triage`
**Full walkthrough docs:** `docs/`
**Incident scenarios:** `docs/incident-scenarios.md`
**On-call playbook:** `docs/troubleshooting-playbook.md`

abdiladif3h@gmail.com · linkedin.com/in/abdiladif-haibah

<!--
Q&A slide. Keep the contact info up so the interviewer doesn't have
to dig for it after the call.

Cheat sheet for likely questions is in docs/demo-script.md.
-->
