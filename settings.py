import logging.handlers
import os
import logging

from dotenv import load_dotenv


load_dotenv()


ALLOWED_USERS = os.getenv('ALLOWED_USERS')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


NOTION_TOKEN = os.getenv('NOTION_TOKEN')

NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

HEADERS = {'Authorization': f'Bearer {NOTION_TOKEN}',
           'Notion-Version': '2022-06-28'}

RETRY_GET_DATA_PERIOD = 3600

TELEGRAM_CHAT_BOT_ID = os.getenv('TELEGRAM_CHAT_BOT_ID')

PRIORITY_OF_GROUPS = (1, 1, 1, 2, 2, 3)

# Логирование
LOG_FORMAT = '%(asctime)s, %(levelname)s, %(message)s, %(name)s'
LOG_FORMATER = logging.Formatter(LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

rotating_file_handler = logging.handlers.RotatingFileHandler(
    'main.log',
    maxBytes=10000000,
    backupCount=5,
    encoding='utf-8'
)
rotating_file_handler.setFormatter(LOG_FORMATER)
logger.addHandler(rotating_file_handler)
