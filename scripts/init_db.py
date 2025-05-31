#!/usr/bin/env python3
"""Script pour initialiser la base de données"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import db
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def init_database():
    """Initialiser la base de données"""
    try:
        logger.info("Connexion à la base de données...")
        await db.connect()
        
        logger.info("Création du schéma...")
        await db.init_schema()
        
        logger.info("Base de données initialisée avec succès!")
        
        # Afficher les statistiques
        accounts_count = len(await db.get_active_accounts())
        tweets_count = await db.get_published_tweets_count()
        
        logger.info(f"Comptes actifs: {accounts_count}")
        logger.info(f"Tweets publiés: {tweets_count}")
        
    except Exception as e:
        logger.error(f"Erreur initialisation base de données: {e}")
        sys.exit(1)
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(init_database())