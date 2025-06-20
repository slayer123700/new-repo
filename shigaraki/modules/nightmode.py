from shigaraki import app as pgram , scheduler
from shigaraki.database.nightmode_db import (
    enable_nightmode,
    disable_nightmode,
    is_nightmode_enabled,
    get_all_nightmode_enabled_chats
)
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.types import Message
from shigaraki.decorator.chatadmin import chatadmin
from config import config 
from shigaraki.helper.log_helper import send_log, format_log
import pytz
import asyncio
from shigaraki.helper.user import NIGHT_MODE_PERMISSIONS , DEFAULT_PERMISSIONS
from shigaraki.decorator.save import save 
from shigaraki.decorator.errors import error

IST = pytz.timezone("Asia/Kolkata")


# Command to toggle announcement status
@pgram.on_message(filters.command("nightmode" , prefixes=config.COMMAND_PREFIXES) & filters.group)
@chatadmin
@error
@save
async def announcement_handler(client: Client, message: Message):
    chat_id = message.chat.id
        
    if await is_nightmode_enabled(chat_id):
        # If already enabled, send a button to disable
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔴 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 Nightmode", callback_data=f"disable_nightmode:{chat_id}")],
            [InlineKeyboardButton("🗑️", callback_data="delete")]]
        )
        await message.reply_text("**📢 Nightmode is 𝖾𝗇𝖺𝖻𝗅𝖾𝖽 𝗂𝗇 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**", reply_markup=button)
    else:
        # If not enabled, send a button to enable
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🟢 𝖤𝗇𝖺𝖻𝗅𝖾 Nightmode", callback_data=f"enable_nightmode:{chat_id}")],
            [InlineKeyboardButton("🗑️", callback_data="delete")]]
             
        )
        await message.reply_text("**📢 Nightmode is 𝖽𝗂𝗌𝖺𝖻𝗅𝖾𝖽 𝗂𝗇 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**", reply_markup=button)
        # Log the command usage
    log_message = await format_log(
        action="Toggle Nightmode Command Used",
        chat=message.chat.title or str(chat_id),
        admin=message.from_user.mention
    )
    await send_log(chat_id, log_message)


# Callback query handler to enable/disable nightmode
@pgram.on_callback_query(filters.regex("^(enable_nightmode|disable_nightmode):"))
@chatadmin
@error
async def toggle_announcements(client: Client, callback_query):
    action, chat_id = callback_query.data.split(":")
    chat_id = int(chat_id)
    chat = await client.get_chat(chat_id)

    if action == "enable_nightmode":
        await enable_nightmode(chat_id, chat.title, chat.username)
        await callback_query.message.edit_text("**🟢 Nightmode 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝖾𝗇𝖺𝖻𝗅𝖾𝖽 𝖿𝗈𝗋 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**")

        # Log the action
        log_message = await format_log(
            action="Nightmode Enabled",
            chat=chat.title or str(chat_id),
            admin=callback_query.from_user.mention
        )

    elif action == "disable_nightmode":
        await disable_nightmode(chat_id)
        await callback_query.message.edit_text("**🔴 Nightmode 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝖽𝗂𝗌𝖺𝖻𝗅𝖾𝖽 𝖿𝗈𝗋 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**")

        # Log the action
        log_message = await format_log(
            action="Nightmode Disabled",
            chat=chat.title or str(chat_id),
            admin=callback_query.from_user.mention
        )

    await send_log(chat_id, log_message)

# Function to enable night mode permissions
async def enable_nightmode_permissions():
    chats = await get_all_nightmode_enabled_chats()
    for chat_id in chats:
        try:
            await pgram.set_chat_permissions(chat_id, NIGHT_MODE_PERMISSIONS)
            await pgram.send_message(chat_id, "**🌙 Nightmode has been enabled.**")
            await asyncio.sleep(1)  # Prevent floodwait
        except Exception as e:
            print(f"Error enabling nightmode for chat {chat_id}: {e}")

