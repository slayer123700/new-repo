from shigaraki.database import afk_collection


async def set_afk(user_id: int, user_first_name: str, username: str, afk_reason: str, afk_start_time: str , media_id: str = None):
    """Set AFK details for a specific user."""
    await afk_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_first_name": user_first_name,
                "username": username,
                "afk_reason": afk_reason,
                "afk_start_time": afk_start_time,
                "media_id": media_id
            }
        },
        upsert=True
    )

async def get_afk(user_id: int):
    """Get the AFK details for a specific user."""
    user_data = await afk_collection.find_one({"user_id": user_id})
    return user_data if user_data else None

async def clear_afk(user_id: int):
    """Clear AFK details for a specific user."""
    await afk_collection.delete_one({"user_id": user_id})

async def get_afk_by_username(username: str):
    """Get the AFK details for a specific user by username."""
    user_data = await afk_collection.find_one({"username": username})  # Await the coroutine
    if user_data:
        return {
            "user_id": user_data["user_id"],
            "user_first_name": user_data["user_first_name"],
            "afk_start_time": user_data["afk_start_time"],
            "afk_reason": user_data.get("afk_reason"),
            "media_id": user_data.get("media_id"),
        }
    return None

async def is_user_afk(user_id: int) -> bool:
    """Check if a user is currently AFK."""
    user_data = await afk_collection.find_one({"user_id": user_id})
    return bool(user_data)
