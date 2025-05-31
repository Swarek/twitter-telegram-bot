# Project Overview

## Description
Twitter-Telegram Bot est une application qui automatise le partage de tweets depuis Twitter vers des canaux Telegram. Le bot surveille des comptes Twitter spécifiques et publie automatiquement leurs nouveaux tweets dans des canaux Telegram désignés, avec support des médias (images, vidéos, GIFs) et formatage adapté.

## Architecture
- **Backend**: Python 3.11 avec architecture asynchrone
- **Scraping Twitter**: twscrape (gratuit) + ScrapFly (fallback optionnel)
- **Bot Telegram**: python-telegram-bot pour publier les messages
- **Base de données**: PostgreSQL local pour stocker l'état
- **Cache**: Redis local pour queue management
- **Monitoring**: Système de logs avec loguru
- **Exécution**: Local sur macOS avec PM2 ou directement

## Technologies Stack
- **Runtime**: Python 3.11+
- **Language**: Python avec type hints
- **Twitter Scraping**: twscrape (GraphQL) + ScrapFly (fallback)
- **Telegram Bot**: python-telegram-bot>=21.0
- **Database**: PostgreSQL + asyncpg
- **Cache**: Redis + redis-py
- **Logging**: loguru
- **Testing**: pytest + pytest-asyncio
- **Process Manager**: PM2 ou systemd
- **Package Manager**: pip + venv

## Key Features
- Surveillance en temps réel de comptes Twitter multiples
- Publication automatique vers canaux Telegram
- Support complet des médias (images, vidéos, GIFs)
- Formatage intelligent des tweets (threads, mentions, hashtags)
- Gestion des erreurs et retry automatique
- Logs détaillés et monitoring
- Configuration flexible par compte/canal
- Rate limiting intelligent
- Mode debug et test

## Project Structure
```
twittertelegram/
├── src/
│   ├── config/          # Configuration et variables d'environnement
│   ├── services/        # Services principaux (Twitter, Telegram)
│   ├── models/          # Modèles de base de données
│   ├── utils/           # Utilitaires et helpers
│   ├── middleware/      # Middleware (rate limiting, auth)
│   └── index.js         # Point d'entrée principal
├── tests/               # Tests unitaires et d'intégration
├── scripts/             # Scripts utilitaires
├── docker/              # Configuration Docker
├── docs/                # Documentation additionnelle
└── config/              # Fichiers de configuration
```

## Development Workflow
1. **Feature Branch**: Créer une branche depuis `develop`
2. **Development**: Développer et tester localement
3. **Tests**: Exécuter les tests unitaires et d'intégration
4. **Pull Request**: Créer une PR vers `develop`
5. **Review**: Code review et validation
6. **Merge**: Fusionner dans `develop` puis `main` pour release

## Important Commands
```bash
# Installation et setup
pip install -r requirements.txt     # Installer les dépendances Python
cp .env.example .env               # Configurer l'environnement
python scripts/init_db.py          # Initialiser la base de données

# Développement
python src/main.py                 # Lancer le bot
python src/main.py --debug         # Mode debug avec logs détaillés
python scripts/test_scraper.py     # Tester le scraping Twitter
python scripts/test_telegram.py    # Tester la connexion Telegram

# Base de données
createdb twitter_telegram          # Créer la base de données
python scripts/init_db.py          # Créer les tables
python scripts/reset_db.py         # Reset complet de la DB

# Services locaux
brew services start postgresql     # Démarrer PostgreSQL
brew services start redis          # Démarrer Redis
brew services list                 # Vérifier les services

# Tests
pytest                            # Exécuter tous les tests
pytest tests/test_scraper.py      # Tests spécifiques
pytest -v --cov=src               # Tests avec coverage

# Monitoring
tail -f logs/bot.log              # Voir les logs en temps réel
python scripts/check_status.py     # Vérifier le statut du bot
```