# Function to disable night mode permissions
async def disable_nightmode_permissions():
    chats = await get_all_nightmode_enabled_chats()
    for chat_id in chats:
        try:
            await pgram.set_chat_permissions(chat_id, DEFAULT_PERMISSIONS)
            await pgram.send_message(chat_id, "**☀️ Nightmode has been disabled.**")
            await asyncio.sleep(1)  # Prevent floodwait
        except Exception as e:
            print(f"Error disabling nightmode for chat {chat_id}: {e}")

scheduler.add_job(enable_nightmode_permissions, "cron", hour=23, minute=0, timezone=IST)
scheduler.add_job(disable_nightmode_permissions, "cron", hour=7, minute=0, timezone=IST)


__module__ = "𝖭𝗂𝗀𝗁𝗍𝗆𝗈𝖽𝖾"


__help__ = """**𝖭𝗂𝗀𝗁𝗍𝗆𝗈𝖽𝖾 𝖬𝗈𝖽𝗎𝗅𝖾:**

- **𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:**

 ✧ `/𝗇𝗂𝗀𝗁𝗍𝗆𝗈𝖽𝖾` : 𝖳𝗈𝗀𝗀𝗅𝖾 𝗍𝗁𝖾 𝖭𝗂𝗀𝗁𝗍𝗆𝗈𝖽𝖾 𝗌𝖾𝗍𝗍𝗂𝗇𝗀𝗌 𝖿𝗈𝗋 𝗍𝗁𝖾 𝖼𝗁𝖺𝗍.
 
   - **𝖨𝖿 𝖭𝗂𝗀𝗁𝗍𝗆𝗈𝖽𝖾 𝗂𝗌 𝖾𝗇𝖺𝖻𝗅𝖾𝖽:**
     ✧ 𝖱𝖾𝗌𝗍𝗋𝗂𝖼𝗍𝗂𝗈𝗇𝗌 𝗐𝗂𝗅𝗅 𝖺𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖻𝖾 𝖺𝗉𝗉𝗅𝗂𝖾𝖽 𝖽𝗎𝗋𝗂𝗇𝗀 𝗇𝗂𝗀𝗁𝗍 𝗁𝗈𝗎𝗋𝗌 (𝟣𝟣:𝟢𝟢 𝖯𝖬 𝗍𝗈 𝟩:𝟢𝟢 𝖠𝖬 𝖨𝖲𝖳).
      ✧ 𝖢𝗁𝖺𝗍 𝗉𝖾𝗋𝗆𝗂𝗌𝗌𝗂𝗈𝗇𝗌 𝖺𝗋𝖾 𝖺𝖽𝗃𝗎𝗌𝗍𝖾𝖽 𝗍𝗈 𝗍𝗁𝖾 𝖽𝖾𝖿𝗂𝗇𝖾𝖽 𝖭𝗂𝗀𝗁𝗍𝗆𝗈𝖽𝖾 𝗋𝖾𝗌𝗍𝗋𝗂𝖼𝗍𝗂𝗈𝗇𝗌.
      

- **𝖭𝗂𝗀𝗁𝗍𝗆𝗈𝖽𝖾 𝖠𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝗈𝗇:**

 ✧ **𝖠𝖼𝗍𝗂𝗏𝖺𝗍𝗂𝗈𝗇:** 𝖭𝗂𝗀𝗁𝗍𝗆𝗈𝖽𝖾 𝖺𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖺𝖼𝗍𝗂𝗏𝖺𝗍𝖾𝗌 𝖺𝗍 𝟣𝟣:𝟢𝟢 𝖯𝖬 𝖨𝖲𝖳.
  ✧ **𝖣𝖾𝖺𝖼𝗍𝗂𝗏𝖺𝗍𝗂𝗈𝗇:** 𝖭𝗂𝗀𝗁𝗍𝗆𝗈𝖽𝖾 𝖺𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖽𝖾𝖺𝖼𝗍𝗂𝗏𝖺𝗍𝖾𝗌 𝖺𝗍 𝟩:𝟢𝟢 𝖠𝖬 𝖨𝖲𝖳.
 
"""
