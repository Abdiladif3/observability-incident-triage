# Troubleshooting Playbook

The runbook for the on-call engineer. By symptom: which dashboard to open, which PromQL query narrows the cause, and what the likely root causes are.

This is the doc you hand to the customer's on-call rotation. It is companion to `incident-scenarios.md` — the scenarios doc explains *how to demo* failure modes; this doc explains *how to triage* them.

---

## Triage Decision Tree

```
You got paged. First check Overview.
│
├─ Request rate dropped to ~0?
│      → Service is down. Check container status. Possible deploy/restart.
│
├─ 5xx error rate elevated?
│      → Open Errors. See "Errors Elevated" below.
│
├─ p95 latency elevated, low/no errors?
│      → Open Latency. See "Latency Elevated" below.
│
└─ Everything looks normal but customers complain?
       → Open Latency, look at per-endpoint p95.
       → If one endpoint is dramatically worse, see "Fan-Out Cascade" below.
```

---

## Symptom: Errors Elevated

**Dashboard to open:** Errors

### Question 1 — Is one endpoint or all?

PromQL:

```
sum by (path) (rate(http_requests_total{job="api", status=~"5.."}[1m]))
```

- One endpoint failing → likely route-specific bug or one downstream dependency.
- All endpoints failing → likely shared infrastructure (database, auth provider, network).

### Question 2 — Is it us or the downstream?

Open Dependencies. Look at "Is It Us Or Them?":

- Downstream success rate at 0% → outage on the downstream. Page their vendor, post a status banner.
- Downstream success rate intermittent → rate limit, partial outage. Slower customer-facing impact, harder to communicate.
- Downstream success rate normal but api still failing → cause is local. Look at deploy history.

### Question 3 — When did it start?

- Use the time window selector in Grafana to find the start of the spike.
- Cross-reference with deploy log / change calendar.
- If timing matches a deploy: roll it back first, debug later.

### Likely Root Causes

| Pattern | Likely Cause |
| --- | --- |
| Single endpoint 5xx, downstream healthy | Recent code change, regression |
| All endpoints 5xx, downstream healthy | DB connectivity, auth provider, shared config |
| All downstream calls failing | Downstream vendor outage |
| Intermittent failures, same endpoint | Rate limit, flaky downstream |
| 502 with `downstream_unavailable` | The downstream returned 503 — page the vendor |
| 504 with `downstream_timeout` | The downstream is slow but not failing — see Latency below |

---

## Symptom: Latency Elevated

**Dashboard to open:** Latency

### Question 1 — Which endpoints?

Look at "p95 Latency by Endpoint." If one endpoint dominates:

- It calls downstream — see Dependencies dashboard.
- It does heavy local work (rare in this codebase) — look for recent changes.

### Question 2 — Is it the downstream?

PromQL:

```
histogram_quantile(0.95, sum by (target, le) (rate(downstream_request_duration_seconds_bucket[1m])))
```

- Downstream p95 climbing in lockstep with api p95 → downstream issue.
- Downstream p95 stable → cause is local (CPU, GC, queue, lock contention).

### Question 3 — Are we hitting the timeout?

If api p95 is pinned near 2.0s, the api is timing out downstream calls. This shows as 504s in the Errors dashboard.

Possible responses:

1. Increase `DOWNSTREAM_TIMEOUT_SECONDS` — if downstream is normally slow.
2. Add a retry layer — if downstream is intermittently slow.
3. Page the downstream vendor — if downstream is genuinely degraded.

### Likely Root Causes

| Pattern | Likely Cause |
| --- | --- |
| Single endpoint slow, downstream slow | Downstream cause. Check vendor status. |
| All endpoints slow, downstream healthy | Shared local resource — CPU, memory, network egress. |
| p95 pinned at exact timeout value | Timeout config issue. See Question 3. |
| Slow during traffic spikes only | Concurrency limit reached. Check container CPU limit. |
| One endpoint dramatically worse than others | Fan-out cascade. See below. |

---

## Symptom: Fan-Out Cascade

**Pattern:** Single-call endpoints look fine. One endpoint is dramatically slower than others.

**Dashboard to open:** Latency → "p95 Latency by Endpoint" panel.

### Confirm the fan-out

PromQL:

```
# api requests per second on the suspect endpoint
rate(http_requests_total{path="/accounts/{account_id}/positions"}[1m])
```

```
# downstream calls per second
rate(downstream_requests_total{target="pricing"}[1m])
```

If the ratio is significantly greater than 1:1, the endpoint is making multiple downstream calls per request — the fan-out is confirmed.

### Short-term Mitigation

- Recover the downstream if it's the cause.
- Cache the most-common downstream responses (e.g., quote cache with 5s TTL).
- Disable the affected endpoint if customer experience is unacceptable.

### Long-term Fix

- Parallelize the downstream calls (`asyncio.gather` in this codebase).
- Batch the downstream API if it supports it (`POST /pricing/quotes` with a list).
- Push the per-position data into the customer record so it doesn't need a live fetch.

Each tradeoff is a separate engineering conversation. The dashboards just tell you the conversation needs to happen.

---

## Symptom: Service Down

**Dashboard to open:** Overview — if request rate dropped to ~0, the api isn't receiving traffic.

Confirm:

```bash
docker compose ps
```

Look for the unhealthy container.

```bash
docker logs <container-name> --tail 100
```

Common causes:

- Crash on startup (config error, missing env var, dependency unavailable)
- OOM kill (check container memory limit)
- Health-check failure (the `/health` endpoint itself is returning non-200)

### Recovery

- `docker compose restart <service>` is the fast path.
- If it crashes immediately on restart, fix the config or roll back the deploy.

---

## When to Escalate

| Scenario | Escalation |
| --- | --- |
| Downstream vendor outage | Page the vendor, notify customer success |
| Production data corruption suspected | Page engineering manager + on-call lead, freeze deploys |
| Customer-impacting incident over 15 min | Open incident channel, assign incident commander |
| Cannot determine cause within 30 min | Page senior on-call, do not stay in tunnel vision |

---

## What to Tell Stakeholders

| Audience | Update format | Frequency |
| --- | --- | --- |
| Customer success | "Pricing requests are slow / failing. Cause is downstream vendor. Mitigation in progress." | Every 15 min during incident |
| Engineering leadership | Short status + ETA to recovery if known | Every 30 min |
| Status page | Customer-facing version of the customer success update | Real-time |
| Post-incident | Full timeline with dashboard screenshots | Within 24 hours |

The dashboards in this platform are the source of truth for all of these updates. Take screenshots at key moments — they make post-incident writeups dramatically faster.
