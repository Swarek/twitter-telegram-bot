#!/usr/bin/env python3
"""Script pour configurer twscrape avec les comptes Twitter"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from twscrape import API
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def setup_twscrape():
    """Configurer les comptes Twitter pour twscrape"""
    try:
        api = API()
        
        # Réinitialiser la base de données twscrape
        logger.info("Réinitialisation de la base de données twscrape...")
        await api.pool.reset_locks()
        
        accounts = settings.get_twitter_accounts()
        if not accounts:
            logger.error("Aucun compte Twitter configuré dans .env")
            return
        
        logger.info(f"Configuration de {len(accounts)} comptes Twitter...")
        
        for username, password, email, email_password in accounts:
            try:
                logger.info(f"Ajout du compte: {username}")
                await api.pool.add_account(
                    username=username,
                    password=password,
                    email=email,
                    email_password=email_password
                )
                logger.info(f"✅ Compte {username} ajouté")
            except Exception as e:
                logger.error(f"❌ Erreur ajout compte {username}: {e}")
        
        logger.info("\nConnexion aux comptes...")
        await api.pool.login_all()
        
        # Vérifier les comptes
        logger.info("\nVérification des comptes:")
        accounts_info = await api.pool.accounts_info()
        
        for acc in accounts_info:
            status = "✅ Actif" if getattr(acc, 'active', False) else "❌ Inactif"
            logger.info(f"  - {getattr(acc, 'username', 'Unknown')}: {status}")
        
        active_count = len([acc for acc in accounts_info if getattr(acc, 'active', False)])
        logger.info(f"\nTotal: {active_count} comptes actifs sur {len(accounts_info)}")
        
        if active_count == 0:
            logger.warning("\n⚠️  Aucun compte actif. Causes possibles:")
            logger.warning("  - IP bannie temporairement par Twitter")
            logger.warning("  - Mauvais identifiants")
            logger.warning("  - Compte nécessite une vérification")
            logger.warning("\nSolutions:")
            logger.warning("  - Essayer avec un VPN")
            logger.warning("  - Vérifier les identifiants")
            logger.warning("  - Utiliser un compte différent")
        
    except Exception as e:
        logger.error(f"Erreur configuration twscrape: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(setup_twscrape())