import logging
import os
from logging.handlers import RotatingFileHandler

# Create logs folder
os.makedirs("logs", exist_ok=True)

# Create rotating file handler
handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=5,
    encoding="utf-8",
)

handler.setFormatter(
    logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
)

# Create logger
logger = logging.getLogger("SalonBot")
logger.setLevel(logging.INFO)

# Prevent duplicate handlers on reload
if not logger.handlers:
    logger.addHandler(handler)

logger.propagate = False


def _clean_value(value):
    if value is None:
        return ""

    return (
        str(value)
        .replace("|", "/")
        .replace("=", ":")
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )


def log_event(event, level="INFO", **fields):
    event_name = event.upper()
    log_parts = [event_name]

    for key, value in fields.items():
        log_parts.append(f"{key.upper()}={_clean_value(value)}")

    message = " | ".join(log_parts)
    log_level = getattr(logging, level.upper(), logging.INFO)

    logger.log(log_level, message)
