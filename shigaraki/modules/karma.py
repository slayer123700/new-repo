from shigaraki.database import karma_db
from pyrogram import Client, filters
from pyrogram.types import Message
from shigaraki import app
import config 

@app.on_message(filters.command("karma", prefixes=config.config.COMMAND_PREFIXES) & filters.group)
async def show_karma(client: Client, message: Message):
    """Show the karma points of a user."""
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Get the user's karma points
    user_karma = await karma_db.get_karma(user_id, chat_id)
    await message.reply_text(f"Your current karma points is  **{user_karma}** ")

@app.on_message(filters.command("topkarma", prefixes=config.config.COMMAND_PREFIXES) & filters.group)
async def show_top_karma(client: Client, message: Message):
    """Show the top users with the highest karma in the group."""
    chat_id = message.chat.id

    # Get the top karma users
    top_users = await karma_db.top_karma(chat_id)
    if not top_users:
        await message.reply_text("No karma data available for this group.")
        return

    leaderboard = "\n".join(
        [f"**{i + 1}.** {user['user_name']} ({user['user_id']}) -: **{user['karma']}** Points" for i, user in enumerate(top_users)]
    )
    await message.reply_text(f"🏆 **Top Karma Users in this Group**\n\n{leaderboard}")

@app.on_message(filters.regex(
        r"^(?i)(\+|\+\+|\+1|thx|tnx|ty|tq|thank you|thanx|thanks|pro|cool|good|agree|makasih|👍|\+\+ .+)$"
    ) & filters.group & filters.reply)
async def increase_karma_handler(client: Client, message: Message):
    target_user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    name = message.reply_to_message.from_user.first_name

    # Increase the target user's karma points
    await karma_db.increase_karma(target_user_id, name , chat_id)
    await message.reply_text(f"Increased karma for **{message.reply_to_message.from_user.mention}**")

@app.on_message(filters.regex(r"^(?i)(-|--|-1|not cool|disagree|worst|bad|👎|-- .+)$") & filters.group & filters.reply)
async def decrease_karma_handler(client: Client, message: Message):

    target_user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    name = message.reply_to_message.from_user.first_name

    # Decrease the target user's karma points
    await karma_db.decrease_karma(target_user_id, name , chat_id)
    await message.reply_text(f"Decreased karma for **{message.reply_to_message.from_user.mention}**")
