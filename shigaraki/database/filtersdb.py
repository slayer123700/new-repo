from shigaraki.database import filter_collection



async def add_filter(chat_id: int, triggers: list, response: dict):
    """
    Add or update a filter for a specific chat.
    :param chat_id: ID of the chat
    :param triggers: List of words/triggers for the filter
    :param response: The response (text, sticker, or media)
    """
    existing_chat_filters = await filter_collection.find_one({"chat_id": chat_id})

    if existing_chat_filters is None:
        # Initialize document if it doesn't exist
        existing_chat_filters = {"chat_id": chat_id, "filters": {}}

    # Ensure the "filters" key exists in the document
    if "filters" not in existing_chat_filters:
        existing_chat_filters["filters"] = {}

    for trigger in triggers:
        existing_chat_filters["filters"][trigger] = response

    # Upsert (update or insert) the document
    await filter_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"filters": existing_chat_filters["filters"]}},
        upsert=True
    )


# Retrieve a specific filter by its trigger
async def get_filter(chat_id: int, text: str):
    """
    Retrieve a specific filter by its trigger.
    :param chat_id: ID of the chat
    :param text: The word/trigger
    :return: The filter response
    """
    chat_filters = await filter_collection.find_one({"chat_id": chat_id})
    if chat_filters and text in chat_filters.get("filters", {}):
        return {"response": chat_filters["filters"][text]}
    return None

# Remove a filter from the database
async def remove_filter(chat_id: int, trigger: str):
    """
    Remove a specific filter by its trigger.
    :param chat_id: ID of the chat
    :param trigger: The word/trigger to remove
    """
    await filter_collection.update_one(
        {"chat_id": chat_id},
        {"$unset": {f"filters.{trigger}": ""}}
    )

# Retrieve all filters for a specific chat
async def get_filters(chat_id: int):
    """
    Retrieve all filters for a specific chat.
    :param chat_id: ID of the chat
    :return: List of filters
    """
    chat_filters = await filter_collection.find_one({"chat_id": chat_id})
    if chat_filters:
        return [{"triggers": [key], "response": value} for key, value in chat_filters.get("filters", {}).items()]
    return []

async def get_filter_statistics():
    """
    Get statistics of the filters set in the database.
    :return: A dictionary with the total number of chats and filters.
    """
    all_filters = await filter_collection.find({}).to_list(length=None)
    total_chats = len(all_filters)
    total_filters = sum(len(chat.get("filters", {})) for chat in all_filters)

    return {
        "total_chats": total_chats,
        "total_filters": total_filters
    }
