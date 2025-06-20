import time
import psutil 
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton , Message
from config import config  
from shigaraki import app , start_time , start_time_str
import pyrogram
import telethon
import motor
from telegram import __version__ as ptb_version
import platform

@app.on_message(filters.command("alive" , config.COMMAND_PREFIXES))
async def alive_command(client : Client , message : Message):
    # Calculate uptime
    current_time = time.time()
    uptime_seconds = int(current_time - start_time)
    uptime_str = time.strftime("%Hh %Mm %Ss", time.gmtime(uptime_seconds))

    # System stats
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent

    # Ping
    start_ping = time.time()
    x = await message.reply_text("Pinging...")  # Temporary response to measure ping
    end_ping = time.time()
    ping = round((end_ping - start_ping) * 1000, 2)

    # Message text
    alive_message = (
        f"『 {app.me.mention} Is Alive Baby 🐾🐾 』\n\n"
        f" • Uptime:`{uptime_str}`\n"
        f" • Version: `{config.BOT_VERSION}`\n\n"
        f"[⚙️]({config.ALIVE_IMG_URL}) **System Status:\n"
        f" • CPU Usage: `{cpu_usage}%`\n"
        f" • Memory Usage: `{memory_usage}%`\n"
        f" • Ping: `{ping} ms`\n"
        f" • Started At: `{start_time_str}`\n\n"
        f"📌 Notes:\n"
        f"I’m here to help you manage your groups effectively! Use the /help command to explore my features."
    )

    # Inline buttons
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🤝 Sᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT_LINK),
            InlineKeyboardButton("⚙️ Ɪɴғᴏ", callback_data="version_info")
        ],
        [
            InlineKeyboardButton("👤 ᴏᴡɴᴇʀ", user_id=config.OWNER_ID)
        ]
    ])

    # Edit the original response
    await x.edit_text(alive_message, reply_markup=buttons , invert_media=True )

@app.on_callback_query(filters.regex("version_info"))
async def callback_query_handler(client: Client, callback_query):
    if callback_query.data == "version_info":
        pyrogram_version = pyrogram.__version__
        telethon_version = telethon.__version__
        motor_version = motor.version
        python_version = platform.python_version()

        version_info = (
            f"⚡ Bot Version: {config.BOT_VERSION}\n"
            f"📦 Pyrogram Version: {pyrogram_version}\n"
            f"📦 Telethon Version: {telethon_version}\n"
            f"📦 PTB Version: {ptb_version}\n"
            f"📦 Motor Version: {motor_version}\n"
            f"🐍 Python Version: {python_version}"
        )

        await callback_query.answer(
            version_info,
            show_alert=True
        )
