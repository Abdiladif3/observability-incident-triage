# Customer Scenario

## Customer Overview

**Customer:** Acme Trading Platform
**Industry:** Financial services SaaS
**Company Size:** Mid-market, growth-stage (Series C, ~400 employees)
**Primary Use Case:** Reducing time-to-detect, time-to-triage, and time-to-recover for backend incidents that affect customer-facing trading workflows.

Acme Trading Platform operates a high-traffic backend that processes order intake, position lookups, and account activity for a customer base of brokers and prop trading firms. Their backend talks to a half-dozen downstream dependencies — pricing feeds, clearing partners, KYC providers, and internal risk services — and a slowdown in any of them is felt by their end customers immediately.

The platform's growth has outpaced its observability. The team can see *that* something is wrong, but rarely *why*, and almost never quickly enough to communicate proactively to customers.

---

## Business Problem

Acme Trading Platform's engineering team is on-call around the clock, but their existing observability stack is making the on-call burden worse, not better.

Their current state creates several problems:

- Incidents are routinely detected by customers, not by engineering.
- When an incident is detected, the team cannot tell whether the cause is one of their own services or a downstream dependency.
- Alert volume is high and signal-to-noise is poor, so on-call engineers acknowledge alerts on instinct rather than triage them.
- Different teams look at different dashboards, so a single incident is investigated three times in parallel.
- Post-incident reviews surface the same root causes repeatedly because the data to fix them upstream is not visible.
- Support cannot give customers status updates during an incident because they do not have a reliable way to see what the platform is doing in real time.

The customer wants an opinionated observability pattern that shortens time-to-detect, shortens time-to-triage, and gives every stakeholder — engineering, support, and product — a single source of truth during an incident.

---

## Stakeholders

### Site Reliability / Platform Engineer

Responsible for keeping the backend healthy and for the on-call rotation.

Key concerns:

- Metric instrumentation across services
- Dashboards that answer "is it us or them" in under sixty seconds
- Reducing alert noise without missing real signal
- Standardized logging and request correlation
- A practical incident playbook the team will actually use

### Engineering Manager

Responsible for the team's sustainable pace and the on-call burden.

Key concerns:

- Mean time to detect and mean time to recover
- On-call hours and pager fatigue
- Eliminating recurring incident root causes
- Justifying observability investment to leadership

### Support / Customer Success

Responsible for communicating with affected customers during an incident.

Key concerns:

- Real-time visibility into platform health
- Ability to answer "is this happening to other customers too?"
- Status page accuracy and proactive customer outreach
- Shared vocabulary with engineering during an active incident

### Product Manager

Responsible for prioritizing reliability work alongside feature work.

Key concerns:

- Reliability data that drives roadmap decisions
- Customer-perceived performance metrics, not just internal ones
- Trend reporting for executive review
- Visibility into which features are causing the most incident load

---

## Current Pain Points

Acme Trading Platform is experiencing the following pain points:

1. **Customer-Detected Incidents**
   The first signal of an incident is often a support ticket or a tweet, not an alert. By the time engineering acknowledges, the customer impact window is already minutes old.

2. **Long Mean Time to Triage**
   When an alert fires, the on-call engineer spends fifteen-to-thirty minutes determining whether the cause is one of their own services, a downstream dependency, an infrastructure issue, or a recent deploy.

3. **Alert Fatigue**
   On-call engineers receive too many alerts per shift. Most are noise. Real signal gets ignored because it looks like more noise.

4. **No Shared View of an Incident**
   Engineering, support, and leadership look at different dashboards, screenshots, and Slack threads. During a high-pressure incident, that fragmentation slows everything down.

5. **Root Causes Recur**
   The same patterns of incident — slow downstream calls, cascading queue buildup, deploy-related latency regressions — recur because the post-incident data does not surface them clearly enough to prioritize a fix.

6. **No Real-Time Customer Communication Path**
   Support cannot tell customers what is happening during an incident because they do not have a reliable, non-engineering-facing view of platform health.

---

## Proposed Solution

Build an observability and incident triage pattern that allows Acme Trading Platform to:

