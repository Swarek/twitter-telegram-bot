# 🎯 Guide des APIs Twitter Gratuites et Très Peu Chères

## 📊 Comparaison des solutions

| Service | Prix | Tweets/mois | Inscription | Fiabilité |
|---------|------|-------------|-------------|-----------|
| **RapidAPI Free** | 0€ | 100-500 | ✅ Facile | ⭐⭐⭐ |
| **TwitterAPI.io** | 0.15$/1000 tweets | Illimité | ✅ Facile | ⭐⭐⭐⭐ |
| **Apify Free** | 0€ | 1000 | ✅ Facile | ⭐⭐⭐ |
| **Twitter Scraper APIs** | 0-10€ | Variable | ⚠️ Variable | ⭐⭐ |

## 🚀 Option 1 : RapidAPI (GRATUIT)

### Étapes d'inscription

1. **Créer un compte RapidAPI** (gratuit)
   - Aller sur https://rapidapi.com/auth/sign-up
   - S'inscrire avec email ou Google/GitHub

2. **Chercher une API Twitter gratuite**
   - Aller sur https://rapidapi.com/search/twitter
   - Filtrer par "Free" ou "Freemium"
   - APIs recommandées :
     - **Twitter135** : 100 requêtes/mois gratuites
     - **Twitter v2 by Tweety** : 500 requêtes/mois gratuites
     - **TwitterData** : 100 requêtes/mois gratuites

3. **S'abonner au plan gratuit**
   - Cliquer sur l'API choisie
   - Aller dans "Pricing"
   - Sélectionner "Basic" (0$/month)
   - Cliquer "Subscribe"

4. **Récupérer votre clé API**
   - Dans "Endpoints", copier votre "X-RapidAPI-Key"
   - Elle ressemble à : `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

5. **Configurer dans le bot**
   ```bash
   # Ajouter dans .env
   RAPIDAPI_KEY=votre_cle_api_ici
   ```

### Exemple de test
```bash
# Tester avec curl
curl -X GET "https://twitter135.p.rapidapi.com/v2/UserTweets/?username=elonmusk&count=5" \
  -H "X-RapidAPI-Key: VOTRE_CLE" \
  -H "X-RapidAPI-Host: twitter135.p.rapidapi.com"
```

## 💰 Option 2 : TwitterAPI.io (0.15$/1000 tweets)

### Pourquoi c'est intéressant ?
- **Ultra peu cher** : 0.15$ = ~0.14€ pour 1000 tweets
- Pour 10 comptes avec 10 tweets/jour = 300 tweets/mois = **0.05€/mois** !
- **Pas d'authentification Twitter** requise
- **Fiable** et rapide

### Inscription
1. Aller sur https://twitterapi.io
2. Cliquer "Get Started"
3. Créer un compte
4. Ajouter 5$ de crédit (durera des mois)
5. Récupérer votre API key

### Configuration
```bash
# Ajouter dans .env
TWITTERAPI_IO_KEY=votre_cle_api_ici
```

## 🆓 Option 3 : Apify Twitter Scraper (1000 tweets gratuits)

### Inscription
1. Aller sur https://apify.com
2. Créer un compte gratuit
3. Chercher "Twitter Scraper"
4. Le plan gratuit offre 1000 résultats

### Utilisation via API
```python
# Exemple d'utilisation
import requests

url = "https://api.apify.com/v2/acts/quacker~twitter-scraper/runs"
headers = {
    "Authorization": "Bearer YOUR_APIFY_TOKEN"
}
data = {
    "searchTerms": ["from:elonmusk"],
    "maxTweets": 10
}
```

## 🔧 Configuration du bot avec APIs gratuites

### 1. Modifier .env
```env
# Ajouter ces lignes
RAPIDAPI_KEY=votre_cle_rapidapi
TWITTERAPI_IO_KEY=votre_cle_twitterapi_io  # Optionnel
APIFY_TOKEN=votre_token_apify  # Optionnel

# Activer le scraper d'APIs cheap
USE_CHEAP_APIS=true
```

### 2. Créer le fichier principal avec APIs
```python
# src/main_cheap.py
from scraper.cheap_api_scraper import CheapAPIScraper
# ... reste du code
```

## 📈 Estimation des coûts mensuels

### Scénario typique : 10 comptes, 10 tweets/jour chacun

| Solution | Calcul | Coût mensuel |
|----------|--------|--------------|
| RapidAPI Free | 100 requêtes gratuites | **0€** |
| TwitterAPI.io | 300 tweets × 0.15$/1000 | **0.05$** (~0.05€) |
| Apify Free | 1000 tweets gratuits | **0€** |
| Mixte (RapidAPI + TwitterAPI.io) | Optimal | **< 0.10€/mois** |

## ✅ Recommandation

Pour votre usage (suivre quelques comptes Twitter) :

1. **Commencer avec RapidAPI gratuit** (0€)
   - 100-500 requêtes/mois suffisent largement
   - Inscription en 2 minutes

2. **Si besoin de plus** : TwitterAPI.io
   - 5$ de crédit durera des mois
   - Ultra fiable

3. **Backup** : Apify gratuit
   - 1000 tweets/mois gratuits
   - Bonne alternative

## 🚀 Lancement rapide

```bash
# 1. S'inscrire sur RapidAPI (2 min)
# 2. Copier la clé API
# 3. Ajouter dans .env :
echo "RAPIDAPI_KEY=votre_cle" >> .env

# 4. Lancer le bot
python run_bot_cheap.py
```

C'est tout ! Votre bot fonctionnera pour moins de 0.10€/mois ! 🎉