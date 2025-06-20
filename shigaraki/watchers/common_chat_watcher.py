from shigaraki.database.common_chat_db import save_user_chat
from shigaraki import app, COMMON_CHAT_WATCHER_GROUP
from pyrogram.types import Message
from pyrogram import filters

@app.on_message(filters.all, group=COMMON_CHAT_WATCHER_GROUP)
async def user_chat_tracker(client, message: Message):
    user = message.from_user
    chat = message.chat

    if user and chat:
        # Save the user-chat mapping
        await save_user_chat(user_id=user.id, chat_id=chat.id)
    else :
        return