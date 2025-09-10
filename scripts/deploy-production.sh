#!/bin/bash

# Script de déploiement en production pour la Traffic Simulation Platform
# Configure et déploie la plateforme en environnement de production

set -e

echo "🚀 Déploiement en production de la Traffic Simulation Platform..."

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration par défaut
ENVIRONMENT=${1:-production}
VERSION=${2:-latest}
REGISTRY=${3:-docker.io}
NAMESPACE=${4:-traffic-simulation}

echo -e "${BLUE}Configuration du déploiement:${NC}"
echo "  Environnement: $ENVIRONMENT"
echo "  Version: $VERSION"
echo "  Registry: $REGISTRY"
echo "  Namespace: $NAMESPACE"
echo ""

# Vérifier les prérequis
echo "🔍 Vérification des prérequis..."

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé${NC}"
    exit 1
fi

# Vérifier Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose n'est pas installé${NC}"
    exit 1
fi

# Vérifier kubectl (si déploiement Kubernetes)
if [ "$ENVIRONMENT" = "kubernetes" ]; then
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl n'est pas installé${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Prérequis vérifiés${NC}"

# Créer les fichiers de configuration de production
echo ""
echo "📝 Création des fichiers de configuration de production..."

# Docker Compose pour la production
cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: traffic_db
      POSTGRES_USER: traffic_user
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U traffic_user -d traffic_db"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://traffic_user:\${POSTGRES_PASSWORD}@postgres:5432/traffic_db
      REDIS_URL: redis://redis:6379
      CORS_ORIGINS: \${CORS_ORIGINS}
      ALLOWED_HOSTS: \${ALLOWED_HOSTS}
      LOG_LEVEL: INFO
      SECRET_KEY: \${SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      NEXT_PUBLIC_API_URL: \${NEXT_PUBLIC_API_URL}
    ports:
      - "3000:3000"
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3

  simulation-workers:
    build:
      context: ./simulation-workers
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://traffic_user:\${POSTGRES_PASSWORD}@postgres:5432/traffic_db
      REDIS_URL: redis://redis:6379
      SIMULATION_WORKER_COUNT: \${SIMULATION_WORKER_COUNT:-3}
      SIMULATION_MAX_CONCURRENT_SESSIONS: \${SIMULATION_MAX_CONCURRENT_SESSIONS:-10}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      backend:
        condition: service_healthy
    restart: unless-stopped
    deploy:
      replicas: \${SIMULATION_WORKER_REPLICAS:-2}

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
EOF

# Fichier d'environnement de production
cat > .env.production << EOF
# Configuration de production
POSTGRES_PASSWORD=your_secure_password_here
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost
SECRET_KEY=your_secret_key_here
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
SIMULATION_WORKER_COUNT=5
SIMULATION_MAX_CONCURRENT_SESSIONS=20
SIMULATION_WORKER_REPLICAS=3
EOF

# Configuration Nginx
mkdir -p nginx
cat > nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        
        # Redirection HTTPS
        return 301 https://\$server_name\$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;
        
        # Configuration SSL
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        
        # Configuration de sécurité
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        
        # Proxy vers le backend
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # Proxy vers le frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
EOF

echo -e "${GREEN}✅ Fichiers de configuration créés${NC}"

# Construire les images Docker
echo ""
echo "🔨 Construction des images Docker..."

# Construire l'image backend
echo "  Construction de l'image backend..."
docker build -t $REGISTRY/traffic-backend:$VERSION ./backend

# Construire l'image frontend
echo "  Construction de l'image frontend..."
docker build -t $REGISTRY/traffic-frontend:$VERSION ./frontend

# Construire l'image simulation-workers
echo "  Construction de l'image simulation-workers..."
docker build -t $REGISTRY/traffic-simulation-workers:$VERSION ./simulation-workers

echo -e "${GREEN}✅ Images Docker construites${NC}"

# Déployer selon l'environnement
if [ "$ENVIRONMENT" = "kubernetes" ]; then
    echo ""
    echo "☸️ Déploiement Kubernetes..."
    
    # Créer le namespace
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    # Appliquer les manifests Kubernetes
    kubectl apply -f k8s/ -n $NAMESPACE
    
    echo -e "${GREEN}✅ Déploiement Kubernetes terminé${NC}"
    
else
    echo ""
    echo "🐳 Déploiement Docker Compose..."
    
    # Arrêter les services existants
    docker-compose -f docker-compose.prod.yml down --remove-orphans
    
    # Démarrer les services de production
    docker-compose -f docker-compose.prod.yml up -d
    
    echo -e "${GREEN}✅ Déploiement Docker Compose terminé${NC}"
fi

# Vérifier le déploiement
echo ""
echo "🔍 Vérification du déploiement..."

# Attendre que les services soient prêts
echo "  Attente que les services soient prêts..."
sleep 30

# Vérifier la santé des services
echo "  Vérification de la santé des services..."

# Vérifier PostgreSQL
if docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U traffic_user -d traffic_db > /dev/null 2>&1; then
    echo -e "    ${GREEN}✅ PostgreSQL${NC}"
else
    echo -e "    ${RED}❌ PostgreSQL${NC}"
fi

# Vérifier Redis
if docker-compose -f docker-compose.prod.yml exec redis redis-cli ping > /dev/null 2>&1; then
    echo -e "    ${GREEN}✅ Redis${NC}"
else
    echo -e "    ${RED}❌ Redis${NC}"
fi

# Vérifier le backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "    ${GREEN}✅ Backend API${NC}"
else
    echo -e "    ${RED}❌ Backend API${NC}"
fi

# Vérifier le frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "    ${GREEN}✅ Frontend${NC}"
else
    echo -e "    ${RED}❌ Frontend${NC}"
fi

# Afficher les informations de déploiement
echo ""
echo "📊 Informations de déploiement"
echo "=============================="
echo "Environnement: $ENVIRONMENT"
echo "Version: $VERSION"
echo "Registry: $REGISTRY"
echo "Namespace: $NAMESPACE"
echo ""
echo "Services déployés:"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - Backend API: localhost:8000"
echo "  - Frontend: localhost:3000"
echo "  - Nginx: localhost:80, localhost:443"
echo ""
echo "Commandes utiles:"
echo "  Voir les logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  Arrêter: docker-compose -f docker-compose.prod.yml down"
echo "  Redémarrer: docker-compose -f docker-compose.prod.yml restart"
echo "  Statut: docker-compose -f docker-compose.prod.yml ps"
echo ""
echo -e "${GREEN}🎉 Déploiement en production terminé avec succès!${NC}"
