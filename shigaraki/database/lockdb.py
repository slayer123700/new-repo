from shigaraki.database import locks_collection



# --- Lock Functions ---
async def set_lock(chat_id: int, lock_type: str):
    """Enable a lock in a chat."""
    await locks_collection.update_one(
        {"chat_id": chat_id},
        {"$addToSet": {"locks": lock_type}},
        upsert=True
    )

async def unset_lock(chat_id: int, lock_type: str):
    """Disable a lock in a chat."""
    await locks_collection.update_one(
        {"chat_id": chat_id},
        {"$pull": {"locks": lock_type}},
    )

async def get_locks(chat_id: int):
    """Retrieve all active locks for a chat."""
    chat_data = await locks_collection.find_one({"chat_id": chat_id})
    return chat_data.get("locks", []) if chat_data else []

async def clear_all_locks(chat_id: int):
    """Clear all locks for a chat."""
    await locks_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"locks": []}}
    )
    
async def get_lock_statistics():
    """
    Get statistics about locks in the database.
    :return: A dictionary with the total number of chats and locks.
    """
    all_locks = await locks_collection.find({}).to_list(length=None)
    total_chats = len(all_locks)
    total_locks = sum(len(chat.get("locks", [])) for chat in all_locks)

    return {
        "total_chats": total_chats,
        "total_locks": total_locks
    }
