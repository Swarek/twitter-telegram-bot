"""Scraper Twitter simplifié pour tester sans authentification"""
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
import json
try:
    from ..utils.logger import get_logger
except ImportError:
    from utils.logger import get_logger

logger = get_logger(__name__)

class SimpleTwitterScraper:
    """Scraper basique qui fonctionne sans authentification"""
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_demo_tweets(self, username: str) -> List[Dict[str, Any]]:
        """Récupérer des tweets de démonstration pour tester"""
        # Pour la démo, on retourne des tweets fictifs
        demo_tweets = [
            {
                'id': '1234567890',
                'text': f'🎯 Premier tweet de test de @{username}!\n\nCeci est un message de démonstration pour vérifier que le bot fonctionne correctement.\n\n#test #bot',
                'created_at': datetime.now(),
                'author': username,
                'author_name': username.title(),
                'url': f'https://twitter.com/{username}/status/1234567890',
                'media': [],
                'is_retweet': False,
                'is_quote': False,
                'reply_to': None,
                'likes': 42,
                'retweets': 10,
                'replies': 5
            },
            {
                'id': '1234567891',
                'text': f'🚀 Deuxième tweet avec des médias!\n\nVoici un exemple avec une image attachée.\n\n#demo #twitter',
                'created_at': datetime.now(),
                'author': username,
                'author_name': username.title(),
                'url': f'https://twitter.com/{username}/status/1234567891',
                'media': [
                    {
                        'type': 'photo',
                        'url': 'https://pbs.twimg.com/profile_images/1683325380441128960/yRsRRjGO_400x400.jpg'
                    }
                ],
                'is_retweet': False,
                'is_quote': False,
                'reply_to': None,
                'likes': 123,
                'retweets': 45,
                'replies': 12
            }
        ]
        
        logger.info(f"Retour de {len(demo_tweets)} tweets de démonstration pour @{username}")
        return demo_tweets
    
    async def fetch_tweets(self, username: str, since_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Interface compatible avec le scraper principal"""
        return await self.get_demo_tweets(username)