# Traffic Simulation Platform - Makefile
# Commandes de développement et de déploiement

.PHONY: help install start stop restart logs test clean build

# Aide par défaut
help:
	@echo "Traffic Simulation Platform - Commandes disponibles:"
	@echo ""
	@echo "🚀 Développement:"
	@echo "  make install     - Installer les dépendances"
	@echo "  make start       - Démarrer la plateforme"
	@echo "  make stop        - Arrêter la plateforme"
	@echo "  make restart     - Redémarrer la plateforme"
	@echo "  make logs        - Voir les logs"
	@echo ""
	@echo "🧪 Tests:"
	@echo "  make test        - Lancer tous les tests"
	@echo "  make test-backend - Lancer les tests backend"
	@echo "  make test-frontend - Lancer les tests frontend"
	@echo "  make test-platform - Tester la plateforme complète"
	@echo ""
	@echo "🔧 Maintenance:"
	@echo "  make clean       - Nettoyer les données"
	@echo "  make build       - Construire les images"
	@echo "  make migrate     - Appliquer les migrations"
	@echo "  make shell       - Ouvrir un shell dans le backend"
	@echo ""

# Installation des dépendances
install:
	@echo "📦 Installation des dépendances..."
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	cd simulation-workers && pip install -r requirements.txt

# Démarrage de la plateforme
start:
	@echo "🚀 Démarrage de la Traffic Simulation Platform..."
	./scripts/start-dev.sh

# Arrêt de la plateforme
stop:
	@echo "🛑 Arrêt de la plateforme..."
	docker-compose down

# Redémarrage de la plateforme
restart: stop start

# Voir les logs
logs:
	@echo "📝 Logs de la plateforme..."
	docker-compose logs -f

# Logs spécifiques
logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-postgres:
	docker-compose logs -f postgres

logs-redis:
	docker-compose logs -f redis

# Tests
test: test-backend test-frontend test-platform

test-backend:
	@echo "🧪 Tests backend..."
	cd backend && python -m pytest tests/ -v --cov=src

test-frontend:
	@echo "🧪 Tests frontend..."
	cd frontend && npm test

test-platform:
	@echo "🧪 Test de la plateforme complète..."
	./scripts/test-platform.sh

# Nettoyage
clean:
	@echo "🧹 Nettoyage des données..."
	docker-compose down -v
	docker system prune -f

# Construction des images
build:
	@echo "🔨 Construction des images..."
	docker-compose build

# Migrations de base de données
migrate:
	@echo "🗄️ Application des migrations..."
	docker-compose exec backend alembic upgrade head

# Shell dans le backend
shell:
	@echo "🐚 Ouverture d'un shell dans le backend..."
	docker-compose exec backend bash

# Shell dans la base de données
db-shell:
	@echo "🗄️ Ouverture d'un shell dans PostgreSQL..."
	docker-compose exec postgres psql -U traffic_user -d traffic_db

# Redémarrage rapide (sans reconstruction)
quick-restart:
	@echo "⚡ Redémarrage rapide..."
	docker-compose restart

# Vérification de l'état
status:
	@echo "📊 État des services..."
	docker-compose ps

# Mise à jour des dépendances
update:
	@echo "🔄 Mise à jour des dépendances..."
	cd backend && pip install -r requirements.txt --upgrade
	cd frontend && npm update
	cd simulation-workers && pip install -r requirements.txt --upgrade

# Sauvegarde de la base de données
backup:
	@echo "💾 Sauvegarde de la base de données..."
	docker-compose exec postgres pg_dump -U traffic_user traffic_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Restauration de la base de données
restore:
	@echo "🔄 Restauration de la base de données..."
	@read -p "Nom du fichier de sauvegarde: " file; \
	docker-compose exec -T postgres psql -U traffic_user -d traffic_db < $$file