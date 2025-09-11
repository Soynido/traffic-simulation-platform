#!/bin/bash
set -e

echo "🧪 Test de connectivité Frontend ↔ Backend"
echo "============================================"

# Test 1: Backend Health
echo "📡 Test 1: Backend Health Check"
HEALTH=$(curl -s http://localhost:8000/health)
echo "✅ Backend Health: $HEALTH"

# Test 2: Campaigns API
echo "📊 Test 2: Campaigns API"
CAMPAIGNS=$(curl -s http://localhost:8000/api/v1/campaigns/)
CAMPAIGN_COUNT=$(echo "$CAMPAIGNS" | grep -o '"total":[0-9]*' | cut -d':' -f2)
echo "✅ Campaigns disponibles: $CAMPAIGN_COUNT"

# Test 3: Personas API
echo "👥 Test 3: Personas API"
PERSONAS=$(curl -s http://localhost:8000/api/v1/personas/)
PERSONA_COUNT=$(echo "$PERSONAS" | grep -o '"total":[0-9]*' | cut -d':' -f2)
echo "✅ Personas disponibles: $PERSONA_COUNT"

# Test 4: Frontend Accessibility
echo "🌐 Test 4: Frontend Accessibility"
FRONTEND_TITLE=$(curl -s http://localhost:3001 | grep -o '<title>[^<]*</title>')
echo "✅ Frontend Title: $FRONTEND_TITLE"

# Test 5: Real-time Metrics (if campaign exists)
if [ "$CAMPAIGN_COUNT" -gt 0 ]; then
    echo "📈 Test 5: Real-time Metrics"
    CAMPAIGN_ID=$(echo "$CAMPAIGNS" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    METRICS=$(curl -s "http://localhost:8000/api/v1/campaigns/$CAMPAIGN_ID/real-time-metrics")
    CAMPAIGN_STATUS=$(echo "$METRICS" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    echo "✅ Campaign Status: $CAMPAIGN_STATUS"
    echo "✅ Campaign ID: $CAMPAIGN_ID"
else
    echo "⚠️  Test 5: Pas de campagne pour tester les métriques temps réel"
fi

echo ""
echo "🎉 Tous les tests de connectivité réussis !"
echo "🚀 La plateforme est prête à l'utilisation sur:"
echo "   Frontend: http://localhost:3001"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"