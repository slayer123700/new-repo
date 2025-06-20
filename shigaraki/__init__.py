from pyrogram import Client 
from config import config
import uvloop
from cachetools import TTLCache
import logging
from telethon import TelegramClient
from telegram.ext import ApplicationBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import time 
from datetime import datetime
import pytz

start_time = time.time() 
ist = pytz.timezone("Asia/Kolkata")
start_time_str = datetime.now(ist).strftime("%d-%b-%Y %I:%M:%S %p")


scheduler = AsyncIOScheduler()

open("log.txt", "w").close()

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - shigaraki - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        logging.FileHandler("log.txt"),
        logging.StreamHandler(),
    ],
)


logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("telethon").setLevel(logging.ERROR)
logging.getLogger("telegram").setLevel(logging.ERROR)


log = logging.getLogger(__name__)

uvloop.install()

class App(Client):
    def __init__(self):
        super().__init__(
            name=config.BOT_NAME,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            workers=config.WORKERS,
            max_concurrent_transmissions=config.MAX_CONCURRENT_TRANSMISSIONS,
            max_message_cache_size=config.MAX_MESSAGE_CACHE_SIZE
)

app = App()

ptb = ApplicationBuilder().token(config.BOT_TOKEN).build()

telebot = TelegramClient(
    f"{config.BOT_NAME}_LOL",
    config.API_ID,
    config.API_HASH,
    timeout=30,
    connection_retries=5
)



admin_cache = TTLCache(maxsize=1000000, ttl=300)
admin_cache_ptb = TTLCache(maxsize=100000 , ttl=300)
admin_cache_reload = {}
BACKUP_FILE_JSON = "last_backup.json"  






#Handler Groups
WATCHER_GROUP = 17
COMMON_CHAT_WATCHER_GROUP = 100
GLOBAL_ACTION_WATCHER_GROUP = 1
LOCK_GROUP = 2 #ptb
ANTI_FLOOD_GROUP = 3 #ptb
BLACKLIST_GROUP = 4
IMPOSTER_GROUP = 5
FILTERS_GROUP = 6
CHATBOT_GROUP = 7
ANTICHANNEL_GROUP = 8
AFK_RETURN_GROUP = 9
AFK_REPLY_GROUP = 10
LOG_GROUP = 11
CHAT_MEMBER_LOG_GROUP = 12
SERVICE_CLEANER_GROUP = 13
KARMA_NEGATIVE_GROUP = 14
KARMA_POSITIVE_GROUP = 15
JOIN_UPDATE_GROUP = 16