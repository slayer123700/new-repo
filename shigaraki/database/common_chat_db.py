from shigaraki.database import user_chat_collection  # Create a new MongoDB collection for user-chat mapping
from typing import List

# Function to save user and chat mapping
async def save_user_chat(user_id: int, chat_id: int):
    """
    Save or update user and chat mapping in MongoDB.
    """
    query = {"user_id": user_id, "chat_id": chat_id}
    update = {"$set": {"user_id": user_id, "chat_id": chat_id}}
    await user_chat_collection.update_one(query, update, upsert=True)

# Function to get common chat count for a user
async def get_common_chat_count(user_id: int) -> int:
    """
    Get the count of common chats for a user.
    """
    query = {"user_id": user_id}
    count = await user_chat_collection.count_documents(query)
    return count

# Function to get common chat IDs for a user
async def get_common_chat_ids(user_id: int) -> List[int]:
    """
    Get the list of common chat IDs for a user.
    """
    query = {"user_id": user_id}
    chats = await user_chat_collection.find(query).to_list(length=None)
    chat_ids = [chat["chat_id"] for chat in chats]
    return chat_ids
