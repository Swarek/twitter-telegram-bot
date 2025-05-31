#!/usr/bin/env python3
"""Script pour tester le scraping via Nitter"""
import asyncio
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper.nitter_scraper import NitterScraper
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def test_nitter_instances():
    """Tester quelles instances Nitter sont actives"""
    logger.info("Test des instances Nitter...")
    
    scraper = NitterScraper()
    results = await scraper.test_instances()
    
    logger.info("\nRésultats des tests:")
    for instance, is_active in results.items():
        status = "✅ Active" if is_active else "❌ Inactive"
        logger.info(f"  {instance}: {status}")
    
    active_count = sum(1 for active in results.values() if active)
    logger.info(f"\nTotal: {active_count}/{len(results)} instances actives")

async def test_scraping(username: str, limit: int = 5):
    """Tester le scraping d'un compte Twitter via Nitter"""
    try:
        username = username.lstrip('@')
        logger.info(f"Test du scraping pour @{username} via Nitter")
        
        async with NitterScraper() as scraper:
            # Récupérer les tweets
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
        logger.error(f"Erreur test Nitter: {e}")
        import traceback
        traceback.print_exc()

async def main():
    parser = argparse.ArgumentParser(description="Tester le scraping Nitter")
    parser.add_argument(
        "action",
        choices=["test-instances", "scrape"],
        help="Action à effectuer"
    )
    parser.add_argument(
        "--username", "-u",
        help="Username Twitter pour le scraping"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=5,
        help="Nombre de tweets à récupérer (défaut: 5)"
    )
    
    args = parser.parse_args()
    
    if args.action == "test-instances":
        await test_nitter_instances()
    elif args.action == "scrape":
        if not args.username:
            logger.error("Username requis pour le scraping")
            sys.exit(1)
        await test_scraping(args.username, args.limit)

if __name__ == "__main__":
    asyncio.run(main())