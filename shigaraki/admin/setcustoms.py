from pyrogram import Client, filters
from pyrogram.types import Message
from shigaraki.database.user_info_db import save_user_info
from shigaraki import app
from shigaraki.decorator.botadmin import genin


@app.on_message(filters.command("settag"))
@genin
async def set_custom_title(client: Client, message: Message):
    if not message.reply_to_message and len(message.command) < 3:
        await message.reply_text("Usage: /settag (username/user_id) (custom_tag) or reply to a user's message with /settag (custom_tag)")
        return

    if message.reply_to_message:
        user = message.reply_to_message.from_user
        custom_title = " ".join(message.command[1:])
    else:
        user_id_or_username = message.command[1]
        custom_title = " ".join(message.command[2:])
        user = await client.get_users(user_id_or_username)

    user_id = user.id

    # Save the custom title
    await save_user_info(user_id=user_id, custom_title=custom_title)
    await message.reply_text(f"Custom title set for {user.first_name}.")

@app.on_message(filters.command("setbio"))
@genin
async def set_custom_bio(client: Client, message: Message):
    if not message.reply_to_message and len(message.command) < 3:
        await message.reply_text("Usage: /setbio (username/user_id) (custom_bio) or reply to a user's message with /setbio (custom_bio)")
        return

    if message.reply_to_message:
        user = message.reply_to_message.from_user
        custom_bio = " ".join(message.command[1:])
    else:
        user_id_or_username = message.command[1]
        custom_bio = " ".join(message.command[2:])
        user = await client.get_users(user_id_or_username)

    user_id = user.id

    # Save the custom bio
    await save_user_info(user_id=user_id, custom_bio=custom_bio)
    await message.reply_text(f"Custom bio set for {user.first_name}.")
