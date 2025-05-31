import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from twscrape import API, gather
from twscrape.logger import set_log_level
try:
    from ..utils.logger import get_logger
    from ..config import settings
except ImportError:
    from utils.logger import get_logger
    from config import settings

logger = get_logger(__name__)

# Réduire le niveau de log de twscrape
set_log_level("ERROR")

class TwitterScraper:
    def __init__(self):
        self.api = API()
        self.initialized = False
        self.rate_limit_delay = 60  # secondes
        
    async def setup_accounts(self):
        """Configurer les comptes Twitter pour twscrape"""
        if self.initialized:
            return
            
        accounts = settings.get_twitter_accounts()
        if not accounts:
            raise ValueError("Aucun compte Twitter configuré dans .env")
        
        logger.info(f"Configuration de {len(accounts)} comptes Twitter")
        
        for username, password, email, email_password in accounts:
            try:
                await self.api.pool.add_account(
                    username=username,
                    password=password,
                    email=email,
                    email_password=email_password
                )
                logger.info(f"Compte ajouté: {username}")
            except Exception as e:
                logger.error(f"Erreur ajout compte {username}: {e}")
        
        # Login sur tous les comptes
        logger.info("Connexion aux comptes Twitter...")
        await self.api.pool.login_all()
        
        # Vérifier les comptes actifs
        active_accounts = await self.api.pool.accounts_info()
        active_count = len([acc for acc in active_accounts if acc.active])
        logger.info(f"{active_count} comptes actifs sur {len(active_accounts)}")
        
        if active_count == 0:
            raise ValueError("Aucun compte Twitter actif")
            
        self.initialized = True
    
    async def get_user_id(self, username: str) -> Optional[str]:
        """Obtenir l'ID d'un utilisateur Twitter"""
        try:
            users = await gather(self.api.search_by_raw_query(f"from:{username}", limit=1))
            if users:
                # Extraire l'user_id du premier tweet
                tweet = users[0]
                return tweet.user.id
            
            # Méthode alternative: rechercher l'utilisateur
            user_search = await gather(self.api.user_by_login(username))
            if user_search:
                return user_search[0].id
                
        except Exception as e:
            logger.error(f"Erreur récupération ID pour {username}: {e}")
        
        return None
    
    async def fetch_tweets(self, username: str, since_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Récupérer les tweets d'un utilisateur"""
        tweets = []
        
        try:
            # Utiliser la méthode user_tweets_and_replies pour plus de contenu
            async for tweet in self.api.user_tweets_and_replies(username, limit=limit):
                # Filtrer les réponses aux autres
                if tweet.inReplyToUser and tweet.inReplyToUser.username != username:
                    continue
                    
                # Arrêter si on atteint un tweet déjà traité
                if since_id and str(tweet.id) == since_id:
                    break
                
                # Vérifier l'âge du tweet
                tweet_age = (datetime.now(timezone.utc) - tweet.date).total_seconds()
                if tweet_age > settings.max_tweet_age:
                    continue
                
                tweet_data = {
                    'id': str(tweet.id),
                    'text': tweet.rawContent,
                    'created_at': tweet.date,
                    'author': tweet.user.username,
                    'author_name': tweet.user.displayname,
                    'url': f"https://twitter.com/{tweet.user.username}/status/{tweet.id}",
                    'media': self._extract_media(tweet),
                    'is_retweet': bool(tweet.retweetedTweet),
                    'is_quote': bool(tweet.quotedTweet),
                    'reply_to': tweet.inReplyToTweetId,
                    'likes': tweet.likeCount,
                    'retweets': tweet.retweetCount,
                    'replies': tweet.replyCount
                }
                
                tweets.append(tweet_data)
                
        except Exception as e:
            logger.error(f"Erreur récupération tweets pour {username}: {e}")
            
            # Si rate limit, attendre
            if "rate limit" in str(e).lower():
                logger.warning(f"Rate limit atteint, attente de {self.rate_limit_delay}s")
                await asyncio.sleep(self.rate_limit_delay)
        
        logger.info(f"Récupéré {len(tweets)} tweets pour {username}")
        return tweets
    
    def _extract_media(self, tweet) -> List[Dict[str, str]]:
        """Extraire les médias d'un tweet"""
        media_list = []
        
        if not hasattr(tweet, 'media') or not tweet.media:
            return media_list
        
        for media in tweet.media:
            if hasattr(media, 'photos') and media.photos:
                # Images
                for photo in media.photos:
                    media_list.append({
                        'type': 'photo',
                        'url': photo.url
                    })
            
            if hasattr(media, 'videos') and media.videos:
                # Vidéos
                for video in media.videos:
                    # Prendre la meilleure qualité
                    variants = sorted(
                        video.variants,
                        key=lambda x: x.bitrate if x.bitrate else 0,
                        reverse=True
                    )
                    if variants:
                        media_list.append({
                            'type': 'video',
                            'url': variants[0].url
                        })
            
            if hasattr(media, 'animated') and media.animated:
                # GIFs
                media_list.append({
                    'type': 'gif',
                    'url': media.animated.videoUrl
                })
        
        return media_list
    
    async def get_thread(self, tweet_id: str, username: str) -> List[Dict[str, Any]]:
        """Récupérer un thread complet"""
        thread_tweets = []
        current_id = tweet_id
        
        while current_id:
            try:
                # Récupérer le tweet spécifique
                tweet = await self.api.tweet_by_id(current_id)
                if tweet:
                    tweet_data = {
                        'id': str(tweet.id),
                        'text': tweet.rawContent,
                        'created_at': tweet.date,
                        'author': tweet.user.username,
                        'reply_to': tweet.inReplyToTweetId
                    }
                    thread_tweets.append(tweet_data)
                    
                    # Remonter au tweet parent si c'est une réponse
                    if tweet.inReplyToTweetId and tweet.inReplyToUser.username == username:
                        current_id = tweet.inReplyToTweetId
                    else:
                        break
                else:
                    break
                    
            except Exception as e:
                logger.error(f"Erreur récupération thread {current_id}: {e}")
                break
        
        # Inverser pour avoir l'ordre chronologique
        return list(reversed(thread_tweets))