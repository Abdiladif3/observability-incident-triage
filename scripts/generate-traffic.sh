#!/usr/bin/env bash
#
# Sends realistic background traffic against the api so the Grafana
# dashboards have a baseline to render during a demo. Ctrl-C to stop.
#
# Usage:
#   ./scripts/generate-traffic.sh                 # default 0.2s between calls
#   SLEEP=0.05 ./scripts/generate-traffic.sh      # faster traffic
#   API=http://1.2.3.4:8000 ./scripts/generate-traffic.sh

set -euo pipefail

API="${API:-http://localhost:8000}"
SLEEP="${SLEEP:-0.2}"

readonly endpoints=(
  "/health"
  "/market/status"
  "/market/quote/AAPL"
  "/market/quote/MSFT"
  "/market/quote/NVDA"
  "/market/quote/TSLA"
  "/accounts/acct-001"
  "/accounts/acct-001/positions"
  "/accounts/acct-002/positions"
  "/accounts/acct-001/orders"
)

readonly order_bodies=(
  '{"account_id":"acct-001","symbol":"AAPL","side":"buy","order_type":"market","quantity":5}'
  '{"account_id":"acct-001","symbol":"MSFT","side":"buy","order_type":"market","quantity":10}'
  '{"account_id":"acct-002","symbol":"TSLA","side":"sell","order_type":"market","quantity":2}'
)

cycle=0

echo "Generating traffic against ${API} (interval ${SLEEP}s). Ctrl-C to stop."

trap 'echo ""; echo "stopped after ${cycle} cycles"; exit 0' INT TERM

while true; do
  for path in "${endpoints[@]}"; do
    curl -s -o /dev/null "${API}${path}" || true
    sleep "${SLEEP}"
  done

  # Submit an order every cycle to keep the business metric alive.
  body="${order_bodies[$((cycle % ${#order_bodies[@]}))]}"
  curl -s -o /dev/null \
    -X POST \
    -H 'Content-Type: application/json' \
    -d "${body}" \
    "${API}/orders" || true

  cycle=$((cycle + 1))
done
