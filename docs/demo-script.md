# Demo Script

A 10–15 minute Sales Engineering walkthrough of the Observability & Incident Triage Demo Platform.

This script is designed to be presented, not read aloud. Use it as a structure — speak naturally and let the customer's questions pull you into the relevant sections.

---

## Audience

Mixed technical + business: typically an SRE / Platform Engineer, an Engineering Manager, a Support/Customer Success lead, and a Product Manager. Plan to land business value with everyone, then go a layer deeper on the technical points when prompted.

## Pre-demo checklist

Before the call:

- `docker compose up -d` and confirm all 4 containers are `(healthy)`
- `./scripts/generate-traffic.sh &` running in the background so dashboards have a baseline
- Grafana open in a browser, **Overview** dashboard loaded, set to 15m time window with 10s auto-refresh
- Tabs ready for **Latency**, **Errors**, **Dependencies** dashboards
- Terminal ready for `./scripts/incident.sh` commands
- `./scripts/incident.sh status` shows `mode: normal` (no stuck simulation from a previous run)

---

## 1. Customer Pain (≈ 2 min)

Set the scene. Use the customer's own language back to them if discovery already happened.

> "Today, when an incident happens, your engineering team is usually told about it by a customer. By the time anyone acknowledges, the impact window is already minutes old. And then the next 15 to 30 minutes is spent figuring out whether the cause is one of your services, a downstream dependency, infrastructure, or a recent deploy. What I'm going to show you is a pattern that shortens both of those timers."

Reference: `docs/customer-scenario.md` is the long form of this for the customer's reference after the call.

---

## 2. Architecture in One Picture (≈ 1 min)

Open `docs/architecture.md` and show the system diagram.

Talking points:

