from pyrogram import Client, filters
from pyrogram.types import Message
from shigaraki import app
import config
from pyrogram.enums import MessageEntityType
from shigaraki.decorator.errors import error
from shigaraki.database.common_chat_db import get_common_chat_count
from shigaraki.database.afk_db import is_user_afk
from shigaraki.database.global_actions_db import is_user_gbanned , is_user_gmuted
from shigaraki.database.user_info_db import get_user_infoo
from pyrogram.types import InputMediaPhoto

@app.on_message(filters.command("id", prefixes=config.config.COMMAND_PREFIXES))
@error
async def get_id(client: Client, message: Message):
    """
    Handles the /id command, providing Chat ID and user IDs based on context.
    """
    chat_id = message.chat.id
    user_id = message.from_user.id
    reply = message.reply_to_message
    entities = message.entities
    command_args = message.command[1:] if len(message.command) > 1 else []

    # Base response
    response = [f"**Chat ID:** `{chat_id}`\n", f"**Your ID:** `{user_id}`\n"]

    # Handle replies
    if reply:
        if reply.forward_from_chat:  # Forwarded message
            response.append(
                f"**Forwarded Chat ID:** `{reply.forward_from_chat.id}`\n"
            )
        elif reply.from_user:  # Reply to a user
            response.append(
                f"**Replied User ID:** `{reply.from_user.id}` ({reply.from_user.mention()})\n"
            )

    # Handle text mentions
    if entities:
        for entity in entities:
            if entity.type == MessageEntityType.TEXT_MENTION:
                response.append(
                    f"**Mentioned User ID:** `{entity.user.id}` ({entity.user.mention()})\n"
                )
                break

    # Handle username arguments
    if command_args:
        username = command_args[0].strip("@")
        try:
            user_details = await client.get_users(username)
            response.append(
                f"**Username ID:** `{user_details.id}` ({user_details.mention()})\n"
            )
        except Exception:
            response.append("")

    # Final fallback: default response
    if len(response) == 2:  # No additional info added
        response.append("")

    await message.reply_text("".join(response))


@app.on_message(filters.command("info", prefixes=config.config.COMMAND_PREFIXES))
@error
async def get_user_info(client: Client, message: Message):
    # Determine target user
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        target = message.command[1]
        if target.isdigit():
            user = await client.get_users(int(target))
        else:
            user = await client.get_users(target)
    else:
        user = message.from_user

    x = await message.reply_text("Fetching User Info.")

    # Get user info
    user_id = user.id
    first_name = user.first_name or "N/A"
    last_name = user.last_name or "N/A"
    username = f"@{user.username}" or "N/A"
    mention = user.mention or "N/A"
    dc_id = user.dc_id or "N/A"

    # Fetch full user info for bio
    try:
        full_user = await app.get_chat(user.id)
        bio = full_user.bio or "N/A"
    except Exception:
        bio = "N/A"

    await x.edit_text("Fetching User Info...")

    # Get profile photo
    photo_count = await client.get_chat_photos_count(user_id)
    user_photo = None
    if photo_count > 0:
        async for photo in client.get_chat_photos(user_id, limit=1):
            user_photo = photo.file_id
            break

    # Fetch additional info from database
    user_info = await get_user_infoo(user_id)
    custom_bio = user_info.get("custom_bio", "N/A") if user_info else "N/A"
    custom_title = user_info.get("custom_title", "N/A") if user_info else "N/A"

    # Calculate health
    health = 100
    if username == "N/A":
        health -= 25
    if photo_count == 0:
        health -= 25
    if bio == "N/A":
        health -= 20

    # Generate health bar
    filled_blocks = health // 10
    empty_blocks = 10 - filled_blocks
    health_bar = f"{'▰' * filled_blocks}{'▱' * empty_blocks}"

    await x.edit_text("Fetching User Info.....")
   
    # Prepare caption
    caption = (
        f"     【 **User Information** 】\n"
        f"➢ **ID:** `{user_id}`\n"
        f"➢ **First Name:** `{first_name}`\n"
        f"➢ **Last Name:** `{last_name}`\n"
        f"➢ **Username:** {username if username != 'N/A' else 'No Username'}\n"
        f"➢ **Mention:** {mention}\n"
        f"➢ **DC ID:** `{dc_id}`\n"
        f"➢ **Bio:** `{bio if bio != 'N/A' else 'No Bio Available'}`\n\n"
        f"➢ **Custom Bio:** `{custom_bio}`\n"
        f"➢ **Custom Tag:** `{custom_title}`\n"
        f"➢ **Profile Photos:** `{photo_count} {'Photo' if photo_count == 1 else 'Photos'}`\n"
        f"➢ **Health:** `{health}%`\n"
        f"    {health_bar}\n\n"
    )

    # Additional statuses
    caption += f"➢ **AFK Status:** `{'Currently Away From Keyboard !!' if await is_user_afk(user_id) else 'No'}`\n"
    common_groups = await get_common_chat_count(user_id)
    caption += f"➢ **Common Groups:** `{common_groups}`\n"
    caption += f"➢ **Globally Banned:** `{'Yes' if await is_user_gbanned(user_id) else 'No'}`\n"
    caption += f"➢ **Globally Muted:** `{'Yes' if await is_user_gmuted(user_id) else 'No'}`\n"

    # Send response
    if user_photo:
        await x.edit_media(InputMediaPhoto(
            media=user_photo,
            caption=caption
        ))
    else:
        await x.edit_text(caption)





