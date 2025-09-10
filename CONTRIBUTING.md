# Guide de Contribution

Merci de votre intérêt pour contribuer au projet Traffic Simulation Platform ! 

## 🚀 Démarrage Rapide

1. **Fork** le repository
2. **Clone** votre fork localement
3. **Créez** une branche pour votre fonctionnalité
4. **Commitez** vos changements
5. **Poussez** vers votre fork
6. **Ouvrez** une Pull Request

## 📋 Processus de Développement

### Structure du Projet
```
├── backend/          # API FastAPI
├── frontend/         # Dashboard Next.js
├── simulation-workers/ # Workers de simulation
├── k8s/             # Configurations Kubernetes
├── scripts/         # Scripts utilitaires
└── specs/           # Documentation technique
```

### Standards de Code

#### Backend (Python)
- **Formatage**: Black + isort
- **Linting**: flake8
- **Tests**: pytest avec couverture > 80%
- **Type hints**: Obligatoires
- **Documentation**: Docstrings Google style

#### Frontend (TypeScript/React)
- **Formatage**: Prettier
- **Linting**: ESLint
- **Tests**: Vitest + Testing Library
- **Types**: TypeScript strict mode
- **Composants**: shadcn/ui + TailwindCSS

### Tests

#### Backend
```bash
cd backend
pytest tests/ --cov=src --cov-report=html
```

#### Frontend
```bash
cd frontend
npm run test
npm run test:ui
```

#### Tests E2E
```bash
./scripts/test-e2e.sh
```

### Commits

Utilisez le format conventionnel :
- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` documentation
- `style:` formatage
- `refactor:` refactoring
- `test:` tests
- `chore:` maintenance

Exemple :
```
feat: add persona management dashboard
fix: resolve simulation worker memory leak
docs: update API documentation
```

## 🔧 Développement Local

### Prérequis
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### Installation
```bash
# Clone du repository
git clone https://github.com/Soynido/traffic-simulation-platform.git
cd traffic-simulation-platform

# Démarrage des services
make start

# Ou avec Docker Compose
docker-compose up -d
```

### Services
- **Frontend**: http://localhost:3001
- **API**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs

## 📝 Pull Requests

### Avant de Soumettre
- [ ] Tests passent localement
- [ ] Code formaté et linté
- [ ] Documentation mise à jour
- [ ] Commit messages clairs
- [ ] Branche à jour avec main

### Template de PR
```markdown
## Description
Brève description des changements

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
- [ ] Performance testée
```

## 🐛 Signaler un Bug

Utilisez le template d'issue GitHub avec :
- Description détaillée
- Étapes de reproduction
- Environnement (OS, versions)
- Logs d'erreur
- Screenshots si applicable

## 💡 Proposer une Fonctionnalité

1. Vérifiez les issues existantes
2. Créez une issue avec le label "enhancement"
3. Décrivez le cas d'usage
4. Attendez validation avant développement

## 📚 Documentation

- **README.md**: Vue d'ensemble du projet
- **specs/**: Documentation technique détaillée
- **docs/**: Guides utilisateur et développeur
- **Code**: Commentaires et docstrings

## 🤝 Code de Conduite

- Respect mutuel
- Communication constructive
- Ouverture aux nouvelles idées
- Focus sur le bien commun du projet

## 📞 Support

- **Issues**: Pour bugs et fonctionnalités
- **Discussions**: Pour questions générales
- **Email**: [votre-email@example.com]

Merci de contribuer ! 🎉
