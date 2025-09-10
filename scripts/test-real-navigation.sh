#!/bin/bash

# Script de test pour la navigation réelle
# Teste la création d'une campagne avec target_url et son exécution

set -e

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3001"
TEST_URL="https://example.com"

echo -e "${BLUE}🧪 Test de la navigation réelle${NC}"
echo "=================================="

# Fonction pour tester un endpoint
test_endpoint() {
    local url=$1
    local method=${2:-GET}
    local data=${3:-""}
    local expected_status=${4:-200}
    
    echo -e "${YELLOW}Testing $method $url${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" -o /tmp/response.json "$url")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "%{http_code}" -o /tmp/response.json -X POST -H "Content-Type: application/json" -d "$data" "$url")
    fi
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✅ $method $url - Status: $response${NC}"
        return 0
    else
        echo -e "${RED}❌ $method $url - Expected: $expected_status, Got: $response${NC}"
        cat /tmp/response.json
        return 1
    fi
}

# Attendre que les services soient prêts
echo -e "${YELLOW}⏳ Attente des services...${NC}"
sleep 5

# Test 1: Vérifier que l'API est accessible
echo -e "\n${BLUE}1. Test de l'API Backend${NC}"
test_endpoint "$BACKEND_URL/health"

# Test 2: Créer un persona
echo -e "\n${BLUE}2. Création d'un persona de test${NC}"
PERSONA_DATA='{
    "name": "Test Persona Navigation '$(date +%s)'",
    "description": "Persona pour tester la navigation réelle",
    "session_duration_min": 5,
    "session_duration_max": 30,
    "pages_min": 3,
    "pages_max": 10,
    "actions_per_page_min": 2,
    "actions_per_page_max": 8,
    "scroll_probability": 0.8,
    "click_probability": 0.6,
    "typing_probability": 0.1
}'

test_endpoint "$BACKEND_URL/api/v1/personas/" "POST" "$PERSONA_DATA" 201

# Récupérer l'ID du persona créé
PERSONA_ID=$(cat /tmp/response.json | jq -r '.id')
echo -e "${GREEN}Persona créé avec l'ID: $PERSONA_ID${NC}"

# Test 3: Créer une campagne avec target_url
echo -e "\n${BLUE}3. Création d'une campagne avec navigation réelle${NC}"
CAMPAIGN_DATA="{
    \"name\": \"Test Real Navigation Campaign $(date +%s)\",
    \"description\": \"Campaign pour tester la navigation réelle vers $TEST_URL\",
    \"target_url\": \"$TEST_URL\",
    \"total_sessions\": 2,
    \"concurrent_sessions\": 2,
    \"persona_id\": \"$PERSONA_ID\",
    \"rate_limit_delay_ms\": 1000,
    \"user_agent_rotation\": true,
    \"respect_robots_txt\": true
}"

test_endpoint "$BACKEND_URL/api/v1/campaigns/" "POST" "$CAMPAIGN_DATA" 201

# Récupérer l'ID de la campagne créée
CAMPAIGN_ID=$(cat /tmp/response.json | jq -r '.id')
echo -e "${GREEN}Campagne créée avec l'ID: $CAMPAIGN_ID${NC}"

# Test 4: Lancer la campagne avec navigation réelle
echo -e "\n${BLUE}4. Lancement de la campagne avec navigation réelle${NC}"
test_endpoint "$BACKEND_URL/api/v1/campaigns/$CAMPAIGN_ID/start-real-navigation" "POST" "" 200

# Test 5: Vérifier le statut de la campagne
echo -e "\n${BLUE}5. Vérification du statut de la campagne${NC}"
sleep 2
test_endpoint "$BACKEND_URL/api/v1/campaigns/$CAMPAIGN_ID/status"

# Afficher les métriques de la campagne
echo -e "\n${BLUE}6. Métriques de la campagne${NC}"
test_endpoint "$BACKEND_URL/api/v1/campaigns/$CAMPAIGN_ID"

echo -e "\n${GREEN}🎉 Test de navigation réelle terminé avec succès !${NC}"
echo -e "${YELLOW}Vérifiez les logs des workers pour voir la navigation en action.${NC}"
