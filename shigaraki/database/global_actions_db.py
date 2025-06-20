from shigaraki.database import gmute_collection, gban_collection , banned_chats


async def add_to_gmute(user_id: int, first_name: str = None, username: str = None):
    """
    Add a user to the GMute collection.
    """
    data = {
        "id": user_id,
        "first_name": first_name,
        "username": username,
    }
    await gmute_collection.update_one({"id": user_id}, {"$set": data}, upsert=True)
    return data


async def add_to_gban(user_id: int, first_name: str = None, username: str = None):
    """
    Add a user to the GBan collection.
    """
    data = {
        "id": user_id,
        "first_name": first_name,
        "username": username,
    }
    await gban_collection.update_one({"id": user_id}, {"$set": data}, upsert=True)
    return data


async def remove_from_gmute(user_id: int):
    """
    Remove a user from the GMute collection.
    """
    result = await gmute_collection.delete_one({"id": user_id})
    return result.deleted_count > 0


async def remove_from_gban(user_id: int):
    """
    Remove a user from the GBan collection.
    """
    result = await gban_collection.delete_one({"id": user_id})
    return result.deleted_count > 0


async def get_all_gmuted_users():
    """
    Get all users in the GMute collection.
    """
    users = await gmute_collection.find().to_list(length=None)
    return users


async def get_all_gbanned_users():
    """
    Get all users in the GBan collection.
    """
    users = await gban_collection.find().to_list(length=None)
    return users


async def is_user_gmuted(user_id: int):
    """
    Check if a user is in the GMute collection.
    """
    user = await gmute_collection.find_one({"id": user_id})
    return user is not None


async def is_user_gbanned(user_id: int):
    """
    Check if a user is in the GBan collection.
    """
    user = await gban_collection.find_one({"id": user_id})
    return user is not None

async def get_total_gbanned_users():
    """
    Get the total number of GBanned users.
    :return: The count of GBanned users.
    """
    count = await gban_collection.count_documents({})
    return count


async def get_total_gmuted_users():
    """
    Get the total number of GMute users.
    :return: The count of GMute users.
    """
    count = await gmute_collection.count_documents({})
    return count

async def save_banned_chats(user_id: int, chat_ids):
    """
    Save the list of chat IDs where the user was banned.
    Handles both a single chat ID and a list of chat IDs.
    """
    # Ensure chat_ids is a list
    if isinstance(chat_ids, int):
        chat_ids = [chat_ids]

    # Add new chat IDs to the existing list (if any)
    existing_data = await banned_chats.find_one({"id": user_id})
    existing_chats = existing_data.get("banned_chats", []) if existing_data else []

    # Combine and remove duplicates
    updated_chats = list(set(existing_chats + chat_ids))

    # Update the database
    data = {
        "id": user_id,
        "banned_chats": updated_chats,
    }
    await banned_chats.update_one({"id": user_id}, {"$set": data}, upsert=True)
    return data


async def get_banned_chats(user_id: int):
    """
    Retrieve the list of chat IDs where the user was banned.
    """
    user_data = await banned_chats.find_one({"id": user_id})
    return user_data.get("banned_chats", []) if user_data else []
