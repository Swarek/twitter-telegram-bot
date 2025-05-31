import sys
from pathlib import Path
from loguru import logger
try:
    from ..config import settings
except ImportError:
    from config import settings

# Créer le dossier de logs
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Supprimer le logger par défaut
logger.remove()

# Console logging
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level.upper(),
    colorize=True
)

# File logging
logger.add(
    "logs/bot.log",
    rotation="500 MB",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    compression="zip"
)

# Error logging
logger.add(
    "logs/errors.log",
    rotation="100 MB",
    retention="30 days",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    compression="zip"
)

def get_logger(name: str):
    """Obtenir un logger avec un nom spécifique"""
    return logger.bind(name=name)