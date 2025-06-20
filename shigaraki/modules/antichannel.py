from shigaraki import app as pgram , ANTICHANNEL_GROUP
from shigaraki.database.anti_channeldb import (
    enable_antichannel,
    disable_antichannel,
    is_antichannel_enabled,
)
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.types import  Message
from pyrogram.errors import ChatAdminRequired
from shigaraki.decorator.chatadmin import chatadmin
from config import config 
from shigaraki.helper.log_helper import send_log, format_log
from shigaraki.decorator.errors import error
from shigaraki.decorator.save import save
from shigaraki.shigaraki import CHAT_ADMIN_REQUIRED

# Command to toggle antichannel status
@pgram.on_message(filters.command("antichannel" , prefixes=config.COMMAND_PREFIXES) & filters.group)
@chatadmin
@error
@save
async def antichannel_handler(client: Client, message: Message):
    chat_id = message.chat.id

    if await is_antichannel_enabled(chat_id):
        # If already enabled, send a button to disable
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔴 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖠𝗇𝗍𝗂𝖼𝗁𝖺𝗇𝗇𝖾𝗅", callback_data=f"disable_antichannel:{chat_id}")],
            [InlineKeyboardButton("🗑️", callback_data="delete")]]
        )
        await message.reply_text("**🛡️ 𝖠𝗇𝗍𝗂𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝖺𝗋𝖾 𝖾𝗇𝖺𝖻𝗅𝖾𝖽 𝗂𝗇 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**", reply_markup=button)
    else:
        # If not enabled, send a button to enable
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🟢 𝖤𝗇𝖺𝖻𝗅𝖾 𝖠𝗇𝗍𝗂𝖼𝗁𝖺𝗇𝗇𝖾𝗅", callback_data=f"enable_antichannel:{chat_id}")],
            [InlineKeyboardButton("🗑️", callback_data="delete")]]
             
        )
        await message.reply_text("**🛡️ 𝖠𝗇𝗍𝗂𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝖺𝗋𝖾 𝖽𝗂𝗌𝖺𝖻𝗅𝖾𝖽 𝗂𝗇 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**", reply_markup=button)


# Callback query handler to enable/disable antichannels
@pgram.on_callback_query(filters.regex("^(enable_antichannel|disable_antichannel):"))
@chatadmin
@error
async def toggle_antichannel(client: Client, callback_query):
    action, chat_id = callback_query.data.split(":")
    chat_id = int(chat_id)
    chat = await client.get_chat(chat_id)
    admin = f"{callback_query.from_user.first_name} ({callback_query.from_user.id})"

    if action == "enable_antichannel":
        await enable_antichannel(chat_id, chat.title, chat.username)
        await callback_query.message.edit_text("**🟢 𝖠𝗇𝗍𝗂𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝖾𝗇𝖺𝖻𝗅𝖾𝖽 𝖿𝗈𝗋 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**")
        log_message = await format_log("Enable Antichannel", chat.title, admin)
        await send_log(chat_id, log_message)
    elif action == "disable_antichannel":
        await disable_antichannel(chat_id)
        await callback_query.message.edit_text("**🔴 𝖠𝗇𝗍𝗂𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝖽𝗂𝗌𝖺𝖻𝗅𝖾𝖽 𝖿𝗈𝗋 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**")
        log_message = await format_log("Disable Antichannel", chat.title, admin)
        await send_log(chat_id, log_message)

# Manage antichannel logic
@pgram.on_message(filters.group , group=ANTICHANNEL_GROUP)
@error
@save
async def manage_antichannel(client: Client, message: Message):
    chat_id = message.chat.id

    if not await is_antichannel_enabled(chat_id):
        return

    if message.sender_chat and message.sender_chat.id == message.chat.id :
        return

    # Check if the message is sent using a channel profile
    if message.sender_chat:
        sender_chat = message.sender_chat

        # Check if the channel is linked to the group
        chat = await client.get_chat(chat_id)
        if chat.linked_chat and sender_chat.id == chat.linked_chat.id:
            return

        # Ban the channel and announce it
        try:
            await client.ban_chat_member(chat_id, sender_chat.id)
            await message.reply_text(
                f"**🚫 Channel {sender_chat.title} has been banned.**\n"
            )
            log_message = await format_log(
                "Ban Channel Profile", chat.title, user=sender_chat.title
            )
            await send_log(chat_id, log_message)
        except ChatAdminRequired :
            await message.reply_text(CHAT_ADMIN_REQUIRED)

        except Exception as e:
            await message.reply_text(f"**❌ Failed to ban {sender_chat.title}.**")


__module__ = "𝖠𝗇𝗍𝗂𝖢𝗁𝖺𝗇𝗇𝖾𝗅"

__help__ = "✧ /𝖺𝗇𝗍𝗂𝖼𝗁𝖺𝗇𝗇𝖾𝗅 : 𝖴𝗌𝖾 𝖨𝗍 𝖳𝗈 𝖤𝗇𝖺𝖻𝗅𝖾 𝖮𝗋 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖠𝗇𝗍𝗂-𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖨𝗇 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉.\𝗇(𝖠𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖱𝖾𝗆𝗈𝗏𝖾𝗌 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖯𝗋𝗈𝖿𝗂𝗅𝖾𝗌 𝖥𝗋𝗈𝗆 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉)"