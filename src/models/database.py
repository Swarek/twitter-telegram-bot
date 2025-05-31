import asyncio
import asyncpg
import json
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
try:
    from ..utils.logger import get_logger
    from ..config import settings
except ImportError:
    from utils.logger import get_logger
    from config import settings

logger = get_logger(__name__)

class Database:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None
    
    async def connect(self):
        """Créer le pool de connexions"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("Pool de connexions PostgreSQL créé")
        except Exception as e:
            logger.error(f"Erreur connexion base de données: {e}")
            raise
    
    async def disconnect(self):
        """Fermer le pool de connexions"""
        if self.pool:
            await self.pool.close()
            logger.info("Pool de connexions fermé")
    
    @asynccontextmanager
    async def acquire(self):
        """Acquérir une connexion du pool"""
        async with self.pool.acquire() as connection:
            yield connection
    
    async def init_schema(self):
        """Créer les tables si elles n'existent pas"""
        async with self.acquire() as conn:
            # Table des comptes Twitter surveillés
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS twitter_accounts (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    twitter_id VARCHAR(255) UNIQUE,
                    telegram_channel_id VARCHAR(255) NOT NULL,
                    last_tweet_id VARCHAR(255),
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Table des tweets publiés
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS published_tweets (
                    id SERIAL PRIMARY KEY,
                    tweet_id VARCHAR(255) NOT NULL UNIQUE,
                    account_id INTEGER REFERENCES twitter_accounts(id) ON DELETE CASCADE,
                    telegram_message_id BIGINT,
                    telegram_channel_id VARCHAR(255),
                    published_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    tweet_data JSONB
                )
            """)
            
            # Table des erreurs
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS error_logs (
                    id SERIAL PRIMARY KEY,
                    error_type VARCHAR(100),
                    error_message TEXT,
                    error_data JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Index pour optimiser les requêtes
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_twitter_accounts_username 
                ON twitter_accounts(username)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_published_tweets_tweet_id 
                ON published_tweets(tweet_id)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_published_tweets_account_id 
                ON published_tweets(account_id)
            """)
            
            logger.info("Schéma de base de données initialisé")
    
    # Méthodes pour twitter_accounts
    
    async def add_twitter_account(self, username: str, channel_id: str, twitter_id: Optional[str] = None) -> int:
        """Ajouter un compte Twitter à surveiller"""
        async with self.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO twitter_accounts (username, telegram_channel_id, twitter_id)
                VALUES ($1, $2, $3)
                ON CONFLICT (username) 
                DO UPDATE SET 
                    telegram_channel_id = EXCLUDED.telegram_channel_id,
                    updated_at = NOW()
                RETURNING id
            """, username, channel_id, twitter_id)
            
            logger.info(f"Compte Twitter ajouté/mis à jour: {username} -> {channel_id}")
            return result['id']
    
    async def get_active_accounts(self) -> List[Dict[str, Any]]:
        """Récupérer tous les comptes actifs"""
        async with self.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM twitter_accounts
                WHERE is_active = true
                ORDER BY username
            """)
            
            return [dict(row) for row in rows]
    
    async def get_account(self, username: str) -> Optional[Dict[str, Any]]:
        """Récupérer un compte par username"""
        async with self.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM twitter_accounts
                WHERE username = $1
            """, username)
            
            return dict(row) if row else None
    
    async def update_last_tweet_id(self, account_id: int, tweet_id: str):
        """Mettre à jour le dernier tweet traité"""
        async with self.acquire() as conn:
            await conn.execute("""
                UPDATE twitter_accounts
                SET last_tweet_id = $1, updated_at = NOW()
                WHERE id = $2
            """, tweet_id, account_id)
    
    async def deactivate_account(self, username: str):
        """Désactiver un compte"""
        async with self.acquire() as conn:
            await conn.execute("""
                UPDATE twitter_accounts
                SET is_active = false, updated_at = NOW()
                WHERE username = $1
            """, username)
    
    async def remove_account(self, username: str) -> bool:
        """Supprimer un compte"""
        async with self.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM twitter_accounts
                WHERE username = $1
            """, username)
            
            return result.split()[-1] != '0'
    
    # Méthodes pour published_tweets
    
    async def is_tweet_published(self, tweet_id: str) -> bool:
        """Vérifier si un tweet a déjà été publié"""
        async with self.acquire() as conn:
            result = await conn.fetchval("""
                SELECT EXISTS(
                    SELECT 1 FROM published_tweets
                    WHERE tweet_id = $1
                )
            """, tweet_id)
            
            return result
    
    async def add_published_tweet(self, tweet_id: str, account_id: int, 
                                 telegram_message_id: int, channel_id: str,
                                 tweet_data: Dict[str, Any]):
        """Enregistrer un tweet publié"""
        async with self.acquire() as conn:
            await conn.execute("""
                INSERT INTO published_tweets 
                (tweet_id, account_id, telegram_message_id, telegram_channel_id, tweet_data)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (tweet_id) DO NOTHING
            """, tweet_id, account_id, telegram_message_id, channel_id, json.dumps(tweet_data, cls=DateTimeEncoder))
    
    async def get_published_tweets_count(self, account_id: Optional[int] = None) -> int:
        """Compter les tweets publiés"""
        async with self.acquire() as conn:
            if account_id:
                return await conn.fetchval("""
                    SELECT COUNT(*) FROM published_tweets
                    WHERE account_id = $1
                """, account_id)
            else:
                return await conn.fetchval("""
                    SELECT COUNT(*) FROM published_tweets
                """)
    
    async def cleanup_old_tweets(self, days: int = 30):
        """Nettoyer les vieux tweets"""
        async with self.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM published_tweets
                WHERE published_at < NOW() - INTERVAL '%s days'
            """, days)
            
            count = int(result.split()[-1])
            if count > 0:
                logger.info(f"Supprimé {count} vieux tweets")
    
    # Méthodes pour error_logs
    
    async def log_error(self, error_type: str, error_message: str, 
                       error_data: Optional[Dict[str, Any]] = None):
        """Enregistrer une erreur"""
        async with self.acquire() as conn:
            await conn.execute("""
                INSERT INTO error_logs (error_type, error_message, error_data)
                VALUES ($1, $2, $3)
            """, error_type, error_message, json.dumps(error_data, cls=DateTimeEncoder) if error_data else None)
    
    async def get_recent_errors(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Récupérer les erreurs récentes"""
        async with self.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM error_logs
                ORDER BY created_at DESC
                LIMIT $1
            """, limit)
            
            return [dict(row) for row in rows]
    
    async def cleanup_old_errors(self, days: int = 7):
        """Nettoyer les vieilles erreurs"""
        async with self.acquire() as conn:
            await conn.execute("""
                DELETE FROM error_logs
                WHERE created_at < NOW() - INTERVAL '%s days'
            """, days)

# Instance globale
db = Database(settings.database_url)