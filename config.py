 # config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
ADMIN_IDS = list(map(int, [id.strip() for id in os.getenv('ADMIN_IDS').split(',') if id.strip().isdigit()]))
BAR_CHANNEL_ID = os.getenv('BAR_CHANNEL_ID')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
