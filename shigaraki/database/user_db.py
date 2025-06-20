from shigaraki.database import user_collection
from typing import Optional

# Function to save user information
async def save_user(user_id: int, first_name: str, last_name: Optional[str], username: Optional[str]):
    """
    Save or update user data in MongoDB.
    """
    query = {"user_id": user_id}
    update = {
        "$set": {
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
        }
    }
    await user_collection.update_one(query, update, upsert=True)

# Function to get user information by username
async def get_user_by_username(username: str) -> Optional[dict]:
    """
    Retrieve user data by username from MongoDB.
    """
    query = {"username": username}
    user = await user_collection.find_one(query)
    return user

# Function to get user information by user ID
async def get_user_by_user_id(user_id: int) -> Optional[dict]:
    """
    Retrieve user data by user ID from MongoDB.
    """
    query = {"user_id": user_id}
    user = await user_collection.find_one(query)
    return user

async def get_interacted_user_count():
    """
    Get the total number of users stored in the database.
    
    Returns:
        int: The total count of users.
    """
    count = await user_collection.count_documents({})
    return count
