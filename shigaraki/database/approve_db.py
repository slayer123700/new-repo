from shigaraki.database import approved_collection


async def get_approved_users(chat_id: int):
    """Get the list of approved users for a specific chat."""
    approved_users = await approved_collection.find({"chat_id": chat_id}).to_list(length=None)
    return [(user['user_id'], user['user_name']) for user in approved_users]

async def is_user_approved(chat_id: int, user_id: int):
    """Check if a user is approved in the given chat."""
    user = await approved_collection.find_one({"chat_id": chat_id, "user_id": user_id})
    return user is not None

async def approve_user(chat_id: int, user_id: int , user_name : str):
    """Approve a user in the given chat."""
    if await is_user_approved(chat_id, user_id):
        return False  # User is already approved

    await approved_collection.insert_one({"chat_id": chat_id, "user_id": user_id , "user_name" : user_name})
    return True

async def unapprove_user(chat_id: int, user_id: int):
    """Unapprove a user in the given chat."""
    await approved_collection.delete_one({"chat_id": chat_id, "user_id": user_id})

async def unapprove_all_users(chat_id: int):
    """Unapprove all users in the given chat."""
    await approved_collection.delete_many({"chat_id": chat_id})
