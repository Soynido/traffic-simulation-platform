#!/bin/bash
set -e

echo "🎮 Test des contrôles de campagne"
echo "=================================="

CAMPAIGN_ID="5dd2f92d-0f34-442c-9b23-896d4d0aa49a"

# Function to get campaign status
get_status() {
    curl -s "http://localhost:8000/api/v1/campaigns/$CAMPAIGN_ID" | grep -o '"status":"[^"]*"' | cut -d'"' -f4
}

# Function to test action and verify status
test_action() {
    local action=$1
    local expected_status=$2
    
    echo "🔄 Test: $action"
    
    # Perform action
    RESULT=$(curl -s -X POST "http://localhost:8000/api/v1/campaigns/$CAMPAIGN_ID/$action")
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://localhost:8000/api/v1/campaigns/$CAMPAIGN_ID/$action")
    
    # Check HTTP status
    if [ "$HTTP_CODE" -eq 200 ]; then
        echo "✅ $action: HTTP 200 OK"
        
        # Verify campaign status
        CURRENT_STATUS=$(get_status)
        if [ "$CURRENT_STATUS" = "$expected_status" ]; then
            echo "✅ Status vérifié: $CURRENT_STATUS"
        else
            echo "❌ Status incorrect: attendu '$expected_status', reçu '$CURRENT_STATUS'"
        fi
    else
        echo "❌ $action: HTTP $HTTP_CODE"
        echo "   Response: $RESULT"
    fi
    echo ""
}

# Get initial status
echo "📊 Status initial:"
INITIAL_STATUS=$(get_status)
echo "✅ Campaign Status: $INITIAL_STATUS"
echo ""

# Test sequence based on current status
case "$INITIAL_STATUS" in
    "running")
        test_action "pause" "paused"
        test_action "resume" "running"
        test_action "stop" "paused"
        ;;
    "paused")
        test_action "resume" "running"
        test_action "pause" "paused"
        test_action "resume" "running"
        test_action "stop" "paused"
        ;;
    "pending")
        echo "⚠️  Campaign en attente - test de start nécessaire"
        test_action "start" "running"
        test_action "pause" "paused"
        test_action "resume" "running"
        test_action "stop" "paused"
        ;;
    *)
        echo "⚠️  Status inattendu: $INITIAL_STATUS"
        ;;
esac

# Final status check
echo "📊 Status final:"
FINAL_STATUS=$(get_status)
echo "✅ Campaign Status: $FINAL_STATUS"

echo ""
echo "🎉 Tests des contrôles de campagne terminés !"