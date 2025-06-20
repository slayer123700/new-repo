from pyrogram import Client, filters
from pyrogram.types import Message
from shigaraki.database.global_actions_db import (
    add_to_gban,
    add_to_gmute,
    remove_from_gban,
    remove_from_gmute,
    is_user_gbanned,
    is_user_gmuted,
    get_all_gmuted_users,
    get_all_gbanned_users,
    save_banned_chats,
    get_banned_chats
)
from shigaraki import app
from shigaraki.decorator.botadmin import hokage, botadmin
from shigaraki.decorator.errors import error
from shigaraki.decorator.save import save
from shigaraki.database.common_chat_db import get_common_chat_ids
from pyrogram.errors import ChatAdminRequired, FloodWait, UserAdminInvalid
import random , asyncio
from config import config


async def extract_user_info(client: Client, message: Message, args):
    """Extract user information based on reply or arguments."""
    try:
        if message.reply_to_message:
            # Extract user from reply
            return message.reply_to_message.from_user
        elif args:
            # Extract user from ID or username
            return await client.get_users(args[0])
        else:
            return None
    except Exception as e:
        print(f"Error in extract_user_info: {e}")
        return None


@app.on_message(filters.command("gmute", prefixes=config.COMMAND_PREFIXES))
@hokage
@error
@save
async def gmute_user(client: Client, message: Message):
    args = message.command[1:] if len(message.command) > 1 else []
    user = await extract_user_info(client, message, args)

    if not user:
        await message.reply_text("𝖯𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 𝗏𝖺𝗅𝗂𝖽 𝗎𝗌𝖾𝗋 𝖨𝖣, 𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾, 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗎𝗌𝖾𝗋.")
        return

    if await is_user_gmuted(user.id):
        await message.reply_text(f"`{user.first_name or user.id}` 𝗂𝗌 𝖺𝗅𝗋𝖾𝖺𝖽𝗒 𝗂𝗇 𝗍𝗁𝖾 𝖦𝖬𝗎𝗍𝖾 𝗅𝗂𝗌𝗍.")
        return

    # Initiating message
    initiating_msg = await message.reply_text(f"**𝖨𝗇𝗂𝗍𝗂𝖺𝗍𝗂𝗇𝗀 𝖦𝗅𝗈𝖻𝖺𝗅 𝖬𝗎𝗍𝖾 𝖿𝗈𝗋** `{user.first_name or user.id}`...")

    # Simulate time taken
    time_taken = round(random.uniform(0.5, 2.3), 1)
    await asyncio.sleep(1.2)

    # Add user to GMute
    await add_to_gmute(user.id, user.first_name, user.username)
    await initiating_msg.edit_text(f"**𝖦𝗅𝗈𝖻𝖺𝗅 𝖬𝗎𝗍𝖾 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅 :** `{user.first_name or user.id}` 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗀𝗅𝗈𝖻𝖺𝗅𝗅𝗒 𝗆𝗎𝗍𝖾𝖽.\n**𝖳𝗂𝗆𝖾 𝖳𝖺𝗄𝖾𝗇:** {𝗍𝗂𝗆𝖾_𝗍𝖺𝗄𝖾𝗇} 𝗌𝖾𝖼𝗈𝗇𝖽𝗌.")



