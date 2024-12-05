import logging
from logging.handlers import RotatingFileHandler

from app.config import settings

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            filename=settings.LOG_FILENAME,
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT,
        ),
    ],
)

db = logging.getLogger("db")
app = logging.getLogger("app")
framework = logging.getLogger("framework")