- Instrument a representative backend API with structured logs, request correlation IDs, and Prometheus metrics covering request volume, latency, error rate, and downstream dependency health.
- Operate a simulated downstream dependency that can be made to fail in realistic, controllable ways (latency injection, error injection, dependency unavailability).
- Visualize the platform's health through a small set of opinionated Grafana dashboards, each designed for a specific question: *Is the platform healthy? Where is the latency coming from? Where are the errors? Is a downstream dependency the cause?*
- Run a documented set of incident scenarios end-to-end, so the on-call rotation can practice triage in a low-stakes environment.
- Provide a troubleshooting playbook that turns "I got paged" into a repeatable triage workflow.
- Provide a Sales Engineering walkthrough that explains how the customer's existing systems would adopt this pattern incrementally.

---

## Success Criteria

The project is successful if Acme Trading Platform can:

- Detect incidents within their backend before customers do.
- Determine in under sixty seconds whether the cause of an incident is internal or a downstream dependency.
- Reduce mean time to recover for the top three incident types.
- Operate a single set of dashboards used by engineering, support, and product.
- Follow a documented triage playbook during an incident instead of inventing a process every time.
- Surface recurring root causes through metric trends, not only through manual post-incident review.

---

## Demo Goals

The walkthrough should show:

1. A healthy steady-state baseline on the dashboards.
2. A latency spike on a single endpoint, isolated and explained.
3. An error-rate increase, broken down by endpoint and root cause.
4. A downstream dependency failure, surfaced clearly as external, not internal.
5. A cascading slowdown caused by one slow endpoint blocking others.
6. A recovery to baseline after the underlying cause is removed, with the incident timeline visible in metrics.

The goal is not only to show that observability tooling works. It is to explain how the platform helps the customer detect faster, triage faster, and communicate faster.

---

## Sales Engineering Angle

This project is designed to simulate how a Sales Engineer would guide a technical customer through adopting an observability pattern for a high-traffic backend.

The walkthrough should cover:

- Customer pain discovery
- Current-state observability problems
- Proposed instrumentation and dashboard model
- Live incident triage demonstration
- Business impact (MTTR, on-call burden, customer perception)
- Implementation handoff for the customer's engineering team
- Recommended next steps for a pilot deployment

By the end of the walkthrough, the customer should understand how their on-call rotation, their incident process, and their customer communications would all improve if they adopted this pattern.

---

## Example Discovery Questions

### Current Observability Posture

- What tooling do you use today for metrics, logs, and traces?
- How are metrics collected — push, pull, agent-based, or library-based?
- Who owns the dashboards that the on-call rotation uses?
- Where does your log data live, and who can query it?

### Incident Detection and Triage

- How are incidents detected today — alerts, customer reports, or both?
- What is your current mean time to detect and mean time to recover?
- When an alert fires, what is the first thing the on-call engineer looks at?
- How do you tell whether the cause is internal or a downstream dependency?

### On-Call Experience

- How many alerts does an on-call engineer receive per shift on average?
- What percentage of those alerts result in real action?
- How is alert fatigue handled — runbooks, alert grooming, or escalation rules?
- What does a good on-call shift look like for your team?

### Cross-Team Visibility

- Who outside engineering needs visibility into incidents?
- How does support get information during an active incident?
- How are post-incident findings shared with product and leadership?
- What reliability metrics show up in executive review?

### Reliability Investment

- What was the last incident that materially affected revenue or customer trust?
- What reliability investments have been proposed but not funded?
- What would justify funding observability work this quarter?

---

## Recommended Next Steps

After the initial walkthrough, the recommended implementation path is:

1. Identify the top three customer-facing endpoints and instrument them first.
2. Define the four dashboards the on-call rotation will actually use — overview, latency, errors, dependencies.
3. Pilot the triage playbook during the next on-call rotation in a low-traffic environment.
4. Wire the existing alert rules into the new dashboards so on-call has one place to land.
5. Run a controlled failure drill against staging using the documented incident scenarios.
6. Review the data with engineering, support, and product after thirty days and refine the dashboard set.
7. Expand instrumentation to the rest of the backend as the team gains confidence.
8. Add alerting refinements only after the dashboards and triage playbook are established.
