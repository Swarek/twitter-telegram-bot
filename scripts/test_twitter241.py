#!/usr/bin/env python3
"""Script pour tester Twitter241 API"""
import asyncio
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper.twitter241_scraper import Twitter241Scraper
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def test_twitter241(username: str = "MrBeast"):
    """Tester Twitter241 API"""
    try:
        logger.info("🔍 Test de Twitter241 API...")
        
        scraper = Twitter241Scraper()
        
        if not scraper.rapidapi_key:
            logger.error("❌ RAPIDAPI_KEY non trouvée dans .env")
            return
        
        logger.info(f"✅ Clé RapidAPI : {scraper.rapidapi_key[:20]}...")
        
        async with scraper:
            # Test 1: Récupérer les infos utilisateur
            logger.info(f"\n📱 Test 1: Infos de @{username}")
            user_info = await scraper.get_user_info(username)
            
            if user_info:
                logger.info("✅ Infos utilisateur récupérées!")
                # Sauvegarder pour analyse
                with open('debug_user_info.json', 'w') as f:
                    json.dump(user_info, f, indent=2, default=str)
                logger.info("💾 Données sauvegardées dans debug_user_info.json")
                
                # Extraire quelques infos
                user_data = user_info.get('result', {}).get('data', {}).get('user', {}).get('result', {})
                if user_data:
                    legacy = user_data.get('legacy', {})
                    logger.info(f"Nom: {legacy.get('name')}")
                    logger.info(f"Username: {legacy.get('screen_name')}")
                    logger.info(f"Followers: {legacy.get('followers_count')}")
                    logger.info(f"Description: {legacy.get('description', '')[:100]}...")
            
            # Test 2: Récupérer les tweets
            logger.info(f"\n📝 Test 2: Tweets de @{username}")
            tweets = await scraper.get_user_tweets(username, limit=5)
            
            if tweets:
                logger.info(f"\n✅ {len(tweets)} tweets récupérés!")
                
                for i, tweet in enumerate(tweets[:3], 1):
                    logger.info(f"\nTweet {i}:")
                    logger.info(f"  📝 Texte: {tweet['text'][:100]}...")
                    logger.info(f"  📅 Date: {tweet['created_at']}")
                    logger.info(f"  ❤️  Likes: {tweet['likes']}")
                    logger.info(f"  🔄 Retweets: {tweet['retweets']}")
                    logger.info(f"  📸 Médias: {len(tweet['media'])}")
                    logger.info(f"  🔗 URL: {tweet['url']}")
                
                logger.info("\n🎉 Twitter241 fonctionne parfaitement!")
                logger.info("Le bot peut maintenant utiliser cette API.")
            else:
                logger.warning("⚠️  Aucun tweet récupéré")
                logger.info("Vérifiez le fichier debug_twitter241_response.json si créé")
                
    except Exception as e:
        logger.error(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "MrBeast"
    asyncio.run(test_twitter241(username))