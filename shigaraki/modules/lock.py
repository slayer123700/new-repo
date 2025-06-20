from telegram import Update, ChatPermissions, MessageEntity
from telegram.ext import CallbackQueryHandler, MessageHandler, filters
from telegram.ext import ContextTypes
from shigaraki.database.lockdb import (
    set_lock,
    unset_lock,
    get_locks,
)
from shigaraki.database.approve_db import is_user_approved
from shigaraki.helper.user import is_user_admin
from shigaraki import ptb , LOCK_GROUP
from shigaraki.helper.handler import MultiCommandHandler
from shigaraki.helper.lock_helper import LOCK_CHAT_RESTRICTION, LOCKABLES, UNLOCK_CHAT_RESTRICTION
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatMemberStatus


async def lock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /lock command to enable locks."""
    chat = update.effective_chat
    user = update.effective_user  # Assign user directly, even if None

    # Check if user exists
    if not user:
        return  # Exit if no user is associated with the update

    if not await is_user_admin(update, context, user.id):
        await update.message.reply_text("🚫 *Access Denied:* Only admins can configure locks.", parse_mode="Markdown")
        return

    lock_types = [lock_type.lower() for lock_type in context.args]  # Convert input to lowercase
    if not lock_types:
        await update.message.reply_text("⚙️ *Usage:* Specify the lock type(s) to enable.\n"
                                        f"Example: `/lock all` or `/lock audio video`", parse_mode="Markdown")
        return

    for lock_type in lock_types:
        if lock_type not in LOCKABLES:
            await update.message.reply_text(f"⚠️ Invalid lock type: `{lock_type}`\n"
                                            f"Use `/locktypes` to view available lock types.", parse_mode="Markdown")
            return

        await set_lock(chat.id, lock_type)

        if lock_type == "all":
            permissions = ChatPermissions(**LOCK_CHAT_RESTRICTION["all"])
            await context.bot.set_chat_permissions(chat.id, permissions)

    await update.message.reply_text(f"🔒 *Locked:* {', '.join(lock_types)}", parse_mode="Markdown")



async def unlock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /unlock command to disable locks."""
    chat = update.effective_chat
    user = update.effective_user  # Assign user directly, even if None

    # Check if user exists
    if not user:
        return  # Exit if no user is associated with the update

    if not await is_user_admin(update, context, user.id):
        await update.message.reply_text("🚫 *Access Denied:* Only admins can configure locks.", parse_mode="Markdown")
        return

    lock_types = context.args
    if not lock_types:
        await update.message.reply_text("⚙️ *Usage:* Specify the lock type(s) to disable.\n"
                                        f"Example: `/unlock all` or `/unlock audio video`", parse_mode="Markdown")
        return

    for lock_type in lock_types:
        if lock_type not in LOCKABLES:
            await update.message.reply_text(f"⚠️ Invalid unlock type: `{lock_type}`\n"
                                            f"Use `/locktypes` to view available lock types.", parse_mode="Markdown")
            return

        await unset_lock(chat.id, lock_type)

        if lock_type == "all":
            permissions = ChatPermissions(**UNLOCK_CHAT_RESTRICTION["all"])
            await context.bot.set_chat_permissions(chat.id, permissions)

    await update.message.reply_text(f"🔓 *Unlocked:* {', '.join(lock_types)}", parse_mode="Markdown")


async def locktypes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /locktypes to list all lockable types with inline buttons."""
    lockables = list(LOCKABLES.items())

    # Create rows of 3 buttons each
    keyboard = [
        [
            InlineKeyboardButton(
                text=lock_type.capitalize(),
                callback_data=f"locktype_{lock_type}"
            )
            for lock_type, _ in lockables[i:i + 3]
        ]
        for i in range(0, len(lockables), 3)
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📜 *Available Lock Types:*\nTap a button to view the description.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def locktype_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show lock type description when an inline button is clicked."""
    query = update.callback_query

    # Extract lock type from callback data
    lock_type = query.data.split("_", 1)[1]
    description = LOCKABLES.get(lock_type, "No description available.")    

    await query.answer(
        text=f"🔒 {lock_type.capitalize()} Lock:\n{description}",
        show_alert=True        
    )
    

