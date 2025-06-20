from shigaraki.database import rules_collection



async def set_rules(chat_id: int, rules: str):
    """Set rules for a specific chat."""
    await rules_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"rules": rules}},
        upsert=True
    )

async def get_rules(chat_id: int):
    """Get the rules for a specific chat."""
    chat_data = await rules_collection.find_one({"chat_id": chat_id})
    return chat_data["rules"] if chat_data else None

async def clear_rules(chat_id: int):
    """Clear rules for a specific chat."""
    await rules_collection.delete_one({"chat_id": chat_id})
    
async def get_rules_enabled_chats_count():
    """
    Get the total number of chats with rules set in the database.
    
    Returns:
        int: The total count of chats with rules set.
    """
    count = await rules_collection.count_documents({})
    return count