__module__ = "𝖨𝖣"


__help__ = """**𝖴𝗌𝖾𝗋 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:**
  ✧ `/𝗂𝖽`**:** 𝖣𝗂𝗌𝗉𝗅𝖺𝗒𝗌 𝗒𝗈𝗎𝗋 𝖼𝗁𝖺𝗍 𝖨𝖣 𝖺𝗇𝖽 𝗎𝗌𝖾𝗋 𝖨𝖣.
 
  ✧ `/𝗂𝖽 <𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾>`**:** 𝖣𝗂𝗌𝗉𝗅𝖺𝗒𝗌 𝗍𝗁𝖾 𝖨𝖣 𝗈𝖿 𝗍𝗁𝖾 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖾𝖽 𝗎𝗌𝖾𝗋 (𝖼𝖺𝗌𝖾-𝗂𝗇𝗌𝖾𝗇𝗌𝗂𝗍𝗂𝗏𝖾 𝗌𝖾𝖺𝗋𝖼𝗁) 𝖺𝗅𝗈𝗇𝗀 𝗐𝗂𝗍𝗁 𝗒𝗈𝗎𝗋 𝖼𝗁𝖺𝗍 𝖨𝖣 𝖺𝗇𝖽 𝗎𝗌𝖾𝗋 𝖨𝖣.
 
**𝖱𝖾𝗉𝗅𝗂𝖾𝖽 𝗍𝗈 𝖺 𝖬𝖾𝗌𝗌𝖺𝗀𝖾:**
  ✧ 𝖨𝖿 𝗍𝗁𝖾 𝖼𝗈𝗆𝗆𝖺𝗇𝖽 𝗂𝗌 𝗋𝖾𝗉𝗅𝗂𝖾𝖽 𝗍𝗈 𝖺 𝗎𝗌𝖾𝗋’𝗌 𝗆𝖾𝗌𝗌𝖺𝗀𝖾, 𝗂𝗍 𝗌𝗁𝗈𝗐𝗌 𝗍𝗁𝖾 𝖨𝖣 𝗈𝖿 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋 𝗐𝗁𝗈 𝗂𝗌𝗌𝗎𝖾𝖽 𝗍𝗁𝖾 𝖼𝗈𝗆𝗆𝖺𝗇𝖽, 𝗍𝗁𝖾 𝖨𝖣 𝗈𝖿 𝗍𝗁𝖾 𝗋𝖾𝗉𝗅𝗂𝖾𝖽-𝗍𝗈 𝗎𝗌𝖾𝗋, 𝖺𝗇𝖽 𝗍𝗁𝖾 𝖼𝗁𝖺𝗍 𝖨𝖣.
 
  ✧ 𝖨𝖿 𝗍𝗁𝖾 𝖼𝗈𝗆𝗆𝖺𝗇𝖽 𝗂𝗌 𝗋𝖾𝗉𝗅𝗂𝖾𝖽 𝗍𝗈 𝖺 𝖿𝗈𝗋𝗐𝖺𝗋𝖽𝖾𝖽 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝖿𝗋𝗈𝗆 𝖺𝗇𝗈𝗍𝗁𝖾𝗋 𝖼𝗁𝖺𝗍, 𝗂𝗍 𝗌𝗁𝗈𝗐𝗌 𝗍𝗁𝖾 𝖨𝖣 𝗈𝖿 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋 𝗐𝗁𝗈 𝗂𝗌𝗌𝗎𝖾𝖽 𝗍𝗁𝖾 𝖼𝗈𝗆𝗆𝖺𝗇𝖽 𝖺𝗇𝖽 𝗍𝗁𝖾 𝖨𝖣 𝗈𝖿 𝗍𝗁𝖾 𝖼𝗁𝖺𝗍 𝖿𝗋𝗈𝗆 𝗐𝗁𝗂𝖼𝗁 𝗍𝗁𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗐𝖺𝗌 𝖿𝗈𝗋𝗐𝖺𝗋𝖽𝖾𝖽.
 
𝖴𝗌𝖾 𝗍𝗁𝖾𝗌𝖾 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌 𝗍𝗈 𝗀𝖾𝗍 𝗎𝗌𝖾𝗋 𝖺𝗇𝖽 𝖼𝗁𝖺𝗍 𝖨𝖣𝗌 𝖿𝗈𝗋 𝗏𝖺𝗋𝗂𝗈𝗎𝗌 𝗉𝗎𝗋𝗉𝗈𝗌𝖾𝗌.
 """