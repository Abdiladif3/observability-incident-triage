# Incident Scenarios

This is the playbook for the live triage demo. Each scenario is something a Sales Engineer can trigger on demand, walk the customer through, and resolve — all in under two minutes.

Every scenario follows the same shape:

1. **Pain** — what the customer feels in their portal
2. **Trigger** — the exact command to cause it (uses `scripts/incident.sh`)
3. **Symptoms** — what the on-call engineer sees
4. **Detection** — which dashboard surfaces the signal first
5. **Triage** — the PromQL query that narrows the cause
6. **Resolution** — how to recover
7. **Business impact** — what you tell the room
8. **Production note** — what would be different in real life

The platform must be running (`docker compose up -d`) and the traffic generator helps (`./scripts/generate-traffic.sh &`) so the graphs have a steady baseline.

---

## Scenario 1 — Downstream Latency Spike

> The trading portal is loading positions slowly. Customers are calling support.

### Trigger

```bash
./scripts/incident.sh latency 800
```

### Symptoms

- `GET /accounts/{id}/positions` jumps from ~10ms to ~1600ms
- `GET /market/quote/{symbol}` jumps from ~70ms to ~810ms
- No errors yet — everything is succeeding, just slowly

### Detection

**Overview dashboard** — the p95 latency stat panel turns yellow then red. The request-rate panel is unchanged (no drop in throughput, just slowness).

### Triage

Three questions to answer in order:

1. *Is it everywhere or one endpoint?*
   Open **Latency** dashboard → "p95 Latency by Endpoint."
   You'll see `/accounts/{account_id}/positions` worst (2x the cascade), then `/market/quote/{symbol}`, while `/health` and `/auth` style endpoints are unaffected.

2. *Is it us or the downstream?*
   Open **Dependencies** dashboard → "Downstream p95 Latency by Target."
   The `pricing` target latency tracks the api latency 1:1 (with the fan-out multiplier for the positions endpoint). Conclusion: it's the downstream.

3. *Quantify the impact.*
   PromQL:
   ```
   histogram_quantile(0.95, sum by (path, le) (rate(http_request_duration_seconds_bucket{job="api"}[1m])))
   ```

### Resolution

```bash
./scripts/incident.sh recover
```

p95 returns to baseline within one Prometheus scrape interval.

### Business Impact

> "Customers are still able to trade, but they think the platform is broken. This is the highest-churn incident type because the user has time to switch tabs. We saw it within 60 seconds because the same dashboard the on-call uses is what status-page automation reads from."

### Production Note

In production the cause might be a downstream provider deploying a slow query, a network path degradation, or a DNS resolution issue. The dashboards and triage path are the same — only the resolution is different (page the downstream vendor, route around them, or roll back our deploy if the cause is local).

---

## Scenario 2 — Intermittent Downstream Errors

> Some customers are seeing errors. Some aren't. Support tickets are stacking up.

### Trigger

```bash
./scripts/incident.sh errors 0.5
```

### Symptoms

- Roughly half of `/market/quote/{symbol}` calls return 502
- The other half succeed normally
- Customers complain inconsistently, which makes it hard to reproduce

### Detection

**Errors dashboard** — the "5xx Rate by Endpoint" panel shows `/market/quote/{symbol}` and `/accounts/{account_id}/positions` climbing. The "Status Code Mix" pie chart shows a meaningful 502 slice. The stacked panel shows the 502 layer growing over the 200 layer.

### Triage

1. *Which endpoints are failing?*
   PromQL:
   ```
   sum by (path) (rate(http_requests_total{job="api", status=~"5.."}[1m]))
   ```

2. *What are the downstream outcomes?*
   Open **Dependencies** → "Downstream Outcomes." You'll see `server_error` climbing while `success` falls. Combined with `success` being non-zero, this tells you it's *intermittent*, not a full outage.

3. *Is the api itself failing or just propagating?*
   The "Is It Us Or Them?" panel shows api success rate dropping in proportion to downstream success rate. They track together → it's downstream.

### Resolution

```bash
./scripts/incident.sh recover
```

### Business Impact

> "Intermittent failures are worse for trust than total outages. Customers retry, get inconsistent results, lose faith in the platform, and call support. The longer this runs, the more support load it creates. Detecting it as a partial-error pattern lets us communicate honestly — 'some pricing requests are failing' — instead of letting customers infer it themselves."

### Production Note

The most common real-world cause is a downstream rate limit being hit during a traffic spike. Our normalized `recommended_action` in the API response would tell customer engineers "Retry with backoff," and a status page update would tell end users.

---

## Scenario 3 — Downstream Total Outage

> The pricing feed is completely down. Nothing involving prices works.

### Trigger

```bash
./scripts/incident.sh outage
```

### Symptoms

