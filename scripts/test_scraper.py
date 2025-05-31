#!/usr/bin/env python3
"""Script pour tester le scraping Twitter"""
import asyncio
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper import TwitterScraper
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def test_scraper(username: str, limit: int = 5):
    """Tester le scraping d'un compte Twitter"""
    try:
        username = username.lstrip('@')
        logger.info(f"Test du scraping pour @{username}")
        
        # Initialiser le scraper
        scraper = TwitterScraper()
        await scraper.setup_accounts()
        
        # Récupérer l'ID utilisateur
        logger.info("Récupération de l'ID utilisateur...")
        user_id = await scraper.get_user_id(username)
        if user_id:
            logger.info(f"ID utilisateur: {user_id}")
        else:
            logger.warning("ID utilisateur non trouvé")
        
        # Récupérer les tweets
        logger.info(f"Récupération des {limit} derniers tweets...")
        tweets = await scraper.fetch_tweets(username, limit=limit)
        
        if not tweets:
            logger.warning("Aucun tweet trouvé")
            return
        
        logger.info(f"\n{len(tweets)} tweets récupérés:\n")
        
        for i, tweet in enumerate(tweets, 1):
            logger.info(f"Tweet {i}:")
            logger.info(f"  ID: {tweet['id']}")
            logger.info(f"  Date: {tweet['created_at']}")
            logger.info(f"  Texte: {tweet['text'][:100]}...")
            logger.info(f"  Likes: {tweet['likes']}")
            logger.info(f"  Retweets: {tweet['retweets']}")
            logger.info(f"  Médias: {len(tweet['media'])} fichier(s)")
            logger.info(f"  URL: {tweet['url']}")
            logger.info("")
        
    except Exception as e:
        logger.error(f"Erreur test scraper: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Tester le scraping Twitter")
    parser.add_argument(
        "username",
        help="Username Twitter à tester (avec ou sans @)"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=5,
        help="Nombre de tweets à récupérer (défaut: 5)"
    )
    
    args = parser.parse_args()
    
    asyncio.run(test_scraper(args.username, args.limit))

if __name__ == "__main__":
    main()