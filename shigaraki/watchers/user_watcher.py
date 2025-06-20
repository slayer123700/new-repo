from pyrogram import filters
from pymongo import UpdateOne
from shigaraki.database.user_db import save_user , user_collection
from shigaraki import app , WATCHER_GROUP
from pyrogram.types import Message
from pyrogram.enums import ChatType
from config import config

# Optional: Batch update for large groups or channels
@app.on_message(filters.all , group=WATCHER_GROUP)
async def batch_user_saver(client, message : Message):

    if message.chat.type == ChatType.PRIVATE:
        
        if message.from_user.id != config.OWNER_ID:
            await message.forward(config.OWNER_ID)

        user = message.from_user
        if user:
            await save_user(
                user_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
            )
    else :
        users = []
        if message.from_user:
            users.append(message.from_user)
        if message.sender_chat:
            # Only include user details, not bots or channel info
            pass
        
        # Process all users in bulk
        if users:
            bulk_updates = [
                UpdateOne(
                    {"user_id": user.id},
                    {
                        "$set": {
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "username": user.username,
                        }
                    },
                    upsert=True,
                )
                for user in users
            ]
            if bulk_updates:
                await user_collection.bulk_write(bulk_updates)

