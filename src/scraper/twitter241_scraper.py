"""Scraper utilisant Twitter241 API de RapidAPI"""
import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
import time
from datetime import datetime
import os
try:
    from ..utils.logger import get_logger
    from ..config import settings
except ImportError:
    from utils.logger import get_logger
    from config import settings

logger = get_logger(__name__)

class Twitter241Scraper:
    """Scraper utilisant Twitter241 API"""
    
    # Cache des IDs utilisateurs connus
    USER_ID_CACHE = {
        'swarek_': '2794288012',
        'elonmusk': '44196397',
        'mrbeast': '2455740283'
    }
    
    def __init__(self):
        self.session = None
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY', '')
        self.host = 'twitter241.p.rapidapi.com'
        self.base_url = f'https://{self.host}'
        self.last_request_time = 0
        self.min_delay = 2.0  # Délai minimum entre requêtes (2 secondes)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _rate_limit(self):
        """Gérer le rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_delay:
            delay = self.min_delay - time_since_last
            logger.debug(f"Rate limit: attente de {delay:.1f}s")
            await asyncio.sleep(delay)
        self.last_request_time = time.time()
    
    async def get_user_info(self, username: str) -> Optional[Dict]:
        """Récupérer les infos d'un utilisateur"""
        await self._rate_limit()
        
        url = f"{self.base_url}/user"
        headers = {
            'x-rapidapi-host': self.host,
            'x-rapidapi-key': self.rapidapi_key
        }
        params = {'username': username}
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Infos utilisateur récupérées pour @{username}")
                    
                    # Mettre en cache l'ID
                    user_data = data.get('result', {}).get('data', {}).get('user', {}).get('result', {})
                    if user_data:
                        user_id = user_data.get('rest_id')
                        if user_id:
                            self.USER_ID_CACHE[username.lower()] = user_id
                    
                    return data
                elif response.status == 429:
                    logger.warning(f"Rate limit atteint (429) - attendre avant de réessayer")
                    return None
                else:
                    logger.error(f"Erreur {response.status} pour get_user_info")
                    return None
        except Exception as e:
            logger.error(f"Exception get_user_info: {e}")
            return None
    
    async def get_user_tweets(self, username: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Récupérer les tweets d'un utilisateur"""
        # Vérifier le cache d'abord
        user_id = self.USER_ID_CACHE.get(username.lower())
        
        # Si pas dans le cache, récupérer l'ID
        if not user_id:
            user_info = await self.get_user_info(username)
            if not user_info:
                logger.error(f"Impossible de récupérer les infos de @{username}")
                return []
            
            user_id = user_info.get('result', {}).get('data', {}).get('user', {}).get('result', {}).get('rest_id')
            if not user_id:
                logger.error(f"ID utilisateur non trouvé pour @{username}")
                return []
        
        logger.info(f"ID utilisateur pour @{username}: {user_id}")
        
        # Rate limiting
        await self._rate_limit()
        
        # Récupérer les tweets
        url = f"{self.base_url}/user-tweets"
        headers = {
            'x-rapidapi-host': self.host,
            'x-rapidapi-key': self.rapidapi_key
        }
        params = {
            'user': user_id,
            'count': str(limit)
        }
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Tweets récupérés pour @{username}")
                    return self._parse_tweets(data, username)
                elif response.status == 429:
                    logger.warning(f"Rate limit atteint (429) pour les tweets")
                    return []
                else:
                    logger.error(f"Erreur {response.status} pour get_user_tweets")
                    text = await response.text()
                    logger.error(f"Réponse: {text[:200]}")
                    return []
        except Exception as e:
            logger.error(f"Exception get_user_tweets: {e}")
            return []
    
    def _parse_tweets(self, data: Dict, username: str) -> List[Dict[str, Any]]:
        """Parser les tweets de Twitter241"""
        tweets = []
        
        try:
            # Debug: voir la structure de la réponse
            logger.debug(f"Clés principales de la réponse: {list(data.keys())}")
            
            # Navigation dans la structure de l'API - Structure corrigée
            timeline = data.get('result', {}).get('timeline', {})
            instructions = timeline.get('instructions', [])
            
            logger.debug(f"Nombre d'instructions: {len(instructions)}")
            
            for instruction in instructions:
                if instruction.get('type') == 'TimelineAddEntries':
                    entries = instruction.get('entries', [])
                    
                    for entry in entries:
                        # Extraire le tweet
                        content = entry.get('content', {})
                        if content.get('entryType') == 'TimelineTimelineItem':
                            tweet_result = content.get('itemContent', {}).get('tweet_results', {}).get('result', {})
                            
                            if tweet_result and tweet_result.get('__typename') == 'Tweet':
                                tweet = self._format_tweet(tweet_result, username)
                                if tweet:
                                    tweets.append(tweet)
                        
        except Exception as e:
            logger.error(f"Erreur parsing tweets: {e}")
            # Sauvegarder pour debug
            with open('debug_twitter241_response.json', 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info("Réponse sauvegardée dans debug_twitter241_response.json")
        
        return tweets
    
    def _format_tweet(self, tweet_data: Dict, username: str) -> Optional[Dict[str, Any]]:
        """Formater un tweet Twitter241"""
        try:
            # Extraire les données du tweet
            legacy = tweet_data.get('legacy', {})
            
            # ID du tweet
            tweet_id = tweet_data.get('rest_id', '')
            
            # Texte complet
            text = legacy.get('full_text', '')
            
            # Date
            created_at = legacy.get('created_at', '')
            tweet_date = self._parse_twitter_date(created_at)
            
            # Statistiques
            likes = legacy.get('favorite_count', 0)
            retweets = legacy.get('retweet_count', 0)
            replies = legacy.get('reply_count', 0)
            
            # Médias
            media = self._extract_media(legacy.get('entities', {}))
            
            # Auteur
            user_data = tweet_data.get('core', {}).get('user_results', {}).get('result', {}).get('legacy', {})
            author_username = user_data.get('screen_name', username)
            author_name = user_data.get('name', username)
            
            return {
                'id': tweet_id,
                'text': text,
                'created_at': tweet_date,
                'author': author_username,
                'author_name': author_name,
                'url': f"https://twitter.com/{author_username}/status/{tweet_id}",
                'media': media,
                'is_retweet': legacy.get('retweeted', False),
                'is_quote': tweet_data.get('quoted_status_result') is not None,
                'reply_to': legacy.get('in_reply_to_status_id_str'),
                'likes': likes,
                'retweets': retweets,
                'replies': replies
            }
            
        except Exception as e:
            logger.error(f"Erreur formatage tweet: {e}")
            return None
    
    def _extract_media(self, entities: Dict) -> List[Dict[str, str]]:
        """Extraire les médias"""
        media_list = []
        
        if 'media' in entities:
            for media in entities['media']:
                media_type = media.get('type', 'photo')
                
                if media_type == 'photo':
                    media_list.append({
                        'type': 'photo',
                        'url': media.get('media_url_https', media.get('media_url', ''))
                    })
                elif media_type in ['video', 'animated_gif']:
                    video_info = media.get('video_info', {})
                    variants = video_info.get('variants', [])
                    
                    # Prendre la meilleure qualité
                    best_variant = max(
                        (v for v in variants if v.get('content_type') == 'video/mp4'),
                        key=lambda x: x.get('bitrate', 0),
                        default=None
                    )
                    
                    if best_variant:
                        media_list.append({
                            'type': 'video' if media_type == 'video' else 'gif',
                            'url': best_variant['url']
                        })
        
        return media_list
    
    def _parse_twitter_date(self, date_str: str) -> datetime:
        """Parser une date Twitter"""
        try:
            # Format: "Wed Oct 10 20:19:24 +0000 2018"
            return datetime.strptime(date_str, "%a %b %d %H:%M:%S +0000 %Y")
        except:
            return datetime.now()
    
    async def fetch_tweets(self, username: str, since_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Interface compatible avec les autres scrapers"""
        tweets = await self.get_user_tweets(username, limit)
        
        # Filtrer par since_id si fourni
        if since_id and tweets:
            # Garder seulement les tweets plus récents que since_id
            filtered_tweets = []
            for tweet in tweets:
                if tweet['id'] == since_id:
                    break
                filtered_tweets.append(tweet)
            tweets = filtered_tweets
        
        return tweets