- Two services: a customer-facing api and a downstream that stands in for a real third-party (pricing, payments, KYC — whatever your customer's actual downstream is).
- Each service exposes structured JSON logs and a Prometheus `/metrics` endpoint.
- Prometheus scrapes both every 10 seconds.
- Grafana queries Prometheus and serves the dashboards your team uses during an incident.

Hand-off question: *"Before I dive in — is this the same shape as what you have today, or are you missing a piece of this stack?"*

---

## 3. The Dashboards (≈ 2 min)

Open Grafana. Walk through the four dashboards quickly so the audience knows the menu.

> "Four dashboards. Each is designed to answer one specific question."

- **Overview** — "Is the platform healthy?" Three stats up top (req/s, 5xx %, p95 latency) plus the request-rate time series. This is the dashboard the on-call rotation opens first.
- **Latency** — "Where is the slowness?" Top panel is p50/p95/p99 over time. Middle is p95 broken out per endpoint. Bottom is a table of the slowest endpoints right now.
- **Errors** — "What's failing and how often?" Per-endpoint 5xx rate, status-code mix, and an all-responses stacked view.
- **Dependencies** — "Is it us or them?" Downstream call rate, outcome breakdown, p95 latency, and side-by-side success rate.

> "The dashboards aren't comprehensive — they're opinionated. Each one is designed to be the first stop for a specific class of incident."

---

## 4. The Healthy Baseline (≈ 1 min)

Stay on Overview. Point to the traffic generator running in the background.

> "Right now we're running about 12 requests a second across a mix of endpoints — the customer profile of a steady-state weekday. p95 latency is around 80ms. Error rate is zero. This is the baseline. The mental model I want to land is: any drift from this picture is a signal."

---

## 5. Live Demo — Pick 3 Scenarios (≈ 5–6 min)

Don't run all five. Pick the ones that match the customer's pain. Reference `docs/incident-scenarios.md` for the full menu. A common three-scenario set for a generic SE pitch:

### Scenario A — Downstream Latency (≈ 2 min)

```bash
./scripts/incident.sh latency 800
```

- Watch the Overview p95 stat panel go yellow then red within ~10 seconds.
- Switch to Latency dashboard — show the per-endpoint breakdown. Point out that `/accounts/{id}/positions` is hit hardest (fan-out amplification).
- Switch to Dependencies — show downstream p95 climbing in lockstep. That's the "us or them" answer.

> "The thing I want to call out: in 15 seconds I went from 'something feels slow' to 'the pricing downstream is the cause, and the worst-affected endpoint is positions because it makes N sequential downstream calls.' That's the triage path you want your on-call to follow without thinking."

Recover before moving on:

```bash
./scripts/incident.sh recover
```

### Scenario B — Total Outage (≈ 1.5 min)

```bash
./scripts/incident.sh outage
```

- Errors dashboard 5xx rate spikes immediately. Status-code mix shifts to red.
- Switch to Dependencies → "Is It Us Or Them?" — downstream success rate drops to zero, api success rate stays partially elevated.

> "This is the single most useful panel in an outage. The downstream is at zero. The api isn't — because endpoints like `/health` and `/accounts/{id}` don't touch the downstream. Visually obvious in two seconds where the problem is. Your support team can post a status banner immediately."

Recover:

```bash
./scripts/incident.sh recover
```

### Scenario C — Fan-Out Cascade (≈ 1.5 min)

```bash
./scripts/incident.sh latency 600
```

- Overview p95 is elevated but not screaming. Easy to miss in a noisy room.
- Open Latency → "p95 by Endpoint." The positions endpoint is dramatically worse than the others.

> "This is the scenario hiring managers — and incident commanders — care most about, because it's the one most platforms miss. 'Fast enough' downstream + a fan-out endpoint = broken-feeling experience for your largest customers. The dashboards have to surface per-endpoint latency, not just the overall."

Recover:

```bash
./scripts/incident.sh recover
```

---

## 6. End-to-End Tracing (≈ 1 min)

Open a terminal. Hit any endpoint with a custom request ID:

```bash
curl -H "X-Request-Id: customer-complaint-001" http://localhost:8000/market/quote/AAPL
```

Then:

```bash
docker logs api 2>&1 | grep customer-complaint-001
docker logs downstream 2>&1 | grep customer-complaint-001
```

> "Same ID, both services. When a customer says 'my position lookup failed at 3:47am,' you give that to your on-call and they grep both services for that single ID. End-to-end trace, no distributed tracing system required."

---

## 7. Implementation Path (≈ 1 min)

Open `docs/troubleshooting-playbook.md` and `docs/implementation-handoff.md` briefly.

> "The playbook is the runbook your on-call team would carry — by symptom, here's the dashboard, here's the PromQL query, here's the likely cause. The handoff doc is how we'd line up owners for environments, deploy pipelines, alert rules, and the rollback plan. Nothing here is meant to surprise an SRE team at 3am."

---

## 8. Recommended Next Steps (≈ 1 min)

> "From here, the natural sequence is a 30-minute review with your SRE lead to walk through the metric model and dashboard set. After that, I'd want to pilot this against your top three customer-facing endpoints — wrap them in the same instrumentation pattern, populate the dashboards with real traffic, run one failure drill against staging. Does that cadence work for you?"

---

## Q&A Cheat Sheet

| Customer says... | You respond with... |
| --- | --- |
| "We already have Datadog / New Relic / Honeycomb." | Reframe — the pattern, not the tooling. The dashboards translate; the *opinions* about which question each dashboard answers are the SE story. |
| "What about traces?" | The request_id propagation here is the foundation. Layering OpenTelemetry on top is the natural extension. |
| "How does this scale?" | Path-template labels and bounded label cardinality are the design choices that keep cardinality sane. Show the metric inventory. |
| "We need alerting." | Acknowledge it. Alertmanager + Grafana Alerts plug in on the same metrics. Skipped for the v1 demo, available in the architecture. |
| "What about the database?" | The pattern applies the same way. Every downstream is a `target` in the metric. We added one target (pricing); your real system has more. |
| "Can we see this on our cloud?" | Walk them through how the docker-compose stack maps to a managed container runtime + a managed Prometheus + a managed Grafana. |
