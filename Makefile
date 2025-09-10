# Traffic Simulation Platform - Makefile
# Commandes de développement et déploiement pour monorepo

.PHONY: help start stop test clean logs dev build deploy install setup

# Couleurs pour les messages
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
BLUE=\033[0;34m
NC=\033[0m # No Color

help: ## Afficher l'aide
	@echo "$(GREEN)Traffic Simulation Platform - Commandes disponibles:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

# ===== INSTALLATION ET SETUP =====
install: ## Installer toutes les dépendances
	@echo "$(GREEN)📦 Installation des dépendances...$(NC)"
	@cd shared && npm ci
	@cd frontend && npm ci
	@cd backend && pip install -r requirements.txt
	@cd simulation-workers && pip install -r requirements.txt

setup: ## Configuration initiale du projet
	@echo "$(GREEN)⚙️  Configuration initiale...$(NC)"
	@make install
	@cd shared && npm run build
	@echo "$(GREEN)✅ Configuration terminée!$(NC)"

# ===== DÉVELOPPEMENT =====
start: ## Démarrer tous les services
	@echo "$(GREEN)🚀 Démarrage de la Traffic Simulation Platform...$(NC)"
	@./scripts/start-dev.sh

stop: ## Arrêter tous les services
	@echo "$(YELLOW)🛑 Arrêt des services...$(NC)"
	@docker-compose down

dev: ## Mode développement (démarrage + logs)
	@make start
	@make logs

logs: ## Afficher les logs
	@docker-compose logs -f

# ===== TESTS =====
test: ## Lancer tous les tests
	@echo "$(GREEN)🧪 Lancement de tous les tests...$(NC)"
	@make test-shared
	@make test-backend
	@make test-frontend
	@make test-simulation

test-shared: ## Tests des types partagés
	@echo "$(BLUE)🧪 Tests shared...$(NC)"
	@cd shared/tests && npm run test:run

test-backend: ## Tests du backend
	@echo "$(BLUE)🧪 Tests backend...$(NC)"
	@cd backend && pytest src/tests/ -v

test-frontend: ## Tests du frontend
	@echo "$(BLUE)🧪 Tests frontend...$(NC)"
	@cd frontend && npm run test:run

test-simulation: ## Tests des simulation workers
	@echo "$(BLUE)🧪 Tests simulation workers...$(NC)"
	@cd simulation-workers && pytest src/tests/ -v

test-e2e: ## Tests end-to-end
	@echo "$(GREEN)🧪 Tests E2E...$(NC)"
	@./scripts/test-e2e.sh

test-performance: ## Tests de performance
	@echo "$(GREEN)🧪 Tests de performance...$(NC)"
	@./scripts/performance-test.sh

test-real-navigation: ## Test de la navigation réelle
	@echo "$(GREEN)🧪 Test de la navigation réelle...$(NC)"
	@./scripts/test-real-navigation.sh

# ===== LINTING ET FORMATAGE =====
lint: ## Lancer le linting sur tous les projets
	@echo "$(GREEN)🔍 Linting...$(NC)"
	@make lint-shared
	@make lint-backend
	@make lint-frontend
	@make lint-simulation

lint-shared: ## Linting shared
	@cd shared && npm run lint

lint-backend: ## Linting backend
	@cd backend && flake8 src/

lint-frontend: ## Linting frontend
	@cd frontend && npm run lint

lint-simulation: ## Linting simulation workers
	@cd simulation-workers && flake8 src/

format: ## Formater le code
	@echo "$(GREEN)🎨 Formatage du code...$(NC)"
	@cd frontend && npm run lint:fix
	@cd backend && black src/ && isort src/
	@cd simulation-workers && black src/ && isort src/

# ===== BUILD =====
build: ## Construire tous les projets
	@echo "$(GREEN)🔨 Construction...$(NC)"
	@make build-shared
	@make build-frontend
	@make build-backend
	@make build-simulation

build-shared: ## Build shared
	@cd shared && npm run build

build-frontend: ## Build frontend
	@cd frontend && npm run build

build-backend: ## Build backend (pas de build nécessaire pour Python)
	@echo "$(YELLOW)Backend: pas de build nécessaire$(NC)"

build-simulation: ## Build simulation workers (pas de build nécessaire pour Python)
	@echo "$(YELLOW)Simulation workers: pas de build nécessaire$(NC)"

# ===== DOCKER =====
docker-build: ## Construire les images Docker
	@echo "$(GREEN)🐳 Construction des images Docker...$(NC)"
	@docker-compose build

docker-up: ## Démarrer avec Docker
	@echo "$(GREEN)🐳 Démarrage avec Docker...$(NC)"
	@docker-compose up -d

docker-down: ## Arrêter Docker
	@echo "$(YELLOW)🐳 Arrêt de Docker...$(NC)"
	@docker-compose down

# ===== NETTOYAGE =====
clean: ## Nettoyer les conteneurs et volumes
	@echo "$(YELLOW)🧹 Nettoyage...$(NC)"
	@docker-compose down -v
	@docker system prune -f

clean-deps: ## Nettoyer les dépendances
	@echo "$(YELLOW)🧹 Nettoyage des dépendances...$(NC)"
	@rm -rf shared/node_modules shared/dist
	@rm -rf frontend/node_modules frontend/.next
	@rm -rf backend/__pycache__ backend/.pytest_cache
	@rm -rf simulation-workers/__pycache__ simulation-workers/.pytest_cache

# ===== DÉPLOIEMENT =====
deploy: ## Déployer en production
	@echo "$(GREEN)🚀 Déploiement en production...$(NC)"
	@./scripts/deploy-production.sh

deploy-staging: ## Déployer en staging
	@echo "$(GREEN)🚀 Déploiement en staging...$(NC)"
	@./scripts/deploy-staging.sh

# ===== GIT WORKFLOW =====
git-start: ## Démarrer une nouvelle branche (usage: make git-start TYPE=feature NAME=my-feature)
	@./scripts/git-workflow.sh start $(TYPE) $(NAME)

git-commit: ## Commiter les changements (usage: make git-commit MESSAGE="my message")
	@./scripts/git-workflow.sh commit "$(MESSAGE)"

git-push: ## Pousser la branche
	@./scripts/git-workflow.sh push

git-pr: ## Créer une Pull Request
	@./scripts/git-workflow.sh pr

git-finish: ## Finaliser la branche
	@./scripts/git-workflow.sh finish

git-status: ## Afficher le statut Git
	@./scripts/git-workflow.sh status

# ===== UTILITAIRES =====
health: ## Vérifier la santé des services
	@./scripts/health-check.sh

docs: ## Générer la documentation
	@echo "$(GREEN)📚 Génération de la documentation...$(NC)"
	@cd frontend && npm run build
	@echo "$(GREEN)✅ Documentation générée!$(NC)"

# ===== DÉVELOPPEMENT RAPIDE =====
quick-start: ## Démarrage rapide (install + start)
	@make install
	@make start

quick-test: ## Test rapide (unit tests seulement)
	@make test-shared
	@make test-backend
	@make test-frontend

# ===== AIDE CONTEXTE =====
context: ## Afficher le contexte du projet
	@echo "$(GREEN)📋 Contexte du projet:$(NC)"
	@echo "  Structure: Monorepo (frontend/backend/shared/simulation-workers)"
	@echo "  Approche: TDD (Tests First)"
	@echo "  Workflow: feature/*, fix/*, refactor/*"
	@echo "  CI/CD: GitHub Actions"
	@echo "  Docker: Multi-container"
	@echo ""
	@echo "$(YELLOW)Commandes utiles:$(NC)"
	@echo "  make quick-start    # Démarrage rapide"
	@echo "  make test           # Tous les tests"
	@echo "  make git-start TYPE=feature NAME=my-feature"
	@echo "  make git-commit MESSAGE=\"my message\""