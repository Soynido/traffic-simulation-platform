#!/bin/bash

# Script de gestion du workflow Git pour Traffic Simulation Platform
# Suit les conventions : feature/*, fix/*, refactor/*
# 1 task = 1 commit (granularité fine)
# Push immédiat (pas de stash local)
# PR obligatoire vers main

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'aide
show_help() {
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  start <type> <name>    - Créer une nouvelle branche (feature/fix/refactor)"
    echo "  commit <message>       - Commiter les changements avec message"
    echo "  push                   - Pousser la branche vers origin"
    echo "  pr                     - Créer une Pull Request vers main"
    echo "  finish                 - Finaliser la branche (merge + cleanup)"
    echo "  status                 - Afficher le statut de la branche actuelle"
    echo "  list                   - Lister les branches disponibles"
    echo "  clean                  - Nettoyer les branches mergées"
    echo ""
    echo "Examples:"
    echo "  $0 start feature persona-management"
    echo "  $0 commit \"feat: add persona creation form\""
    echo "  $0 push"
    echo "  $0 pr"
}

# Vérifier si on est dans un repo Git
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${RED}❌ Erreur: Pas dans un repository Git${NC}"
        exit 1
    fi
}

# Vérifier si on est sur la branche main
check_not_on_main() {
    current_branch=$(git branch --show-current)
    if [ "$current_branch" = "main" ]; then
        echo -e "${RED}❌ Erreur: Ne pas travailler directement sur main${NC}"
        echo -e "${YELLOW}💡 Utilisez 'git workflow start <type> <name>' pour créer une branche${NC}"
        exit 1
    fi
}

# Vérifier si on est sur une branche de travail
check_work_branch() {
    current_branch=$(git branch --show-current)
    if [[ ! "$current_branch" =~ ^(feature|fix|refactor)/ ]]; then
        echo -e "${RED}❌ Erreur: Pas sur une branche de travail (feature/*, fix/*, refactor/*)${NC}"
        echo -e "${YELLOW}💡 Branche actuelle: $current_branch${NC}"
        exit 1
    fi
}

