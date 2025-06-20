from shigaraki.database import imposter_collection



async def save_or_check_user(user):
    """
    Saves a user's information or checks for any changes in their info.

    Args:
        user (telegram.User): The user object from the Telegram API.

    Returns:
        list: A list of tuples containing change type, old value, and new value for each change detected.
    """
    if not user:
        return []  # Skip invalid data

    # Prepare new user data
    new_data = {
        "user_id": user.id,
        "username": user.username.lower() if user.username else None,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }

    # Check for existing user in the database
    existing_user = await imposter_collection.find_one({"user_id": user.id})
    changes = []

    if existing_user:
        # Detect and handle each type of change
        for field in ["username", "first_name", "last_name"]:
            if existing_user.get(field) != new_data[field]:
                changes.append((field, existing_user.get(field), new_data[field]))
                # Update the database with the new value
                await imposter_collection.update_one(
                    {"user_id": user.id},
                    {"$set": {field: new_data[field]}}
                )
    else:
        # Insert new user data if not found
        await imposter_collection.insert_one(new_data)

    return changes

async def enable_imposter(chat_id: int, chat_title: str, chat_username: str = None):
    """Enable imposter for a specific chat and save details."""
    await imposter_collection.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "imposter_enabled": True,
                "chat_title": chat_title,
                "chat_username": chat_username,
            }
        },
        upsert=True
    )

async def disable_imposter(chat_id: int):
    """Disable imposter for a specific chat."""
    await imposter_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"imposter_enabled": False}},
        upsert=True
    )

async def is_imposter_enabled(chat_id: int) -> bool:
    """Check if the imposter is enabled for a specific chat."""
    chat_data = await imposter_collection.find_one({"chat_id": chat_id})
    return chat_data["imposter_enabled"] if chat_data else False