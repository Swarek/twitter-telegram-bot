#!/usr/bin/env python3
import asyncio
import signal
import sys
from typing import Dict, List, Set
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from config import settings
from utils.logger import get_logger
from scraper import TwitterScraper
from publisher import TelegramPublisher
from models import db

logger = get_logger(__name__)

class TwitterTelegramBot:
    def __init__(self):
        self.scraper = TwitterScraper()
        self.publisher = None
        self.running = False
        self.processed_tweets: Set[str] = set()
        
    async def setup(self):
        """Initialiser tous les composants"""
        logger.info("Initialisation du bot Twitter-Telegram...")
        
        # Connexion à la base de données
        await db.connect()
        await db.init_schema()
        
        # Initialiser le scraper Twitter
        await self.scraper.setup_accounts()
        
        # Initialiser le publisher Telegram
        self.publisher = TelegramPublisher(settings.telegram_bot_token)
        
        # Tester la connexion Telegram
        if not await self.publisher.test_connection():
            raise Exception("Impossible de se connecter au bot Telegram")
        
        logger.info("Bot initialisé avec succès")
    
    async def cleanup(self):
        """Nettoyer les ressources"""
        logger.info("Arrêt du bot...")
        self.running = False
        
        if self.publisher and hasattr(self.publisher, 'session'):
            await self.publisher.__aexit__(None, None, None)
        
        await db.disconnect()
        logger.info("Bot arrêté proprement")
    
    async def process_account(self, account: Dict):
        """Traiter un compte Twitter"""
        username = account['username']
        channel_id = account['telegram_channel_id']
        last_tweet_id = account['last_tweet_id']
        
        try:
            logger.info(f"Vérification des tweets de @{username}")
            
            # Récupérer les nouveaux tweets
            tweets = await self.scraper.fetch_tweets(
                username=username,
                since_id=last_tweet_id,
                limit=20
            )
            
            if not tweets:
                logger.debug(f"Aucun nouveau tweet pour @{username}")
                return
            
            logger.info(f"{len(tweets)} nouveaux tweets trouvés pour @{username}")
            
            # Traiter les tweets du plus ancien au plus récent
            for tweet in reversed(tweets):
                tweet_id = tweet['id']
                
                # Vérifier si déjà publié
                if await db.is_tweet_published(tweet_id):
                    logger.debug(f"Tweet {tweet_id} déjà publié")
                    continue
                
                # Publier sur Telegram
                logger.info(f"Publication du tweet {tweet_id} de @{username}")
                
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
                    
                    logger.info(f"Tweet {tweet_id} publié avec succès")
                    
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
    
    async def run_cycle(self):
        """Exécuter un cycle de vérification"""
        try:
            # Récupérer les comptes actifs
            accounts = await db.get_active_accounts()
            
            if not accounts:
                logger.warning("Aucun compte Twitter configuré")
                return
            
            logger.info(f"Traitement de {len(accounts)} comptes")
            
            # Traiter chaque compte
            for account in accounts:
                if not self.running:
                    break
                    
                await self.process_account(account)
                
                # Délai entre les comptes pour éviter le rate limiting
                await asyncio.sleep(5)
            
            # Nettoyage périodique
            if datetime.now().hour == 3 and datetime.now().minute < 5:
                await db.cleanup_old_tweets(days=30)
                await db.cleanup_old_errors(days=7)
                
        except Exception as e:
            logger.error(f"Erreur dans le cycle principal: {e}")
            await db.log_error(
                error_type="main_cycle",
                error_message=str(e)
            )
    
    async def run(self):
        """Boucle principale du bot"""
        self.running = True
        
        logger.info(f"Démarrage de la boucle principale (intervalle: {settings.poll_interval}s)")
        
        while self.running:
            try:
                # Exécuter un cycle
                await self.run_cycle()
                
                # Attendre avant le prochain cycle
                logger.info(f"Attente de {settings.poll_interval}s avant le prochain cycle")
                await asyncio.sleep(settings.poll_interval)
                
            except Exception as e:
                logger.error(f"Erreur critique: {e}")
                await asyncio.sleep(60)  # Attendre 1 minute avant de réessayer

def signal_handler(bot: TwitterTelegramBot):
    """Gestionnaire de signaux pour arrêt propre"""
    def handler(signum, frame):
        logger.info(f"Signal {signum} reçu, arrêt du bot...")
        bot.running = False
    return handler

async def main():
    """Point d'entrée principal"""
    bot = TwitterTelegramBot()
    
    # Configurer les gestionnaires de signaux
    signal.signal(signal.SIGINT, signal_handler(bot))
    signal.signal(signal.SIGTERM, signal_handler(bot))
    
    try:
        # Initialisation
        await bot.setup()
        
        # Lancer le bot
        await bot.run()
        
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
    logger.info("Twitter-Telegram Bot v1.0.0")
    logger.info(f"Environnement: {settings.environment}")
    logger.info(f"Log level: {settings.log_level}")
    logger.info("=" * 50)
    
    # Lancer le bot
    asyncio.run(main())