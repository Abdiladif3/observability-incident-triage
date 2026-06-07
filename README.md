# Observability & Incident Triage Demo Platform

A backend API with simulated downstream dependencies, instrumented with Prometheus metrics, structured logs, and Grafana dashboards. Built and structured as a Sales Engineering walkthrough — customer pain, architecture, dashboards, live incident triage, and implementation path.

This is not a production monitoring system. It is an SE demo with production-shaped patterns.

## Status

In progress. See [`docs/customer-scenario.md`](docs/customer-scenario.md) for the customer context. Full walkthrough documentation will land as milestones complete.

## Planned Layout

```
observability-incident-triage/
├── apps/
│   ├── api/             Instrumented backend API (FastAPI)
│   └── downstream/      Simulated downstream dependency with controllable failure modes
├── observability/
│   ├── prometheus/      Scrape config
│   └── grafana/         Provisioned datasource + dashboards
├── infra/               Deployment plan
├── docs/                Sales Engineering walkthrough material
└── .github/workflows/   CI: tests + Docker build
```

## Companion Project

[`api-integration-security`](https://github.com/Abdiladif3/api-integration-security) — an API integration & security platform demo, structured the same way.
