#!/bin/bash
# Script de configuration pour exécution locale sur macOS

echo "🚀 Configuration du bot Twitter-Telegram pour macOS..."

# Vérifier si Homebrew est installé
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew n'est pas installé. Installation..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Installer les dépendances système
echo "📦 Installation des dépendances système..."
brew install postgresql@15 redis python@3.11

# Démarrer les services
echo "🔧 Démarrage des services..."
brew services start postgresql@15
brew services start redis

# Créer l'environnement Python
echo "🐍 Configuration de l'environnement Python..."
python3.11 -m venv venv
source venv/bin/activate

# Installer les dépendances Python
echo "📚 Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Créer la base de données
echo "🗄️ Configuration de la base de données..."
createdb twitter_telegram 2>/dev/null || echo "Base de données déjà existante"

# Copier le fichier de configuration
if [ ! -f .env ]; then
    echo "⚙️ Création du fichier .env..."
    cp .env.example .env
    echo "⚠️  N'oubliez pas de configurer votre fichier .env !"
fi

# Créer les dossiers nécessaires
echo "📁 Création des dossiers..."
mkdir -p logs data/cache

echo "✅ Configuration terminée !"
echo ""
echo "Prochaines étapes:"
echo "1. Éditer le fichier .env avec vos tokens"
echo "2. Lancer: python src/main.py"
echo ""
echo "Pour arrêter les services:"
echo "brew services stop postgresql@15"
echo "brew services stop redis"