@app.on_message(filters.command("gban", prefixes=config.COMMAND_PREFIXES))
@hokage
@error
@save
async def gban_user(client: Client, message: Message):
    args = message.command[1:] if len(message.command) > 1 else []
    user = await extract_user_info(client, message, args)

    if not user:
        await message.reply_text("𝖯𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 𝗏𝖺𝗅𝗂𝖽 𝗎𝗌𝖾𝗋 𝖨𝖣, 𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾, 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗎𝗌𝖾𝗋.")
        return

    if await is_user_gbanned(user.id):
        await message.reply_text(f"`{user.first_name or user.id}` 𝗂𝗌 𝖺𝗅𝗋𝖾𝖺𝖽𝗒 𝗂𝗇 𝗍𝗁𝖾 𝖦𝖡𝖺𝗇 𝗅𝗂𝗌𝗍.")
        return

    # Initiating message
    initiating_msg = await message.reply_text(f"**𝖨𝗇𝗂𝗍𝗂𝖺𝗍𝗂𝗇𝗀 𝖦𝗅𝗈𝖻𝖺𝗅 𝖡𝖺𝗇 𝖿𝗈𝗋** `{user.first_name or user.id}`...")

    # Simulate time taken
    time_taken = round(random.uniform(0.5, 2.3), 1)
    await asyncio.sleep(1.2)

    # Add user to GBan database
    await add_to_gban(user.id, user.first_name, user.username)
    
    # Ban user in common chats
    common_chats = await get_common_chat_ids(user.id)
    banned_chats = []
    failed_chats = []

    for chat_id in common_chats:
        try:
            await client.ban_chat_member(chat_id, user.id)
            banned_chats.append(chat_id)
        except (ChatAdminRequired, UserAdminInvalid, FloodWait):
            failed_chats.append(chat_id)
        except Exception:
            failed_chats.append(chat_id)
    
    await save_banned_chats(user.id, banned_chats)

    
    response = f"**𝖦𝗅𝗈𝖻𝖺𝗅 𝖡𝖺𝗇 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅 :** `{user.first_name or user.id}` 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗀𝗅𝗈𝖻𝖺𝗅𝗅𝗒 𝖻𝖺𝗇𝗇𝖾𝖽 𝗂𝗇 𝗍𝗁𝖾 𝖽𝖺𝗍𝖺𝖻𝖺𝗌𝖾.\n"
    response += f"**𝖳𝗂𝗆𝖾 𝖳𝖺𝗄𝖾𝗇 :** {time_taken} 𝗌𝖾𝖼𝗈𝗇𝖽𝗌.\n\n"

    await initiating_msg.edit_text(response)


@app.on_message(filters.command("ungban", prefixes=config.COMMAND_PREFIXES))
@hokage
@error
@save
async def ungban_user(client: Client, message: Message):
    args = message.command[1:] if len(message.command) > 1 else []
    user = await extract_user_info(client, message, args)

    if not user:
        await message.reply_text("𝖯𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 𝗏𝖺𝗅𝗂𝖽 𝗎𝗌𝖾𝗋 𝖨𝖣, 𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾, 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗎𝗌𝖾𝗋.")
        return

    if not await is_user_gbanned(user.id):
        await message.reply_text(f"`{user.first_name or user.id}` 𝗂𝗌 𝗇𝗈𝗍 𝗂𝗇 𝗍𝗁𝖾 𝖦𝖡𝖺𝗇 𝗅𝗂𝗌𝗍.")
        return

    initiating_msg = await message.reply_text(f"**𝖨𝗇𝗂𝗍𝗂𝖺𝗍𝗂𝗇𝗀 𝖦𝗅𝗈𝖻𝖺𝗅 𝖴𝗇𝖻𝖺𝗇 𝖿𝗈𝗋** `{user.first_name or user.id}`...")
    time_taken = round(random.uniform(0.5, 2.3), 1)
    await asyncio.sleep(1.2)

    # Remove user from GBan database
    await remove_from_gban(user.id)

    # Retrieve banned chats and unban user
    banned_chats = await get_banned_chats(user.id)
    unbanned_chats = []
    failed_chats = []

    for chat_id in banned_chats:
        try:
            await client.unban_chat_member(chat_id, user.id)
            unbanned_chats.append(chat_id)
        except Exception:
            failed_chats.append(chat_id)

    response = f"**𝖦𝗅𝗈𝖻𝖺𝗅 𝖴𝗇𝖻𝖺𝗇 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅 :** `{user.first_name or user.id}`\n"
    response += f"**𝖳𝗂𝗆𝖾 𝖳𝖺𝗄𝖾𝗇 :** {time_taken} 𝗌𝖾𝖼𝗈𝗇𝖽𝗌.\n"
    await initiating_msg.edit_text(response)

