"""Scraper utilisant les flux RSS alternatifs pour Twitter"""
import asyncio
import aiohttp
import feedparser
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
try:
    from ..utils.logger import get_logger
    from ..config import settings
except ImportError:
    from utils.logger import get_logger
    from config import settings

logger = get_logger(__name__)

class RSSTwitterScraper:
    """Scraper utilisant des services RSS pour Twitter"""
    
    # Services RSS pour Twitter
    RSS_SERVICES = [
        {
            'name': 'RSSHub',
            'url': 'https://rsshub.app/twitter/user/{username}',
            'active': True
        },
        {
            'name': 'Nitter RSS',
            'url': 'https://nitter.net/{username}/rss',
            'active': False  # Actuellement down
        },
        {
            'name': 'TwitRSS',
            'url': 'https://twitrss.me/twitter_user_to_rss/?user={username}',
            'active': False
        }
    ]
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; TwitterBot/1.0)'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _fetch_rss(self, url: str) -> Optional[str]:
        """Récupérer le flux RSS"""
        try:
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"Erreur HTTP {response.status} pour {url}")
                    return None
        except Exception as e:
            logger.error(f"Erreur fetch RSS {url}: {e}")
            return None
    
    def _parse_rss_entry(self, entry, username: str) -> Dict[str, Any]:
        """Parser une entrée RSS en format tweet"""
        # Extraire l'ID du tweet depuis le lien
        tweet_id = None
        if hasattr(entry, 'link'):
            match = re.search(r'/status/(\d+)', entry.link)
            if match:
                tweet_id = match.group(1)
        
        if not tweet_id and hasattr(entry, 'id'):
            # Certains flux utilisent l'ID directement
            tweet_id = entry.id.split('/')[-1]
        
        # Texte du tweet
        text = ""
        if hasattr(entry, 'summary'):
            text = entry.summary
        elif hasattr(entry, 'description'):
            text = entry.description
        elif hasattr(entry, 'title'):
            text = entry.title
        
        # Nettoyer le HTML
        text = re.sub(r'<[^>]+>', '', text)
        text = text.strip()
        
        # Date
        published_date = datetime.now()
        if hasattr(entry, 'published_parsed'):
            published_date = datetime(*entry.published_parsed[:6])
        
        # Extraire les médias si présents
        media = []
        if hasattr(entry, 'links'):
            for link in entry.links:
                if link.get('type', '').startswith('image/'):
                    media.append({
                        'type': 'photo',
                        'url': link.get('href', '')
                    })
        
        return {
            'id': tweet_id or f"rss_{hash(text)}",
            'text': text,
            'created_at': published_date,
            'author': username,
            'author_name': username.title(),
            'url': entry.link if hasattr(entry, 'link') else f"https://twitter.com/{username}",
            'media': media,
            'is_retweet': text.startswith('RT @'),
            'is_quote': False,
            'reply_to': None,
            'likes': 0,
            'retweets': 0,
            'replies': 0
        }
    
    async def fetch_tweets(self, username: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Récupérer les tweets via RSS"""
        tweets = []
        
        for service in self.RSS_SERVICES:
            if not service['active']:
                continue
                
            url = service['url'].format(username=username)
            logger.info(f"Tentative RSS via {service['name']} pour @{username}")
            
            rss_content = await self._fetch_rss(url)
            if not rss_content:
                continue
            
            try:
                # Parser le flux RSS
                feed = feedparser.parse(rss_content)
                
                if not feed.entries:
                    logger.warning(f"Aucune entrée dans le flux RSS de {service['name']}")
                    continue
                
                # Convertir les entrées en tweets
                for entry in feed.entries[:limit]:
                    tweet = self._parse_rss_entry(entry, username)
                    tweets.append(tweet)
                
                logger.info(f"Récupéré {len(tweets)} tweets via {service['name']}")
                break
                
            except Exception as e:
                logger.error(f"Erreur parsing RSS {service['name']}: {e}")
                continue
        
        return tweets


class HybridScraper:
    """Scraper hybride qui essaie plusieurs méthodes"""
    
    def __init__(self):
        self.rss_scraper = RSSTwitterScraper()
        self.last_method = None
    
    async def fetch_tweets(self, username: str, since_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Récupérer les tweets en essayant plusieurs méthodes"""
        
        # Méthode 1: RSS
        logger.info(f"Tentative de récupération via RSS pour @{username}")
        async with self.rss_scraper as scraper:
            tweets = await scraper.fetch_tweets(username, limit)
        
        if tweets:
            self.last_method = "RSS"
            logger.info(f"✅ Succès avec RSS: {len(tweets)} tweets")
            
            # Filtrer par since_id si fourni
            if since_id:
                tweets = [t for t in tweets if t['id'] != since_id]
            
            return tweets
        
        # Méthode 2: Fallback sur des données de démo
        logger.warning("Aucune méthode de scraping n'a fonctionné, utilisation de données de démo")
        self.last_method = "DEMO"
        
        return [
            {
                'id': f'demo_{username}_1',
                'text': f'🤖 Tweet de démo pour @{username}\n\nLe scraping Twitter est temporairement indisponible.',
                'created_at': datetime.now(),
                'author': username,
                'author_name': username.title(),
                'url': f'https://twitter.com/{username}',
                'media': [],
                'is_retweet': False,
                'is_quote': False,
                'reply_to': None,
                'likes': 0,
                'retweets': 0,
                'replies': 0
            }
        ]