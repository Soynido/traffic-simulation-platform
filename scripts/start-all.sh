#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Traffic Simulation Platform - Démarrage Complet"
echo "=================================================="

# Configuration
API_BASE="${API_BASE:-http://localhost:8000}"
API_V1="$API_BASE/api/v1"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3001}"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Nettoyer les anciens containers si nécessaire
log_info "Nettoyage des anciens containers..."
docker-compose down --remove-orphans

# Construire et démarrer tous les services
log_info "Construction et démarrage de tous les services..."
docker-compose up -d --build

# Fonction d'attente avec timeout
wait_for_service() {
    local service_name=$1
    local url=$2
    local max_attempts=${3:-60}
    local attempt=0
    
    log_info "Attente du service $service_name..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -fsS "$url" >/dev/null 2>&1; then
            log_success "$service_name est opérationnel"
            return 0
        fi
        
        attempt=$((attempt + 1))
        if [ $((attempt % 10)) -eq 0 ]; then
            log_warning "$service_name toujours en démarrage... ($attempt/$max_attempts)"
        fi
        sleep 2
    done
    
    log_error "$service_name n'a pas démarré après $((max_attempts * 2)) secondes"
    return 1
}

# Attendre que tous les services soient prêts
log_info "Vérification de l'état des services..."

# PostgreSQL
log_info "Vérification de PostgreSQL..."
docker-compose exec -T postgres pg_isready -U traffic_user -d traffic_db || {
    log_error "PostgreSQL n'est pas prêt"
    exit 1
}
log_success "PostgreSQL est prêt"

# Redis  
log_info "Vérification de Redis..."
docker-compose exec -T redis redis-cli ping >/dev/null || {
    log_error "Redis n'est pas prêt"
    exit 1
}
log_success "Redis est prêt"

# Backend API
wait_for_service "Backend API" "$API_BASE/health" 60

# Frontend
wait_for_service "Frontend" "$FRONTEND_URL" 30

# Vérifier que simulation-worker est en cours d'exécution
log_info "Vérification du Simulation Worker..."
if docker-compose ps simulation-worker | grep -q "Up"; then
    log_success "Simulation Worker est en cours d'exécution"
else
    log_warning "Simulation Worker pourrait avoir des problèmes, vérification des logs..."
    docker-compose logs --tail=5 simulation-worker
fi

# Test des endpoints critiques
log_info "Test des endpoints critiques..."

# Test API Personas
if curl -fsS "$API_V1/personas/" >/dev/null; then
    log_success "API Personas fonctionne"
else
    log_error "API Personas ne répond pas"
fi

# Test API Campaigns
if curl -fsS "$API_V1/campaigns/" >/dev/null; then
    log_success "API Campaigns fonctionne"
else
    log_error "API Campaigns ne répond pas"
fi

# Affichage du statut final
echo ""
echo "🎯 État des Services:"
echo "===================="
docker-compose ps

echo ""
echo "📊 URLs d'accès:"
echo "================"
echo "🌐 Frontend Dashboard: $FRONTEND_URL"
echo "🔧 Backend API: $API_BASE"
echo "📚 API Documentation: $API_BASE/docs"
echo "📈 API Redoc: $API_BASE/redoc"

echo ""
echo "🔍 Commandes utiles:"
echo "==================="
echo "Logs Backend:        docker-compose logs -f backend"
echo "Logs Frontend:       docker-compose logs -f frontend" 
echo "Logs Worker:         docker-compose logs -f simulation-worker"
echo "Logs Tous:           docker-compose logs -f"
echo "Arrêter:             docker-compose down"

log_success "🚀 Tous les services sont démarrés et opérationnels !"
log_info "Vous pouvez maintenant accéder à l'application sur $FRONTEND_URL"