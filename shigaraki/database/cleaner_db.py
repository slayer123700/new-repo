from shigaraki.database import cleaner_collection


async def enable_cleaner(chat_id: int, chat_title: str, chat_username: str = None, chat_link: str = None):
    """Enable cleaner for a specific chat and save details."""
    await cleaner_collection.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "cleaner_enabled": True,
                "chat_title": chat_title,
                "chat_username": chat_username,
                "chat_link": chat_link,
            }
        },
        upsert=True
    )

async def disable_cleaner(chat_id: int):
    """Disable cleaner for a specific chat."""
    await cleaner_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"cleaner_enabled": False}},
        upsert=True
    )

async def is_cleaner_enabled(chat_id: int) -> bool:
    """Check if cleaner are enabled for a specific chat."""
    chat_data = await cleaner_collection.find_one({"chat_id": chat_id})
    return chat_data["cleaner_enabled"] if chat_data else False

async def get_chat_info(chat_id: int):
    """Retrieve information about a specific chat."""
    return await cleaner_collection.find_one({"chat_id": chat_id})

async def count_cleaner_enabled_chats():
    """Count the number of chats with cleaner enabled."""
    count = await cleaner_collection.count_documents({"cleaner_enabled": True})
    return count
