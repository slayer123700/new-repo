from shigaraki.database import announcement_collection



async def enable_announcements(chat_id: int, chat_title: str, chat_username: str = None, chat_link: str = None):
    """Enable announcements for a specific chat and save details."""
    await announcement_collection.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "announcements_enabled": True,
                "chat_title": chat_title,
                "chat_username": chat_username,
                "chat_link": chat_link,
            }
        },
        upsert=True
    )

async def disable_announcements(chat_id: int):
    """Disable announcements for a specific chat."""
    await announcement_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"announcements_enabled": False}},
        upsert=True
    )

async def is_announcements_enabled(chat_id: int) -> bool:
    """Check if announcements are enabled for a specific chat."""
    chat_data = await announcement_collection.find_one({"chat_id": chat_id})
    return chat_data["announcements_enabled"] if chat_data else False

async def get_all_enabled_chats():
    """Get all chats where announcements are enabled."""
    enabled_chats = await announcement_collection.find({"announcements_enabled": True}).to_list(length=None)
    return enabled_chats

async def get_chat_info(chat_id: int):
    """Retrieve information about a specific chat."""
    return await announcement_collection.find_one({"chat_id": chat_id})