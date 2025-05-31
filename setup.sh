#!/bin/bash
# Script d'installation automatique pour Twitter-Telegram Bot

echo "🚀 Installation du Twitter-Telegram Bot"
echo "======================================"

# Vérifier Python 3.11+
echo "📌 Vérification de Python..."
if ! python3 --version | grep -E "3\.(11|12|13)" > /dev/null; then
    echo "❌ Python 3.11+ requis. Installer avec: brew install python@3.11"
    exit 1
fi
echo "✅ Python $(python3 --version)"

# Créer l'environnement virtuel
echo ""
echo "📌 Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
echo ""
echo "📌 Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Vérifier PostgreSQL
echo ""
echo "📌 Vérification de PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL non trouvé. Installation recommandée:"
    echo "   brew install postgresql@15"
    echo "   brew services start postgresql@15"
else
    echo "✅ PostgreSQL installé"
fi

# Vérifier Redis
echo ""
echo "📌 Vérification de Redis..."
if ! command -v redis-cli &> /dev/null; then
    echo "⚠️  Redis non trouvé. Installation recommandée:"
    echo "   brew install redis"
    echo "   brew services start redis"
else
    echo "✅ Redis installé"
fi

# Créer la base de données
echo ""
echo "📌 Configuration de la base de données..."
if command -v createdb &> /dev/null; then
    createdb twitter_telegram 2>/dev/null || echo "   Base 'twitter_telegram' existe déjà"
    echo "✅ Base de données prête"
else
    echo "⚠️  Impossible de créer la base. Créez-la manuellement: createdb twitter_telegram"
fi

# Copier .env.example si .env n'existe pas
if [ ! -f .env ]; then
    echo ""
    echo "📌 Création du fichier .env..."
    cp .env.example .env
    echo "✅ Fichier .env créé (à configurer via l'interface web)"
fi

# Créer les dossiers nécessaires
echo ""
echo "📌 Création des dossiers..."
mkdir -p logs data temp

# Initialiser la base de données
echo ""
echo "📌 Initialisation des tables..."
python scripts/init_db.py 2>/dev/null || echo "⚠️  Configurez d'abord votre .env via l'interface web"

echo ""
echo "✅ Installation terminée !"
echo ""
echo "🎯 Prochaines étapes:"
echo "   1. Lancez l'interface web: python web_app.py"
echo "   2. Ouvrez http://localhost:5000"
echo "   3. Suivez les 3 étapes de configuration"
echo ""
echo "💡 Pour lancer le bot après configuration: python src/main.py"