async def locks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /locks to view active locks in the chat."""
    chat = update.effective_chat
    locks = await get_locks(chat.id)
    if not locks:
        await update.message.reply_text("🔓 *No locks are currently enabled in this chat.*", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"🔒 *Active Locks:*\n`{', '.join(locks)}`", parse_mode="Markdown")


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete messages violating locks."""
    chat = update.effective_chat
    user = update.effective_user  # Assign user directly, even if None

    # Get active locks
    locks = await get_locks(chat.id)
    if not locks:
        return

    # Check if user exists
    if not user:
        return  # Exit if no user is associated with the update

    # Ignore admin messages
    if await is_user_admin(update, context, user.id):
        return
 
    if await is_user_approved(chat.id , user.id):
        return



    msg = update.effective_message
    to_delete = False

    # Check lock conditions
    if "all" in locks:
        to_delete = True  # "all" locks everything

    if "album" in locks and (msg.media_group_id is not None):
        to_delete = True
    if "anonchannel" in locks and (msg.sender_chat and not msg.sender_chat.is_forum):
        to_delete = True
    if "audio" in locks and msg.audio:
        to_delete = True
    if "bot" in locks and msg.via_bot:
        to_delete = True
    if "botlink" in locks and (
        any(ent.type == MessageEntity.MENTION for ent in msg.entities or [])
        and "bot" in msg.text.lower()
    ):
        to_delete = True
    if "btn" in locks and msg.reply_markup:
        to_delete = True
    if "cjk" in locks and msg.text and any(
        ord(c) >= 0x4E00 and ord(c) <= 0x9FFF for c in msg.text
    ):
        to_delete = True
    if "command" in locks and msg.text and msg.text.startswith("/"):
        to_delete = True
    if "contact" in locks and msg.contact:
        to_delete = True
    if "cyrillic" in locks and msg.text and any(
        ord(c) in range(0x0400, 0x04FF) for c in msg.text
    ):
        to_delete = True
    if "document" in locks and msg.document:
        to_delete = True
    if "email" in locks and (
        any(ent.type == MessageEntity.EMAIL for ent in msg.entities or [])
    ):
        to_delete = True
    if "emoji" in locks and msg.text and any(
        ord(c) > 0x1F600 for c in msg.text if ord(c) < 0x1F64F
    ):
        to_delete = True
    if "emoji_custom" in locks and (
        any(ent.type == MessageEntity.CUSTOM_EMOJI for ent in msg.entities or [])
    ):
        to_delete = True
    if "dice" in locks and msg.dice:
        to_delete = True
    if "external_reply" in locks and msg.reply_to_message:
        try:
            chat_member = await context.bot.get_chat_member(chat.id, msg.reply_to_message.from_user.id)
            if chat_member.status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED):
                to_delete = True
        except Exception as e:
            to_delete = True
    if "forward" in locks and filters.FORWARDED.filter(msg):  # Use `.filter()` method
        to_delete = True
    if "game" in locks and msg.game:
        to_delete = True
    if "gif" in locks and msg.animation:
        to_delete = True
    if "inline" in locks and msg.via_bot:
        to_delete = True
    if "invitelink" in locks and (
        any(ent.type == MessageEntity.MENTION for ent in msg.entities or [])
        or any(ent.type == MessageEntity.URL for ent in msg.entities or [])
    ):
        to_delete = True
    if "location" in locks and msg.location:
        to_delete = True
    if "phone" in locks and (
        any(ent.type == MessageEntity.PHONE_NUMBER for ent in msg.entities or [])
    ):
        to_delete = True
    if "photo" in locks and msg.photo:
        to_delete = True
    if "poll" in locks and msg.poll:
        to_delete = True
    if "rtl" in locks and msg.text and any(
        ord(c) in range(0x0590, 0x08FF) for c in msg.text
    ):
        to_delete = True
    if "spoiler" in locks and (
        any(ent.type == MessageEntity.SPOILER for ent in msg.entities or [])
    ):
        to_delete = True
    if "sticker" in locks and msg.sticker:
        to_delete = True
    if "animated_sticker" in locks and msg.sticker and msg.sticker.is_animated:
        to_delete = True
    if "premium_sticker" in locks and msg.sticker and msg.sticker.premium_animation:
        to_delete = True
    if "text" in locks and msg.text:
        to_delete = True
    if "url" in locks and (
        any(ent.type == MessageEntity.URL for ent in msg.entities or [])
        or any(ent.type == MessageEntity.URL for ent in msg.caption_entities or [])
    ):  # Added check for `caption_entities`
        to_delete = True
    if "video" in locks and msg.video:
        to_delete = True
    if "videonote" in locks and msg.video_note:
        to_delete = True
    if "voice" in locks and msg.voice:
        to_delete = True

    # Delete the message if any lock condition matches
    if to_delete:
        try:
            await msg.delete()
        except Exception as e:
            await update.message.reply_text(
                "⚠️ *Unable to delete message. Please ensure I have the required permissions.*",
                parse_mode="Markdown"
            )



locktype_desc_handler = CallbackQueryHandler(locktype_description, pattern=r"^locktype_")

# Register handlers
ptb.add_handler(MultiCommandHandler("lock", lock_command))
ptb.add_handler(MultiCommandHandler("unlock", unlock_command))
ptb.add_handler(MultiCommandHandler("locktypes", locktypes_command))
ptb.add_handler(MultiCommandHandler("locks", locks_command))
ptb.add_handler(MessageHandler(filters.ALL & ~filters.StatusUpdate.ALL, message_handler), group=LOCK_GROUP)
ptb.add_handler(locktype_desc_handler)


