"""Scraper utilisant les instances Nitter (gratuit et sans authentification)"""
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from bs4 import BeautifulSoup
import random
try:
    from ..utils.logger import get_logger
    from ..config import settings
except ImportError:
    from utils.logger import get_logger
    from config import settings

logger = get_logger(__name__)

class NitterScraper:
    """Scraper utilisant les instances publiques de Nitter"""
    
    # Instances Nitter actives (à mettre à jour régulièrement)
    NITTER_INSTANCES = [
        "nitter.privacydev.net",
        "nitter.poast.org",
        "nitter.1d4.us",
        "nitter.kavin.rocks",
        "nitter.unixfox.eu",
    ]
    
    def __init__(self):
        self.session = None
        self.current_instance = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _select_instance(self) -> str:
        """Sélectionner une instance Nitter aléatoire"""
        return random.choice(self.NITTER_INSTANCES)
    
    async def _fetch_page(self, url: str) -> Optional[str]:
        """Récupérer le contenu HTML d'une page"""
        try:
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"Erreur HTTP {response.status} pour {url}")
                    return None
        except Exception as e:
            logger.error(f"Erreur fetch {url}: {e}")
            return None
    
    def _parse_tweet_card(self, tweet_element) -> Optional[Dict[str, Any]]:
        """Parser un élément tweet HTML de Nitter"""
        try:
            # ID du tweet
            tweet_link = tweet_element.find('a', class_='tweet-link')
            if not tweet_link:
                return None
            
            tweet_url = tweet_link.get('href', '')
            tweet_id_match = re.search(r'/status/(\d+)', tweet_url)
            if not tweet_id_match:
                return None
            
            tweet_id = tweet_id_match.group(1)
            
            # Contenu du tweet
            content_div = tweet_element.find('div', class_='tweet-content')
            if not content_div:
                return None
            
            text = content_div.get_text(strip=True)
            
            # Date
            date_elem = tweet_element.find('span', class_='tweet-date')
            date_str = date_elem.get('title', '') if date_elem else ''
            
            # Stats
            stats_container = tweet_element.find('div', class_='tweet-stats')
            likes = 0
            retweets = 0
            replies = 0
            
            if stats_container:
                # Extraire les stats
                stat_spans = stats_container.find_all('span', class_='tweet-stat')
                for stat in stat_spans:
                    stat_text = stat.get_text(strip=True)
                    if '❤' in stat_text or 'likes' in stat_text:
                        likes = self._extract_number(stat_text)
                    elif '🔁' in stat_text or 'retweets' in stat_text:
                        retweets = self._extract_number(stat_text)
                    elif '💬' in stat_text or 'replies' in stat_text:
                        replies = self._extract_number(stat_text)
            
            # Médias
            media = []
            
            # Images
            images = tweet_element.find_all('img', class_='tweet-media')
            for img in images:
                src = img.get('src', '')
                if src:
                    # Convertir l'URL Nitter en URL Twitter
                    if '/pic/' in src:
                        # Extraire l'ID de l'image
                        media_id = src.split('/pic/')[-1].split('?')[0]
                        twitter_url = f"https://pbs.twimg.com/media/{media_id}"
                        media.append({
                            'type': 'photo',
                            'url': twitter_url
                        })
            
            # Vidéos
            video_elem = tweet_element.find('video')
            if video_elem:
                video_src = video_elem.find('source')
                if video_src:
                    media.append({
                        'type': 'video',
                        'url': video_src.get('src', '')
                    })
            
            return {
                'id': tweet_id,
                'text': text,
                'created_at': self._parse_date(date_str),
                'url': f"https://twitter.com/{tweet_element.get('data-username', 'user')}/status/{tweet_id}",
                'media': media,
                'likes': likes,
                'retweets': retweets,
                'replies': replies,
                'is_retweet': 'RT @' in text,
                'is_quote': False,  # Plus difficile à détecter
                'reply_to': None
            }
            
        except Exception as e:
            logger.error(f"Erreur parsing tweet: {e}")
            return None
    
    def _extract_number(self, text: str) -> int:
        """Extraire un nombre d'une chaîne"""
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        return 0
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parser une date Nitter"""
        try:
            # Format typique: "Dec 31, 2023 · 10:30 PM UTC"
            date_str = date_str.split('·')[0].strip()
            return datetime.strptime(date_str, "%b %d, %Y")
        except:
            return datetime.now()
    
    async def fetch_tweets(self, username: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Récupérer les tweets d'un utilisateur via Nitter"""
        tweets = []
        
        # Essayer plusieurs instances si nécessaire
        for _ in range(3):
            instance = self._select_instance()
            url = f"https://{instance}/{username}"
            
            logger.info(f"Scraping {username} via {instance}")
            
            html = await self._fetch_page(url)
            if not html:
                logger.warning(f"Échec avec {instance}, essai suivant...")
                continue
            
            # Parser le HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Vérifier si le profil existe
            error_panel = soup.find('div', class_='error-panel')
            if error_panel:
                logger.error(f"Profil @{username} non trouvé ou erreur Nitter")
                continue
            
            # Trouver tous les tweets
            timeline = soup.find('div', class_='timeline')
            if not timeline:
                logger.warning("Timeline non trouvée")
                continue
            
            tweet_elements = timeline.find_all('div', class_='timeline-item')
            
            for tweet_elem in tweet_elements[:limit]:
                tweet_data = self._parse_tweet_card(tweet_elem)
                if tweet_data:
                    tweet_data['author'] = username
                    tweet_data['author_name'] = username.title()
                    tweets.append(tweet_data)
            
            if tweets:
                logger.info(f"Récupéré {len(tweets)} tweets pour @{username}")
                break
            
        return tweets
    
    async def test_instances(self) -> Dict[str, bool]:
        """Tester quelles instances Nitter sont actives"""
        results = {}
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for instance in self.NITTER_INSTANCES:
                try:
                    url = f"https://{instance}/Twitter"
                    async with session.get(url, timeout=5) as response:
                        results[instance] = response.status == 200
                except:
                    results[instance] = False
                    
        return results