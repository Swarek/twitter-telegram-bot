import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime
from telegram import Bot, InputMediaPhoto, InputMediaVideo, InputMediaAnimation
from telegram.error import TelegramError, RetryAfter
from telegram.constants import MessageLimit
try:
    from ..utils.logger import get_logger
    from ..config import settings
except ImportError:
    from utils.logger import get_logger
    from config import settings

logger = get_logger(__name__)

class TelegramPublisher:
    def __init__(self, bot_token: str):
        self.bot = Bot(token=bot_token)
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def publish_tweet(self, tweet: Dict[str, Any], channel_id: str) -> Optional[int]:
        """Publier un tweet dans un canal Telegram"""
        try:
            # Formater le texte du tweet
            text = self._format_tweet_text(tweet)
            
            # Si pas de médias ou médias désactivés
            if not tweet.get('media') or not settings.enable_media:
                message = await self.bot.send_message(
                    chat_id=channel_id,
                    text=text,
                    parse_mode='HTML',
                    disable_web_page_preview=False
                )
                return message.message_id
            
            # Gérer les médias
            media_items = tweet['media']
            
            if len(media_items) == 1:
                # Un seul média
                return await self._send_single_media(channel_id, media_items[0], text)
            else:
                # Plusieurs médias (media group)
                return await self._send_media_group(channel_id, media_items, text)
                
        except RetryAfter as e:
            logger.warning(f"Rate limit Telegram, attente de {e.retry_after}s")
            await asyncio.sleep(e.retry_after)
            return await self.publish_tweet(tweet, channel_id)  # Retry
            
        except TelegramError as e:
            logger.error(f"Erreur Telegram: {e}")
            return None
            
        except Exception as e:
            logger.error(f"Erreur publication tweet: {e}")
            return None
    
    def _format_tweet_text(self, tweet: Dict[str, Any]) -> str:
        """Formater le texte du tweet pour Telegram"""
        # Échapper les caractères HTML
        text = tweet['text']
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        
        # Convertir les mentions Twitter en liens
        import re
        text = re.sub(
            r'@(\w+)',
            r'<a href="https://twitter.com/\1">@\1</a>',
            text
        )
        
        # Convertir les hashtags en liens
        text = re.sub(
            r'#(\w+)',
            r'<a href="https://twitter.com/hashtag/\1">#\1</a>',
            text
        )
        
        # Ajouter les métadonnées
        formatted = f"""🐦 <b>{tweet['author_name']}</b> (@{tweet['author']})

{text}"""
        
        # Ajouter les statistiques si disponibles
        if any([tweet.get('likes'), tweet.get('retweets'), tweet.get('replies')]):
            stats = []
            if tweet.get('likes'):
                stats.append(f"❤️ {tweet['likes']}")
            if tweet.get('retweets'):
                stats.append(f"🔄 {tweet['retweets']}")
            if tweet.get('replies'):
                stats.append(f"💬 {tweet['replies']}")
            
            formatted += f"\n\n{' • '.join(stats)}"
        
        # Ajouter la date et le lien
        date_str = tweet['created_at'].strftime('%d/%m/%Y %H:%M')
        formatted += f"""

📅 {date_str}
🔗 <a href="{tweet['url']}">Tweet original</a>"""
        
        # Tronquer si trop long
        if len(formatted) > MessageLimit.CAPTION_LENGTH:
            formatted = formatted[:MessageLimit.CAPTION_LENGTH - 3] + "..."
        
        return formatted
    
    async def _send_single_media(self, channel_id: str, media: Dict[str, str], caption: str) -> Optional[int]:
        """Envoyer un seul média"""
        media_type = media['type']
        media_url = media['url']
        
        try:
            if media_type == 'photo':
                message = await self.bot.send_photo(
                    chat_id=channel_id,
                    photo=media_url,
                    caption=caption,
                    parse_mode='HTML'
                )
            elif media_type == 'video':
                message = await self.bot.send_video(
                    chat_id=channel_id,
                    video=media_url,
                    caption=caption,
                    parse_mode='HTML'
                )
            elif media_type == 'gif':
                message = await self.bot.send_animation(
                    chat_id=channel_id,
                    animation=media_url,
                    caption=caption,
                    parse_mode='HTML'
                )
            else:
                logger.warning(f"Type de média non supporté: {media_type}")
                return None
                
            return message.message_id
            
        except Exception as e:
            logger.error(f"Erreur envoi média {media_type}: {e}")
            # Fallback: envoyer juste le texte
            message = await self.bot.send_message(
                chat_id=channel_id,
                text=caption,
                parse_mode='HTML'
            )
            return message.message_id
    
    async def _send_media_group(self, channel_id: str, media_items: List[Dict[str, str]], caption: str) -> Optional[int]:
        """Envoyer un groupe de médias"""
        media_group = []
        
        for i, media in enumerate(media_items[:10]):  # Telegram limite à 10 médias
            media_type = media['type']
            media_url = media['url']
            
            # Ajouter la caption seulement au premier média
            media_caption = caption if i == 0 else None
            
            if media_type == 'photo':
                media_group.append(InputMediaPhoto(
                    media=media_url,
                    caption=media_caption,
                    parse_mode='HTML' if media_caption else None
                ))
            elif media_type == 'video':
                media_group.append(InputMediaVideo(
                    media=media_url,
                    caption=media_caption,
                    parse_mode='HTML' if media_caption else None
                ))
            elif media_type == 'gif':
                media_group.append(InputMediaAnimation(
                    media=media_url,
                    caption=media_caption,
                    parse_mode='HTML' if media_caption else None
                ))
        
        if not media_group:
            return None
        
        try:
            messages = await self.bot.send_media_group(
                chat_id=channel_id,
                media=media_group
            )
            return messages[0].message_id if messages else None
            
        except Exception as e:
            logger.error(f"Erreur envoi media group: {e}")
            # Fallback: envoyer juste le texte
            message = await self.bot.send_message(
                chat_id=channel_id,
                text=caption,
                parse_mode='HTML'
            )
            return message.message_id
    
    async def publish_thread(self, thread_tweets: List[Dict[str, Any]], channel_id: str) -> List[int]:
        """Publier un thread Twitter complet"""
        message_ids = []
        
        if not settings.enable_threads:
            # Si threads désactivés, publier seulement le premier tweet
            if thread_tweets:
                msg_id = await self.publish_tweet(thread_tweets[0], channel_id)
                if msg_id:
                    message_ids.append(msg_id)
            return message_ids
        
        # Créer un message consolidé pour le thread
        thread_text = "🧵 <b>Thread</b>\n\n"
        
        for i, tweet in enumerate(thread_tweets, 1):
            tweet_text = tweet['text']
            thread_text += f"{i}. {tweet_text}\n\n"
        
        # Ajouter les infos du premier tweet
        first_tweet = thread_tweets[0]
        thread_text += f"""
📅 {first_tweet['created_at'].strftime('%d/%m/%Y %H:%M')}
🔗 <a href="{first_tweet['url']}">Thread original</a>"""
        
        # Envoyer le thread consolidé
        try:
            message = await self.bot.send_message(
                chat_id=channel_id,
                text=thread_text,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
            message_ids.append(message.message_id)
        except Exception as e:
            logger.error(f"Erreur publication thread: {e}")
        
        return message_ids
    
    async def delete_message(self, channel_id: str, message_id: int):
        """Supprimer un message (utile pour les tests)"""
        try:
            await self.bot.delete_message(chat_id=channel_id, message_id=message_id)
        except Exception as e:
            logger.error(f"Erreur suppression message {message_id}: {e}")
    
    async def test_connection(self) -> bool:
        """Tester la connexion au bot Telegram"""
        try:
            me = await self.bot.get_me()
            logger.info(f"Bot Telegram connecté: @{me.username}")
            return True
        except Exception as e:
            logger.error(f"Erreur connexion bot Telegram: {e}")
            return False