__module__ = "𝖫𝗈𝖼𝗄𝗌"

__help__ = """🔒 **𝖫𝗈𝖼𝗄𝗌 𝖬𝗈𝖽𝗎𝗅𝖾**:
𝖬𝖺𝗇𝖺𝗀𝖾 𝖼𝗁𝖺𝗍 𝗋𝖾𝗌𝗍𝗋𝗂𝖼𝗍𝗂𝗈𝗇𝗌 𝖾𝖿𝖿𝖾𝖼𝗍𝗂𝗏𝖾𝗅𝗒. 𝖫𝗈𝖼𝗄 𝗈𝗋 𝗎𝗇𝗅𝗈𝖼𝗄 𝗏𝖺𝗋𝗂𝗈𝗎𝗌 𝗍𝗒𝗉𝖾𝗌 𝗈𝖿 𝖼𝗈𝗇𝗍𝖾𝗇𝗍 𝗂𝗇 𝗍𝗁𝖾 𝖼𝗁𝖺𝗍.
 
**𝖠𝗏𝖺𝗂𝗅𝖺𝖻𝗅𝖾 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌**:
- `/𝗅𝗈𝖼𝗄 <𝗍𝗒𝗉𝖾(𝗌)>` - 𝖤𝗇𝖺𝖻𝗅𝖾 𝗅𝗈𝖼𝗄𝗌 𝖿𝗈𝗋 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖼 𝖼𝗈𝗇𝗍𝖾𝗇𝗍 𝗍𝗒𝗉𝖾𝗌 (𝖾.𝗀., `/𝗅𝗈𝖼𝗄 𝗉𝗁𝗈𝗍𝗈`).
   - 𝖴𝗌𝖾 `/𝗅𝗈𝖼𝗄 𝖺𝗅𝗅` 𝗍𝗈 𝖾𝗇𝖺𝖻𝗅𝖾 𝖺𝗅𝗅 𝗅𝗈𝖼𝗄𝗌.
 - `/𝗎𝗇𝗅𝗈𝖼𝗄 <𝗍𝗒𝗉𝖾(𝗌)>` - 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝗅𝗈𝖼𝗄𝗌 𝖿𝗈𝗋 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖼 𝖼𝗈𝗇𝗍𝖾𝗇𝗍 𝗍𝗒𝗉𝖾𝗌 (𝖾.𝗀., `/𝗎𝗇𝗅𝗈𝖼𝗄 𝗏𝗂𝖽𝖾𝗈`).
   - 𝖴𝗌𝖾 `/𝗎𝗇𝗅𝗈𝖼𝗄 𝖺𝗅𝗅` 𝗍𝗈 𝖽𝗂𝗌𝖺𝖻𝗅𝖾 𝖺𝗅𝗅 𝗅𝗈𝖼𝗄𝗌.
 - `/𝗅𝗈𝖼𝗄𝗍𝗒𝗉𝖾𝗌` - 𝖵𝗂𝖾𝗐 𝖺𝗅𝗅 𝗅𝗈𝖼𝗄𝖺𝖻𝗅𝖾 𝖼𝗈𝗇𝗍𝖾𝗇𝗍 𝗍𝗒𝗉𝖾𝗌 𝖺𝗇𝖽 𝗍𝗁𝖾𝗂𝗋 𝖽𝖾𝗌𝖼𝗋𝗂𝗉𝗍𝗂𝗈𝗇𝗌.
 - `/𝗅𝗈𝖼𝗄𝗌` - 𝖢𝗁𝖾𝖼𝗄 𝖼𝗎𝗋𝗋𝖾𝗇𝗍𝗅𝗒 𝖺𝖼𝗍𝗂𝗏𝖾 𝗅𝗈𝖼𝗄𝗌 𝗂𝗇 𝗍𝗁𝖾 𝖼𝗁𝖺𝗍.
 
**𝖴𝗌𝖺𝗀𝖾 𝖤𝗑𝖺𝗆𝗉𝗅𝖾𝗌**:
- `/𝗅𝗈𝖼𝗄 𝗉𝗁𝗈𝗍𝗈 𝗏𝗂𝖽𝖾𝗈` - 𝖱𝖾𝗌𝗍𝗋𝗂𝖼𝗍 𝗎𝗌𝖾𝗋𝗌 𝖿𝗋𝗈𝗆 𝗌𝖾𝗇𝖽𝗂𝗇𝗀 𝗉𝗁𝗈𝗍𝗈𝗌 𝖺𝗇𝖽 𝗏𝗂𝖽𝖾𝗈𝗌.
 - `/𝗎𝗇𝗅𝗈𝖼𝗄 𝗍𝖾𝗑𝗍 𝖼𝗈𝗆𝗆𝖺𝗇𝖽` - 𝖠𝗅𝗅𝗈𝗐 𝗍𝖾𝗑𝗍 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖺𝗇𝖽 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌.
 
"""

