from shigaraki.database import karma_collection

async def increase_karma(user_id: int, user_name: str, chat_id: int, points: int = 1):
    """Increase the karma points for a user in a specific chat."""
    karma_collection.update_one(
        {"user_id": user_id, "chat_id": chat_id},
        {
            "$inc": {"karma": points},
            "$setOnInsert": {"user_id": user_id, "chat_id": chat_id, "user_name": user_name},
        },
        upsert=True,
    )

async def decrease_karma(user_id: int, user_name: str, chat_id: int, points: int = 1):
    """Decrease the karma points for a user in a specific chat."""
    karma_collection.update_one(
        {"user_id": user_id, "chat_id": chat_id},
        {
            "$inc": {"karma": -points},
            "$setOnInsert": {"user_id": user_id, "chat_id": chat_id, "user_name": user_name},
        },
        upsert=True,
    )


async def get_karma(user_id: int, chat_id: int) -> int:
    """Get the current karma points for a user in a specific chat."""
    user_karma = await karma_collection.find_one({"user_id": user_id, "chat_id": chat_id})
    return user_karma["karma"] if user_karma else 0


async def top_karma(chat_id: int, limit: int = 10) -> list:
    """Get the top users with the highest karma in a specific chat."""
    cursor = karma_collection.find({"chat_id": chat_id}).sort("karma", -1).limit(limit)
    top_users = []
    async for user in cursor:
        top_users.append({"user_id": user["user_id"], "karma": user["karma"], "user_name": user.get("user_name", "Unknown")})
    return top_users
