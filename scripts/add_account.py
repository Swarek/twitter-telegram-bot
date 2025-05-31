#!/usr/bin/env python3
"""Script pour ajouter un compte Twitter à surveiller"""
import asyncio
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import db
from src.scraper import TwitterScraper
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def add_account(username: str, channel_id: str):
    """Ajouter un compte Twitter à surveiller"""
    try:
        # Nettoyer le username (enlever @)
        username = username.lstrip('@')
        
        logger.info(f"Ajout du compte @{username} -> {channel_id}")
        
        # Connexion à la base de données
        await db.connect()
        
        # Vérifier si le compte existe déjà
        existing = await db.get_account(username)
        if existing:
            logger.warning(f"Le compte @{username} existe déjà")
            response = input("Voulez-vous mettre à jour le canal? (o/n): ")
            if response.lower() != 'o':
                return
        
        # Optionnel: vérifier que le compte Twitter existe
        logger.info("Vérification du compte Twitter...")
        scraper = TwitterScraper()
        await scraper.setup_accounts()
        
        user_id = await scraper.get_user_id(username)
        if not user_id:
            logger.warning(f"Impossible de vérifier le compte @{username}")
            response = input("Continuer quand même? (o/n): ")
            if response.lower() != 'o':
                return
        else:
            logger.info(f"Compte Twitter vérifié: @{username} (ID: {user_id})")
        
        # Ajouter à la base de données
        account_id = await db.add_twitter_account(
            username=username,
            channel_id=channel_id,
            twitter_id=user_id
        )
        
        logger.info(f"Compte ajouté avec succès (ID: {account_id})")
        
        # Afficher la liste des comptes
        accounts = await db.get_active_accounts()
        logger.info(f"\nComptes surveillés ({len(accounts)}):")
        for acc in accounts:
            logger.info(f"  - @{acc['username']} -> {acc['telegram_channel_id']}")
        
    except Exception as e:
        logger.error(f"Erreur ajout compte: {e}")
        sys.exit(1)
    finally:
        await db.disconnect()

def main():
    parser = argparse.ArgumentParser(description="Ajouter un compte Twitter à surveiller")
    parser.add_argument(
        "--username", "-u",
        required=True,
        help="Username Twitter (avec ou sans @)"
    )
    parser.add_argument(
        "--channel", "-c",
        required=True,
        help="ID du canal Telegram (ex: @mychannel ou -1001234567890)"
    )
    
    args = parser.parse_args()
    
    asyncio.run(add_account(args.username, args.channel))

if __name__ == "__main__":
    main()