#!/usr/bin/env python3
"""Script pour lister les comptes Twitter surveillés"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import db
from src.utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

async def list_accounts():
    """Lister tous les comptes surveillés"""
    try:
        await db.connect()
        
        accounts = await db.get_active_accounts()
        
        if not accounts:
            logger.info("Aucun compte Twitter surveillé")
            return
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Comptes Twitter surveillés: {len(accounts)}")
        logger.info(f"{'='*60}\n")
        
        for account in accounts:
            logger.info(f"Username: @{account['username']}")
            logger.info(f"  Canal Telegram: {account['telegram_channel_id']}")
            logger.info(f"  Twitter ID: {account['twitter_id'] or 'Non vérifié'}")
            logger.info(f"  Actif: {'✓' if account['is_active'] else '✗'}")
            logger.info(f"  Dernier tweet: {account['last_tweet_id'] or 'Aucun'}")
            logger.info(f"  Créé le: {account['created_at'].strftime('%d/%m/%Y %H:%M')}")
            logger.info(f"  Mis à jour: {account['updated_at'].strftime('%d/%m/%Y %H:%M')}")
            
            # Statistiques
            tweets_count = await db.get_published_tweets_count(account['id'])
            logger.info(f"  Tweets publiés: {tweets_count}")
            logger.info("")
        
        # Statistiques globales
        total_tweets = await db.get_published_tweets_count()
        logger.info(f"{'='*60}")
        logger.info(f"Total tweets publiés: {total_tweets}")
        logger.info(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        sys.exit(1)
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(list_accounts())