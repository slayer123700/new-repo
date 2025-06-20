from shigaraki.database import nightmode_collection

async def enable_nightmode(chat_id: int, chat_title: str, chat_username: str = None, chat_link: str = None):
    """Enable night mode for a specific chat and save details."""
    await nightmode_collection.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "nightmode_enabled": True,
                "chat_title": chat_title,
                "chat_username": chat_username,
                "chat_link": chat_link,
            }
        },
        upsert=True
    )

async def disable_nightmode(chat_id: int):
    """Disable night mode for a specific chat."""
    await nightmode_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"nightmode_enabled": False}},
        upsert=True
    )

async def is_nightmode_enabled(chat_id: int) -> bool:
    """Check if night mode is enabled for a specific chat."""
    chat_data = await nightmode_collection.find_one({"chat_id": chat_id})
    return chat_data["nightmode_enabled"] if chat_data else False

async def get_nightmode_chat_info(chat_id: int):
    """Retrieve information about a specific chat in night mode."""
    return await nightmode_collection.find_one({"chat_id": chat_id})

async def get_all_nightmode_enabled_chats():
    """Retrieve all chat IDs with night mode enabled."""
    cursor = nightmode_collection.find({"nightmode_enabled": True}, {"chat_id": 1, "_id": 0})
    return [chat["chat_id"] async for chat in cursor]
