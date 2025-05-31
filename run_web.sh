#!/bin/bash
# Lancer l'interface web

echo "🌐 Démarrage de l'interface web Twitter-Telegram Bot..."
echo "📍 URL: http://localhost:5000"
echo ""

# Activer l'environnement virtuel
source venv/bin/activate

# Lancer l'interface
python web_app.py