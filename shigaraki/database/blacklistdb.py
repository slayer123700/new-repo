from shigaraki.database import blacklist_collection


# --- Word Blacklist Functions ---
async def add_blacklisted_word(chat_id: int, word: str):
    """Add a word to the blacklist for a specific chat."""
    await blacklist_collection.update_one(
        {"chat_id": chat_id},
        {"$addToSet": {"blacklisted_words": word}},
        upsert=True
    )

async def remove_blacklisted_word(chat_id: int, word: str):
    """Remove a word from the blacklist for a specific chat."""
    await blacklist_collection.update_one(
        {"chat_id": chat_id},
        {"$pull": {"blacklisted_words": word}},
    )

async def get_blacklisted_words(chat_id: int):
    """Retrieve the list of blacklisted words for a specific chat."""
    chat_data = await blacklist_collection.find_one({"chat_id": chat_id})
    return chat_data.get("blacklisted_words", []) if chat_data else []

async def set_blacklist_mode(chat_id: int, mode: str, duration: int = 0):
    """
    Set the blacklist mode for a specific chat.
    Mode can be: off, del, ban, kick, mute, tban, tmute.
    Duration is only relevant for tban or tmute.
    """
    mode_data = {"mode": mode}
    if mode in ["tban", "tmute"]:
        mode_data["duration"] = duration
    await blacklist_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"blacklist_mode": mode_data}},
        upsert=True
    )

async def get_blacklist_mode(chat_id: int):
    """Retrieve the blacklist mode for a specific chat."""
    chat_data = await blacklist_collection.find_one({"chat_id": chat_id})
    mode_data = chat_data.get("blacklist_mode", {"mode": "off"}) if chat_data else {"mode": "off"}
    return mode_data

# --- Sticker Blacklist Functions ---
async def add_blacklisted_sticker(chat_id: int, sticker_id: str):
    """Add a sticker to the blacklist for a specific chat."""
    await blacklist_collection.update_one(
        {"chat_id": chat_id},
        {"$addToSet": {"blacklisted_stickers": sticker_id}},
        upsert=True
    )

async def remove_blacklisted_sticker(chat_id: int, sticker_id: str):
    """Remove a sticker from the blacklist for a specific chat."""
    await blacklist_collection.update_one(
        {"chat_id": chat_id},
        {"$pull": {"blacklisted_stickers": sticker_id}},
    )

async def get_blacklisted_stickers(chat_id: int):
    """Retrieve the list of blacklisted stickers for a specific chat."""
    chat_data = await blacklist_collection.find_one({"chat_id": chat_id})
    return chat_data.get("blacklisted_stickers", []) if chat_data else []

async def set_blacklist_sticker_mode(chat_id: int, mode: str, duration: int = 0):
    """
    Set the blacklist sticker mode for a specific chat.
    Mode can be: delete, ban, mute, tban, tmute.
    Duration is only relevant for tban or tmute.
    """
    mode_data = {"mode": mode}
    if mode in ["tban", "tmute"]:
        mode_data["duration"] = duration
    await blacklist_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"sticker_mode": mode_data}},
        upsert=True
    )

async def get_blacklist_sticker_mode(chat_id: int):
    """Retrieve the blacklist sticker mode for a specific chat."""
    chat_data = await blacklist_collection.find_one({"chat_id": chat_id})
    mode_data = chat_data.get("sticker_mode", {"mode": "delete"}) if chat_data else {"mode": "delete"}
    return mode_data


async def get_blacklist_summary():
    """
    Calculate the total number of blacklisted words and stickers across all chats
    and the number of chats with blacklisted words or stickers.
    
    Returns:
        dict: A dictionary containing the counts.
            {
                "total_blacklisted_words": int,
                "total_blacklisted_stickers": int,
                "chats_with_blacklisted_words": int,
                "chats_with_blacklisted_stickers": int
            }
    """
    cursor = blacklist_collection.find({})
    total_blacklisted_words = 0
    total_blacklisted_stickers = 0
    chats_with_blacklisted_words = 0
    chats_with_blacklisted_stickers = 0

    async for chat_data in cursor:
        # Count blacklisted words
        blacklisted_words = chat_data.get("blacklisted_words", [])
        if blacklisted_words:
            total_blacklisted_words += len(blacklisted_words)
            chats_with_blacklisted_words += 1

        # Count blacklisted stickers
        blacklisted_stickers = chat_data.get("blacklisted_stickers", [])
        if blacklisted_stickers:
            total_blacklisted_stickers += len(blacklisted_stickers)
            chats_with_blacklisted_stickers += 1

    return {
        "total_blacklisted_words": total_blacklisted_words,
        "total_blacklisted_stickers": total_blacklisted_stickers,
        "chats_with_blacklisted_words": chats_with_blacklisted_words,
        "chats_with_blacklisted_stickers": chats_with_blacklisted_stickers
    }
