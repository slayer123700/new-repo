from shigaraki import app as pgram , SERVICE_CLEANER_GROUP
from shigaraki.database.cleaner_db import (
    enable_cleaner,
    disable_cleaner,
    is_cleaner_enabled,
)
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.types import  Message
from shigaraki.decorator.chatadmin import chatadmin
from config import config 
from shigaraki.helper.log_helper import send_log, format_log
from shigaraki.decorator.save import save 
from shigaraki.decorator.errors import error

# Command to toggle cleaner status
@pgram.on_message(filters.command("cleaner" , prefixes=config.COMMAND_PREFIXES) & filters.group)
@chatadmin
@error
@save
async def cleaner_handler(client: Client, message: Message):
    chat_id = message.chat.id

    if await is_cleaner_enabled(chat_id):
        # If already enabled, send a button to disable
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔴 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖢𝗅𝖾𝖺𝗇𝖾𝗋", callback_data=f"disable_cleaner:{chat_id}")],
            [InlineKeyboardButton("🗑️", callback_data="delete")]]
        )
        await message.reply_text("**🛡️ 𝖢𝗅𝖾𝖺𝗇𝖾𝗋 𝖺𝗋𝖾 𝖾𝗇𝖺𝖻𝗅𝖾𝖽 𝗂𝗇 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**", reply_markup=button)
    else:
        # If not enabled, send a button to enable
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🟢 𝖤𝗇𝖺𝖻𝗅𝖾 𝖢𝗅𝖾𝖺𝗇𝖾𝗋", callback_data=f"enable_cleaner:{chat_id}")],
            [InlineKeyboardButton("🗑️", callback_data="delete")]]
             
        )
        await message.reply_text("**🛡️ 𝖢𝗅𝖾𝖺𝗇 𝖲𝖾𝗋𝗏𝗂𝖼𝖾 𝖺𝗋𝖾 𝖽𝗂𝗌𝖺𝖻𝗅𝖾𝖽 𝗂𝗇 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**", reply_markup=button)


# Callback query handler to enable/disable cleaners
@pgram.on_callback_query(filters.regex("^(enable_cleaner|disable_cleaner):"))
@chatadmin
@error
async def toggle_cleaner(client: Client, callback_query):
    action, chat_id = callback_query.data.split(":")
    chat_id = int(chat_id)
    chat = await client.get_chat(chat_id)
    admin = f"{callback_query.from_user.first_name} ({callback_query.from_user.id})"

    if action == "enable_cleaner":
        await enable_cleaner(chat_id, chat.title, chat.username)
        await callback_query.message.edit_text("**🟢 𝖢𝗅𝖾𝖺𝗇𝖾𝗋 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝖾𝗇𝖺𝖻𝗅𝖾𝖽 𝖿𝗈𝗋 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**")
        log_message = await format_log("Enable cleaner", chat.title, admin)
        await send_log(chat_id, log_message)
    elif action == "disable_cleaner":
        await disable_cleaner(chat_id)
        await callback_query.message.edit_text("**🔴 𝖢𝗅𝖾𝖺𝗇𝖾𝗋 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝖽𝗂𝗌𝖺𝖻𝗅𝖾𝖽 𝖿𝗈𝗋 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**")
        log_message = await format_log("Disable cleaner", chat.title, admin)
        await send_log(chat_id, log_message)

@pgram.on_message(filters.group, group=SERVICE_CLEANER_GROUP)
@error
@save
async def manage_antichannel(client: Client, message: Message):
    chat_id = message.chat.id

    # Check if the cleaner feature is enabled for the group
    if not await is_cleaner_enabled(chat_id):
        return

    try :

        # Delete service messages
        if message.service:
            await message.delete()
            return
    
        # Check if the message starts with any of the defined command prefixes
        if message.text and any(message.text.startswith(prefix) for prefix in config.COMMAND_PREFIXES):
            await message.delete()
            return
        
    except:
        return
    
__module__ = "𝖢𝗅𝖾𝖺𝗇𝖾𝗋"
__help__ = """✧ /cleaner : 𝖳𝗈𝗀𝗀𝗅𝖾 𝗍𝗁𝖾 𝗌𝖾𝗋𝗏𝗂𝖼𝖾 𝖼𝗅𝖾𝖺𝗇𝖾𝗋 𝗌𝗍𝖺𝗍𝗎𝗌 𝗂𝗇 𝗍𝗁𝖾 𝖼𝗁𝖺𝗍.
✧ Service Cleaner:
   - 𝖤𝗇𝖺𝖻𝗅𝖾𝗌 𝗍𝗁𝖾 𝖺𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼 𝖽𝖾𝗅𝖾𝗍𝗂𝗈𝗇 𝗈𝖿 𝗌𝖾𝗋𝗏𝗂𝖼𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝗂𝗇 𝗍𝗁𝖾 𝖼𝗁𝖺𝗍.
   - 𝖠𝗅𝗌𝗈 𝖽𝖾𝗅𝖾𝗍𝖾𝗌 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝗌𝗍𝖺𝗋𝗍𝗂𝗇𝗀 𝗐𝗂𝗍𝗁 𝖼𝗈𝗆𝗆𝖺𝗇𝖽 𝗉𝗋𝖾𝖿𝗂𝗑𝖾𝗌.
✧ 𝖴𝗌𝖾 /cleaner 𝗍𝗈 𝖾𝗇𝖺𝖻𝗅𝖾 𝗈𝗋 𝖽𝗂𝗌𝖺𝖻𝗅𝖾 𝗍𝗁𝗂𝗌 𝖿𝖾𝖺𝗍𝗎𝗋𝖾.
"""
