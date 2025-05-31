#!/usr/bin/env python3
"""Bot Twitter-Telegram avec APIs gratuites/peu chères"""
import asyncio
import signal
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Dict, List, Set
from datetime import datetime, timedelta

from config import settings
from utils.logger import get_logger
from scraper.cheap_api_scraper import CheapAPIScraper
from publisher import TelegramPublisher
from models import db

logger = get_logger(__name__)

class TwitterTelegramBotCheap:
    def __init__(self):
        self.scraper = CheapAPIScraper()
        self.publisher = None
        self.running = False
        self.processed_tweets: Set[str] = set()
        
    async def setup(self):
        """Initialiser tous les composants"""
        logger.info("Initialisation du bot Twitter-Telegram (APIs économiques)...")
        
        # Connexion à la base de données
        await db.connect()
        await db.init_schema()
        
        # Initialiser le publisher Telegram
        self.publisher = TelegramPublisher(settings.telegram_bot_token)
        
        # Tester la connexion Telegram
        if not await self.publisher.test_connection():
            raise Exception("Impossible de se connecter au bot Telegram")
        
        logger.info("✅ Bot initialisé avec APIs économiques")
    
    async def cleanup(self):
        """Nettoyer les ressources"""
        logger.info("Arrêt du bot...")
        self.running = False
        
        await db.disconnect()
        logger.info("Bot arrêté proprement")
    
    async def process_account(self, account: Dict):
        """Traiter un compte Twitter"""
        username = account['username']
        channel_id = account['telegram_channel_id']
        last_tweet_id = account['last_tweet_id']
        
        try:
            logger.info(f"Vérification des tweets de @{username}")
            
            async with self.scraper:
                # Récupérer les nouveaux tweets - On peut en prendre plusieurs par requête
                tweets = await self.scraper.fetch_tweets(
                    username=username,
                    since_id=last_tweet_id,
                    limit=5  # 1 requête = jusqu'à 5 tweets (économise l'API)
                )
            
            if not tweets:
                logger.debug(f"Aucun nouveau tweet pour @{username}")
                return
            
            logger.info(f"📊 {len(tweets)} tweets trouvés pour @{username}")
            
            # Traiter les tweets du plus ancien au plus récent
            new_tweets = 0
            for tweet in reversed(tweets):
                tweet_id = tweet['id']
                
                # Vérifier si déjà publié
                if await db.is_tweet_published(tweet_id):
                    logger.debug(f"Tweet {tweet_id} déjà publié")
                    continue
                
                # Publier sur Telegram
                logger.info(f"📤 Publication du tweet {tweet_id} de @{username}")
                
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
                    
                    new_tweets += 1
                    logger.info(f"✅ Tweet publié avec succès")
                    
                    # Petit délai entre les publications
                    await asyncio.sleep(2)
                else:
                    logger.error(f"❌ Échec publication tweet {tweet_id}")
            
            if new_tweets > 0:
                logger.info(f"📈 {new_tweets} nouveaux tweets publiés pour @{username}")
                    
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
                logger.info("Utilisez: python scripts/add_account_simple.py --username compte --channel @canal")
                return
            
            logger.info(f"🔄 Traitement de {len(accounts)} comptes")
            
            # Traiter chaque compte
            for account in accounts:
                if not self.running:
                    break
                    
                await self.process_account(account)
                
                # Délai entre les comptes
                await asyncio.sleep(5)
            
            # Statistiques
            total_tweets = await db.get_published_tweets_count()
            logger.info(f"📊 Total tweets publiés: {total_tweets}")
            
            # Nettoyage périodique
            if datetime.now().hour == 3 and datetime.now().minute < 5:
                logger.info("🧹 Nettoyage automatique...")
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
        
        logger.info(f"⏰ Intervalle de vérification: {settings.poll_interval} secondes")
        logger.info("💡 Astuce: Les APIs gratuites ont des limites, le bot optimise les requêtes")
        
        while self.running:
            try:
                # Exécuter un cycle
                await self.run_cycle()
                
                # Attendre avant le prochain cycle
                logger.info(f"⏳ Prochain cycle dans {settings.poll_interval} secondes...")
                logger.info("💤 Appuyez Ctrl+C pour arrêter")
                await asyncio.sleep(settings.poll_interval)
                
            except Exception as e:
                logger.error(f"Erreur critique: {e}")
                logger.info("🔄 Redémarrage dans 60 secondes...")
                await asyncio.sleep(60)

def signal_handler(bot: TwitterTelegramBotCheap):
    """Gestionnaire de signaux pour arrêt propre"""
    def handler(signum, frame):
        logger.info(f"\n👋 Arrêt demandé...")
        bot.running = False
    return handler

async def main():
    """Point d'entrée principal"""
    bot = TwitterTelegramBotCheap()
    
    # Configurer les gestionnaires de signaux
    signal.signal(signal.SIGINT, signal_handler(bot))
    signal.signal(signal.SIGTERM, signal_handler(bot))
    
    try:
        # Initialisation
        await bot.setup()
        
        logger.info("=" * 60)
        logger.info("🤖 Bot Twitter-Telegram démarré avec succès!")
        logger.info("💰 Mode économique: APIs gratuites ou très peu chères")
        logger.info("📡 Le bot vérifiera les nouveaux tweets régulièrement")
        logger.info("=" * 60)
        
        # Lancer le bot
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Nettoyage
        await bot.cleanup()
        logger.info("👋 Bot arrêté. À bientôt!")

if __name__ == "__main__":
    asyncio.run(main())