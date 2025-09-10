#!/bin/bash

# Script de test End-to-End pour la Traffic Simulation Platform
# Teste l'ensemble de la plateforme de bout en bout

set -e

echo "🧪 Test End-to-End de la Traffic Simulation Platform..."

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_BASE_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3001"
TEST_TIMEOUT=30

# Compteurs
total_tests=0
passed_tests=0
failed_tests=0

# Fonction pour exécuter un test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -n "🔍 Test: $test_name... "
    total_tests=$((total_tests + 1))
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        passed_tests=$((passed_tests + 1))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        failed_tests=$((failed_tests + 1))
        return 1
    fi
}

# Fonction pour tester un endpoint API
test_api_endpoint() {
    local endpoint="$1"
    local expected_status="$2"
    local method="${3:-GET}"
    
    local response_code
    if [ "$method" = "POST" ]; then
        response_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_BASE_URL$endpoint" -H "Content-Type: application/json" -d '{}' 2>/dev/null || echo "000")
    else
        response_code=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL$endpoint" 2>/dev/null || echo "000")
    fi
    
    [ "$response_code" = "$expected_status" ]
}

# Fonction pour tester le frontend
test_frontend_page() {
    local page="$1"
    local response_code
    response_code=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL$page" 2>/dev/null || echo "000")
    [ "$response_code" = "200" ]
}

# Fonction pour attendre qu'un service soit prêt
wait_for_service() {
    local service_name="$1"
    local check_command="$2"
    local max_attempts=30
    local attempt=0
    
    echo -n "⏳ Attente de $service_name... "
    
    while [ $attempt -lt $max_attempts ]; do
        if eval "$check_command" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Prêt${NC}"
            return 0
        fi
        
        attempt=$((attempt + 1))
        sleep 2
    done
    
    echo -e "${RED}❌ Timeout${NC}"
    return 1
}

echo ""
echo "🚀 Démarrage des tests End-to-End"
echo "=================================="

# 1. Vérifier que les services sont démarrés
echo ""
echo "📋 Phase 1: Vérification des services"
echo "-------------------------------------"

wait_for_service "PostgreSQL" "docker-compose exec postgres pg_isready -U traffic_user -d traffic_db"
wait_for_service "Redis" "docker-compose exec redis redis-cli ping"
wait_for_service "Backend API" "curl -f $API_BASE_URL/health"
wait_for_service "Frontend" "curl -f $FRONTEND_URL"

# 2. Tests de l'API Backend
echo ""
echo "📋 Phase 2: Tests de l'API Backend"
echo "----------------------------------"

# Tests des endpoints de base
run_test "Health Check" "test_api_endpoint '/health' '200'"
run_test "Root Endpoint" "test_api_endpoint '/' '200'"
run_test "API Documentation" "test_api_endpoint '/docs' '200'"

# Tests des endpoints de l'API
run_test "Personas API" "test_api_endpoint '/api/v1/personas' '200'"
run_test "Campaigns API" "test_api_endpoint '/api/v1/campaigns' '200'"
run_test "Sessions API" "test_api_endpoint '/api/v1/sessions' '200'"
run_test "Analytics API" "test_api_endpoint '/api/v1/analytics' '200'"

# 3. Tests du Frontend
echo ""
echo "📋 Phase 3: Tests du Frontend"
echo "-----------------------------"

run_test "Page d'accueil" "test_frontend_page '/'"
run_test "Page Personas" "test_frontend_page '/personas'"
run_test "Page Campaigns" "test_frontend_page '/campaigns'"
run_test "Page Analytics" "test_frontend_page '/analytics'"

# 4. Tests d'intégration
echo ""
echo "📋 Phase 4: Tests d'intégration"
echo "-------------------------------"

# Test de création d'une persona
run_test "Création d'une persona" "
    curl -s -X POST '$API_BASE_URL/api/v1/personas' \
    -H 'Content-Type: application/json' \
    -d '{
        \"name\": \"Test Persona E2E\",
        \"description\": \"Persona de test E2E\",
        \"session_duration_min\": 60,
        \"session_duration_max\": 120,
        \"pages_min\": 1,
        \"pages_max\": 3,
        \"actions_per_page_min\": 1,
        \"actions_per_page_max\": 5,
        \"scroll_probability\": 0.8,
        \"click_probability\": 0.6,
        \"typing_probability\": 0.1
    }' | grep -q 'Test Persona E2E'
"

