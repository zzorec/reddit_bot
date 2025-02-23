import logging
import os
from logging.handlers import RotatingFileHandler

log_handler = RotatingFileHandler(
    os.path.join(os.getcwd(), "inter_bot.log"),
    maxBytes=1000000000,
    backupCount=1,
    encoding='utf-8'
)

log_handler.setFormatter(logging.Formatter("%(asctime)s || %(levelname)s || %(message)s"))

logger = logging.getLogger('inter_bot')

logger.setLevel(logging.INFO)

logger.addHandler(log_handler)

if __name__ == "__main__":
    pass
