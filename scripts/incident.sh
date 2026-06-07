#!/usr/bin/env bash
#
# Trigger named incident scenarios on the downstream service.
#
# Usage:
#   ./scripts/incident.sh <scenario> [args]
#
# Scenarios match docs/incident-scenarios.md.

set -euo pipefail

DOWNSTREAM="${DOWNSTREAM:-http://localhost:8001}"

scenario="${1:-help}"

post() {
  curl -s -X POST -H 'Content-Type: application/json' -d "$2" "${DOWNSTREAM}$1" | python3 -m json.tool
}

case "${scenario}" in
  latency)
    ms="${2:-800}"
    echo "Injecting ${ms}ms latency on every downstream call..."
    post /simulate/latency "{\"latency_ms\":${ms}}"
    ;;
  errors)
    rate="${2:-0.5}"
    echo "Injecting downstream errors at rate ${rate}..."
    post /simulate/errors "{\"error_rate\":${rate}}"
    ;;
  timeout)
    echo "Setting latency to 3000ms (above the api's 2s timeout) to force 504s..."
    post /simulate/latency '{"latency_ms":3000}'
    ;;
  outage)
    echo "Triggering 100% downstream outage..."
    post /simulate/outage '{}'
    ;;
  recover|recovery)
    echo "Recovering downstream to normal operation..."
    post /simulate/recovery '{}'
    ;;
  status)
    curl -s "${DOWNSTREAM}/simulate/status" | python3 -m json.tool
    ;;
  *)
    cat <<EOF
Usage: $(basename "$0") <scenario> [args]

Scenarios:
  latency [ms]      Inject downstream latency (default 800ms)
  errors  [rate]    Inject downstream errors at rate (default 0.5)
  timeout           Latency above the api's 2s timeout (forces 504s)
  outage            100% downstream 503
  recover           Reset to normal
  status            Show current simulation state

Environment overrides:
  DOWNSTREAM=http://...   downstream service URL (default http://localhost:8001)
EOF
    ;;
esac
