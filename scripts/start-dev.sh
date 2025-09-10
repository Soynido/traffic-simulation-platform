#!/bin/bash

# Script de démarrage pour l'environnement de développement
# Traffic Simulation Platform

set -e

echo "🚀 Démarrage de la Traffic Simulation Platform..."

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez installer Docker d'abord."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Veuillez installer Docker Compose d'abord."
    exit 1
fi

# Créer les dossiers nécessaires
echo "📁 Création des dossiers nécessaires..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis

# Démarrer les services de base (PostgreSQL et Redis)
echo "🐘 Démarrage de PostgreSQL et Redis..."
docker-compose up -d postgres redis

# Attendre que les services soient prêts
echo "⏳ Attente que les services soient prêts..."
sleep 10

# Vérifier la connexion à PostgreSQL
echo "🔍 Vérification de la connexion à PostgreSQL..."
until docker-compose exec postgres pg_isready -U traffic_user -d traffic_db; do
    echo "⏳ Attente de PostgreSQL..."
    sleep 2
done

# Vérifier la connexion à Redis
echo "🔍 Vérification de la connexion à Redis..."
until docker-compose exec redis redis-cli ping; do
    echo "⏳ Attente de Redis..."
    sleep 2
done

echo "✅ Services de base démarrés avec succès!"

# Démarrer le backend
echo "🐍 Démarrage du backend Python..."
docker-compose up -d backend

# Attendre que le backend soit prêt
echo "⏳ Attente que le backend soit prêt..."
sleep 15

# Vérifier que l'API est accessible
echo "🔍 Vérification de l'API..."
until curl -f http://localhost:8000/health > /dev/null 2>&1; do
    echo "⏳ Attente de l'API..."
    sleep 2
done

echo "✅ Backend démarré avec succès!"

# Démarrer le frontend
echo "⚛️ Démarrage du frontend Next.js..."
docker-compose up -d frontend

# Attendre que le frontend soit prêt
echo "⏳ Attente que le frontend soit prêt..."
sleep 20

# Vérifier que le frontend est accessible
echo "🔍 Vérification du frontend..."
until curl -f http://localhost:3001 > /dev/null 2>&1; do
    echo "⏳ Attente du frontend..."
    sleep 2
done

echo "✅ Frontend démarré avec succès!"

# Démarrer les workers de simulation
echo "🤖 Démarrage des workers de simulation..."
docker-compose up -d simulation-worker

echo "✅ Workers de simulation démarrés avec succès!"

echo ""
echo "🎉 Traffic Simulation Platform démarrée avec succès!"
echo ""
echo "📊 Accès aux services:"
echo "   Frontend:     http://localhost:3001"
echo "   API:          http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   PostgreSQL:   localhost:5432"
echo "   Redis:        localhost:6379"
echo ""
echo "📝 Logs:"
echo "   docker-compose logs -f backend"
echo "   docker-compose logs -f frontend"
echo "   docker-compose logs -f simulation-worker"
echo ""
echo "🛑 Pour arrêter:"
echo "   docker-compose down"
echo ""
