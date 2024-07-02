import os

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
