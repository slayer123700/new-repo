from pyrogram import Client
from pyrogram.errors import RPCError , ChatAdminRequired
from shigaraki.database import warnings_collection
from shigaraki import app

MAX_WARNS = 3  # Threshold for banning a user

async def add_warn(chat_id: int, user_id: int, reason: None, client: Client):
    """
    Add a warning to a user in a specific chat and check for ban conditions.
    """
    warn_data = await warnings_collection.find_one({"chat_id": chat_id, "user_id": user_id})
    if not warn_data:
        warn_data = {"chat_id": chat_id, "user_id": user_id, "warn_count": 0, "reasons": []}

    warn_data["warn_count"] += 1
    warn_data["reasons"].append(reason)

    await warnings_collection.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": warn_data},
        upsert=True
    )

    # Check if the user has reached the maximum warning count
    if warn_data["warn_count"] >= MAX_WARNS:
        await ban_user(chat_id, user_id, client)

    return warn_data["warn_count"]

async def ban_user(chat_id: int, user_id: int, client: Client):
    """
    Ban a user from the chat and remove all their warnings.
    """
    try:
        await app.ban_chat_member(chat_id, user_id)
        await clear_warns(chat_id, user_id)
    except ChatAdminRequired :
        return
    except Exception :
        return

async def remove_warn(chat_id: int, user_id: int):
    """
    Remove a warning from a user in a specific chat.
    """
    warn_data = await warnings_collection.find_one({"chat_id": chat_id, "user_id": user_id})
    if not warn_data or warn_data["warn_count"] == 0:
        return 0

    warn_data["warn_count"] -= 1
    if warn_data["reasons"]:
        warn_data["reasons"].pop()

    await warnings_collection.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": warn_data}
    )
    return warn_data["warn_count"]

async def get_warn_count(chat_id: int, user_id: int):
    """
    Get the warning count for a user in a specific chat.
    """
    warn_data = await warnings_collection.find_one({"chat_id": chat_id, "user_id": user_id})
    if not warn_data:
        return 0
    return warn_data["warn_count"]

async def get_warn_reasons(chat_id: int, user_id: int):
    """
    Get the reasons for warnings for a user in a specific chat.
    """
    warn_data = await warnings_collection.find_one({"chat_id": chat_id, "user_id": user_id})
    if not warn_data:
        return []
    return warn_data["reasons"]

async def clear_warns(chat_id: int, user_id: int):
    """
    Clear all warnings for a user in a specific chat.
    """
    await warnings_collection.delete_one({"chat_id": chat_id, "user_id": user_id})
