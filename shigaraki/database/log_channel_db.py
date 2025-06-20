from shigaraki.database import log_channel_collection

async def set_log_channel(chat_id: int, log_channel_id: int):
    """
    Set or update the log channel for a specific chat.
    """
    await log_channel_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"log_channel_id": log_channel_id}},
        upsert=True
    )

async def get_log_channel(chat_id: int) -> int:
    """
    Get the log channel ID for a specific chat.

    Returns:
        int: The log channel ID, or None if not set.
    """
    chat_data = await log_channel_collection.find_one({"chat_id": chat_id})
    return chat_data["log_channel_id"] if chat_data else None

async def remove_log_channel(chat_id: int):
    """
    Remove the log channel for a specific chat.
    """
    await log_channel_collection.delete_one({"chat_id": chat_id})

async def get_all_log_channels():
    """
    Retrieve all chat-log channel mappings.

    Returns:
        list: A list of all chat-log channel mappings.
    """
    return await log_channel_collection.find({}).to_list(length=None)

async def is_log_channel_set(chat_id: int) -> bool:
    """
    Check if a log channel is set for a specific chat.

    Returns:
        bool: True if a log channel is set, False otherwise.
    """
    chat_data = await log_channel_collection.find_one({"chat_id": chat_id})
    return True if chat_data else False

async def get_chats_with_log_channels():
    """
    Get all chats with their respective log channels.

    Returns:
        list: A list of dictionaries containing chat IDs and their log channel IDs.
    """
    chats = await log_channel_collection.find({}).to_list(length=None)
    return [{"chat_id": chat["chat_id"], "log_channel_id": chat["log_channel_id"]} for chat in chats]


async def get_log_channel_count():
    """
    Get the total number of log channels set in the database.
    
    Returns:
        int: The total count of log channels set.
    """
    count = await log_channel_collection.count_documents({})
    return count
