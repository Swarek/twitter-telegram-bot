import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Telegram
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    telegram_channel_id: str = Field(..., env="TELEGRAM_CHANNEL_ID")
    
    # Twitter Scraping
    twitter_username_1: Optional[str] = Field(None, env="TWITTER_USERNAME_1")
    twitter_password_1: Optional[str] = Field(None, env="TWITTER_PASSWORD_1")
    twitter_email_1: Optional[str] = Field(None, env="TWITTER_EMAIL_1")
    
    twitter_username_2: Optional[str] = Field(None, env="TWITTER_USERNAME_2")
    twitter_password_2: Optional[str] = Field(None, env="TWITTER_PASSWORD_2")
    twitter_email_2: Optional[str] = Field(None, env="TWITTER_EMAIL_2")
    
    # ScrapFly (optionnel)
    scrapfly_api_key: Optional[str] = Field(None, env="SCRAPFLY_API_KEY")
    
    # Database
    database_url: str = Field("postgresql://localhost/twitter_telegram", env="DATABASE_URL")
    
    # Redis
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")
    
    # Application
    environment: str = Field("development", env="ENVIRONMENT")
    log_level: str = Field("info", env="LOG_LEVEL")
    poll_interval: int = Field(300, env="POLL_INTERVAL")  # secondes
    max_tweet_age: int = Field(3600, env="MAX_TWEET_AGE")  # secondes
    workers: int = Field(1, env="WORKERS")
    
    # Features
    enable_media: bool = Field(True, env="ENABLE_MEDIA")
    enable_threads: bool = Field(True, env="ENABLE_THREADS")
    enable_metrics: bool = Field(True, env="ENABLE_METRICS")
    enable_filters: bool = Field(True, env="ENABLE_FILTERS")
    
    # Monitoring
    healthcheck_url: Optional[str] = Field(None, env="HEALTHCHECK_URL")
    metrics_port: int = Field(8000, env="METRICS_PORT")
    
    # APIs tierces économiques
    rapidapi_key: Optional[str] = Field(None, env="RAPIDAPI_KEY")
    twitterapi_io_key: Optional[str] = Field(None, env="TWITTERAPI_IO_KEY")
    use_cheap_apis: bool = Field(True, env="USE_CHEAP_APIS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_twitter_accounts(self) -> List[tuple]:
        """Retourne la liste des comptes Twitter configurés"""
        accounts = []
        
        if all([self.twitter_username_1, self.twitter_password_1, self.twitter_email_1]):
            accounts.append((
                self.twitter_username_1,
                self.twitter_password_1,
                self.twitter_email_1,
                self.twitter_email_1  # email password (même que email pour l'instant)
            ))
            
        if all([self.twitter_username_2, self.twitter_password_2, self.twitter_email_2]):
            accounts.append((
                self.twitter_username_2,
                self.twitter_password_2,
                self.twitter_email_2,
                self.twitter_email_2
            ))
            
        return accounts

# Instance globale
settings = Settings()