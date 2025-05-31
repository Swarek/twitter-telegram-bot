# Twitter → Telegram Bot 🐦➡️💬

Republier automatiquement les tweets de vos comptes préférés vers Telegram. Simple, efficace, économique.

![Demo](https://img.shields.io/badge/Demo-Live-green)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)

## 🎯 À quoi ça sert ?

Ce bot surveille les comptes Twitter que vous choisissez et republie automatiquement leurs tweets dans vos canaux Telegram. Parfait pour :
- 📰 Suivre l'actualité sans ouvrir Twitter
- 🎮 Créer des canaux thématiques (crypto, tech, gaming...)
- 👥 Partager du contenu avec votre communauté

## ⚡ Installation en 5 minutes

### 1. Cloner le projet
```bash
git clone https://github.com/Swarek/twitter-telegram-bot.git
cd twitter-telegram-bot
```

### 2. Installation automatique (Mac/Linux)
```bash
# Lancez le script d'installation
./setup.sh
```

Ou manuellement :
```bash
# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'interface web
python web_app.py
```

### 3. Ouvrir votre navigateur
Allez sur http://localhost:5000 et suivez les 3 étapes :
1. **Créez votre bot Telegram** avec @BotFather
2. **Obtenez une clé RapidAPI** (gratuit, 100 requêtes/mois)
3. **Ajoutez vos premiers comptes Twitter** à suivre

C'est tout ! 🎉

## 💡 Configuration simple

Tout se fait via l'interface web :
- ➕ Ajouter/supprimer des comptes Twitter
- 📊 Voir les statistiques
- ⚙️ Régler la fréquence de vérification

## 🚀 Lancer le bot

```bash
# Mode normal
python src/main.py

# Ou en arrière-plan avec PM2
pm2 start src/main.py --interpreter python3.11 --name twitter-bot
```

## 💰 Coûts

- **RapidAPI Free** : 100 requêtes/mois = ~3 comptes Twitter
- **RapidAPI Basic** : 1000 requêtes/mois pour 10€ = ~30 comptes
- **Hébergement** : Gratuit sur votre PC/Mac

## 📋 Prérequis

- Python 3.11+
- PostgreSQL (optionnel, SQLite par défaut)
- Redis (optionnel, pour les fonctionnalités avancées)

### Installation des prérequis sur Mac
```bash
brew install python@3.11 postgresql@15 redis
brew services start postgresql@15
brew services start redis
```

## 🛠️ Commandes utiles

```bash
# Initialiser la base de données
python scripts/init_db.py

# Voir les comptes surveillés
python scripts/list_accounts.py

# Ajouter un compte manuellement
python scripts/add_account.py username @channel_telegram

# Tester la connexion
python scripts/test_telegram.py
```

## 📦 Structure simple

```
twitter-telegram-bot/
├── web_app.py          # Interface web
├── src/main.py         # Bot principal
├── .env                # Configuration
└── README.md           # Ce fichier
```

## ❓ FAQ

**Q: Combien de comptes puis-je suivre ?**  
R: Avec le plan gratuit, 1-3 comptes. Avec le plan Basic (10€/mois), jusqu'à 30 comptes.

**Q: Le bot fonctionne-t-il 24/7 ?**  
R: Oui, tant que votre ordinateur est allumé ou si vous l'hébergez sur un serveur.

**Q: Puis-je filtrer les tweets ?**  
R: Pas encore, mais c'est prévu dans la prochaine version !

## 🤝 Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à :
- 🐛 Signaler des bugs
- 💡 Proposer des améliorations
- 🔧 Soumettre des pull requests

## 📄 License

MIT - Utilisez-le comme vous voulez !

---

<p align="center">
  Fait avec ❤️ pour simplifier votre veille Twitter
</p>