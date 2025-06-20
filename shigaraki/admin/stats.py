import platform
import psutil
import time
from datetime import timedelta
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton , CallbackQuery
from shigaraki.database.total_user_chat_db import get_total_users_count, get_total_chats_count
from shigaraki.helper.time import format_time_delta
from shigaraki import app, start_time, start_time_str
from shigaraki.decorator.botadmin import botadmin
from config import config
import pyrogram , motor , telegram , telethon
from shigaraki.database.blacklistdb import get_blacklist_summary
from shigaraki.database.cleaner_db import count_cleaner_enabled_chats
from shigaraki.database.filtersdb import get_filter_statistics
from shigaraki.database.global_actions_db import get_total_gbanned_users , get_total_gmuted_users
from shigaraki.database.lockdb import get_lock_statistics
from shigaraki.database.log_channel_db import get_log_channel_count
from shigaraki.database.rules_db import get_rules_enabled_chats_count
from shigaraki.database.user_db import get_interacted_user_count

btn = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📚 Version", callback_data="version_stats") , InlineKeyboardButton("📁 Database" , callback_data="database_stats")],
         [InlineKeyboardButton("🗑️" , callback_data="delete")]
        ]
    )

# Inline buttons to go back to main stats
main = InlineKeyboardMarkup(
    [[InlineKeyboardButton("🔙 Back", callback_data="main_stats")],
     [InlineKeyboardButton("🗑️" , callback_data="delete")] 
    ]
)

@app.on_message(filters.command("stats", config.COMMAND_PREFIXES))
@botadmin
async def stats(client: Client, message: Message):
   
    # Get system information
    node_name = platform.node()
    system = platform.system()
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    memory_percentage = memory.percent

    # Calculate uptime
    uptime_seconds = time.time() - start_time
    uptime_delta = timedelta(seconds=uptime_seconds)
    human_readable_uptime = format_time_delta(uptime_delta)

    # Main Stats Message
    main_stats_message = (
        f"**➣ System Details:**\n"
        f"**🌐 Node Name:** {node_name}\n"
        f"**🖥️ OS:** {system}\n"
        f"**📈 CPU Usage:** {cpu_usage}%\n"
        f"**[💾]({config.STATS_IMG_URL}) Memory Usage:** {memory_percentage}%\n\n"
        f"**➣ Time Details:**\n"
        f"**⏱️ Uptime:** {human_readable_uptime}\n"
        f"**📅 Started At:** {start_time_str}\n\n"
    )


    # Inline buttons for toggling
    buttons = btn

    # Send the main stats message
    await message.reply_text(main_stats_message, reply_markup=buttons, disable_web_page_preview=False , invert_media=True)


@app.on_callback_query(filters.regex("version_stats"))
@botadmin
async def show_version_stats(client: Client, callback_query : CallbackQuery):
    # Get library versions
    python_version = platform.python_version()
    pyrogram_version = pyrogram.__version__
    telethon_version = telethon.__version__
    telegram_version = telegram.__version__
    motor_version = motor.version

    # Version Stats Message
    version_stats_message = (
        f"**➣ Library Versions:**\n"
        f"**🐍 Python:** {python_version}\n"
        f"**🚀 Pyrogram:** {pyrogram_version}\n"
        f"**[📡]({config.STATS_IMG_URL}) Telethon:** {telethon_version}\n"
        f"**💬 Telegram:** {telegram_version}\n"
        f"**⚡ Motor:** {motor_version}\n"
    )

    # Inline buttons to go back to main stats
    buttons = main

    # Edit the message with version stats
    await callback_query.message.edit_text(version_stats_message, reply_markup=buttons, disable_web_page_preview=False, invert_media=True)


@app.on_callback_query(filters.regex("database_stats"))
@botadmin
async def show_database_stats(client: Client, callback_query : CallbackQuery):
    
    total_users = await get_total_users_count()
    total_chats = await get_total_chats_count()
    blacklist_summary = await get_blacklist_summary()
    cleaner_enabled_chats = await count_cleaner_enabled_chats()
    filter_statistics = await get_filter_statistics()
    total_gbanned_users = await get_total_gbanned_users()
    total_gmuted_users = await get_total_gmuted_users()
    lock_statistics = await get_lock_statistics()
    log_channel_count = await get_log_channel_count()
    rules_enabled_chats = await get_rules_enabled_chats_count()
    interacted_users = await get_interacted_user_count()

    # Version Stats Message
    version_stats_message = (
        f"**➣ Database Stats:**\n"
        f"**👤 Total Users:** {total_users}\n"
        f"**💬 Total Chats:** {total_chats}\n"
        f"**📝 Blacklist Stats:**\n"
        f"   - **Total Blacklisted Words:** {blacklist_summary['total_blacklisted_words']}\n"
        f"   - **Total Blacklisted Stickers:** {blacklist_summary['total_blacklisted_stickers']}\n"
        f"   - **Chats with Bl Words:** {blacklist_summary['chats_with_blacklisted_words']}\n"
        f"   - **Chats with Bl Stickers:** {blacklist_summary['chats_with_blacklisted_stickers']}\n"
        f"**🧹 Cleaner-Enabled Chats:** {cleaner_enabled_chats}\n"
        f"**[🔍]({config.STATS_IMG_URL}) Filter Stats:**\n"
        f"   - **Total Chats with Filters:** {filter_statistics['total_chats']}\n"
        f"   - **Total Filters:** {filter_statistics['total_filters']}\n"
        f"**🔐 Lock Stats:**\n"
        f"   - **Total Chats with Locks:** {lock_statistics['total_chats']}\n"
        f"   - **Total Locks:** {lock_statistics['total_locks']}\n"
        f"**📢 Log Channels Set:** {log_channel_count}\n"
        f"**📜 Rules-Enabled Chats:** {rules_enabled_chats}\n"
        f"**👥 Interacted Users:** {interacted_users}\n"
        f"**🚫 GBanned Users:** {total_gbanned_users}\n"
        f"**🔇 GMuted Users:** {total_gmuted_users}\n"
    )

    # Inline buttons to go back to main stats
    buttons = main

    # Edit the message with version stats
    await callback_query.message.edit_text(version_stats_message, reply_markup=buttons, disable_web_page_preview=False, invert_media=True)



@app.on_callback_query(filters.regex("main_stats"))
@botadmin
async def show_main_stats(client: Client, callback_query : CallbackQuery):
    # Get system information
    node_name = platform.node()
    system = platform.system()
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    memory_percentage = memory.percent

    # Calculate uptime
    uptime_seconds = time.time() - start_time
    uptime_delta = timedelta(seconds=uptime_seconds)
    human_readable_uptime = format_time_delta(uptime_delta)

    # Main Stats Message
    main_stats_message = (
        f"**➣ System Details:**\n"
        f"**🌐 Node Name:** {node_name}\n"
        f"**🖥️ OS:** {system}\n"
        f"**📈 CPU Usage:** {cpu_usage}%\n"
        f"**[💾]({config.STATS_IMG_URL}) Memory Usage:** {memory_percentage}%\n\n"
        f"**➣ Time Details:**\n"
        f"**⏱️ Uptime:** {human_readable_uptime}\n"
        f"**📅 Started At:** {start_time_str}\n\n"
    )

    # Inline buttons for toggling
    buttons = btn

    # Edit the message with main stats
    await callback_query.message.edit_text(main_stats_message, reply_markup=buttons, disable_web_page_preview=False , invert_media=True)