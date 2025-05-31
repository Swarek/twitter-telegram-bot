#!/usr/bin/env python3
"""Version de démonstration du bot pour tester sans authentification Twitter"""
import asyncio
import signal
import sys
from typing import Dict, List, Set
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings
from utils.logger import get_logger
from scraper.simple_scraper import SimpleTwitterScraper
from publisher import TelegramPublisher
from models import db

logger = get_logger(__name__)

class TwitterTelegramBotDemo:
    def __init__(self):
        self.scraper = SimpleTwitterScraper()
        self.publisher = None
        self.running = False
        self.processed_tweets: Set[str] = set()
        
    async def setup(self):
        """Initialiser tous les composants"""
        logger.info("Initialisation du bot Twitter-Telegram (MODE DEMO)...")
        
        # Connexion à la base de données
        await db.connect()
        await db.init_schema()
        
        # Initialiser le publisher Telegram
        self.publisher = TelegramPublisher(settings.telegram_bot_token)
        
        # Tester la connexion Telegram
        if not await self.publisher.test_connection():
            raise Exception("Impossible de se connecter au bot Telegram")
        
        logger.info("Bot initialisé avec succès (MODE DEMO)")
    
    async def cleanup(self):
        """Nettoyer les ressources"""
        logger.info("Arrêt du bot...")
        self.running = False
        
        if self.scraper:
            await self.scraper.__aexit__(None, None, None)
        
        await db.disconnect()
        logger.info("Bot arrêté proprement")
    
    async def process_account(self, account: Dict):
        """Traiter un compte Twitter"""
        username = account['username']
        channel_id = account['telegram_channel_id']
        last_tweet_id = account['last_tweet_id']
        
        try:
            logger.info(f"[DEMO] Vérification des tweets de @{username}")
            
            async with self.scraper:
                # Récupérer les tweets de démo
                tweets = await self.scraper.fetch_tweets(
                    username=username,
                    since_id=last_tweet_id,
                    limit=5
                )
            
            if not tweets:
                logger.debug(f"Aucun nouveau tweet pour @{username}")
                return
            
            logger.info(f"[DEMO] {len(tweets)} tweets de démonstration pour @{username}")
            
            # Traiter les tweets
            for tweet in tweets:
                tweet_id = tweet['id']
                
                # Vérifier si déjà publié
                if await db.is_tweet_published(tweet_id):
                    logger.debug(f"Tweet {tweet_id} déjà publié")
                    continue
                
                # Publier sur Telegram
                logger.info(f"[DEMO] Publication du tweet {tweet_id} de @{username}")
                
                telegram_msg_id = await self.publisher.publish_tweet(
                    tweet=tweet,
                    channel_id=channel_id
                )
                
                if telegram_msg_id:
                    # Enregistrer dans la base de données
                    await db.add_published_tweet(
                        tweet_id=tweet_id,
                        account_id=account['id'],
                        telegram_message_id=telegram_msg_id,
                        channel_id=channel_id,
                        tweet_data=tweet
                    )
                    
                    # Mettre à jour le dernier tweet traité
                    await db.update_last_tweet_id(account['id'], tweet_id)
                    
                    logger.info(f"✅ Tweet {tweet_id} publié avec succès")
                    
                    # Petit délai entre les publications
                    await asyncio.sleep(2)
                else:
                    logger.error(f"Échec publication tweet {tweet_id}")
                    
        except Exception as e:
            logger.error(f"Erreur traitement compte @{username}: {e}")
            await db.log_error(
                error_type="account_processing",
                error_message=str(e),
                error_data={"username": username}
            )
    
    async def run_once(self):
        """Exécuter un seul cycle pour la démo"""
        try:
            # Récupérer les comptes actifs
            accounts = await db.get_active_accounts()
            
            if not accounts:
                logger.warning("Aucun compte Twitter configuré")
                return
            
            logger.info(f"[DEMO] Traitement de {len(accounts)} comptes")
            
            # Traiter chaque compte
            for account in accounts:
                await self.process_account(account)
                
        except Exception as e:
            logger.error(f"Erreur dans le cycle de démo: {e}")

def signal_handler(bot: TwitterTelegramBotDemo):
    """Gestionnaire de signaux pour arrêt propre"""
    def handler(signum, frame):
        logger.info(f"Signal {signum} reçu, arrêt du bot...")
        bot.running = False
    return handler

async def main():
    """Point d'entrée principal"""
    bot = TwitterTelegramBotDemo()
    
    # Configurer les gestionnaires de signaux
    signal.signal(signal.SIGINT, signal_handler(bot))
    signal.signal(signal.SIGTERM, signal_handler(bot))
    
    try:
        # Initialisation
        await bot.setup()
        
        logger.info("=" * 50)
        logger.info("MODE DÉMONSTRATION")
        logger.info("Ce mode envoie des tweets de test pour vérifier")
        logger.info("que la connexion Telegram fonctionne correctement.")
        logger.info("=" * 50)
        
        # Exécuter une fois
        await bot.run_once()
        
        logger.info("\n✅ Démonstration terminée!")
        logger.info("Vérifiez votre canal Telegram pour voir les messages.")
        
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)
    finally:
        # Nettoyage
        await bot.cleanup()

if __name__ == "__main__":
    # Afficher les informations de démarrage
    logger.info("=" * 50)
    logger.info("Twitter-Telegram Bot v1.0.0 - MODE DEMO")
    logger.info(f"Environnement: {settings.environment}")
    logger.info(f"Canal Telegram: {settings.telegram_channel_id}")
    logger.info("=" * 50)
    
    # Lancer le bot
    asyncio.run(main())