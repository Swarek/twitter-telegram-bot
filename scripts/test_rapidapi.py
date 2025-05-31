#!/usr/bin/env python3
"""Script pour tester la connexion RapidAPI"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper.cheap_api_scraper import CheapAPIScraper
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def test_rapidapi(username: str = "elonmusk"):
    """Tester la connexion RapidAPI"""
    try:
        logger.info("🔍 Test de la connexion RapidAPI...")
        
        scraper = CheapAPIScraper()
        
        if not scraper.rapidapi_key:
            logger.error("❌ RAPIDAPI_KEY non trouvée dans .env")
            return
        
        logger.info(f"✅ Clé RapidAPI trouvée : {scraper.rapidapi_key[:20]}...")
        logger.info(f"📱 Test de récupération des tweets de @{username}")
        
        async with scraper:
            tweets = await scraper.fetch_via_rapidapi_free(username, limit=5)
        
        if tweets:
            logger.info(f"\n✅ Succès ! {len(tweets)} tweets récupérés :\n")
            
            for i, tweet in enumerate(tweets[:3], 1):
                logger.info(f"Tweet {i}:")
                logger.info(f"  📝 Texte: {tweet['text'][:100]}...")
                logger.info(f"  📅 Date: {tweet['created_at']}")
                logger.info(f"  ❤️  Likes: {tweet['likes']}")
                logger.info("")
            
            logger.info("🎉 RapidAPI fonctionne parfaitement !")
            logger.info("Vous pouvez maintenant lancer le bot : python run_bot_cheap.py")
        else:
            logger.warning("⚠️  Aucun tweet récupéré. Vérifiez :")
            logger.warning("1. Que vous êtes abonné à une API Twitter sur RapidAPI")
            logger.warning("2. Que l'API choisie est active et fonctionne")
            logger.warning("3. Que le username existe")
            
    except Exception as e:
        logger.error(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "elonmusk"
    asyncio.run(test_rapidapi(username))