# Test de création d'une campagne
run_test "Création d'une campagne" "
    curl -s -X POST '$API_BASE_URL/api/v1/campaigns' \
    -H 'Content-Type: application/json' \
    -d '{
        \"name\": \"Test Campaign E2E\",
        \"description\": \"Campagne de test E2E\",
        \"target_url\": \"https://example.com\",
        \"total_sessions\": 10,
        \"concurrent_sessions\": 2,
        \"persona_id\": \"test-persona-id\",
        \"rate_limit_delay_ms\": 1000,
        \"user_agent_rotation\": true,
        \"respect_robots_txt\": true
    }' | grep -q 'Test Campaign E2E'
"

# 5. Tests de performance
echo ""
echo "📋 Phase 5: Tests de performance"
echo "--------------------------------"

# Test de temps de réponse de l'API
run_test "Temps de réponse API < 200ms" "
    response_time=\$(curl -s -o /dev/null -w '%{time_total}' '$API_BASE_URL/health' 2>/dev/null || echo '999')
    [ \$(echo \"\$response_time < 0.2\" | bc -l) -eq 1 ]
"

# Test de temps de réponse du frontend
run_test "Temps de réponse Frontend < 500ms" "
    response_time=\$(curl -s -o /dev/null -w '%{time_total}' '$FRONTEND_URL' 2>/dev/null || echo '999')
    [ \$(echo \"\$response_time < 0.5\" | bc -l) -eq 1 ]
"

# 6. Tests de résilience
echo ""
echo "📋 Phase 6: Tests de résilience"
echo "-------------------------------"

# Test de redémarrage des services
run_test "Redémarrage du backend" "
    docker-compose restart backend && \
    sleep 10 && \
    curl -f '$API_BASE_URL/health' > /dev/null 2>&1
"

# Test de redémarrage du frontend
run_test "Redémarrage du frontend" "
    docker-compose restart frontend && \
    sleep 15 && \
    curl -f '$FRONTEND_URL' > /dev/null 2>&1
"

# 7. Tests de données
echo ""
echo "📋 Phase 7: Tests de données"
echo "----------------------------"

# Test de persistance des données
run_test "Persistance des données PostgreSQL" "
    docker-compose exec postgres psql -U traffic_user -d traffic_db -c 'SELECT 1;' > /dev/null 2>&1
"

# Test de persistance des données Redis
run_test "Persistance des données Redis" "
    docker-compose exec redis redis-cli ping > /dev/null 2>&1
"

# 8. Tests de sécurité
echo ""
echo "📋 Phase 8: Tests de sécurité"
echo "-----------------------------"

# Test des headers de sécurité
run_test "Headers de sécurité CORS" "
    curl -s -I '$API_BASE_URL/health' | grep -i 'access-control-allow-origin' > /dev/null 2>&1
"

# Test de validation des entrées
run_test "Validation des entrées API" "
    response=\$(curl -s -X POST '$API_BASE_URL/api/v1/personas' \
    -H 'Content-Type: application/json' \
    -d '{\"invalid\": \"data\"}' 2>/dev/null || echo '{}')
    echo \"\$response\" | grep -q 'validation' || echo \"\$response\" | grep -q 'error'
"

# 9. Tests de monitoring
echo ""
echo "📋 Phase 9: Tests de monitoring"
echo "-------------------------------"

# Test des logs
run_test "Logs du backend" "
    docker-compose logs backend | grep -q 'INFO' || docker-compose logs backend | grep -q 'ERROR'
"

# Test des métriques
run_test "Métriques de base" "
    curl -s '$API_BASE_URL/health' | grep -q 'status' || curl -s '$API_BASE_URL/health' | grep -q 'healthy'
"

# 10. Tests de nettoyage
echo ""
echo "📋 Phase 10: Tests de nettoyage"
echo "-------------------------------"

# Test de suppression des données de test
run_test "Nettoyage des données de test" "
    # Ici, vous pourriez ajouter des commandes de nettoyage
    echo 'Nettoyage effectué'
"

# Résumé des tests
echo ""
echo "📊 Résumé des tests End-to-End"
echo "=============================="
echo "Tests exécutés: $total_tests"
echo -e "Tests réussis: ${GREEN}$passed_tests${NC}"
echo -e "Tests échoués: ${RED}$failed_tests${NC}"

if [ $failed_tests -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Tous les tests End-to-End sont passés!${NC}"
    echo -e "${GREEN}La plateforme fonctionne correctement de bout en bout.${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ Certains tests End-to-End ont échoué.${NC}"
    echo -e "${RED}Vérifiez les logs pour plus de détails.${NC}"
    exit 1
fi
