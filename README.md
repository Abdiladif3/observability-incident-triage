# Observability & Incident Triage Demo Platform

[![CI](https://github.com/Abdiladif3/observability-incident-triage/actions/workflows/ci.yml/badge.svg)](https://github.com/Abdiladif3/observability-incident-triage/actions/workflows/ci.yml)

A four-service Docker Compose stack that demonstrates a complete production-shaped observability pattern: an instrumented backend API, a controllable downstream dependency, Prometheus scraping, and Grafana with provisioned dashboards. Built and structured as a Sales Engineering walkthrough — customer pain, architecture, dashboards, live incident triage, and implementation path.

This is not a production monitoring system. It is an SE demo with production-shaped patterns.

---

## What It Shows

- Two instrumented FastAPI services with structured JSON logging and Prometheus metrics
- End-to-end request-ID propagation across services (foundation for distributed tracing)
- 5 demoable incident scenarios with normalized downstream errors and recommended actions
- 4 production-shaped Grafana dashboards, each answering one specific operational question
- A complete SE documentation set covering customer scenario, architecture, discovery, demo script, incident scenarios, troubleshooting playbook, and implementation handoff
- A green CI pipeline (39 tests passing, both Docker images building) on every push

---

## Quick Start

```bash
git clone https://github.com/Abdiladif3/observability-incident-triage
cd observability-incident-triage
docker compose up -d
```

This launches:

- `api` at <http://localhost:8000> (Swagger at `/docs`)
- `downstream` at <http://localhost:8001> (Swagger at `/docs`)
- `prometheus` at <http://localhost:9090>
- `grafana` at <http://localhost:3000> (anonymous viewer access, no login)

Generate baseline traffic so the dashboards have something to render:

```bash
./scripts/generate-traffic.sh
```

Trigger an incident scenario:

```bash
./scripts/incident.sh latency 800     # 800ms downstream latency
./scripts/incident.sh outage          # 100% downstream 503
./scripts/incident.sh recover         # back to normal
./scripts/incident.sh help            # full menu
```

Open <http://localhost:3000/dashboards> → **Acme Trading** folder → pick a dashboard.

---

## Architecture

```
API Client                            On-Call Engineer
    │                                       │
    ▼                                       ▼
api (:8000)  ──►  downstream (:8001)    grafana (:3000)
    │                  │                    │
    ▼                  ▼                    │ queries
  /metrics          /metrics                │
    │                  │                    │
    └──►  prometheus (:9090)  ◄─────────────┘
              ▲                  ▲
              └──── scrapes ─────┘
                  every 10s
```

Full system diagram, sequence diagram, and design decisions live in [`docs/architecture.md`](docs/architecture.md).

---

## Project Layout

```
observability-incident-triage/
├── README.md
├── docker-compose.yml
├── .github/workflows/ci.yml         CI: tests + Docker build on every push
├── apps/
│   ├── api/                         Instrumented backend API (FastAPI, port 8000)
│   │   ├── src/                       routes, middleware, services, metrics
│   │   ├── tests/                     27 pytest tests
│   │   └── Dockerfile
│   └── downstream/                  Simulated downstream service (FastAPI, port 8001)
│       ├── src/                       routes, middleware, simulation modes
│       ├── tests/                     12 pytest tests
│       └── Dockerfile
├── observability/
│   ├── prometheus/prometheus.yml    Scrape config
│   └── grafana/
│       ├── provisioning/              Datasource + dashboard auto-load
│       └── dashboards/                4 dashboard JSON files
├── scripts/
│   ├── generate-traffic.sh          Baseline traffic for demos
│   └── incident.sh                  Trigger named incident scenarios
└── docs/                            Sales Engineering walkthrough material
    ├── customer-scenario.md
    ├── architecture.md
    ├── discovery-questions.md
    ├── incident-scenarios.md
    ├── troubleshooting-playbook.md
    ├── demo-script.md
    ├── demo-transcript.md
    ├── implementation-handoff.md
    └── se-demo-deck.md
```

---

## The Four Dashboards

Each dashboard is opinionated. Each answers one specific operational question.

| Dashboard | Question | Key Panel |
| --- | --- | --- |
| **Overview** | Is the platform healthy right now? | p95 latency stat with thresholds |
| **Latency** | Where is the slowness? | p95 by endpoint |
| **Errors** | What's failing and how often? | 5xx rate by endpoint + status-code mix |
| **Dependencies** | Is it us or them? | "Is It Us Or Them?" — api vs downstream success rate |

The **"Is It Us Or Them?"** panel is the single most useful visual in the platform. During an outage, the two lines diverge unambiguously — you know within two seconds where the problem lives.

---

## Incident Scenarios

5 scenarios are triggerable on demand. Full table in [`docs/incident-scenarios.md`](docs/incident-scenarios.md).

| Scenario | Trigger | What it demonstrates |
| --- | --- | --- |
| Downstream latency spike | `./scripts/incident.sh latency 800` | Single-call slowness + per-endpoint cascade |
| Intermittent errors | `./scripts/incident.sh errors 0.5` | Partial failures, harder to communicate than total outages |
| Total outage | `./scripts/incident.sh outage` | "Is It Us Or Them?" panel sells itself |
| Timeout cascade | `./scripts/incident.sh timeout` | p95 pinned at exactly the timeout value — config tell |
| Fan-out cascade | `./scripts/incident.sh latency 600` | Moderate latency × N positions = broken positions endpoint |

---

## SE Walkthrough

The demo is designed as a 10–15 minute Sales Engineering presentation. Run the docs in this order:

1. [`docs/customer-scenario.md`](docs/customer-scenario.md) — who the customer is and what they need
2. [`docs/discovery-questions.md`](docs/discovery-questions.md) — the questions that shape the conversation
3. [`docs/architecture.md`](docs/architecture.md) — system and sequence diagrams
4. [`docs/incident-scenarios.md`](docs/incident-scenarios.md) — the 5 named scenarios
5. [`docs/demo-script.md`](docs/demo-script.md) — section-by-section talk track with live actions
6. [`docs/demo-transcript.md`](docs/demo-transcript.md) — the natural-sounding spoken version
7. [`docs/troubleshooting-playbook.md`](docs/troubleshooting-playbook.md) — on-call decision tree
8. [`docs/implementation-handoff.md`](docs/implementation-handoff.md) — customer team handoff template
9. [`docs/se-demo-deck.md`](docs/se-demo-deck.md) — Marp slide deck

---

## Local Development

Each service has its own Python venv. To run them outside Docker:

```bash
cd apps/api
python3.12 -m venv .venv
.venv/bin/pip install -e .[dev]
.venv/bin/python -m uvicorn src.main:app --reload --port 8000
```

Same pattern for `apps/downstream` on port 8001.

Run tests:

```bash
cd apps/api && .venv/bin/python -m pytest -v
cd apps/downstream && .venv/bin/python -m pytest -v
```

---

## Tech Stack

- **Backend**: Python 3.12, FastAPI, Pydantic v2
- **HTTP client**: httpx (AsyncClient, enforced timeouts)
- **Logging**: structlog with JSON output + stdlib bridge
- **Metrics**: prometheus-client
- **Containers**: Docker, Docker Compose
- **Observability**: Prometheus, Grafana (with provisioned datasource + dashboards)
- **Testing**: pytest + FastAPI TestClient + httpx MockTransport
- **CI**: GitHub Actions

---

## Companion Project

[`api-integration-security`](https://github.com/Abdiladif3/api-integration-security) — an API integration and security platform demo, structured the same way.
