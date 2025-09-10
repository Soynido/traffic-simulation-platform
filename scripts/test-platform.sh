#!/bin/bash

# Script de test pour la Traffic Simulation Platform
# Vérifie que tous les services fonctionnent correctement

set -e

echo "🧪 Test de la Traffic Simulation Platform..."

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour tester un endpoint
test_endpoint() {
    local url=$1
    local name=$2
    local expected_status=${3:-200}
    
    echo -n "🔍 Test de $name... "
    
    if response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null); then
        if [ "$response" = "$expected_status" ]; then
            echo -e "${GREEN}✅ OK${NC}"
            return 0
        else
            echo -e "${RED}❌ Échec (HTTP $response)${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Échec (connexion)${NC}"
        return 1
    fi
}

# Fonction pour tester un service Docker
test_docker_service() {
    local service=$1
    local name=$2
    
    echo -n "🔍 Test de $name... "
    
    if docker-compose ps "$service" | grep -q "Up"; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ Échec${NC}"
        return 1
    fi
}

# Compteurs
total_tests=0
passed_tests=0

# Test des services Docker
echo "🐳 Test des services Docker..."
services=("postgres" "redis" "backend" "frontend" "simulation-worker")
for service in "${services[@]}"; do
    total_tests=$((total_tests + 1))
    if test_docker_service "$service" "$service"; then
        passed_tests=$((passed_tests + 1))
    fi
done

echo ""

# Test des endpoints API
echo "🌐 Test des endpoints API..."
api_tests=(
    "http://localhost:8000/health:Health Check:200"
    "http://localhost:8000/:Root:200"
    "http://localhost:8000/docs:API Documentation:200"
    "http://localhost:8000/api/v1/personas:Personas API:200"
    "http://localhost:8000/api/v1/campaigns:Campaigns API:200"
    "http://localhost:8000/api/v1/sessions:Sessions API:200"
    "http://localhost:8000/api/v1/analytics/summary:Analytics Summary API:200"
)

for test in "${api_tests[@]}"; do
    IFS=':' read -r url name expected_status <<< "$test"
    total_tests=$((total_tests + 1))
    if test_endpoint "$url" "$name" "$expected_status"; then
        passed_tests=$((passed_tests + 1))
    fi
done

echo ""

# Test du frontend
echo "⚛️ Test du frontend..."
total_tests=$((total_tests + 1))
if test_endpoint "http://localhost:3001" "Frontend" "200"; then
    passed_tests=$((passed_tests + 1))
fi

echo ""

# Test de la base de données
echo "🗄️ Test de la base de données..."
total_tests=$((total_tests + 1))
if docker-compose exec -T postgres psql -U traffic_user -d traffic_db -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "🔍 Test de la base de données... ${GREEN}✅ OK${NC}"
    passed_tests=$((passed_tests + 1))
else
    echo -e "🔍 Test de la base de données... ${RED}❌ Échec${NC}"
fi

echo ""

# Test de Redis
echo "🔴 Test de Redis..."
total_tests=$((total_tests + 1))
if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
    echo -e "🔍 Test de Redis... ${GREEN}✅ OK${NC}"
    passed_tests=$((passed_tests + 1))
else
    echo -e "🔍 Test de Redis... ${RED}❌ Échec${NC}"
fi

echo ""

# Résumé des tests
echo "📊 Résumé des tests:"
echo "   Tests réussis: $passed_tests/$total_tests"

if [ $passed_tests -eq $total_tests ]; then
    echo -e "${GREEN}🎉 Tous les tests sont passés! La plateforme fonctionne correctement.${NC}"
    exit 0
else
    echo -e "${RED}❌ Certains tests ont échoué. Vérifiez les logs pour plus de détails.${NC}"
    echo ""
    echo "📝 Pour voir les logs:"
    echo "   docker-compose logs backend"
    echo "   docker-compose logs frontend"
    echo "   docker-compose logs postgres"
    echo "   docker-compose logs redis"
    exit 1
fi
