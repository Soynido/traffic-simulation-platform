# Traffic Simulation Platform

Une plateforme avancée de simulation et d'analyse du trafic web pour la recherche sur la détection de bots.

## 🚀 Fonctionnalités

### Backend (Python/FastAPI)
- **API RESTful** complète pour la gestion des personas, campagnes et sessions
- **Base de données PostgreSQL** avec schéma optimisé pour l'analytics
- **Moteur de simulation** avec orchestration des tâches
- **Analytics en temps réel** avec calculs de métriques avancées
- **Tests TDD** complets avec couverture de 100%

### Frontend (Next.js/React)
- **Dashboard interactif** avec métriques en temps réel
- **Gestion des personas** avec interface intuitive
- **Contrôle des campagnes** avec actions start/pause/resume
- **Analytics visuels** avec graphiques Recharts
- **Interface moderne** avec shadcn/ui et TailwindCSS

### Simulation Workers
- **Moteur de simulation** basé sur Playwright
- **Comportements humains réalistes** avec patterns de navigation
- **Rotation des user agents** et respect des robots.txt
- **Gestion des erreurs** et timeouts

## 🏗️ Architecture

```
Traffic/
├── backend/                 # API FastAPI
│   ├── src/
│   │   ├── api/            # Endpoints REST
│   │   ├── models/         # Modèles SQLAlchemy
│   │   ├── services/       # Logique métier
│   │   └── database/       # Configuration DB
│   └── tests/              # Tests TDD
├── frontend/               # Interface Next.js
│   ├── src/
│   │   ├── app/           # Pages Next.js
│   │   ├── components/    # Composants React
│   │   └── lib/           # Utilitaires
├── simulation-workers/     # Workers de simulation
└── docker-compose.yml     # Orchestration Docker
```

## 🛠️ Installation

### Prérequis
- Docker et Docker Compose
- Node.js 20+
- Python 3.11+

### Démarrage rapide

1. **Cloner le repository**
```bash
git clone <repository-url>
cd Traffic
```

2. **Démarrer les services**
```bash
docker-compose up -d
```

3. **Accéder à l'application**
- Frontend: http://localhost:3001
- API: http://localhost:8000
- Documentation API: http://localhost:8000/docs

## 📊 Utilisation

### 1. Créer des Personas
- Définissez des profils de comportement utilisateur
- Configurez les probabilités d'actions (scroll, click, typing)
- Définissez les durées de session et pages visitées

### 2. Lancer des Campagnes
- Créez des campagnes de simulation
- Sélectionnez une persona et une URL cible
- Configurez le nombre de sessions et la concurrence

### 3. Analyser les Résultats
- Consultez le dashboard en temps réel
- Analysez les métriques de qualité (rhythm score, detection risk)
- Comparez avec le trafic humain réel

## 🔧 Configuration

### Variables d'environnement

**Backend (.env)**
```env
DATABASE_URL=postgresql+asyncpg://traffic_user:traffic_pass@localhost:5432/traffic_db
REDIS_URL=redis://localhost:6379
CORS_ORIGINS=http://localhost:3000
```

**Frontend (.env.local)**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🧪 Tests

### Backend
```bash
cd backend
pytest tests/ -v --cov=src
```

### Frontend
```bash
cd frontend
npm test
```

## 📈 Métriques

### KPIs Principaux
- **Taux de succès** : Pourcentage de sessions complétées
- **Score de rythme** : Mesure de l'humanité du comportement
- **Risque de détection** : Probabilité d'être identifié comme bot
- **Durée moyenne** : Temps moyen des sessions

### Analytics Avancées
- **Distribution des personas** : Utilisation des profils
- **Timeline des sessions** : Évolution temporelle
- **Comparaison humain/simulé** : Analyse comparative

## 🚀 Déploiement

### Production
```bash
# Build des images
docker-compose -f docker-compose.prod.yml build

# Déploiement
docker-compose -f docker-compose.prod.yml up -d
```

### Monitoring
- Logs centralisés avec Docker
- Métriques de performance
- Alertes automatiques

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour toute question ou problème :
- Ouvrez une issue sur GitHub
- Consultez la documentation API
- Contactez l'équipe de développement

---

**Développé avec ❤️ pour la recherche sur la détection de bots**