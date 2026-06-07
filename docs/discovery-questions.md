# Discovery Questions

These are the questions a Sales Engineer would ask the customer's SRE, engineering, support, and product stakeholders before recommending an observability and incident-triage pattern. The goal is not to interrogate — it is to understand what an incident actually feels like inside their org today, and where the slow points are.

Use this as a discovery bank. In a 10–15 minute walkthrough, you pick 4–6 questions across categories, not all of them.

---

## Current Observability Posture

- What tooling do you use today for metrics, logs, and traces?
- How are metrics collected — push, pull, agent-based, or library-based?
- Who owns the dashboards that the on-call rotation uses?
- Where do your logs live, and who can query them?
- How many separate places does someone have to look during an incident?
- When was the last time someone built a dashboard, and what triggered them to do it?

## Incident Detection and Triage

- How are incidents detected today — alerts, customer reports, or both?
- What is your current mean time to detect, and your mean time to recover?
- When an alert fires, what is the first thing the on-call engineer looks at?
- How do you tell whether the cause is internal or a downstream dependency?
- Has the team ever spent more than 30 minutes deciding *which* service is the cause?
- What was the last incident that caused real customer pain, and how was it resolved?

## On-Call Experience

- How many alerts does an on-call engineer receive per shift on average?
- What percentage of those alerts result in real action?
- How is alert fatigue handled — runbooks, alert grooming, or escalation rules?
- What does a good on-call shift look like for your team?
- Are engineers rotated through on-call, or is there a dedicated SRE team?
- Are there incident scenarios that recur, and what would it take to make them stop?

## Cross-Team Visibility

- Who outside engineering needs visibility into incidents — support, product, leadership?
- How does support get information during an active incident?
- How are post-incident findings shared with product and leadership?
- What reliability metrics show up in executive review?
- Has a customer ever known about an incident before the team did?

## Reliability Investment

- What was the last incident that materially affected revenue or customer trust?
- What reliability investments have been proposed but not funded?
- What would justify funding observability work this quarter?
- Is reliability a separate engineering goal, or rolled into feature delivery?
- If you could change one thing about how on-call works here, what would it be?

---

## How These Map to the Demo

The walkthrough is designed to answer the questions above without needing to read from a script. Each demo moment ties back to one or more discovery threads:

| Discovery Thread | Demo Moment |
| --- | --- |
| "Which service is to blame?" | Dependencies dashboard → "Is It Us Or Them?" panel |
| Alert fatigue / signal-to-noise | Errors dashboard status-code mix — separating 5xx from baseline noise |
| Slow MTTT (mean time to triage) | Walking from Overview → Latency → Dependencies in <60s |
| Customer-detected incidents | Showing the dashboards lighting up *before* a customer would notice |
| Recurring root causes | Trend lines on the Latency dashboard for the same endpoint over time |
| Cross-team visibility | Anonymous viewer access on Grafana — support can watch without paging engineering |
| "Is it the deploy?" | Audit trail of request IDs through structured logs |
| Cascading failures | The `/positions` fan-out scenario in incident-scenarios.md |
