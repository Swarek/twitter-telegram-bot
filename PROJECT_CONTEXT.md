# Project Context

## Business Context
Le Twitter-Telegram Bot répond au besoin de partager automatiquement du contenu Twitter vers des audiences Telegram. Ce projet est particulièrement utile pour :
- Les créateurs de contenu multi-plateformes
- Les entreprises avec présence sur Twitter et Telegram
- Les communautés souhaitant centraliser l'information
- Les agrégateurs de news et actualités

### Objectifs principaux
1. Automatiser le partage cross-platform
2. Maintenir l'engagement sur Telegram
3. Réduire le travail manuel de republication
4. Assurer la cohérence du contenu

### Contraintes
- Respect des limites API Twitter et Telegram
- Conformité aux ToS des deux plateformes
- Protection des données personnelles
- Performance et fiabilité 24/7

## User Stories
### En tant qu'administrateur
- Je veux ajouter/retirer des comptes Twitter à surveiller
- Je veux configurer les canaux Telegram de destination
- Je veux voir les statistiques de publication
- Je veux recevoir des alertes en cas d'erreur

### En tant qu'utilisateur Telegram
- Je veux recevoir les tweets rapidement après publication
- Je veux voir les médias (images, vidéos) directement
- Je veux que les liens soient cliquables
- Je veux comprendre le contexte (threads, réponses)

### En tant que gestionnaire de communauté
- Je veux filtrer certains types de tweets
- Je veux personnaliser le format des messages
- Je veux programmer des pauses dans les publications
- Je veux modérer avant publication (optionnel)

## Technical Decisions
### Architecture
- **Monolithique modulaire**: Simplicité de déploiement et maintenance
- **Polling vs Webhooks**: Polling pour fiabilité, webhooks en option
- **PostgreSQL**: Robustesse et support JSON pour flexibilité
- **Node.js**: Écosystème riche pour APIs Twitter/Telegram

### Patterns
- **Service Pattern**: Séparation Twitter/Telegram/Database
- **Repository Pattern**: Abstraction de la couche données
- **Observer Pattern**: Gestion des événements asynchrones
- **Circuit Breaker**: Protection contre les défaillances API

### Trade-offs
- Polling vs Real-time: Choix de la fiabilité sur la latence
- Stateful vs Stateless: État en DB pour résilience
- Sync vs Async: Processing asynchrone pour performance

## Integration Points
### Twitter API v2
- Authentification OAuth 2.0
- Endpoints: users, tweets, media
- Rate limits: 300 requests/15min (app)
- Webhooks Account Activity API (optionnel)

### Telegram Bot API
- Token-based authentication
- Methods: sendMessage, sendPhoto, sendVideo
- Rate limits: 30 messages/second
- File size limits: 50MB video, 10MB photo

### External Services
- **CDN** (optionnel): Cache des médias
- **Monitoring**: Sentry, New Relic, ou DataDog
- **Analytics**: Google Analytics ou Matomo
- **Backup**: AWS S3 ou équivalent

