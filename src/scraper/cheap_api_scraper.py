"""Scraper utilisant des APIs tierces très peu chères ou gratuites"""
import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
try:
    from ..utils.logger import get_logger
    from ..config import settings
except ImportError:
    from utils.logger import get_logger
    from config import settings

logger = get_logger(__name__)

class CheapAPIScraper:
    """Scraper utilisant des APIs tierces peu chères"""
    
    def __init__(self):
        self.session = None
        # APIs disponibles (à configurer dans .env)
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY', '')
        self.twitterapi_io_key = os.getenv('TWITTERAPI_IO_KEY', '')
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_via_rapidapi_free(self, username: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Utiliser une API gratuite sur RapidAPI
        Plusieurs APIs offrent 100-500 requêtes gratuites/mois
        """
        if not self.rapidapi_key:
            logger.warning("RAPIDAPI_KEY non configurée")
            return []
        
        # Twitter135 API - Gratuite avec limite
        url = f"https://twitter135.p.rapidapi.com/v2/UserTweets/"
        
        headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "twitter135.p.rapidapi.com"
        }
        
        params = {
            "username": username,
            "count": str(limit)
        }
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_rapidapi_tweets(data)
                else:
                    logger.error(f"Erreur RapidAPI: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Erreur fetch RapidAPI: {e}")
            return []
    
    async def fetch_via_twitterapi_io(self, username: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        TwitterAPI.io - 0.15$ pour 1000 tweets (très peu cher)
        Offre souvent un essai gratuit
        """
        if not self.twitterapi_io_key:
            logger.warning("TWITTERAPI_IO_KEY non configurée")
            return []
        
        url = f"https://api.twitter-data.io/v1/users/{username}/tweets"
        
        headers = {
            "Authorization": f"Bearer {self.twitterapi_io_key}",
            "Content-Type": "application/json"
        }
        
        params = {
            "limit": limit,
            "exclude_replies": "true"
        }
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_twitterapi_io_tweets(data)
                else:
                    logger.error(f"Erreur TwitterAPI.io: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Erreur fetch TwitterAPI.io: {e}")
            return []
    
    async def fetch_via_free_proxy(self, username: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Utiliser des proxies gratuits pour Twitter
        """
        # ProxyTwitter - Service gratuit avec limitations
        proxy_services = [
            {
                'name': 'ProxyAPI',
                'url': f'https://api.proxyscrape.com/v2/twitter/user/{username}',
                'active': False
            },
            {
                'name': 'TweetFetch',
                'url': f'https://tweetfetch.com/api/user/{username}/tweets',
                'active': False
            }
        ]
        
        for service in proxy_services:
            if not service['active']:
                continue
                
            try:
                async with self.session.get(service['url']) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Succès avec {service['name']}")
                        return self._parse_generic_tweets(data)
            except Exception as e:
                logger.debug(f"Échec {service['name']}: {e}")
                continue
        
        return []
    
    def _parse_rapidapi_tweets(self, data: Dict) -> List[Dict[str, Any]]:
        """Parser les tweets de RapidAPI"""
        tweets = []
        
        try:
            tweet_list = data.get('data', {}).get('user_result', {}).get('result', {}).get('timeline_response', {}).get('timeline', {}).get('instructions', [])
            
            for instruction in tweet_list:
                if instruction.get('type') == 'TimelineAddEntries':
                    for entry in instruction.get('entries', []):
                        tweet_data = entry.get('content', {}).get('tweet_results', {}).get('result', {})
                        if tweet_data:
                            tweets.append(self._format_tweet(tweet_data))
        except Exception as e:
            logger.error(f"Erreur parsing RapidAPI: {e}")
        
        return tweets
    
    def _parse_twitterapi_io_tweets(self, data: Dict) -> List[Dict[str, Any]]:
        """Parser les tweets de TwitterAPI.io"""
        tweets = []
        
        try:
            for tweet in data.get('data', []):
                tweets.append({
                    'id': tweet.get('id'),
                    'text': tweet.get('text'),
                    'created_at': datetime.fromisoformat(tweet.get('created_at', '').replace('Z', '+00:00')),
                    'author': tweet.get('author', {}).get('username'),
                    'author_name': tweet.get('author', {}).get('name'),
                    'url': f"https://twitter.com/{tweet.get('author', {}).get('username')}/status/{tweet.get('id')}",
                    'media': self._extract_media(tweet.get('attachments', {})),
                    'likes': tweet.get('public_metrics', {}).get('like_count', 0),
                    'retweets': tweet.get('public_metrics', {}).get('retweet_count', 0),
                    'replies': tweet.get('public_metrics', {}).get('reply_count', 0),
                    'is_retweet': False,
                    'is_quote': False,
                    'reply_to': tweet.get('in_reply_to_user_id')
                })
        except Exception as e:
            logger.error(f"Erreur parsing TwitterAPI.io: {e}")
        
        return tweets
    
    def _parse_generic_tweets(self, data: Any) -> List[Dict[str, Any]]:
        """Parser générique pour différents formats"""
        tweets = []
        
        # Adapter selon le format de l'API
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and 'text' in item:
                    tweets.append(self._format_tweet(item))
        elif isinstance(data, dict):
            if 'tweets' in data:
                return self._parse_generic_tweets(data['tweets'])
            elif 'data' in data:
                return self._parse_generic_tweets(data['data'])
        
        return tweets
    
    def _format_tweet(self, raw_tweet: Dict) -> Dict[str, Any]:
        """Formater un tweet brut en format standard"""
        return {
            'id': raw_tweet.get('id_str') or raw_tweet.get('id'),
            'text': raw_tweet.get('full_text') or raw_tweet.get('text', ''),
            'created_at': self._parse_date(raw_tweet.get('created_at')),
            'author': raw_tweet.get('user', {}).get('screen_name', 'unknown'),
            'author_name': raw_tweet.get('user', {}).get('name', 'Unknown'),
            'url': f"https://twitter.com/{raw_tweet.get('user', {}).get('screen_name')}/status/{raw_tweet.get('id_str')}",
            'media': self._extract_media(raw_tweet.get('entities', {})),
            'likes': raw_tweet.get('favorite_count', 0),
            'retweets': raw_tweet.get('retweet_count', 0),
            'replies': raw_tweet.get('reply_count', 0),
            'is_retweet': raw_tweet.get('retweeted', False),
            'is_quote': raw_tweet.get('is_quote_status', False),
            'reply_to': raw_tweet.get('in_reply_to_status_id_str')
        }
    
    def _extract_media(self, entities: Dict) -> List[Dict[str, str]]:
        """Extraire les médias"""
        media_list = []
        
        if 'media' in entities:
            for media in entities['media']:
                media_type = media.get('type', 'photo')
                media_url = media.get('media_url_https') or media.get('media_url', '')
                
                if media_type == 'video':
                    # Chercher la meilleure qualité vidéo
                    variants = media.get('video_info', {}).get('variants', [])
                    best_variant = max(
                        (v for v in variants if v.get('bitrate')),
                        key=lambda x: x.get('bitrate', 0),
                        default={}
                    )
                    if best_variant:
                        media_url = best_variant.get('url', media_url)
                
                media_list.append({
                    'type': media_type,
                    'url': media_url
                })
        
        return media_list
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parser une date Twitter"""
        if not date_str:
            return datetime.now()
        
        try:
            # Format Twitter classique
            return datetime.strptime(date_str, "%a %b %d %H:%M:%S +0000 %Y")
        except:
            try:
                # Format ISO
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                return datetime.now()
    
    async def fetch_tweets(self, username: str, since_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Méthode principale qui essaie plusieurs APIs"""
        tweets = []
        
        # Essayer les APIs dans l'ordre de préférence
        
        # 0. Twitter241 (si disponible) - PRIORITAIRE
        if self.rapidapi_key:
            logger.info(f"Tentative via Twitter241 pour @{username}")
            try:
                from .twitter241_scraper import Twitter241Scraper
                async with Twitter241Scraper() as scraper:
                    tweets = await scraper.fetch_tweets(username, since_id, limit)
                    if tweets:
                        logger.info(f"✅ Succès Twitter241: {len(tweets)} tweets")
                        return tweets
            except Exception as e:
                logger.warning(f"Twitter241 échoué: {e}")
        
        # 1. RapidAPI autres APIs (gratuit jusqu'à 100-500 requêtes/mois)
        if self.rapidapi_key:
            logger.info(f"Tentative via RapidAPI générique pour @{username}")
            tweets = await self.fetch_via_rapidapi_free(username, limit)
            if tweets:
                logger.info(f"✅ Succès RapidAPI: {len(tweets)} tweets")
                return tweets
        
        # 2. TwitterAPI.io (très peu cher, 0.15$/1000 tweets)
        if self.twitterapi_io_key:
            logger.info(f"Tentative via TwitterAPI.io pour @{username}")
            tweets = await self.fetch_via_twitterapi_io(username, limit)
            if tweets:
                logger.info(f"✅ Succès TwitterAPI.io: {len(tweets)} tweets")
                return tweets
        
        # 3. Services proxy gratuits
        logger.info(f"Tentative via proxies gratuits pour @{username}")
        tweets = await self.fetch_via_free_proxy(username, limit)
        if tweets:
            logger.info(f"✅ Succès proxy: {len(tweets)} tweets")
            return tweets
        
        logger.warning(f"Aucune API disponible pour récupérer les tweets de @{username}")
        return []