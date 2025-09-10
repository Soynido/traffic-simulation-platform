#!/usr/bin/env bash
set -euo pipefail

API_BASE="${API_BASE:-http://localhost:8000}"
API_V1="$API_BASE/api/v1"

echo "🚀 Building and starting services..."
docker-compose up -d --build

echo "⏳ Waiting for backend to be healthy..."
ATTEMPTS=0
until curl -fsS "$API_BASE/health" >/dev/null; do
  ATTEMPTS=$((ATTEMPTS+1))
  if [ $ATTEMPTS -ge 60 ]; then
    echo "❌ Backend not responding after 2 minutes. Showing logs:"
    docker-compose ps
    docker-compose logs --tail=200 backend || true
    exit 1
  fi
  sleep 2
done
echo "✅ Backend is up"

echo "🔎 Probing API routes..."
CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_V1/personas/")
if [ "$CODE" != "200" ]; then
  echo "❌ Route $API_V1/personas/ not reachable (HTTP $CODE)"
  echo "OpenAPI (first 1KB):"
  curl -s "$API_BASE/openapi.json" | head -c 1024 || true
  echo ""
  exit 1
fi

echo "👤 Creating demo persona..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PERSONA_JSON=$(cat <<JSON
{
  "name": "Demo Persona $TIMESTAMP",
  "description": "Auto-created by run-demo.sh at $TIMESTAMP",
  "session_duration_min": 60,
  "session_duration_max": 120,
  "pages_min": 1,
  "pages_max": 5,
  "actions_per_page_min": 1,
  "actions_per_page_max": 10,
  "scroll_probability": 0.8,
  "click_probability": 0.6,
  "typing_probability": 0.1
}
JSON
)
PERSONA_ID=$(curl -fsS -X POST "$API_V1/personas/" \
  -H 'Content-Type: application/json' \
  -d "$PERSONA_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')
echo "   → Persona ID: $PERSONA_ID"

echo "📣 Creating demo campaign..."
TARGET_URL=${TARGET_URL:-https://example.com}
CAMPAIGN_JSON=$(cat <<JSON
{
  "name": "Demo Campaign $TIMESTAMP",
  "description": "Auto-created by run-demo.sh at $TIMESTAMP",
  "target_url": "$TARGET_URL",
  "total_sessions": ${TOTAL_SESSIONS:-10},
  "concurrent_sessions": ${CONCURRENT_SESSIONS:-3},
  "persona_id": "$PERSONA_ID",
  "rate_limit_delay_ms": 800,
  "user_agent_rotation": true,
  "respect_robots_txt": true
}
JSON
)
CAMPAIGN_ID=$(curl -fsS -X POST "$API_V1/campaigns/" \
  -H 'Content-Type: application/json' \
  -d "$CAMPAIGN_JSON" | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])')
echo "   → Campaign ID: $CAMPAIGN_ID"

echo "▶️  Starting campaign..."
curl -fsS -X POST "$API_V1/campaigns/$CAMPAIGN_ID/start" >/dev/null
echo "   → Started"

echo "📊 Open dashboard: http://localhost:3001/analytics"
echo "🧭 Filter by: $CAMPAIGN_ID"
echo "🔎 Logs: docker-compose logs -f simulation-worker"
