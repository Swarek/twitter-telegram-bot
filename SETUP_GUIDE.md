# 🚀 Guide de Configuration Rapide

## 1. Installer les dépendances

D'abord, vous devez installer les dépendances Python :

```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## 2. Clés et tokens nécessaires

Vous devez me fournir les informations suivantes pour configurer le bot :

### 🤖 Bot Telegram
1. Allez sur Telegram et parlez à [@BotFather](https://t.me/botfather)
2. Créez un nouveau bot avec `/newbot`
3. **Donnez-moi le token** qui ressemble à : `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`

### 📢 Canal Telegram
1. Créez un canal Telegram (ou utilisez un existant)
2. Ajoutez votre bot comme administrateur du canal
3. **Donnez-moi l'identifiant du canal** :
   - Pour un canal public : `@nom_du_canal`
   - Pour un canal privé : utilisez ce bot pour obtenir l'ID : [@userinfobot](https://t.me/userinfobot)

### 🐦 Compte Twitter pour twscrape
Pour scraper Twitter gratuitement, twscrape a besoin d'un compte Twitter réel :

1. **Username Twitter** : votre_username (sans le @)
2. **Mot de passe Twitter** : votre_mot_de_passe
3. **Email associé au compte** : votre_email@example.com

> ⚠️ **Recommandation** : Utilisez un compte Twitter secondaire dédié au scraping, pas votre compte principal.

### 📝 Comptes Twitter à surveiller
Listez les comptes Twitter que vous voulez suivre :
- @compte1
- @compte2
- etc.

## 3. Format pour me donner les informations

Copiez et remplissez ceci :

```
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHANNEL_ID=

TWITTER_USERNAME=
TWITTER_PASSWORD=
TWITTER_EMAIL=

Comptes à surveiller:
- 
- 
```

## 4. Optionnel : PostgreSQL et Redis

Si PostgreSQL et Redis ne sont pas installés :

```bash
# Installer avec Homebrew
brew install postgresql@15 redis

# Démarrer les services
brew services start postgresql@15
brew services start redis

# Créer la base de données
createdb twitter_telegram
```

---

Une fois que vous m'avez donné ces informations, je configurerai automatiquement le fichier `.env` et le bot sera prêt à démarrer !