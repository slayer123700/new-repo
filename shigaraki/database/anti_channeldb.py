from shigaraki.database import antichannel_collection


async def enable_antichannel(chat_id: int, chat_title: str, chat_username: str = None, chat_link: str = None):
    """Enable antichannel for a specific chat and save details."""
    await antichannel_collection.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "antichannel_enabled": True,
                "chat_title": chat_title,
                "chat_username": chat_username,
                "chat_link": chat_link,
            }
        },
        upsert=True
    )

async def disable_antichannel(chat_id: int):
    """Disable antichannel for a specific chat."""
    await antichannel_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"antichannel_enabled": False}},
        upsert=True
    )

async def is_antichannel_enabled(chat_id: int) -> bool:
    """Check if antichannel are enabled for a specific chat."""
    chat_data = await antichannel_collection.find_one({"chat_id": chat_id})
    return chat_data["antichannel_enabled"] if chat_data else False

async def get_chat_info(chat_id: int):
    """Retrieve information about a specific chat."""
    return await antichannel_collection.find_one({"chat_id": chat_id})