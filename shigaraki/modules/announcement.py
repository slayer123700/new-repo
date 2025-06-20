from shigaraki import app as pgram
from shigaraki.database.announcementdb import (
    enable_announcements,
    disable_announcements,
    is_announcements_enabled,
)
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.types import ChatMemberUpdated, Message
from pyrogram.enums import ChatMemberStatus , ParseMode
from shigaraki.decorator.chatadmin import chatadmin
from config import config 
from shigaraki.helper.log_helper import send_log, format_log  # Import logging functions
from shigaraki.decorator.errors import error
from shigaraki.decorator.save import save

# Command to toggle announcement status
@pgram.on_message(filters.command("announcement" , prefixes=config.COMMAND_PREFIXES) & filters.group)
@chatadmin
@error
@save
async def announcement_handler(client: Client, message: Message):
    chat_id = message.chat.id
        
    if await is_announcements_enabled(chat_id):
        # If already enabled, send a button to disable
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔴 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖠𝗇𝗇𝗈𝗎𝗇𝖼𝖾𝗆𝖾𝗇𝗍𝗌", callback_data=f"disable_announcements:{chat_id}")],
            [InlineKeyboardButton("🗑️", callback_data="delete")]]
        )
        await message.reply_text("**📢 𝖠𝗇𝗇𝗈𝗎𝗇𝖼𝖾𝗆𝖾𝗇𝗍𝗌 𝖺𝗋𝖾 𝖾𝗇𝖺𝖻𝗅𝖾𝖽 𝗂𝗇 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**", reply_markup=button)
    else:
        # If not enabled, send a button to enable
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🟢 𝖤𝗇𝖺𝖻𝗅𝖾 𝖠𝗇𝗇𝗈𝗎𝗇𝖼𝖾𝗆𝖾𝗇𝗍𝗌", callback_data=f"enable_announcements:{chat_id}")],
            [InlineKeyboardButton("🗑️", callback_data="delete")]]
             
        )
        await message.reply_text("**📢 𝖠𝗇𝗇𝗈𝗎𝗇𝖼𝖾𝗆𝖾𝗇𝗍𝗌 𝖺𝗋𝖾 𝖽𝗂𝗌𝖺𝖻𝗅𝖾𝖽 𝗂𝗇 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**", reply_markup=button)
        # Log the command usage
    log_message = await format_log(
        action="Toggle Announcements Command Used",
        chat=message.chat.title or str(chat_id),
        admin=message.from_user.mention
    )
    await send_log(chat_id, log_message)


# Callback query handler to enable/disable announcements
@pgram.on_callback_query(filters.regex("^(enable_announcements|disable_announcements):"))
@chatadmin
@error
async def toggle_announcements(client: Client, callback_query):
    action, chat_id = callback_query.data.split(":")
    chat_id = int(chat_id)
    chat = await client.get_chat(chat_id)

    if action == "enable_announcements":
        await enable_announcements(chat_id, chat.title, chat.username)
        await callback_query.message.edit_text("**🟢 𝖠𝗇𝗇𝗈𝗎𝗇𝖼𝖾𝗆𝖾𝗇𝗍𝗌 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝖾𝗇𝖺𝖻𝗅𝖾𝖽 𝖿𝗈𝗋 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**")

        # Log the action
        log_message = await format_log(
            action="Announcements Enabled",
            chat=chat.title or str(chat_id),
            admin=callback_query.from_user.mention
        )

    elif action == "disable_announcements":
        await disable_announcements(chat_id)
        await callback_query.message.edit_text("**🔴 𝖠𝗇𝗇𝗈𝗎𝗇𝖼𝖾𝗆𝖾𝗇𝗍𝗌 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝖽𝗂𝗌𝖺𝖻𝗅𝖾𝖽 𝖿𝗈𝗋 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.**")

        # Log the action
        log_message = await format_log(
            action="Announcements Disabled",
            chat=chat.title or str(chat_id),
            admin=callback_query.from_user.mention
        )

    await send_log(chat_id, log_message)


