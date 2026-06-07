# Implementation Handoff

The artifact a Sales Engineer would leave behind for the customer's SRE / Platform team after a successful technical walkthrough. The bridge between "we like this" and "we have it deployed."

This document is a template — the customer's team would fill in the empty fields. It is not a runbook for the demo platform; it is the plan for the customer's adoption.

---

## 1. Engagement Summary

| Field | Value |
| --- | --- |
| Customer | _Acme Trading Platform (replace with real customer name)_ |
| Primary use case | Reducing time-to-detect and time-to-triage for backend incidents |
| Walkthrough date | _to be filled_ |
| Stakeholders present | SRE / Platform, Engineering Manager, Support / CS, Product |
| Pilot scope | Top 3 customer-facing endpoints, single downstream dependency |
| Target go-live | _to be filled_ |

## 2. Roles and Owners

| Area | Customer Owner | Internal Owner (SE side) | Status |
| --- | --- | --- | --- |
| API instrumentation | SRE | SE + Engineering | open |
| Dashboard provisioning | SRE | SE | open |
| Alert rule definition | SRE | SE | open |
| Prometheus retention + storage | Platform | SE | open |
| Grafana access + auth | Platform | SE | open |
| Runbook integration | SRE / On-call lead | SE | open |
| Status page integration | Support / CS | SE | open |
| Post-incident review process | Engineering Manager | SE | open |

## 3. Environments

| Environment | Purpose | Notes |
| --- | --- | --- |
| local | Developer machines | Docker Compose only |
| staging | Failure drills, dashboard tuning | Real Prometheus + Grafana, controllable failure modes |
| production | Live customer traffic | Approved after pilot validation |

## 4. Decisions Captured

| Decision | Outcome / Direction |
| --- | --- |
| Metric backend | Customer's existing Prometheus / Mimir / Cortex / managed service |
| Visualization | Customer's existing Grafana or replacement |
| Log aggregation | Forward structlog JSON to customer's existing log pipeline |
| Distributed tracing | Layer OpenTelemetry on top of request_id propagation when ready |
| Alerting | Wire Alertmanager / Grafana Alerts to the new metrics |
| Dashboard ownership | SRE / Platform team owns provisioning, engineering teams own their service dashboards |
| Endpoint rollout order | Top 3 customer-facing endpoints first, then expand by impact |

## 5. Open Questions / Risks

Items that surfaced during the walkthrough and still need resolution:

- _What is the customer's current Prometheus retention budget?_
- _Are the four demo dashboards a fit, or does the SRE team want to start with one and iterate?_
- _Does the customer already use request-ID propagation? If yes, what header name?_
- _What is the customer's preferred alerting destination — PagerDuty, Opsgenie, native Slack?_
- _Are there compliance requirements that affect log retention or PII in metrics?_

## 6. Suggested Next Steps

In order:

1. **30-minute SRE review** — walk through the metric model, dashboards, and request-ID pattern with the SRE lead.
2. **Pilot instrumentation** — wrap top 3 customer-facing endpoints in the same middleware pattern.
3. **Dashboard provisioning** — port the four dashboard JSON files into the customer's Grafana (with adjusted job labels).
4. **Failure drill** — run one scenario from `incident-scenarios.md` against staging during business hours with the on-call rotation watching.
5. **Quantify** — time-to-detect, time-to-triage, before vs after. This is the conversation that justifies broader rollout.
6. **Production rollout** — endpoint by endpoint, fastest impact first.

## 7. References

- `docs/customer-scenario.md` — the business problem this implementation solves
- `docs/architecture.md` — system diagram, endpoints, metric inventory, design decisions
- `docs/incident-scenarios.md` — the 5 named incident scenarios
- `docs/troubleshooting-playbook.md` — on-call decision tree
- `docs/demo-script.md` — the 10–15 minute walkthrough
- `infra/deployment-plan.md` — cloud deployment path (when written)

## 8. Contact

- _Customer SRE lead_: name + email
- _Internal Sales Engineer_: name + email
- _Escalation_: account team / customer success owner