# Créer une nouvelle branche
start_branch() {
    local type=$1
    local name=$2
    
    if [ -z "$type" ] || [ -z "$name" ]; then
        echo -e "${RED}❌ Erreur: Type et nom requis${NC}"
        echo -e "${YELLOW}Usage: $0 start <type> <name>${NC}"
        echo -e "${YELLOW}Types: feature, fix, refactor${NC}"
        exit 1
    fi
    
    if [[ ! "$type" =~ ^(feature|fix|refactor)$ ]]; then
        echo -e "${RED}❌ Erreur: Type invalide. Utilisez: feature, fix, refactor${NC}"
        exit 1
    fi
    
    # Nettoyer le nom de la branche
    clean_name=$(echo "$name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')
    branch_name="${type}/${clean_name}"
    
    echo -e "${BLUE}🚀 Création de la branche: $branch_name${NC}"
    
    # Vérifier si la branche existe déjà
    if git show-ref --verify --quiet refs/heads/"$branch_name"; then
        echo -e "${YELLOW}⚠️  La branche $branch_name existe déjà${NC}"
        read -p "Voulez-vous la supprimer et la recréer? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git branch -D "$branch_name"
        else
            echo -e "${YELLOW}💡 Basculement vers la branche existante${NC}"
            git checkout "$branch_name"
            return
        fi
    fi
    
    # Créer et basculer vers la nouvelle branche
    git checkout -b "$branch_name"
    echo -e "${GREEN}✅ Branche $branch_name créée et activée${NC}"
}

# Commiter les changements
commit_changes() {
    local message=$1
    
    if [ -z "$message" ]; then
        echo -e "${RED}❌ Erreur: Message de commit requis${NC}"
        echo -e "${YELLOW}Usage: $0 commit \"<message>\"${NC}"
        exit 1
    fi
    
    # Vérifier s'il y a des changements à commiter
    if git diff --staged --quiet && git diff --quiet; then
        echo -e "${YELLOW}⚠️  Aucun changement à commiter${NC}"
        return
    fi
    
    # Ajouter tous les changements
    git add .
    
    # Commiter avec le message
    git commit -m "$message"
    
    echo -e "${GREEN}✅ Changements commités: $message${NC}"
}

# Pousser la branche
push_branch() {
    local current_branch=$(git branch --show-current)
    
    echo -e "${BLUE}📤 Poussée de la branche $current_branch${NC}"
    
    # Pousser la branche vers origin
    git push -u origin "$current_branch"
    
    echo -e "${GREEN}✅ Branche poussée vers origin${NC}"
}

# Créer une Pull Request
create_pr() {
    local current_branch=$(git branch --show-current)
    local title=""
    local body=""
    
    # Générer un titre basé sur le type de branche
    if [[ "$current_branch" =~ ^feature/ ]]; then
        title="✨ Feature: $(echo "$current_branch" | sed 's/feature\///' | sed 's/-/ /g' | sed 's/\b\w/\U&/g')"
    elif [[ "$current_branch" =~ ^fix/ ]]; then
        title="🐛 Fix: $(echo "$current_branch" | sed 's/fix\///' | sed 's/-/ /g' | sed 's/\b\w/\U&/g')"
    elif [[ "$current_branch" =~ ^refactor/ ]]; then
        title="♻️  Refactor: $(echo "$current_branch" | sed 's/refactor\///' | sed 's/-/ /g' | sed 's/\b\w/\U&/g')"
    else
        title="📝 Update: $current_branch"
    fi
    
    # Générer le body de la PR
    body="## Description
$(echo "$current_branch" | sed 's/.*\///' | sed 's/-/ /g' | sed 's/\b\w/\U&/g')

## Type de Changement
- [ ] Bug fix
- [ ] Nouvelle fonctionnalité
- [ ] Breaking change
- [ ] Documentation

## Tests
- [ ] Tests unitaires
- [ ] Tests d'intégration
- [ ] Tests E2E

## Checklist
- [ ] Code auto-documenté
- [ ] Pas de console.log/debug
- [ ] Performance testée"

    echo -e "${BLUE}🔗 Création de la Pull Request${NC}"
    echo -e "${YELLOW}Titre: $title${NC}"
    
    # Créer la PR avec GitHub CLI
    if command -v gh &> /dev/null; then
        gh pr create --title "$title" --body "$body" --base main --head "$current_branch"
        echo -e "${GREEN}✅ Pull Request créée${NC}"
    else
        echo -e "${YELLOW}⚠️  GitHub CLI non installé. Créez la PR manuellement:${NC}"
        echo -e "${BLUE}https://github.com/Soynido/traffic-simulation-platform/compare/$current_branch${NC}"
    fi
}

# Finaliser la branche
finish_branch() {
    local current_branch=$(git branch --show-current)
    
    echo -e "${BLUE}🏁 Finalisation de la branche $current_branch${NC}"
    
    # Vérifier que la PR est mergée
    if command -v gh &> /dev/null; then
        pr_status=$(gh pr status --json state --jq '.currentBranch.state' 2>/dev/null || echo "NOT_FOUND")
        if [ "$pr_status" != "MERGED" ]; then
            echo -e "${YELLOW}⚠️  La PR n'est pas encore mergée${NC}"
            echo -e "${YELLOW}💡 Attendez que la PR soit mergée avant de finaliser${NC}"
            return
        fi
    fi
    
    # Basculement vers main
    git checkout main
    
    # Mise à jour de main
    git pull origin main
    
    # Suppression de la branche locale
    git branch -d "$current_branch"
    
    # Suppression de la branche distante
    git push origin --delete "$current_branch"
    
    echo -e "${GREEN}✅ Branche finalisée et nettoyée${NC}"
}

# Afficher le statut
show_status() {
    local current_branch=$(git branch --show-current)
    local status=$(git status --porcelain)
    
    echo -e "${BLUE}📊 Statut de la branche actuelle${NC}"
    echo -e "${YELLOW}Branche: $current_branch${NC}"
    
    if [ -n "$status" ]; then
        echo -e "${YELLOW}Changements non commités:${NC}"
        echo "$status"
    else
        echo -e "${GREEN}✅ Aucun changement en attente${NC}"
    fi
    
    # Afficher les commits en avance
    local ahead=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
    if [ "$ahead" -gt 0 ]; then
        echo -e "${YELLOW}📈 $ahead commit(s) en avance sur main${NC}"
    fi
}

# Lister les branches
list_branches() {
    echo -e "${BLUE}📋 Branches disponibles${NC}"
    echo ""
    echo -e "${YELLOW}Branches de travail:${NC}"
    git branch -r | grep -E 'origin/(feature|fix|refactor)/' | sed 's/origin\///' | sed 's/^/  /'
    echo ""
    echo -e "${YELLOW}Branche actuelle:${NC}"
    git branch --show-current | sed 's/^/  /'
}

# Nettoyer les branches mergées
clean_branches() {
    echo -e "${BLUE}🧹 Nettoyage des branches mergées${NC}"
    
    # Mise à jour des références distantes
    git fetch --prune
    
    # Suppression des branches locales mergées
    git branch --merged main | grep -v main | xargs -r git branch -d
    
    echo -e "${GREEN}✅ Branches mergées nettoyées${NC}"
}

# Fonction principale
main() {
    check_git_repo
    
    case "${1:-}" in
        "start")
            start_branch "$2" "$3"
            ;;
        "commit")
            check_work_branch
            commit_changes "$2"
            ;;
        "push")
            check_work_branch
            push_branch
            ;;
        "pr")
            check_work_branch
            create_pr
            ;;
        "finish")
            check_not_on_main
            finish_branch
            ;;
        "status")
            show_status
            ;;
        "list")
            list_branches
            ;;
        "clean")
            clean_branches
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo -e "${RED}❌ Commande inconnue: ${1:-}${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Exécuter la fonction principale
main "$@"
