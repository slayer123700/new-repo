from shigaraki.database import chatbot_collection



async def save_or_update_chat(chat_id: int, chat_username: str = None, chat_title: str = None, chat_link: str = None, chatbot_enabled: bool = False):
    """
    Save or update chat details in the database.
    If the chat exists, update its data. If not, create a new entry.
    """
    await chatbot_collection.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "chat_username": chat_username,
                "chat_title": chat_title,
                "chat_link": chat_link,
                "chatbot_enabled": chatbot_enabled,
            }
        },
        upsert=True
    )

async def enable_chatbot(chat_id: int, chat_title: str, chat_username: str = None, chat_link: str = None):
    """Enable chatbot for a specific chat and save details."""
    await chatbot_collection.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "chatbot_enabled": True,
                "chat_title": chat_title,
                "chat_username": chat_username,
                "chat_link": chat_link,
            }
        },
        upsert=True
    )

async def disable_chatbot(chat_id: int):
    """Disable chatbot for a specific chat."""
    await chatbot_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"chatbot_enabled": False}},
        upsert=True
    )

async def is_chatbot_enabled(chat_id: int) -> bool:
    """Check if the chatbot is enabled for a specific chat."""
    chat_data = await chatbot_collection.find_one({"chat_id": chat_id})
    return chat_data["chatbot_enabled"] if chat_data else False

async def get_all_enabled_chats():
    """Get all chats where the chatbot is enabled."""
    enabled_chats = await chatbot_collection.find({"chatbot_enabled": True}).to_list(length=None)
    return enabled_chats

async def get_chat_info(chat_id: int):
    """Retrieve information about a specific chat."""
    return await chatbot_collection.find_one({"chat_id": chat_id})