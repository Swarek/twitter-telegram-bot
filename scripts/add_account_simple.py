#!/usr/bin/env python3
"""Script simplifié pour ajouter un compte Twitter à surveiller"""
import asyncio
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import db
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def add_account(username: str, channel_id: str):
    """Ajouter un compte Twitter à surveiller sans vérification"""
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
            logger.info("Mise à jour du canal...")
        
        # Ajouter à la base de données
        account_id = await db.add_twitter_account(
            username=username,
            channel_id=channel_id,
            twitter_id=None  # On récupérera l'ID plus tard
        )
        
        logger.info(f"✅ Compte ajouté avec succès (ID: {account_id})")
        
        # Afficher la liste des comptes
        accounts = await db.get_active_accounts()
        logger.info(f"\n📋 Comptes surveillés ({len(accounts)}):")
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