#!/bin/bash

# Health check script for Traffic Simulation Platform
# Checks all services and reports status

set -e

echo "🔍 Traffic Simulation Platform - Health Check"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check service health
check_service() {
    local service_name="$1"
    local url="$2"
    local expected_status="$3"
    
    echo -n "Checking $service_name... "
    
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ Unhealthy${NC}"
        return 1
    fi
}

# Function to check database connectivity
check_database() {
    echo -n "Checking PostgreSQL... "
    
    if docker-compose exec -T postgres pg_isready -U traffic_user > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Connected${NC}"
        return 0
    else
        echo -e "${RED}❌ Not connected${NC}"
        return 1
    fi
}

# Function to check Redis
check_redis() {
    echo -n "Checking Redis... "
    
    if redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Connected${NC}"
        return 0
    else
        echo -e "${RED}❌ Not connected${NC}"
        return 1
    fi
}

# Main health checks
failed_checks=0

# Check backend API
check_service "Backend API" "http://localhost:8000/health" || ((failed_checks++))

# Check frontend
check_service "Frontend" "http://localhost:3001" || ((failed_checks++))

# Check database
check_database || ((failed_checks++))

# Check Redis
check_redis || ((failed_checks++))

# Check Docker services
echo -n "Checking Docker services... "
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${RED}❌ Not running${NC}"
    ((failed_checks++))
fi

# Summary
echo ""
echo "=============================================="
if [ $failed_checks -eq 0 ]; then
    echo -e "${GREEN}🎉 All services healthy!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  $failed_checks service(s) unhealthy${NC}"
    echo ""
    echo "Troubleshooting tips:"
    echo "1. Run 'docker-compose up -d' to start services"
    echo "2. Check logs with 'docker-compose logs'"
    echo "3. Verify .env configuration"
    exit 1
fi