@pgram.on_chat_member_updated(~filters.me)
async def announce_member_update(client: Client, chat_member_updated: ChatMemberUpdated):
    chat_id = chat_member_updated.chat.id

    from_user = chat_member_updated.from_user
    target_user = None

    old_status = None
    new_status = None
    old_title = None
    new_title = None
    message_text = None  # Initialize message_text to None
    log_action = None

    if chat_member_updated.old_chat_member:
        old_status = chat_member_updated.old_chat_member.status
        old_title = getattr(chat_member_updated.old_chat_member, "custom_title", None)

    if chat_member_updated.new_chat_member:
        new_status = chat_member_updated.new_chat_member.status
        new_title = getattr(chat_member_updated.new_chat_member, "custom_title", None)
        target_user = chat_member_updated.new_chat_member.user

    # Validate both `from_user` and `target_user`
    if not from_user or not target_user:
        return  # Exit if either user information is missing

    # If the action is performed by the bot itself, do not announce
    bot_id = config.BOT_ID
    if from_user.id == bot_id:
        return

    # Helper function for mention
    from_user_mention = f"<a href='tg://user?id={from_user.id}'>{from_user.first_name}</a>"
    target_user_mention = f"<a href='tg://user?id={target_user.id}'>{target_user.first_name}</a>"

    # Example logging
    a = f"{from_user_mention} ({from_user.id})"
    b = f"{target_user_mention} ({target_user.id})"

    # Handle Promotion
    if old_status in [ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED] and new_status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        if new_title:
            message_text = (
                f"<pre>{target_user_mention} is promoted by {from_user_mention} with the title {new_title}</pre>"
            )
        else:
            message_text = f"<pre>{target_user_mention} is promoted by {from_user_mention}.</pre>"
        log_action = "Promotion"

    # Handle Demotion
    elif old_status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] and new_status in [ChatMemberStatus.MEMBER, ChatMemberStatus.BANNED]:
        if new_status == ChatMemberStatus.MEMBER:
            message_text = f"<pre>{target_user_mention} is demoted by {from_user_mention}.</pre>"
        else:
            message_text = f"<pre>{target_user_mention} is demoted and banned by {from_user_mention}.</pre>"
        log_action = "Demotion"

    # Handle Mute/Unmute
    elif old_status == ChatMemberStatus.RESTRICTED and new_status == ChatMemberStatus.MEMBER:
        message_text = f"<pre>{target_user_mention} is unmuted by {from_user_mention}.</pre>"
        log_action = "Unmute"

    elif new_status == ChatMemberStatus.RESTRICTED and chat_member_updated.new_chat_member.is_member:
        message_text = f"<pre>{target_user_mention} is muted by {from_user_mention}.</pre>"
        log_action = "Mute"

    # Handle Title Change (for admins only)
    elif old_status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] and new_status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        if old_title != new_title:
            if new_title is None:
                message_text = (
                    f"<pre>{target_user_mention}'s title is removed by {from_user_mention}.</pre>\n"
                    f"<pre>Old title: <code>{old_title}</code>\nNew title: None</pre>\n\n"
                )
            elif old_title is None:
                message_text = (
                    f"<pre>{target_user_mention}'s title is set by {from_user_mention}.</pre>\n"
                    f"<pre>New title: {new_title}</pre>"
                )
            else:
                message_text = (
                    f"<pre>{target_user_mention}'s title is changed by {from_user_mention}.</pre>\n"
                    f"<pre>Old title: <code>{old_title}</code>\nNew title: {new_title}</pre>"
                )

    # Handle Banning/Unbanning
    elif new_status == ChatMemberStatus.BANNED:
        message_text = f"<pre>{target_user_mention} is banned by {from_user_mention}.</pre>"
        log_action = "Ban"

    elif old_status == ChatMemberStatus.BANNED and new_status != ChatMemberStatus.BANNED:
        message_text = f"<pre>{target_user_mention} is unbanned by {from_user_mention}.</pre>"
        log_action = "Unban"

    # Send announcement if enabled
    if message_text and await is_announcements_enabled(chat_id):
        await client.send_message(chat_id, message_text, parse_mode=ParseMode.HTML)

    # Always send log
    if log_action:
        log_message = await format_log(
            action=log_action,
            chat=chat_member_updated.chat.title or str(chat_id),
            admin=a,
            user=b
        )
        await send_log(chat_id, log_message)


__module__ = "𝖠𝗇𝗇𝗈𝗎𝗇𝖼𝖾𝗆𝖾𝗇𝗍"


__help__ = """**✧ /𝖺𝗇𝗇𝗈𝗎𝗇𝖼𝖾𝗆𝖾𝗇𝗍** - 𝖳𝗈 𝖤𝗇𝖺𝖻𝗅𝖾 𝖠𝗇𝗇𝗈𝗎𝗇𝖼𝖾𝗆𝖾𝗇𝗍𝗌 𝖨𝗇 𝖠 𝖢𝗁𝖺𝗍.
 
"""