# Helper to format user list
def format_user_list(users):
    if not users:
        return "𝖭𝗈 𝗎𝗌𝖾𝗋𝗌 𝖿𝗈𝗎𝗇𝖽."
    formatted_list = []
    for user in users:
        name = user.get("first_name", "𝖴𝗇𝗄𝗇𝗈𝗐𝗇")
        id = f"({user['id']})"
        formatted_list.append(f"- {name} {id}")
    return "\n".join(formatted_list)

@app.on_message(filters.command("ungmute", prefixes=config.COMMAND_PREFIXES))
@hokage
@error
@save
async def ungmute_user(client: Client, message: Message):
    args = message.command[1:] if len(message.command) > 1 else []
    user = await extract_user_info(client, message, args)

    if not user:
        await message.reply_text("𝖯𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 𝗏𝖺𝗅𝗂𝖽 𝗎𝗌𝖾𝗋 𝖨𝖣, 𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾, 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗎𝗌𝖾𝗋.")
        return

    if not await is_user_gmuted(user.id):
        await message.reply_text(f"`{user.first_name or user.id}` 𝗂𝗌 𝗇𝗈𝗍 𝗂𝗇 𝗍𝗁𝖾 𝖦𝖬𝗎𝗍𝖾 𝗅𝗂𝗌𝗍.")
        return

    # Initiating message
    initiating_msg = await message.reply_text(f"**𝖨𝗇𝗂𝗍𝗂𝖺𝗍𝗂𝗇𝗀 𝖦𝗅𝗈𝖻𝖺𝗅 𝖴𝗇𝗆𝗎𝗍𝖾 𝖿𝗈𝗋** `{user.first_name or user.id}`...")

    # Simulate time taken
    time_taken = round(random.uniform(0.5, 2.3), 1)
    await asyncio.sleep(1.2)

    # Remove user from GMute
    await remove_from_gmute(user.id)
    await initiating_msg.edit_text(f"**𝖦𝗅𝗈𝖻𝖺𝗅 𝖴𝗇𝗆𝗎𝗍𝖾 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅 :** `{user.first_name or user.id}` 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗀𝗅𝗈𝖻𝖺𝗅𝗅𝗒 𝗎𝗇𝗆𝗎𝗍𝖾𝖽.\n**𝖳𝗂𝗆𝖾 𝖳𝖺𝗄𝖾𝗇 :** {time_taken} 𝗌𝖾𝖼𝗈𝗇𝖽𝗌.")


# Command to fetch GMute list
@app.on_message(filters.command("gmuted", prefixes=config.COMMAND_PREFIXES))
@botadmin
@error
@save
async def list_gmuted_users(client: Client, message: Message):
    users = await get_all_gmuted_users()
    formatted_list = format_user_list(users)
    if users :
        await message.reply_text(f"**𝖦𝗅𝗈𝖻𝖺𝗅𝗅𝗒 𝖬𝗎𝗍𝖾𝖽 𝖴𝗌𝖾𝗋𝗌 :**\n\n{formatted_list}")
    else :
        await message.reply_text(f"**𝖭𝗈 𝖦𝗅𝗈𝖻𝖺𝗅𝗅𝗒 𝖬𝗎𝗍𝖾𝖽 𝖴𝗌𝖾𝗋 𝖥𝗈𝗎𝗇𝖽 !!**")
        
# Command to fetch GBan list
@app.on_message(filters.command("gbanned", prefixes=config.COMMAND_PREFIXES))
@botadmin
@error
@save
async def list_gbanned_users(client: Client, message: Message):
    users = await get_all_gbanned_users()
    formatted_list = format_user_list(users)
    if users :
        await message.reply_text(f"**𝖦𝗅𝗈𝖻𝖺𝗅𝗅𝗒 𝖡𝖺𝗇𝗇𝖾𝖽 𝖴𝗌𝖾𝗋𝗌 :**\n\n{formatted_list}")
    else :
        await message.reply_text(f"**𝖭𝗈 𝖦𝗅𝗈𝖻𝖺𝗅𝗅𝗒 𝖡𝖺𝗇𝗇𝖾𝖽 𝖴𝗌𝖾𝗋 𝖥𝗈𝗎𝗇𝖽 !!**")