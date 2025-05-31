#!/bin/bash

echo "🚀 Configuration du repository GitHub pour Twitter-Telegram Bot"
echo "============================================="

# Initialiser git si pas déjà fait
if [ ! -d ".git" ]; then
    echo "📦 Initialisation de Git..."
    git init
fi

# Ajouter tous les fichiers
echo "📝 Ajout des fichiers..."
git add .

# Premier commit
echo "💾 Création du premier commit..."
git commit -m "🎉 Initial commit - Twitter-Telegram Bot

- Bot automatique Twitter vers Telegram
- Interface web moderne
- Support multi-comptes
- APIs économiques (100 req/mois gratuit)
- Configuration guidée étape par étape"

echo ""
echo "✅ Repository local prêt !"
echo ""
echo "📌 Prochaines étapes :"
echo "1. Créez un nouveau repository sur GitHub : https://github.com/new"
echo "   - Nom : twitter-telegram-bot"
echo "   - Description : Bot automatique qui republie les tweets vers Telegram"
echo "   - Public"
echo "   - NE PAS initialiser avec README, .gitignore ou license"
echo ""
echo "2. Puis exécutez ces commandes :"
echo "   git remote add origin https://github.com/VOTRE_USERNAME/twitter-telegram-bot.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "💡 Remplacez VOTRE_USERNAME par votre nom d'utilisateur GitHub"