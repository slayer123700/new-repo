from shigaraki.database import couple_collection , waifu_collection
from datetime import datetime
from pytz import timezone

# Define IST timezone
IST = timezone('Asia/Kolkata')

async def save_couple(chat_id: int, couple_id: int, couple_first_name: str , couple_id_2 : int , couple_first_name_2 : str):
    """Save the couple details in the database."""
    date_chosen = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "chat_id": chat_id,
        "couple_id": couple_id,
        "couple_first_name": couple_first_name,
        "couple_id_2" : couple_id_2,
        "couple_first_name_2" : couple_first_name_2,
        "date": date_chosen
    }
    await couple_collection.update_one(
        {"chat_id": chat_id},
        {"$set": data},
        upsert=True
    )

async def is_couple_already_chosen(chat_id: int) -> bool:
    """Check if a couple is already chosen for the given chat."""
    couple = await couple_collection.find_one({"chat_id": chat_id})
    return couple is not None

async def get_couple(chat_id: int) -> dict:
    """Get the couple details for the given chat."""
    return await couple_collection.find_one({"chat_id": chat_id})

async def remove_couple(chat_id: int):
    """Remove the couple details from the database."""
    await couple_collection.delete_one({"chat_id": chat_id})

async def get_all_couples() -> list:
    """Get all saved couples from the database."""
    return await couple_collection.find().to_list(length=1000)

async def save_waifu(chat_id: int, user_id: int, user_first_name: str, bond: str, waifu_id: int, waifu_first_name: str, waifu_photo: str = None):
    """Save the waifu details in the database for a specific chat and user."""
    date_chosen = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "chat_id": chat_id,
        "user_id": user_id,
        "user_first_name": user_first_name,
        "waifu_id": waifu_id,
        "waifu_first_name": waifu_first_name,
        "waifu_photo": waifu_photo,
        "bond": bond,
        "date": date_chosen
    }
    await waifu_collection.update_one(
        {"chat_id": chat_id, "user_id": user_id},  # Use both chat_id and user_id as unique identifiers
        {"$set": data},
        upsert=True  # Insert a new document if none exists
    )


async def is_waifu_already_chosen(user_id: int) -> bool:
    """Check if a couple is already chosen for the given chat."""
    couple = await waifu_collection.find_one({"user_id": user_id})
    return couple is not None

async def get_waifu(user_id: int) -> dict:
    """Get the couple details for the given chat."""
    return await waifu_collection.find_one({"user_id": user_id})
