#!/bin/bash

# Script de test de performance pour la Traffic Simulation Platform
# Teste les performances de l'API et de la base de données

set -e

echo "⚡ Test de performance de la Traffic Simulation Platform..."

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_BASE_URL="http://localhost:8000"
CONCURRENT_USERS=10
TEST_DURATION=60
RAMP_UP_TIME=10

# Vérifier que les services sont démarrés
echo "🔍 Vérification des services..."

if ! curl -f "$API_BASE_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ L'API n'est pas accessible${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Services vérifiés${NC}"

# Créer un fichier de test pour Apache Bench
echo "📝 Création du fichier de test..."

cat > performance_test.txt << EOF
# Test de performance pour la Traffic Simulation Platform
# Endpoints à tester

# Health Check
GET $API_BASE_URL/health

# API Endpoints
GET $API_BASE_URL/api/v1/personas
GET $API_BASE_URL/api/v1/campaigns
GET $API_BASE_URL/api/v1/sessions
GET $API_BASE_URL/api/v1/analytics

# Documentation
GET $API_BASE_URL/docs
EOF

# Fonction pour exécuter un test de performance
run_performance_test() {
    local endpoint="$1"
    local name="$2"
    local method="${3:-GET}"
    
    echo ""
    echo "🧪 Test de performance: $name"
    echo "Endpoint: $endpoint"
    echo "Méthode: $method"
    echo "Utilisateurs concurrents: $CONCURRENT_USERS"
    echo "Durée: ${TEST_DURATION}s"
    echo "Ramp-up: ${RAMP_UP_TIME}s"
    echo "----------------------------------------"
    
    # Exécuter le test avec Apache Bench
    if [ "$method" = "POST" ]; then
        ab -n $((CONCURRENT_USERS * TEST_DURATION)) -c $CONCURRENT_USERS -T "application/json" -p /dev/null "$endpoint" 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests|Connection Times)"
    else
        ab -n $((CONCURRENT_USERS * TEST_DURATION)) -c $CONCURRENT_USERS "$endpoint" 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests|Connection Times)"
    fi
    
    echo ""
}

# Tests de performance
echo ""
echo "🚀 Démarrage des tests de performance"
echo "====================================="

# Test 1: Health Check
run_performance_test "$API_BASE_URL/health" "Health Check"

# Test 2: API Personas
run_performance_test "$API_BASE_URL/api/v1/personas" "API Personas"

# Test 3: API Campaigns
run_performance_test "$API_BASE_URL/api/v1/campaigns" "API Campaigns"

# Test 4: API Sessions
run_performance_test "$API_BASE_URL/api/v1/sessions" "API Sessions"

# Test 5: API Analytics
run_performance_test "$API_BASE_URL/api/v1/analytics" "API Analytics"

# Test 6: Documentation
run_performance_test "$API_BASE_URL/docs" "API Documentation"

# Test de charge avec plusieurs endpoints
echo ""
echo "🔥 Test de charge multi-endpoints"
echo "================================="

# Créer un script de test multi-endpoints
cat > multi_endpoint_test.sh << 'EOF'
#!/bin/bash

# Test de charge multi-endpoints
endpoints=(
    "http://localhost:8000/health"
    "http://localhost:8000/api/v1/personas"
    "http://localhost:8000/api/v1/campaigns"
    "http://localhost:8000/api/v1/sessions"
    "http://localhost:8000/api/v1/analytics"
)

# Exécuter les tests en parallèle
for endpoint in "${endpoints[@]}"; do
    ab -n 1000 -c 10 "$endpoint" > "test_$(basename "$endpoint").log" 2>&1 &
done

# Attendre que tous les tests se terminent
wait

# Analyser les résultats
echo "Résultats des tests multi-endpoints:"
echo "===================================="

for endpoint in "${endpoints[@]}"; do
    log_file="test_$(basename "$endpoint").log"
    if [ -f "$log_file" ]; then
        echo ""
        echo "Endpoint: $endpoint"
        echo "-------------------"
        grep -E "(Requests per second|Time per request|Failed requests)" "$log_file" | head -3
        rm "$log_file"
    fi
done
EOF

chmod +x multi_endpoint_test.sh
./multi_endpoint_test.sh

# Test de stress
echo ""
echo "💪 Test de stress"
echo "================="

# Test avec un nombre élevé d'utilisateurs concurrents
echo "Test de stress avec 50 utilisateurs concurrents..."
ab -n 5000 -c 50 "$API_BASE_URL/health" 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests|Connection Times)"

# Test de durée prolongée
echo ""
echo "Test de stress avec durée prolongée (5 minutes)..."
ab -n 10000 -c 20 -t 300 "$API_BASE_URL/health" 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests|Connection Times)"

# Test de la base de données
echo ""
echo "🗄️ Test de performance de la base de données"
echo "============================================"

# Test de connexion à la base de données
echo "Test de connexion à PostgreSQL..."
time docker-compose exec postgres psql -U traffic_user -d traffic_db -c "SELECT 1;" > /dev/null 2>&1

# Test de requête complexe
echo "Test de requête complexe..."
time docker-compose exec postgres psql -U traffic_user -d traffic_db -c "
SELECT 
    p.name as persona_name,
    COUNT(s.id) as session_count,
    AVG(s.pages_visited) as avg_pages,
    AVG(s.actions_performed) as avg_actions
FROM personas p
LEFT JOIN sessions s ON p.id = s.persona_id
GROUP BY p.id, p.name
ORDER BY session_count DESC;
" > /dev/null 2>&1

# Test de Redis
echo ""
echo "🔴 Test de performance de Redis"
echo "==============================="

# Test de ping Redis
echo "Test de ping Redis..."
time docker-compose exec redis redis-cli ping > /dev/null 2>&1

# Test de set/get Redis
echo "Test de set/get Redis..."
time docker-compose exec redis redis-cli eval "
for i=1,1000 do
    redis.call('SET', 'test:key:' .. i, 'value:' .. i)
    redis.call('GET', 'test:key:' .. i)
end
return 'OK'
" 0 > /dev/null 2>&1

# Nettoyage des clés de test
docker-compose exec redis redis-cli eval "
for i=1,1000 do
    redis.call('DEL', 'test:key:' .. i)
end
return 'OK'
" 0 > /dev/null 2>&1

# Résumé des tests
echo ""
echo "📊 Résumé des tests de performance"
echo "=================================="
echo "Tests exécutés:"
echo "  - Health Check API"
echo "  - Endpoints API (personas, campaigns, sessions, analytics)"
echo "  - Documentation API"
echo "  - Test de charge multi-endpoints"
echo "  - Test de stress (50 utilisateurs concurrents)"
echo "  - Test de stress prolongé (5 minutes)"
echo "  - Test de performance PostgreSQL"
echo "  - Test de performance Redis"
echo ""
echo "Configuration des tests:"
echo "  - Utilisateurs concurrents: $CONCURRENT_USERS"
echo "  - Durée des tests: ${TEST_DURATION}s"
echo "  - Ramp-up: ${RAMP_UP_TIME}s"
echo ""
echo -e "${GREEN}✅ Tests de performance terminés${NC}"
echo ""
echo "💡 Conseils d'optimisation:"
echo "  - Surveillez les métriques de CPU et mémoire"
echo "  - Ajustez les paramètres de connexion à la base de données"
echo "  - Configurez le cache Redis selon vos besoins"
echo "  - Utilisez un load balancer pour la production"
echo "  - Surveillez les logs d'erreur"
