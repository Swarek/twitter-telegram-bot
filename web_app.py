#!/usr/bin/env python3
"""Interface web pour gérer le bot Twitter-Telegram"""
import asyncio
from functools import wraps
from flask import Flask, jsonify, request, render_template, redirect
from flask_cors import CORS
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from models import db
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

app = Flask(__name__, 
    static_url_path='/static',
    static_folder='web/static',
    template_folder='web/templates'
)
CORS(app)

# Helper pour gérer les fonctions async dans Flask
def async_route(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    return wrapper

# Routes API
@app.route('/api/accounts', methods=['GET'])
@async_route
async def get_accounts():
    """Récupérer tous les comptes"""
    try:
        await db.connect()
        accounts = await db.get_active_accounts()
        await db.disconnect()
        
        return jsonify({
            'success': True,
            'accounts': accounts,
            'total': len(accounts)
        })
    except Exception as e:
        logger.error(f"Erreur get_accounts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/accounts', methods=['POST'])
@async_route
async def add_account():
    """Ajouter un compte"""
    try:
        data = request.json
        username = data.get('username', '').lstrip('@')
        channel_id = data.get('channel_id', '')
        
        if not username or not channel_id:
            return jsonify({'success': False, 'error': 'Username et channel requis'}), 400
        
        await db.connect()
        account_id = await db.add_twitter_account(
            username=username,
            channel_id=channel_id,
            twitter_id=None
        )
        await db.disconnect()
        
        return jsonify({
            'success': True,
            'account_id': account_id,
            'message': f'Compte @{username} ajouté avec succès'
        })
    except Exception as e:
        logger.error(f"Erreur add_account: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/accounts/<username>/toggle', methods=['POST'])
@async_route
async def toggle_account(username):
    """Activer/désactiver un compte"""
    try:
        data = request.json
        active = data.get('active', True)
        
        await db.connect()
        query = """
        UPDATE twitter_accounts 
        SET is_active = $1, updated_at = NOW()
        WHERE username = $2
        RETURNING id
        """
        
        async with db.pool.acquire() as conn:
            result = await conn.fetchval(query, active, username)
        
        await db.disconnect()
        
        if result:
            return jsonify({
                'success': True,
                'message': f'Compte @{username} {"activé" if active else "désactivé"}'
            })
        else:
            return jsonify({'success': False, 'error': 'Compte non trouvé'}), 404
            
    except Exception as e:
        logger.error(f"Erreur toggle_account: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
@async_route
async def get_stats():
    """Récupérer les statistiques"""
    try:
        await db.connect()
        
        # Stats globales
        total_tweets = await db.get_published_tweets_count()
        accounts = await db.get_active_accounts()
        active_accounts = len([a for a in accounts if a['is_active']])
        
        # Tweets récents
        query = """
        SELECT pt.tweet_id, pt.telegram_message_id, pt.published_at, 
               pt.tweet_data->>'text' as text, ta.username
        FROM published_tweets pt
        JOIN twitter_accounts ta ON ta.id = pt.account_id
        ORDER BY pt.published_at DESC
        LIMIT 10
        """
        
        async with db.pool.acquire() as conn:
            recent_tweets = await conn.fetch(query)
        
        await db.disconnect()
        
        # Calcul utilisation API
        checks_per_day = 24 * 3600 / settings.poll_interval
        requests_per_month = active_accounts * 2 * checks_per_day * 30
        
        return jsonify({
            'success': True,
            'stats': {
                'total_tweets': total_tweets,
                'total_accounts': len(accounts),
                'active_accounts': active_accounts,
                'api_usage': {
                    'monthly_limit': 100,
                    'estimated_usage': int(requests_per_month),
                    'percentage': int(requests_per_month / 100 * 100)
                },
                'poll_interval': settings.poll_interval,
                'recent_tweets': [dict(t) for t in recent_tweets]
            }
        })
    except Exception as e:
        logger.error(f"Erreur get_stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bot/status', methods=['GET'])
@async_route
async def bot_status():
    """Statut du bot"""
    try:
        # Vérifier si le bot tourne (simple check)
        bot_running = os.path.exists('/tmp/twitter_telegram_bot.pid')
        
        return jsonify({
            'success': True,
            'running': bot_running,
            'config': {
                'poll_interval': settings.poll_interval,
                'telegram_channel': settings.telegram_channel_id
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Route principale
@app.route('/')
def index():
    """Page principale"""
    # Vérifier si le bot est configuré
    if not settings.telegram_bot_token or settings.telegram_bot_token.startswith('YOUR_'):
        return redirect('/setup')
    return render_template('index_clean.html')

@app.route('/setup')
def setup():
    """Page de configuration initiale"""
    return render_template('setup.html')

@app.route('/api/config', methods=['POST'])
@async_route
async def save_config():
    """Sauvegarder la configuration"""
    try:
        data = request.json
        
        # Valider les données
        telegram_token = data.get('telegram_token', '').strip()
        rapidapi_key = data.get('rapidapi_key', '').strip()
        
        if not telegram_token or not rapidapi_key:
            return jsonify({'success': False, 'error': 'Token et clé API requis'}), 400
        
        # Sauvegarder dans .env
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        env_example_path = env_path + '.example'
        
        # Si .env n'existe pas, le créer à partir de .env.example
        if not os.path.exists(env_path) and os.path.exists(env_example_path):
            import shutil
            shutil.copy(env_example_path, env_path)
        
        # Lire le .env actuel ou créer un nouveau
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()
        else:
            # Créer un .env minimal si aucun fichier n'existe
            lines = []
        
        # Créer un dictionnaire des lignes existantes
        env_dict = {}
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key = line.split('=')[0].strip()
                env_dict[key] = line
        
        # Mettre à jour ou ajouter les valeurs
        env_dict['TELEGRAM_BOT_TOKEN'] = f'TELEGRAM_BOT_TOKEN={telegram_token}\n'
        env_dict['RAPIDAPI_KEY'] = f'RAPIDAPI_KEY={rapidapi_key}\n'
        
        # Si le canal est fourni, l'ajouter aussi
        if data.get('first_channel'):
            env_dict['TELEGRAM_CHANNEL_ID'] = f'TELEGRAM_CHANNEL_ID={data["first_channel"]}\n'
        
        # Reconstruire le fichier en conservant l'ordre et les commentaires
        new_lines = []
        keys_written = set()
        
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key = line.split('=')[0].strip()
                if key in env_dict:
                    new_lines.append(env_dict[key])
                    keys_written.add(key)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        # Ajouter les nouvelles clés qui n'étaient pas dans le fichier
        for key, value in env_dict.items():
            if key not in keys_written:
                new_lines.append(value)
        
        # Écrire le fichier mis à jour
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
        
        # Si premier compte fourni, l'ajouter
        if data.get('first_account') and data.get('first_channel'):
            await db.connect()
            await db.add_twitter_account(
                username=data['first_account'],
                channel_id=data['first_channel'],
                twitter_id=None
            )
            await db.disconnect()
        
        return jsonify({
            'success': True,
            'message': 'Configuration sauvegardée avec succès'
        })
        
    except Exception as e:
        logger.error(f"Erreur save_config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("🌐 Démarrage de l'interface web...")
    app.run(debug=True, port=5000)