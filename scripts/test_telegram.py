#!/usr/bin/env python3
"""Script pour tester la connexion Telegram"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.publisher import TelegramPublisher
from src.config import settings
from src.utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

async def test_telegram():
    """Tester la connexion et l'envoi via Telegram"""
    try:
        logger.info("Test de la connexion Telegram...")
        
        publisher = TelegramPublisher(settings.telegram_bot_token)
        
        # Tester la connexion
        if not await publisher.test_connection():
            logger.error("Impossible de se connecter au bot Telegram")
            return
        
        logger.info("✓ Connexion au bot réussie")
        
        # Créer un tweet de test
        test_tweet = {
            'id': 'test_123',
            'text': """🧪 Test du bot Twitter-Telegram

Ceci est un message de test pour vérifier que le bot fonctionne correctement.

#test #bot #telegram""",
            'created_at': datetime.now(),
            'author': 'test_bot',
            'author_name': 'Bot de Test',
            'url': 'https://twitter.com/test_bot/status/123',
            'media': [],
            'likes': 42,
            'retweets': 10,
            'replies': 5
        }
        
        logger.info(f"\nEnvoi d'un message de test vers {settings.telegram_channel_id}")
        logger.info("Appuyez sur Entrée pour envoyer ou Ctrl+C pour annuler")
        input()
        
        # Envoyer le message
        message_id = await publisher.publish_tweet(
            tweet=test_tweet,
            channel_id=settings.telegram_channel_id
        )
        
        if message_id:
            logger.info(f"✓ Message envoyé avec succès (ID: {message_id})")
            
            # Proposer de supprimer
            logger.info("\nVoulez-vous supprimer le message de test? (o/n)")
            response = input()
            if response.lower() == 'o':
                await publisher.delete_message(
                    channel_id=settings.telegram_channel_id,
                    message_id=message_id
                )
                logger.info("✓ Message supprimé")
        else:
            logger.error("✗ Échec de l'envoi du message")
        
    except KeyboardInterrupt:
        logger.info("\nTest annulé")
    except Exception as e:
        logger.error(f"Erreur test Telegram: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_telegram())