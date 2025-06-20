from shigaraki.database.global_actions_db import (
    is_user_gmuted, 
    is_user_gbanned,
    save_banned_chats
    )
from shigaraki import app, GLOBAL_ACTION_WATCHER_GROUP
from pyrogram import filters
from pyrogram.types import Message
from config import config 

@app.on_message(filters.all, group=GLOBAL_ACTION_WATCHER_GROUP)
async def gmute_gban_watcher(client, message: Message):
    user = message.from_user
    chat = message.chat

    if not user or not chat:
        return

    # Check if the user is globally banned
    if await is_user_gbanned(user.id):
        try:
            await app.ban_chat_member(chat.id, user.id)
            await save_banned_chats(user.id , chat.id)
            # Notify the group
            try:
                await message.reply_text(
                    f"{user.mention} 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗀𝗅𝗈𝖻𝖺𝗅𝗅𝗒 𝖻𝖺𝗇𝗇𝖾𝖽 𝖺𝗇𝖽 𝗋𝖾𝗆𝗈𝗏𝖾𝖽 𝖿𝗋𝗈𝗆 𝗍𝗁𝗂𝗌 𝗀𝗋𝗈𝗎𝗉. "
                    f"𝖨𝖿 𝗒𝗈𝗎 𝖻𝖾𝗅𝗂𝖾𝗏𝖾 𝗍𝗁𝗂𝗌 𝗂𝗌 𝖺𝗇 𝖾𝗋𝗋𝗈𝗋, 𝗒𝗈𝗎 𝖼𝖺𝗇 𝖺𝗉𝗉𝖾𝖺𝗅 𝖻𝗒 𝖼𝗈𝗇𝗍𝖺𝖼𝗍𝗂𝗇𝗀 𝗌𝗎𝗉𝗉𝗈𝗋𝗍: @{config.SUPPORT_CHAT_USERNAME}."
                )
            except Exception:
                pass

            # Notify the user via private message
            try:
                await app.send_message(
                    user.id,
                    f"𝖸𝗈𝗎 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝗀𝗅𝗈𝖻𝖺𝗅𝗅𝗒 𝖻𝖺𝗇𝗇𝖾𝖽 𝖿𝗋𝗈𝗆 𝖺𝗅𝗅 𝗀𝗋𝗈𝗎𝗉𝗌 𝗆𝖺𝗇𝖺𝗀𝖾𝖽 𝖻𝗒 𝗍𝗁𝗂𝗌 𝖻𝗈𝗍."
                    f"𝖨𝖿 𝗒𝗈𝗎 𝖻𝖾𝗅𝗂𝖾𝗏𝖾 𝗍𝗁𝗂𝗌 𝗂𝗌 𝖺𝗇 𝖾𝗋𝗋𝗈𝗋, 𝗉𝗅𝖾𝖺𝗌𝖾 𝖼𝗈𝗇𝗍𝖺𝖼𝗍 𝗌𝗎𝗉𝗉𝗈𝗋𝗍: @{config.SUPPORT_CHAT_USERNAME}."
                )
            except Exception:
                pass

            return
        except Exception:
            return

    # Check if the user is globally muted
    if await is_user_gmuted(user.id):
        try:
            await message.delete()
        except Exception:
            return

