# 🚀 Configuration RapidAPI - Guide étape par étape

## ✅ Votre clé RapidAPI est configurée !

Clé : `YOUR_RAPIDAPI_KEY_HERE`

## ⚠️ Il faut maintenant s'abonner à une API Twitter

### Étapes à suivre :

1. **Aller sur RapidAPI** : https://rapidapi.com/hub

2. **Rechercher une API Twitter gratuite**
   - Dans la barre de recherche, tapez "Twitter"
   - Filtrer par "Freemium" ou "Free"

3. **APIs recommandées (GRATUITES)** :

   ### Option A : Twitter135 (Recommandé)
   - Lien direct : https://rapidapi.com/soroushparviz/api/twitter135
   - Plan gratuit : 100 requêtes/mois
   - Cliquer "Subscribe to Test" → Choisir "Basic (Free)"

   ### Option B : Twitter v2
   - Lien : https://rapidapi.com/twitter-api-twitter-api-default/api/twitter-v24
   - Plan gratuit disponible

   ### Option C : Twitter API v2
   - Lien : https://rapidapi.com/UnlimitedAPI/api/twitter-v23
   - Plan gratuit disponible

4. **S'abonner au plan GRATUIT**
   - Cliquer sur l'API choisie
   - Aller dans l'onglet "Pricing"
   - Sélectionner "Basic" ou "Free" (0$/month)
   - Cliquer "Subscribe"

5. **Tester l'API**
   - Aller dans l'onglet "Endpoints"
   - Tester "Get User Tweets" avec username "elonmusk"
   - Si ça marche, c'est bon !

## 🔧 Après l'abonnement

Une fois abonné à une API Twitter, relancez le test :

```bash
cd /Users/mathisblanc/Documents/Projets/twittertelegram
source venv/bin/activate
python scripts/test_rapidapi.py elonmusk
```

Si ça fonctionne, lancez le bot :

```bash
python run_bot_cheap.py
```

## 📝 Notes importantes

- Chaque API a ses propres endpoints et formats
- Le bot essaiera automatiquement plusieurs formats
- 100 requêtes/mois suffisent largement pour suivre quelques comptes
- Vous pouvez vous abonner à plusieurs APIs gratuites pour plus de requêtes

## 🆘 Si ça ne fonctionne pas

1. Vérifiez que vous êtes bien abonné (allez dans "My Apps" sur RapidAPI)
2. Essayez une autre API de la liste
3. Vérifiez que le compte Twitter existe (@elonmusk)

Besoin d'aide ? Dites-moi quelle API vous avez choisie !