## API Endpoints
```
# Webhook Twitter (si utilisé)
POST /webhook/twitter       # Recevoir les événements Twitter

# API de gestion
GET  /api/health           # Health check
GET  /api/status           # Statut du bot
GET  /api/accounts         # Liste des comptes surveillés
POST /api/accounts         # Ajouter un compte
PUT  /api/accounts/:id     # Modifier un compte
DELETE /api/accounts/:id   # Supprimer un compte

# Monitoring
GET  /api/metrics          # Métriques du système
GET  /api/logs             # Logs récents
```

## Environment Variables
```bash
# Twitter Scraping (twscrape)
TWITTER_USERNAME_1=         # Username compte Twitter 1
TWITTER_PASSWORD_1=         # Password compte Twitter 1
TWITTER_EMAIL_1=            # Email compte Twitter 1
TWITTER_USERNAME_2=         # Username compte Twitter 2 (optionnel)
TWITTER_PASSWORD_2=         # Password compte Twitter 2 (optionnel)

# ScrapFly (fallback optionnel)
SCRAPFLY_API_KEY=           # Clé API ScrapFly si utilisé

# Telegram Bot
TELEGRAM_BOT_TOKEN=         # Token du bot Telegram
TELEGRAM_CHANNEL_ID=        # ID du canal principal

# Database
DATABASE_URL=               # URL PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=twitter_telegram
DB_USER=postgres
DB_PASSWORD=

# Application
ENVIRONMENT=development     # Environment (development/production)
LOG_LEVEL=info             # Niveau de log (debug/info/warning/error)
POLL_INTERVAL=300          # Intervalle de vérification (secondes)
MAX_TWEET_AGE=3600         # Âge max des tweets à publier (secondes)
WORKERS=1                  # Nombre de workers asynchrones

# Features
ENABLE_MEDIA=true          # Activer le support des médias
ENABLE_THREADS=true        # Activer le support des threads
ENABLE_METRICS=true        # Activer les métriques
```

## Database Schema
```sql
-- Table des comptes Twitter surveillés
CREATE TABLE twitter_accounts (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    twitter_id VARCHAR(255) UNIQUE,
    telegram_channel_id VARCHAR(255) NOT NULL,
    last_tweet_id VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table des tweets publiés
CREATE TABLE published_tweets (
    id SERIAL PRIMARY KEY,
    tweet_id VARCHAR(255) NOT NULL UNIQUE,
    account_id INTEGER REFERENCES twitter_accounts(id),
    telegram_message_id INTEGER,
    published_at TIMESTAMP DEFAULT NOW(),
    tweet_data JSONB
);

-- Table des erreurs
CREATE TABLE error_logs (
    id SERIAL PRIMARY KEY,
    error_type VARCHAR(100),
    error_message TEXT,
    error_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Known Issues & TODOs
### Issues
- Rate limiting Twitter API lors de pics d'activité
- Gestion des vidéos > 50MB pour Telegram
- Délai occasionnel dans la détection de nouveaux tweets

### TODOs
- [ ] Implémenter webhook Twitter pour temps réel
- [ ] Ajouter support des polls Twitter
- [ ] Interface web d'administration
- [ ] Notifications d'erreurs par email
- [ ] Support multi-langue
- [ ] Archivage automatique des vieux tweets
- [ ] Analytics et statistiques détaillées

## Deployment
### Exécution locale sur macOS
```bash
# Installation des dépendances système
brew install postgresql@15 redis python@3.11

# Démarrage des services
brew services start postgresql@15
brew services start redis

# Configuration Python
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configuration de la base de données
createdb twitter_telegram
python scripts/init_db.py

# Lancement du bot
python src/main.py

# Ou avec PM2 pour un fonctionnement en arrière-plan
pm install -g pm2
pm2 start src/main.py --interpreter python3.11
```

### Docker local (optionnel)
```bash
# Utiliser Docker Compose pour tout lancer
docker-compose up -d

# Voir les logs
docker-compose logs -f bot
```

## Additional Notes
- Le bot vérifie les nouveaux tweets toutes les minutes par défaut
- Les médias sont téléchargés temporairement puis supprimés
- Un système de retry est en place pour les erreurs temporaires
- Les logs sont rotation automatiquement (7 jours de rétention)
- Monitoring recommandé: Uptime Robot ou Pingdom
- Backup database quotidien recommandé