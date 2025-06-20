from shigaraki.database import info_collection


async def save_user_info(user_id: int, custom_bio: str = None, custom_title: str = None):

    user_data = {
        "user_id": user_id,
        "custom_bio": custom_bio,
        "custom_title": custom_title,
    }
    await info_collection.update_one(
        {"user_id": user_id},
        {"$set": user_data},
        upsert=True
    )

async def get_user_infoo(user_id: int):

    return await info_collection.find_one({"user_id": user_id})

async def delete_user_info(user_id: int):

    await info_collection.delete_one({"user_id": user_id})

async def get_all_user_info():

    return await info_collection.find().to_list(None)
