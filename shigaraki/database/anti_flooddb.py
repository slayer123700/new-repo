from shigaraki.database import antiflood_collection


async def get_antiflood_settings(chat_id: int):
    """Get antiflood settings for a specific chat."""
    settings = await antiflood_collection.find_one({"chat_id": chat_id})
    return settings or {
        "flood_threshold": 0,
        "flood_timer_count": 0,
        "flood_timer_duration": 0,
        "flood_action": "mute",
        "delete_flood_messages": False,
        "action_duration": 86400,  # Default duration of 1 day in seconds
    }

async def set_flood_threshold(chat_id: int, threshold: int):
    """Set the flood message threshold for triggering antiflood."""
    await antiflood_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"flood_threshold": threshold}},
        upsert=True
    )

async def set_flood_timer(chat_id: int, count: int, duration: int):
    """Set the timed antiflood settings: number of messages and duration in seconds."""
    await antiflood_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"flood_timer_count": count, "flood_timer_duration": duration}},
        upsert=True
    )

async def set_flood_action(chat_id: int, action: str):
    """Set the action to be taken when antiflood is triggered."""
    await antiflood_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"flood_action": action}},
        upsert=True
    )

async def set_delete_flood_messages(chat_id: int, delete: bool):
    """Set whether to delete the messages that triggered the antiflood."""
    await antiflood_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"delete_flood_messages": delete}},
        upsert=True
    )

async def set_flood_action_duration(chat_id: int, duration_seconds: int):
    """Set the custom action duration for tban or tmute in seconds."""
    await antiflood_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"action_duration": duration_seconds}},
        upsert=True
    )

async def get_flood_action_duration(chat_id: int):
    """Get the custom action duration for tban or tmute in seconds."""
    settings = await antiflood_collection.find_one({"chat_id": chat_id})
    return settings.get("action_duration", 86400) if settings else 86400  # Default to 1 day