- `/market/quote/{symbol}` — 502 every time
- `/accounts/{id}/positions` — 502 (cascade — the first downstream call fails, the endpoint can't proceed)
- `/admin/risk-check` — 502
- `/accounts/{id}` and `/health` — still 200 (no downstream dependency)

### Detection

**Errors dashboard** — 5xx rate jumps sharply, immediate visual signal. The "All Responses Stacked by Status" panel shows the 200 layer collapsing.

But the *real* tell is on the **Dependencies** dashboard — the "Is It Us Or Them?" panel shows the downstream success rate going to **zero**, while the api success rate stays partially elevated (the endpoints that don't call downstream still work).

### Triage

That one panel is enough. You don't need to PromQL anything. The story is visually obvious:

- Downstream success rate: 0%
- API success rate: ~40% (only the local endpoints)
- Therefore: the downstream is down, and we're a passthrough.

### Resolution

```bash
./scripts/incident.sh recover
```

### Business Impact

> "Total outages are easier to communicate than intermittent ones — you can put up a status page banner immediately. The api's normalized error responses are critical here: every customer integration team that hits us gets back a 502 with `error: downstream_unavailable` and a `recommended_action`. They don't have to guess what to do."

### Production Note

In production this is when an incident commander gets paged. The Sales Engineer's job isn't to fix the outage — it's to make sure customers and customer-success teams know what's happening before they have to ask.

---

## Scenario 4 — Timeout Cascade

> Customers are reporting "the platform feels frozen." The dashboards aren't screaming yet.

### Trigger

```bash
./scripts/incident.sh timeout
```

(This sets downstream latency to 3000ms, which exceeds the api's 2s `DOWNSTREAM_TIMEOUT_SECONDS`.)

### Symptoms

- Every downstream-dependent endpoint returns 504 *after exactly 2 seconds*
- Endpoints that don't call downstream are unaffected
- This is the trickiest scenario because it looks like a "slowness" problem from the outside

### Detection

**Overview** — p95 latency stat panel pins at ~2.0s (exactly the timeout value). This is a tell: when p95 sits perfectly on the timeout threshold, the cause is almost certainly a timeout, not real latency.

**Errors** — 504 starts appearing in the "Status Code Mix" pie. 504 is in the 5xx family but means something specific.

### Triage

1. *Why is p95 pinned at exactly 2s?*
   PromQL:
   ```
   histogram_quantile(0.95, sum by (path, le) (rate(http_request_duration_seconds_bucket{job="api"}[1m])))
   ```
   Multiple endpoints reporting `≈2.005s` is the smoking gun.

2. *Confirm the cause is downstream.*
   On **Dependencies**, "Downstream Outcomes" shows the `timeout` series climbing.

### Resolution

```bash
./scripts/incident.sh recover
```

### Business Impact

> "Timeout cascades teach the team something important: 'slow' and 'timing out' are different problems with different fixes. Real latency means you investigate the slow path. Timeouts on a fixed value mean you investigate the *timeout configuration* — is 2s right? Is the downstream genuinely getting slower over time? Should we add a retry layer? These are config decisions, not code decisions, and observability is how you make them with data."

### Production Note

The timeout value (`DOWNSTREAM_TIMEOUT_SECONDS=2`) is the most important config knob on the api. Too short and you create artificial outages during normal downstream slowness. Too long and one slow dependency takes down the whole platform. Watching p95 latency over time is how you calibrate it.

---

## Scenario 5 — Fan-Out Cascade (the SE-favorite)

> Single-product lookups are fine. The positions page is unusable.

### Trigger

```bash
./scripts/incident.sh latency 600
```

This is *not* a dramatic latency injection. 600ms is well within timeout. It's the cascade that makes it visible.

### Symptoms

- `GET /market/quote/AAPL` — ~650ms. Acceptable.
- `GET /accounts/acct-001/positions` — ~1300ms (2 positions × 600ms + overhead). Bad.
- `GET /accounts/acct-002/positions` — ~700ms (1 position). Acceptable.
- The pain is non-uniform: accounts with many positions feel broken; accounts with few don't.

### Detection

**Overview** p95 latency is elevated but not red — easy to miss in a noisy room. **Latency** dashboard "p95 Latency by Endpoint" is where the story is: `/accounts/{account_id}/positions` is dramatically worse than every other route.

### Triage

1. *Why is one endpoint so much worse than the others?*
   The positions endpoint makes N downstream calls sequentially, one per position held. PromQL:
   ```
   sum by (path) (rate(downstream_requests_total[1m]))
   ```
   You'll see the `pricing` target's call rate is much higher per positions-endpoint request than per quote-endpoint request.

2. *Quantify the amplification.*
   Compare `rate(http_requests_total{path="/accounts/{account_id}/positions"})` to `rate(downstream_requests_total{target="pricing"})`. A ratio of ~1:N tells you the endpoint makes N downstream calls.

### Resolution

Short-term: `./scripts/incident.sh recover`.

Long-term: parallelize the downstream calls with `asyncio.gather`. The `routes/accounts.py` code intentionally calls them sequentially to make this cascade demoable.

### Business Impact

> "This is the scenario hiring managers care most about, because it's the one most platforms get wrong. A 'fast enough' downstream can still produce a broken-feeling experience if a single endpoint fans out. Customers with the most data feel it worst — usually your biggest, most strategic accounts. The dashboards have to surface per-endpoint latency, not just overall, or you'd miss it entirely."

### Production Note

The fix isn't always parallelization. Sometimes the answer is batching the downstream API (`POST /pricing/quotes` with a list of symbols), or caching, or pushing the per-position price into the customer record rather than fetching it live. Each tradeoff is a separate conversation with the customer.

---

## Scenario Selection for a Demo

You should never run all five in a single demo. Pick the two or three that match what the customer cares about:

| Customer profile | Recommended scenarios |
|---|---|
| Trading / fintech | Scenario 1 (latency) + Scenario 5 (fan-out) — speed is money |
| Healthcare / regulated | Scenario 2 (intermittent) + Scenario 3 (outage) — uptime and incident comms |
| Developer-platform / API-first | Scenario 4 (timeout) + Scenario 5 (fan-out) — config nuance |
| General SaaS | Scenario 1 + Scenario 3 — covers latency and availability |

Keep Scenario 4 in your back pocket as the "what about X?" answer during Q&A. It's the most nuanced of the five and shows depth without taking demo time.