## Security Considerations
### API Keys
- Stockage sécurisé (variables d'environnement)
- Rotation régulière des tokens
- Principe du moindre privilège
- Audit logs des accès

### Data Protection
- Pas de stockage de données personnelles
- Chiffrement des tokens en DB
- HTTPS pour toutes les communications
- Validation/sanitization des entrées

### Rate Limiting
- Protection contre les abus
- Queuing intelligent des requêtes
- Backoff exponentiel sur erreurs
- Monitoring des quotas

## Performance Requirements
### Latence
- Détection nouveau tweet: < 2 minutes
- Publication sur Telegram: < 30 secondes
- API response time: < 500ms
- Database queries: < 100ms

### Throughput
- Support 100+ comptes Twitter
- 1000+ tweets/jour
- 10+ canaux Telegram simultanés
- Gestion pics d'activité (events)

### Disponibilité
- Uptime cible: 99.9%
- Recovery time: < 5 minutes
- Pas de perte de tweets
- Retry automatique sur erreurs

## Scalability Plan
### Horizontal
- Multiple workers pour processing
- Load balancing des requêtes API
- Sharding par compte Twitter
- Queue distribuée (Redis/RabbitMQ)

### Vertical
- Optimisation queries PostgreSQL
- Caching stratégique (Redis)
- Compression des logs
- Archivage des vieilles données

### Future
- Microservices si > 1000 comptes
- Kubernetes pour orchestration
- Event sourcing pour historique
- GraphQL API pour flexibilité

## Dependencies & External Services
### NPM Packages
```json
{
  "twitter-api-v2": "^1.15.0",
  "node-telegram-bot-api": "^0.61.0",
  "sequelize": "^6.35.0",
  "pg": "^8.11.0",
  "winston": "^3.11.0",
  "dotenv": "^16.3.0",
  "express": "^4.18.0",
  "node-cron": "^3.0.0",
  "axios": "^1.6.0",
  "joi": "^17.11.0"
}
```

### Services Tiers
- Twitter Developer Account
- Telegram BotFather
- PostgreSQL hosting (Supabase, Neon, etc.)
- VPS ou PaaS (DigitalOcean, Heroku, etc.)
- Monitoring service
- Domain name (optionnel)

## Monitoring & Logging Strategy
### Logs
- Structured logging (JSON)
- Niveaux: ERROR, WARN, INFO, DEBUG
- Rotation quotidienne
- Centralisation (ELK stack optionnel)

### Métriques
- Tweets processed/hour
- API call success rate
- Response time percentiles
- Error rate by type
- Queue depth

### Alertes
- Bot offline > 5 minutes
- API errors > 10/minute
- Database connection lost
- Disk space < 10%
- Memory usage > 80%

## Testing Strategy
### Unit Tests
- Services isolés (mocks API)
- Utils et helpers
- Data transformations
- Error handling
- Coverage cible: 80%

### Integration Tests
- Database operations
- API integrations (sandbox)
- End-to-end workflows
- Rate limiting behavior

### Load Tests
- Simulation 1000 tweets/minute
- Concurrent API calls
- Database connection pooling
- Memory leak detection

## Code Style & Conventions
### JavaScript/TypeScript
- ESLint configuration standard
- Prettier pour formatage
- JSDoc pour documentation
- Naming: camelCase, PascalCase for classes

### Git Commits
- Conventional Commits format
- Type: feat, fix, docs, style, refactor, test, chore
- Scope: twitter, telegram, db, api, etc.
- Messages en anglais

### Code Review
- PR obligatoire pour main/develop
- Au moins 1 reviewer
- Tests passants requis
- Documentation à jour

## Git Workflow
### Branches
- `main`: Production stable
- `develop`: Intégration development
- `feature/*`: Nouvelles fonctionnalités
- `fix/*`: Corrections de bugs
- `release/*`: Préparation releases

### Release Process
1. Feature freeze sur develop
2. Création branche release
3. Tests et fixes finaux
4. Merge dans main et tag
5. Deploy production
6. Merge back dans develop

## CI/CD Pipeline
### GitHub Actions
```yaml
# Tests sur chaque PR
- Lint code
- Run unit tests
- Run integration tests
- Check code coverage
- Security audit

# Deploy sur merge main
- Build Docker image
- Push to registry
- Deploy to production
- Run smoke tests
- Notify team
```

### Environnements
- **Development**: Local uniquement
- **Staging**: Pré-production (optionnel)
- **Production**: Serveur principal

## Rollback Strategy
### Immediate (< 5 min)
1. Revert to previous Docker image
2. Restore database backup si nécessaire
3. Clear cache Redis
4. Notify monitoring

### Planned
1. Git revert du commit problématique
2. Hotfix et tests
3. Deploy nouvelle version
4. Post-mortem

### Data Corruption
1. Stop bot immediately
2. Analyze extent of corruption
3. Restore from backup
4. Replay missed tweets if possible
5. Implement safeguards