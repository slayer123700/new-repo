from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message , CallbackQuery
from shigaraki.decorator.chatadmin import can_restrict_members
from pyrogram.enums import ChatMemberStatus
from config import config as c
from shigaraki import app 
from pyrogram.errors import ChatAdminRequired , UserNotParticipant
from shigaraki.helper.user import resolve_user , MUTE , UNMUTE
from datetime import datetime, timedelta
from shigaraki.helper.log_helper import send_log, format_log
from shigaraki.decorator.errors import error 
from shigaraki.decorator.save import save
from shigaraki.shigaraki import CHAT_ADMIN_REQUIRED , USER_ALREADY_BANNED , USER_NOT_MUTED , USER_ALREADY_MUTED , USER_NOT_BANNED , USER_IS_ADMIN , USER_IS_OWNER
import json

def load_sudoers():
    """Load the sudoers.json file dynamically."""
    with open("sudoers.json", "r") as f:
        return json.load(f)

def get_privileged_users():
    """Combine all privileged user IDs into one list dynamically."""
    sudoers = load_sudoers()
    return (
        sudoers.get("Hokages", []) +
        sudoers.get("Jonins", []) +
        sudoers.get("Chunins", [])
    )


@app.on_message(filters.command(["ban" , "fuck"], prefixes=c.COMMAND_PREFIXES) & filters.group)
@app.on_message(filters.regex(r"^(?i)(Ban|Fuck) (him|her)$") & filters.group & filters.reply)
@can_restrict_members
@error
@save
async def ban_user(client: app, message: Message):  # type: ignore
    chat_id = message.chat.id

    if not message.from_user:
        return
    
    target_user = None

    reason = None

    # Case 1: Command is a reply
    if message.reply_to_message:
        target_user = await resolve_user(client, message)
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            reason = args[1]  # Use the second argument as the title

    # Case 2: Command with username/ID and title
    else:
        args = message.text.split(maxsplit=2)
        if len(args) > 1:
            # Resolve the username or user ID
            target_user = await resolve_user(client, message)
        if len(args) > 2:
            reason = args[2]  # Use the third argument as the title


    if not target_user:
        await message.reply(
            "𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖿𝗂𝗇𝖽 𝗍𝗁𝖾 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖾𝖽 𝗎𝗌𝖾𝗋. 𝖯𝗅𝖾𝖺𝗌𝖾 𝗆𝖺𝗄𝖾 𝗌𝗎𝗋𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾/𝗂𝖽 𝗂𝗌 𝗏𝖺𝗅𝗂𝖽 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾."
        )
        return

    # Ban the user with the provided title
    try:
                
        
            # Check the user's current status in the chat
        x = await app.get_chat_member(chat_id, target_user.id)
    
        if x.status == ChatMemberStatus.OWNER:
            await message.reply(USER_IS_OWNER)
            return
    
        if x.status == ChatMemberStatus.ADMINISTRATOR:
            await message.reply(USER_IS_ADMIN)
            return
    
        if x.status == ChatMemberStatus.BANNED:
            await message.reply(USER_ALREADY_BANNED)
            return

        privileged_users = get_privileged_users()
        
        if target_user.id in privileged_users:
            return

        await app.ban_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
        )

        # Construct promotion message
        promotion_message = (
            f"✪ **𝖡𝖺𝗇 𝖤𝖵𝖤𝖭𝖳**\n\n"
            f"👤 **𝖴𝗌𝖾𝗋:** {target_user.mention()} (`{target_user.id}`)\n"
            f"⬆️ **𝖡𝖺𝗇𝗇𝖾𝖽 𝖡𝗒:** {message.from_user.mention()}\n"
        )

        if reason :
            promotion_message += f"📝 **𝖱𝖾𝖺𝗌𝗈𝗇** : {reason}"


        # Send promotion message with inline buttons
        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("𝖴𝗇𝖻𝖺𝗇", callback_data=f"unban:{target_user.id}")],
                [InlineKeyboardButton("🗑️", callback_data="delete")],
            ]
        )
        await message.reply(promotion_message, reply_markup=buttons)
        # Log the ban action
        log_message = await format_log(
            action="Ban",
            chat=message.chat.title,
            admin=message.from_user.mention(),
            user=target_user.mention(),
            pinned_link=None,
        )
        await send_log(chat_id, log_message)

    except ChatAdminRequired:
        await message.reply(CHAT_ADMIN_REQUIRED)
    except UserNotParticipant:
        await message.reply("𝖴𝗌𝖾𝗋 𝖨𝗌 𝖭𝗈𝗍 𝖯𝗋𝖾𝗌𝖾𝗇𝗍 𝖨𝗇 𝖳𝗁𝗂𝗌 𝖢𝗁𝖺𝗍 !!")
    except Exception as e:
        await message.reply(f"𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖯𝗋𝗈𝗆𝗈𝗍𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋: {e}")


@app.on_callback_query(filters.regex("^unban:(\d+)$"))
@can_restrict_members
@error
async def demote_user(client: app, callback_query: CallbackQuery): # type: ignore
    if not callback_query.from_user:
        return

    user_id = int(callback_query.data.split(":")[1])
    chat_id = callback_query.message.chat.id
    d_user = await app.get_users(user_id)


    try:

        d = await app.get_chat_member(chat_id , user_id)

        if d.status != ChatMemberStatus.BANNED:
            await callback_query.message.edit_text(USER_NOT_BANNED)
            return

        # Demote the user
        await app.unban_chat_member(
            chat_id=chat_id,
            user_id=user_id
        )
        await callback_query.answer("𝖴𝗌𝖾𝗋 𝖴𝗇𝖻𝖺𝗇𝖾𝖽 𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒.")
        await callback_query.message.edit_text(f"{d_user.mention()} 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝖴𝗇𝖻𝖺𝗇𝖾𝖽 𝖻𝗒 {callback_query.from_user.mention()}")

        # Log the unban action
        log_message = await format_log(
            action="Unban",
            chat=callback_query.message.chat.title,
            admin=callback_query.from_user.mention(),
            user=d_user.mention(),
        )
        await send_log(chat_id, log_message)

    except ChatAdminRequired:
        await callback_query.message.edit_text(CHAT_ADMIN_REQUIRED)
    except Exception as e:
        await callback_query.answer(f"𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝖴𝗇𝖻𝖺𝗇 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋:", show_alert=True)


@app.on_message(filters.command("unban", prefixes=c.COMMAND_PREFIXES) & filters.group)
@app.on_message(filters.regex(r"^(?i)Unban (him|her)$") & filters.group & filters.reply)
@can_restrict_members
@error
@save
async def demote_user(client: app, message: Message):  # type: ignore
    chat_id = message.chat.id
    if not message.from_user:
        return
    
    # Resolve the target user
    target_user = await resolve_user(client, message)
    if not target_user:
        await message.reply(
            "𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖿𝗂𝗇𝖽 𝗍𝗁𝖾 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖾𝖽 𝗎𝗌𝖾𝗋. 𝖯𝗅𝖾𝖺𝗌𝖾 𝖾𝗇𝗌𝗎𝗋𝖾 𝖨 𝗁𝖺𝗏𝖾 𝗂𝗇𝗍𝖾𝗋𝖺𝖼𝗍𝖾𝖽 𝗐𝗂𝗍𝗁 𝗍𝗁𝖺𝗍 𝗎𝗌𝖾𝗋 𝖻𝖾𝖿𝗈𝗋𝖾. 𝖸𝗈𝗎 𝖼𝖺𝗇 𝖿𝗈𝗋𝗐𝖺𝗋𝖽 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝖿𝗋𝗈𝗆 𝗍𝗁𝖺𝗍 𝗎𝗌𝖾𝗋 𝗍𝗈 𝗆𝖾 𝗌𝗈 𝖨 𝖼𝖺𝗇 𝗋𝖾𝗍𝗋𝗂𝖾𝗏𝖾 𝗍𝗁𝖾𝗂𝗋 𝗂𝗇𝖿𝗈𝗋𝗆𝖺𝗍𝗂𝗈𝗇."
        )
        return

    user = message.from_user  # The user who sent the promote command



    # Promote the target user with the specified privileges
    try:
        
        x = await app.get_chat_member(chat_id , target_user.id)

        if x.status == ChatMemberStatus.OWNER:
            await message.reply(USER_IS_OWNER)
            return
    
        if x.status == ChatMemberStatus.ADMINISTRATOR:
            await message.reply(USER_IS_ADMIN)
            return
    
        if x.status != ChatMemberStatus.BANNED:
            await message.reply(USER_NOT_BANNED)
            return

        await app.unban_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
        )

        # Construct the promotion message
        promotion_message = (
            f"✪ **𝖴𝗇𝖻𝖺𝗇 𝖤𝖵𝖤𝖭𝖳**\n\n"
            f"👤 **𝖴𝗌𝖾𝗋:** {target_user.mention()} (`{target_user.id}`)\n"
            f"⬆️ **𝖴𝗇𝖻𝖺𝗇𝖾𝖽 𝖡𝗒:** {user.mention()}\n"
        )

        await message.reply(promotion_message)
        # Log the unban event
        log_message = await format_log(
            action="Unban",
            chat=message.chat.title,
            admin=user.mention(),
            user=target_user.mention(),
        )
        await send_log(chat_id, log_message)
    
    except ChatAdminRequired:
        await message.reply(CHAT_ADMIN_REQUIRED)
    except Exception as e:
        await message.reply(f"𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝖴𝗇𝖻𝖺𝗇 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋 !!")

@app.on_message(filters.command(["kickme"], prefixes=c.COMMAND_PREFIXES) & filters.group)
@error
@save
async def ban_user(client: app, message: Message):  # type: ignore
    chat_id = message.chat.id
    user = message.from_user

    if not user:
        return
    
    target_user = user



    # Ban the user with the provided title
    try:
    
        # Check the user's current status in the chat
        x = await app.get_chat_member(chat_id, target_user.id)
    
        if x.status == ChatMemberStatus.OWNER:
            await message.reply(USER_IS_OWNER)
            return
    
        if x.status == ChatMemberStatus.ADMINISTRATOR:
            await message.reply(USER_IS_ADMIN)
            return
    
    
        await app.ban_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
        )
        await app.unban_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
        )

        # Construct promotion message
        promotion_message = ("𝖮𝗄𝖺𝗒 𝖥𝗎𝖼𝗄 𝖮𝖿𝖿 !!")

        await message.reply(promotion_message)

        # Log the self-kick event
        log_message = await format_log(
            action="Self-Kick",
            chat=message.chat.title,
            user=target_user.mention(),
        )
        await send_log(chat_id, log_message)

    except ChatAdminRequired:
        await message.reply(CHAT_ADMIN_REQUIRED)
    except Exception as e:
        await message.reply(f"𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖪𝗂𝖼𝗄 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋")


@app.on_message(filters.command(["banme"], prefixes=c.COMMAND_PREFIXES) & filters.group)
@error
@save
async def ban_user(client: app, message: Message):  # type: ignore
    chat_id = message.chat.id
    user = message.from_user

    if not user:
        return
    
    target_user = user



    # Ban the user with the provided title
    try:

        # Check the user's current status in the chat
        x = await app.get_chat_member(chat_id, target_user.id)
    
        if x.status == ChatMemberStatus.OWNER:
            await message.reply(USER_IS_OWNER)
            return
    
        if x.status == ChatMemberStatus.ADMINISTRATOR:
            await message.reply(USER_IS_ADMIN)
            return

        await app.ban_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
        )

        # Construct promotion message
        promotion_message = ("𝖮𝗄𝖺𝗒 𝖥𝗎𝖼𝗄 𝖮𝖿𝖿 !!")

        await message.reply(promotion_message)

        # Log the self-ban event
        log_message = await format_log(
            action="Self-Ban",
            chat=message.chat.title,
            user=target_user.mention(),
        )
        await send_log(chat_id, log_message)

    except ChatAdminRequired:
        await message.reply(CHAT_ADMIN_REQUIRED)
    except Exception as e:
        await message.reply(f"𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖡𝖺𝗇 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋")

@app.on_message(filters.command("sban", prefixes=c.COMMAND_PREFIXES) & filters.group)
@can_restrict_members
@error
@save
async def silently_ban_user(client: app, message: Message):  # type: ignore
    chat_id = message.chat.id

    if not message.from_user:
        return

    target_user = None

    # Case 1: Command is a reply
    if message.reply_to_message:
        target_user = await resolve_user(client, message)

    # Case 2: Command with username/ID
    else:
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            target_user = await resolve_user(client, message)

    if not target_user:
        # Delete the command silently if no user was found
        await message.delete()
        return

    # Check the user's current status in the chat
    try:
        x = await app.get_chat_member(chat_id, target_user.id)

        if x.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            # Owner/Admin can't be banned, delete the command silently
            await message.delete()
            return

        if x.status == ChatMemberStatus.BANNED:
            # User is already banned, delete the command silently
            await message.delete()
            return

        privileged_users = get_privileged_users()
        
        if target_user.id in privileged_users:
            return

        # Ban the user
        await app.ban_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
        )

        # Delete the command and the replied message (if applicable)
        await message.delete()
        if message.reply_to_message:
            await message.reply_to_message.delete()

        # Log the ban event
        log_message = await format_log(
            action="Silently Banned",
            chat=message.chat.title,
            admin=message.from_user.mention(),
            user=target_user.mention()
        )
        await send_log(chat_id, log_message)

    except ChatAdminRequired:
        # Silently handle if the bot lacks admin rights
        await message.delete()

    except UserNotParticipant:
        await message.delete()
    except Exception:
        # Silently handle other errors
        await message.delete()


@app.on_message(filters.command(["dban" , "dfuck"], prefixes=c.COMMAND_PREFIXES) & filters.group)
@can_restrict_members
@error
@save
async def dban_user(client: app, message: Message):  # type: ignore
    chat_id = message.chat.id

    if not message.from_user:
        return
    
    target_user = None
    reason = None

    # Case 1: Command is a reply
    if message.reply_to_message:
        target_user = await resolve_user(client, message)
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            reason = args[1]  # Use the second argument as the title

    # Case 2: Command with username/ID and title
    else:
        await message.reply("𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖿𝗂𝗇𝖽 𝗍𝗁𝖾 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖾𝖽 𝗎𝗌𝖾𝗋. 𝖯𝗅𝖾𝖺𝗌𝖾 𝗆𝖺𝗄𝖾 𝗌𝗎𝗋𝖾 𝗍𝗁𝖾 𝗏𝖺𝗅𝗂𝖽 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾.")
        return


    # Ban the user with the provided title
    try:

        # Check the user's current status in the chat
        x = await app.get_chat_member(chat_id, target_user.id)
    
        if x.status == ChatMemberStatus.OWNER:
            await message.reply(USER_IS_OWNER)
            return
    
        if x.status == ChatMemberStatus.ADMINISTRATOR:
            await message.reply(USER_IS_ADMIN)
            return
    
        if x.status == ChatMemberStatus.BANNED:
            await message.reply(USER_ALREADY_BANNED)
            return
    
        await message.reply_to_message.delete()
        
        privileged_users = get_privileged_users()
        
        if target_user.id in privileged_users:
            return

        await app.ban_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
        )

        # Construct promotion message
        promotion_message = (
            f"✪ **𝖡𝖺𝗇 𝖤𝖵𝖤𝖭𝖳**\n\n"
            f"👤 **𝖴𝗌𝖾𝗋:** {target_user.mention()} (`{target_user.id}`)\n"
            f"⬆️ **𝖡𝖺𝗇𝗇𝖾𝖽 𝖡𝗒:** {message.from_user.mention()}\n"
        )

        if reason :
            promotion_message += f"📝 **𝖱𝖾𝖺𝗌𝗈𝗇** : {reason}"


        # Send promotion message with inline buttons
        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("𝖴𝗇𝖻𝖺𝗇", callback_data=f"unban:{target_user.id}")],
                [InlineKeyboardButton("🗑️", callback_data="delete")],
            ]
        )
        await message.reply(promotion_message, reply_markup=buttons)

        # Log the ban event
        log_message = await format_log(
            action="Delete Banned",
            chat=message.chat.title,
            admin=message.from_user.mention(),
            user=target_user.mention(),
        )
        if reason:
            log_message += f"\n**Reason:** {reason}"
        
        await send_log(chat_id, log_message)

    except ChatAdminRequired:
        await message.reply(CHAT_ADMIN_REQUIRED)
    except UserNotParticipant:
        await message.reply("𝖴𝗌𝖾𝗋 𝖨𝗌 𝖭𝗈𝗍 𝖯𝗋𝖾𝗌𝖾𝗇𝗍 𝖨𝗇 𝖳𝗁𝗂𝗌 𝖢𝗁𝖺𝗍 !!")
    except Exception as e:
        await message.reply(f"𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 Ban 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋: {e}")

@app.on_message(filters.command("tban", prefixes=c.COMMAND_PREFIXES) & filters.group)
@can_restrict_members
@error
@save
async def temporary_ban_user(client: app, message: Message):  # type: ignore
    chat_id = message.chat.id

    if not message.from_user:
        return

    target_user = None
    duration = None
    reason = None

    # Parse the command arguments
    args = message.text.split(maxsplit=1)

    # Case 1: Command is a reply
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        if len(args) > 1:
            # Extract duration and optional reason
            try:
                duration_and_reason = args[1].split(maxsplit=1)
                duration = int(duration_and_reason[0])
                if len(duration_and_reason) > 1:
                    reason = duration_and_reason[1]
            except ValueError:
                await message.reply("𝖴𝗌𝖺𝗀𝖾: /𝗍𝖻𝖺𝗇 [𝗎𝗌𝖾𝗋] [𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇 𝗂𝗇 𝗆𝗂𝗇𝗎𝗍𝖾𝗌] [𝗋𝖾𝖺𝗌𝗈𝗇 (𝗈𝗉𝗍𝗂𝗈𝗇𝖺𝗅)]")
                return

    # Case 2: Command with username/ID and duration
    else:
        args = message.text.split(maxsplit=2)
        if len(args) > 1:
            target_user = await resolve_user(client, message, args[1])
        if len(args) > 2:
            try:
                duration_and_reason = args[2].split(maxsplit=1)
                duration = int(duration_and_reason[0])
                if len(duration_and_reason) > 1:
                    reason = duration_and_reason[1]
            except ValueError:
                await message.reply("𝖴𝗌𝖺𝗀𝖾: /𝗍𝖻𝖺𝗇 [𝗎𝗌𝖾𝗋] [𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇 𝗂𝗇 𝗆𝗂𝗇𝗎𝗍𝖾𝗌] [𝗋𝖾𝖺𝗌𝗈𝗇 (𝗈𝗉𝗍𝗂𝗈𝗇𝖺𝗅)]")
                return

    if not target_user or not duration:
        await message.reply("𝖴𝗌𝖺𝗀𝖾: /𝗍𝖻𝖺𝗇 [𝗎𝗌𝖾𝗋] [𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇 𝗂𝗇 𝗆𝗂𝗇𝗎𝗍𝖾𝗌] [𝗋𝖾𝖺𝗌𝗈𝗇 (𝗈𝗉𝗍𝗂𝗈𝗇𝖺𝗅)]")
        return

    # Check the user's current status in the chat
    try:
        x = await app.get_chat_member(chat_id, target_user.id)

        if x.status == ChatMemberStatus.OWNER:
            await message.reply(USER_IS_OWNER)
            return

        if x.status == ChatMemberStatus.ADMINISTRATOR:
            await message.reply(USER_IS_ADMIN)
            return

        if x.status == ChatMemberStatus.BANNED:
            await message.reply(USER_ALREADY_BANNED)
            return

        privileged_users = get_privileged_users()
        
        if target_user.id in privileged_users:
            return

        # Ban the user temporarily
        until_date = datetime.utcnow() + timedelta(minutes=duration)
        await app.ban_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            until_date=until_date,
        )

        # Send promotion message with inline buttons
        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("𝖴𝗇𝖻𝖺𝗇", callback_data=f"unban:{target_user.id}")],
                [InlineKeyboardButton("🗑️", callback_data="delete")],
            ]
        )
        h = (
            f"✪ **𝖡𝖺𝗇 𝖤𝖵𝖤𝖭𝖳**\n\n"
            f"👤 **𝖴𝗌𝖾𝗋:** {target_user.mention()} (`{target_user.id}`)\n"
            f"⬆️ **𝖡𝖺𝗇𝗇𝖾𝖽 𝖡𝗒:** {message.from_user.mention()}\n"
        )
        if reason:
            h += f"📝 **𝖱𝖾𝖺𝗌𝗈𝗇:** {reason}"
        await message.reply(h, reply_markup=buttons)

        # Log the temporary ban event
        log_message = await format_log(
            action=f"Temporarily Banned for {duration} minutes",
            chat=message.chat.title,
            admin=message.from_user.mention(),
            user=target_user.mention()
        )
        if reason:
            log_message += f"\n**Reason:** {reason}"
        
        await send_log(chat_id, log_message)

    except ChatAdminRequired:
        await message.reply(CHAT_ADMIN_REQUIRED)
    except UserNotParticipant:
        await message.reply("𝖴𝗌𝖾𝗋 𝖨𝗌 𝖭𝗈𝗍 𝖯𝗋𝖾𝗌𝖾𝗇𝗍 𝖨𝗇 𝖳𝗁𝗂𝗌 𝖢𝗁𝖺𝗍!")
    except Exception as e:
        await message.reply(f"𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽: `{e}`")

#====================================================================================================================================================#

@app.on_message(filters.command(["mute"], prefixes=c.COMMAND_PREFIXES) & filters.group)
@app.on_message(filters.regex(r"^(?i)Mute (him|her)$") & filters.group & filters.reply)
@can_restrict_members
@error
@save
async def mute_user(client: app, message: Message):  # type: ignore
    chat_id = message.chat.id

    if not message.from_user:
        return

    target_user = None
    reason = None

    # Case 1: Command is a reply
    if message.reply_to_message:
        target_user = await resolve_user(client, message)
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            reason = args[1]  # Use the second argument as the title

    # Case 2: Command with username/ID and title
    else:
        args = message.text.split(maxsplit=2)
        if len(args) > 1:
            # Resolve the username or user ID
            target_user = await resolve_user(client, message)
        if len(args) > 2:
            reason = args[2]  # Use the third argument as the title



    if not target_user:
        await message.reply(
            "𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖿𝗂𝗇𝖽 𝗍𝗁𝖾 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖾𝖽 𝗎𝗌𝖾𝗋. 𝖯𝗅𝖾𝖺𝗌𝖾 𝗆𝖺𝗄𝖾 𝗌𝗎𝗋𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾/𝗂𝖽 𝗂𝗌 𝗏𝖺𝗅𝗂𝖽 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾."
        )
        return


    # Promote the user with the provided title
    try:

        # Check the user's current status in the chat
        x = await app.get_chat_member(chat_id, target_user.id)
    
        if x.status == ChatMemberStatus.OWNER:
            await message.reply(USER_IS_OWNER)
            return
    
        if x.status == ChatMemberStatus.ADMINISTRATOR:
            await message.reply(USER_IS_ADMIN)
            return
    
        if x.permissions and not x.permissions.can_send_messages:
            await message.reply(USER_ALREADY_MUTED)
            return

        privileged_users = get_privileged_users()
        
        if target_user.id in privileged_users:
            return

        await app.restrict_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            permissions=MUTE
        )

        # Construct promotion message
        promotion_message = (
            f"✪ **𝖬𝗎𝗍𝖾 𝖤𝖵𝖤𝖭𝖳**\n\n"
            f"👤 **𝖴𝗌𝖾𝗋:** {target_user.mention()} (`{target_user.id}`)\n"
            f"⬆️ **𝖬𝗎𝗍𝖾𝖽 𝖡𝗒:** {message.from_user.mention()}\n"
        )

        if reason :
            promotion_message += f"📝 **𝖱𝖾𝖺𝗌𝗈𝗇** : {reason}"

        # Send promotion message with inline buttons
        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("𝖴𝗇𝗆𝗎𝗍𝖾", callback_data=f"unmute:{target_user.id}")],
                [InlineKeyboardButton("🗑️", callback_data="delete")],
            ]
        )
        await message.reply(promotion_message, reply_markup=buttons)

        # Log the mute action
        log_message = await format_log(
            action="Mute",
            chat=message.chat.title,
            admin=message.from_user.mention(),
            user=target_user.mention(),
        )
        await send_log(chat_id, log_message)

    except ChatAdminRequired:
        await message.reply(CHAT_ADMIN_REQUIRED)
    except UserNotParticipant:
        await message.reply("𝖴𝗌𝖾𝗋 𝖨𝗌 𝖭𝗈𝗍 𝖯𝗋𝖾𝗌𝖾𝗇𝗍 𝖨𝗇 𝖳𝗁𝗂𝗌 𝖢𝗁𝖺𝗍 !!")
    except Exception as e:
        await message.reply(f"𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝗆𝗎𝗍𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋: {e}")

@app.on_message(filters.command(["unmute"], prefixes=c.COMMAND_PREFIXES) & filters.group)
@app.on_message(filters.regex(r"^(?i)Unmute (him|her)$") & filters.group & filters.reply)
@can_restrict_members
@error
@save
async def unmute_user(client: app, message: Message):  # type: ignore
    chat_id = message.chat.id

    if not message.from_user:
        return

    target_user = None

    # Case 1: Command is a reply
    if message.reply_to_message:
        target_user = await resolve_user(client, message)


    # Case 2: Command with username/ID and title
    else:
        args = message.text.split(maxsplit=2)
        if len(args) > 1:
            # Resolve the username or user ID
            target_user = await resolve_user(client, message)



    if not target_user:
        await message.reply(
            "𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖿𝗂𝗇𝖽 𝗍𝗁𝖾 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖾𝖽 𝗎𝗌𝖾𝗋. 𝖯𝗅𝖾𝖺𝗌𝖾 𝗆𝖺𝗄𝖾 𝗌𝗎𝗋𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾/𝗂𝖽 𝗂𝗌 𝗏𝖺𝗅𝗂𝖽 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾."
        )
        return


    # Promote the user with the provided title
    try:

        # Check the user's current status in the chat
        x = await app.get_chat_member(chat_id, target_user.id)
    
        if x.status == ChatMemberStatus.OWNER:
            await message.reply(USER_IS_OWNER)
            return
    
        if x.status == ChatMemberStatus.ADMINISTRATOR:
            await message.reply(USER_IS_ADMIN)
            return
    
        if x.permissions and  x.permissions.can_send_messages:
            await message.reply(USER_NOT_MUTED)
            return

        await app.restrict_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            permissions=UNMUTE
        )

        # Construct promotion message
        promotion_message = (
            f"✪ **𝖴𝗇𝗆𝗎𝗍𝖾 𝖤𝖵𝖤𝖭𝖳**\n\n"
            f"👤 **𝖴𝗌𝖾𝗋:** {target_user.mention()} (`{target_user.id}`)\n"
            f"⬆️ **𝖴𝗇𝗆𝗎𝗍𝖾𝖽 𝖡𝗒:** {message.from_user.mention()}\n"
        )

        await message.reply(promotion_message)

        # Log the unmute action
        log_message = await format_log(
            action="Unmute",
            chat=message.chat.title,
            admin=message.from_user.mention(),
            user=target_user.mention(),
            pinned_link=None
        )
        await send_log(chat_id, log_message)


    except ChatAdminRequired:
        await message.reply(CHAT_ADMIN_REQUIRED)
    except UserNotParticipant:
        await message.reply("𝖴𝗌𝖾𝗋 𝖨𝗌 𝖭𝗈𝗍 𝖯𝗋𝖾𝗌𝖾𝗇𝗍 𝖨𝗇 𝖳𝗁𝗂𝗌 𝖢𝗁𝖺𝗍 !!")
    except Exception as e:
        await message.reply(f"𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖴𝗇𝗆𝗎𝗍𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋: {e}")

@app.on_callback_query(filters.regex("^unmute:(\d+)$"))
@can_restrict_members
@error
async def demote_user(client: app, callback_query: CallbackQuery): # type: ignore
    if not callback_query.from_user:
        return

    user_id = int(callback_query.data.split(":")[1])
    chat_id = callback_query.message.chat.id
    d_user = await app.get_users(user_id)

    d = await app.get_chat_member(chat_id , user_id)

    if d.status != ChatMemberStatus.RESTRICTED:
        await callback_query.message.edit_text(USER_NOT_MUTED)
        return


    try:
        # Demote the user
        await app.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=UNMUTE
        )
        await callback_query.answer("𝖴𝗌𝖾𝗋 𝖴𝗇𝗆𝗎𝗍𝖾𝖽 𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒.")
        await callback_query.message.edit_text(f"{d_user.mention()} 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝖴𝗇𝗆𝗎𝗍𝖾𝖽 𝖻𝗒 {callback_query.from_user.mention()}")

        # Log the unmute action
        log_message = await format_log(
            action="Unmute",
            chat=callback_query.message.chat.title,
            admin=callback_query.from_user.mention(),
            user=d_user.mention(),
        )
        await send_log(chat_id, log_message)

    except ChatAdminRequired:
        await callback_query.message.edit_text(CHAT_ADMIN_REQUIRED)
    except Exception as e:
        await callback_query.answer(f"𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝖴𝗇𝗆𝗎𝗍𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋", show_alert=True)


@app.on_message(filters.command("smute", prefixes=c.COMMAND_PREFIXES) & filters.group)
@can_restrict_members
@error
@save
async def silently_mute_user(client: app, message: Message):  # type: ignore
    chat_id = message.chat.id

    if not message.from_user:
        return

    target_user = None

    # Case 1: Command is a reply
    if message.reply_to_message:
        target_user = await resolve_user(client, message)

    # Case 2: Command with username/ID
    else:
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            target_user = await resolve_user(client, message)

    if not target_user:
        # Delete the command silently if no user was found
        await message.delete()
        return

    # Check the user's current status in the chat
    try:
        x = await app.get_chat_member(chat_id, target_user.id)

        if x.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            # Owner/Admin can't be muted, delete the command silently
            await message.delete()
            return

        if not x.permissions.can_send_messages:
           await message.delete()
           return
        
        privileged_users = get_privileged_users()
        
        if target_user.id in privileged_users:
            return
        
        # Ban the user
        await app.restrict_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            permissions=MUTE
        )

        # Delete the command and the replied message (if applicable)
        await message.delete()
        if message.reply_to_message:
            await message.reply_to_message.delete()

        # Log the mute event
        log_message = await format_log(
            action="Silently Muted",
            chat=message.chat.title,
            admin=message.from_user.mention(),
            user=target_user.mention()
        )
        await send_log(chat_id, log_message)

    except ChatAdminRequired:
        # Silently handle if the bot lacks admin rights
        await message.delete()

    except UserNotParticipant:
        await message.delete()
    except Exception:
        # Silently handle other errors
        await message.delete()

@app.on_message(filters.command("tmute", prefixes=c.COMMAND_PREFIXES) & filters.group)
@can_restrict_members
@error
@save
async def temporary_mute_user(client: app, message: Message):  # type: ignore
    chat_id = message.chat.id

    if not message.from_user:
        return

    target_user = None
    duration = None
    reason = None

    # Parse the command arguments
    args = message.text.split(maxsplit=1)

    # Case 1: Command is a reply
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        if len(args) > 1:
            # Extract duration and optional reason
            try:
                duration_and_reason = args[1].split(maxsplit=1)
                duration = int(duration_and_reason[0])
                if len(duration_and_reason) > 1:
                    reason = duration_and_reason[1]
            except ValueError:
                await message.reply("𝖴𝗌𝖺𝗀𝖾: /𝗍𝗆𝗎𝗍𝖾 [𝗎𝗌𝖾𝗋] [𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇 𝗂𝗇 𝗆𝗂𝗇𝗎𝗍𝖾𝗌] [𝗋𝖾𝖺𝗌𝗈𝗇 (𝗈𝗉𝗍𝗂𝗈𝗇𝖺𝗅)]")
                return

    # Case 2: Command with username/ID and duration
    else:
        args = message.text.split(maxsplit=2)
        if len(args) > 1:
            target_user = await resolve_user(client, message)
        if len(args) > 2:
            try:
                duration_and_reason = args[2].split(maxsplit=1)
                duration = int(duration_and_reason[0])
                if len(duration_and_reason) > 1:
                    reason = duration_and_reason[1]
            except ValueError:
                await message.reply("𝖴𝗌𝖺𝗀𝖾: /𝗍𝗆𝗎𝗍𝖾 [𝗎𝗌𝖾𝗋] [𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇 𝗂𝗇 𝗆𝗂𝗇𝗎𝗍𝖾𝗌] [𝗋𝖾𝖺𝗌𝗈𝗇 (𝗈𝗉𝗍𝗂𝗈𝗇𝖺𝗅)]")
                return

    if not target_user or not duration:
        await message.reply("𝖴𝗌𝖺𝗀𝖾: /𝗍𝗆𝗎𝗍𝖾 [𝗎𝗌𝖾𝗋] [𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇 𝗂𝗇 𝗆𝗂𝗇𝗎𝗍𝖾𝗌] [𝗋𝖾𝖺𝗌𝗈𝗇 (𝗈𝗉𝗍𝗂𝗈𝗇𝖺𝗅)]")
        return

    # Check the user's current status in the chat
    try:
        x = await app.get_chat_member(chat_id, target_user.id)

        if x.status == ChatMemberStatus.OWNER:
            await message.reply(USER_IS_OWNER)
            return

        if x.status == ChatMemberStatus.ADMINISTRATOR:
            await message.reply(USER_IS_ADMIN)
            return

        if x.permissions and not x.permissions.can_send_messages:
            await message.reply(USER_ALREADY_MUTED)
            return

        privileged_users = get_privileged_users()
        
        if target_user.id in privileged_users:
            return

        # Ban the user temporarily
        until_date = datetime.utcnow() + timedelta(minutes=duration)
        await app.restrict_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            until_date=until_date,
            permissions=MUTE
        )

        # Send promotion message with inline buttons
        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("𝖴𝗇𝗆𝗎𝗍𝖾", callback_data=f"unmute:{target_user.id}")],
                [InlineKeyboardButton("🗑️", callback_data="delete")],
            ]
        )
        h = (
            f"✪ **𝖬𝗎𝗍𝖾 𝖤𝖵𝖤𝖭𝖳**\n\n"
            f"👤 **𝖴𝗌𝖾𝗋:** {target_user.mention()} (`{target_user.id}`)\n"
            f"⬆️ **𝖬𝗎𝗍𝖾𝖽 𝖡𝗒:** {message.from_user.mention()}\n"
        )
        if reason:
            h += f"📝 **𝖱𝖾𝖺𝗌𝗈𝗇:** {reason}"
        await message.reply(h, reply_markup=buttons)

        # Log the temporary mute event
        log_message = await format_log(
            action="Temporarily Muted",
            chat=message.chat.title,
            admin=message.from_user.mention(),
            user=target_user.mention(),
        )
        await send_log(chat_id, log_message)

    except ChatAdminRequired:
        await message.reply(CHAT_ADMIN_REQUIRED)
    except UserNotParticipant:
        await message.reply("𝖴𝗌𝖾𝗋 𝖨𝗌 𝖭𝗈𝗍 𝖯𝗋𝖾𝗌𝖾𝗇𝗍 𝖨𝗇 𝖳𝗁𝗂𝗌 𝖢𝗁𝖺𝗍!")
    except Exception as e:
        await message.reply(f"𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽: `{e}`")


@app.on_message(filters.command(["kick"], prefixes=c.COMMAND_PREFIXES) & filters.group)
@app.on_message(filters.regex(r"^(?i)Nikal Yaha Se$") & filters.group & filters.reply)
@can_restrict_members
@error
@save
async def ban_user(client: app, message: Message):  # type: ignore
    chat_id = message.chat.id

    if not message.from_user:
        return
    
    target_user = None

    reason = None

    # Case 1: Command is a reply
    if message.reply_to_message:
        target_user = await resolve_user(client, message)
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            reason = args[1]  # Use the second argument as the title

    # Case 2: Command with username/ID and title
    else:
        args = message.text.split(maxsplit=2)
        if len(args) > 1:
            # Resolve the username or user ID
            target_user = await resolve_user(client, message)
        if len(args) > 2:
            reason = args[2]  # Use the third argument as the title


    if not target_user:
        await message.reply(
            "𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖿𝗂𝗇𝖽 𝗍𝗁𝖾 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖾𝖽 𝗎𝗌𝖾𝗋. 𝖯𝗅𝖾𝖺𝗌𝖾 𝗆𝖺𝗄𝖾 𝗌𝗎𝗋𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾/𝗂𝖽 𝗂𝗌 𝗏𝖺𝗅𝗂𝖽 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾."
        )
        return

    # Ban the user with the provided title
    try:
            # Check the user's current status in the chat
        x = await app.get_chat_member(chat_id, target_user.id)
    
        if x.status == ChatMemberStatus.OWNER:
            await message.reply(USER_IS_OWNER)
            return
    
        if x.status == ChatMemberStatus.ADMINISTRATOR:
            await message.reply(USER_IS_ADMIN)
            return

        privileged_users = get_privileged_users()
        
        if target_user.id in privileged_users:
            return

        await app.ban_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
        )
        await app.unban_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
        )

        # Construct promotion message
        promotion_message = (
            f"✪ **𝖪𝗂𝖼𝗄 𝖤𝖵𝖤𝖭𝖳**\n\n"
            f"👤 **𝖴𝗌𝖾𝗋:** {target_user.mention()} (`{target_user.id}`)\n"
            f"⬆️ **𝖪𝗂𝖼𝗄𝖾𝖽 𝖡𝗒:** {message.from_user.mention()}\n"
        )

        if reason :
            promotion_message += f"📝 **𝖱𝖾𝖺𝗌𝗈𝗇** : {reason}"

        await message.reply(promotion_message)

        # Log the action
        log_message = await format_log(
            action="Kick",
            chat=message.chat.title,
            admin=message.from_user.mention(),
            user=target_user.mention(),
            pinned_link=None  # Optional, no relevant link here
        )
        await send_log(chat_id, log_message)

    except ChatAdminRequired:
        await message.reply(CHAT_ADMIN_REQUIRED)
    except UserNotParticipant:
        await message.reply("𝖴𝗌𝖾𝗋 𝖨𝗌 𝖭𝗈𝗍 𝖯𝗋𝖾𝗌𝖾𝗇𝗍 𝖨𝗇 𝖳𝗁𝗂𝗌 𝖢𝗁𝖺𝗍 !!")
    except Exception as e:
        await message.reply(f"𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖯𝗋𝗈𝗆𝗈𝗍𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋: {e}")


__module__ = "𝖡𝖺𝗇"


__help__ = """**𝖴𝗌𝖾𝗋 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:**
  ✧ `/𝗄𝗂𝖼𝗄𝗆𝖾`**:** 𝖪𝗂𝖼𝗄𝗌 𝖳𝗁𝖾 𝖴𝗌𝖾𝗋 𝖶𝗁𝗈 𝖨𝗌𝗌𝗎𝖾𝖽 𝖳𝗁𝖾 𝖢𝗈𝗆𝗆𝖺𝗇𝖽
  ✧ `/𝖻𝖺𝗇𝗆𝖾`**:** 𝖡𝖺𝗇𝗌 𝖳𝗁𝖾 𝖴𝗌𝖾𝗋 𝖶𝗁𝗈 𝖨𝗌𝗌𝗎𝖾𝖽 𝗍𝗁𝖾 𝖢𝗈𝗆𝗆𝖺𝗇𝖽
  
**𝖠𝖽𝗆𝗂𝗇𝗌 𝗈𝗇𝗅𝗒:**
  ✧ `/𝖻𝖺𝗇` (𝗎𝗌𝖾𝗋) **:** 𝖡𝖺𝗇𝗌 𝖠 𝖴𝗌𝖾𝗋. (𝗏𝗂𝖺 𝗁𝖺𝗇𝖽𝗅𝖾, 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒)
  ✧ `/𝗌𝖻𝖺𝗇` (𝗎𝗌𝖾𝗋) **:** 𝖲𝗂𝗅𝖾𝗇𝗍𝗅𝗒 𝖡𝖺𝗇 𝖠 𝖴𝗌𝖾𝗋. 𝖣𝖾𝗅𝖾𝗍𝖾𝗌 𝖢𝗈𝗆𝗆𝖺𝗇𝖽, 𝖱𝖾𝗉𝗅𝗂𝖾𝖽 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖠𝗇𝖽 𝖣𝗈𝖾𝗌𝗇'𝗍 𝖱𝖾𝗉𝗅𝗒. (𝗏𝗂𝖺 𝗁𝖺𝗇𝖽𝗅𝖾, 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒)
  ✧ `/𝗍𝖻𝖺𝗇` (𝗎𝗌𝖾𝗋) (𝗑) **:** 𝖡𝖺𝗇𝗌 𝖠 𝖴𝗌𝖾𝗋 𝖥𝗈𝗋 `𝗑` 𝖬𝗂𝗇𝗎𝗍𝖾. (𝗏𝗂𝖺 𝗁𝖺𝗇𝖽𝗅𝖾, 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒).
  ✧ `/d𝖻𝖺𝗇` (𝗎𝗌𝖾𝗋) **:** 𝖣𝖾𝗅𝖾𝗍𝖾 𝖳𝗁𝖺𝗍 𝖬𝗌𝗀 𝖠𝗇𝖽 𝖡𝖺𝗇 𝖳𝗁𝖺𝗍 𝖴𝗌𝖾𝗋. (𝗋𝖾𝗉𝗅𝗒).
  ✧ `/𝗎𝗇𝖻𝖺𝗇` (𝗎𝗌𝖾𝗋) **:** 𝖴𝗇𝖻𝖺𝗇𝗌 𝖠 𝖴𝗌𝖾𝗋. (𝗏𝗂𝖺 𝗁𝖺𝗇𝖽𝗅𝖾, 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒)
  ✧ `/𝗄𝗂𝖼𝗄` (𝗎𝗌𝖾𝗋) **:** 𝖪𝗂𝖼𝗄𝗌 𝖠 𝖴𝗌𝖾𝗋 𝖮𝗎𝗍 𝖮𝖿 𝖳𝗁𝖾 𝖦𝗋𝗈𝗎𝗉, (𝗏𝗂𝖺 𝗁𝖺𝗇𝖽𝗅𝖾, 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒)
  ✧ `/𝗆𝗎𝗍𝖾` (𝗎𝗌𝖾𝗋) **:** 𝖲𝗂𝗅𝖾𝗇𝖼𝖾𝗌 𝖠 𝖴𝗌𝖾𝗋. 𝖢𝖺𝗇 𝖠𝗅𝗌𝗈 𝖡𝖾 𝖴𝗌𝖾𝖽 𝖠𝗌 𝖠 𝖱𝖾𝗉𝗅𝗒, 𝖬𝗎𝗍𝗂𝗇𝗀 𝖳𝗁𝖾 𝖱𝖾𝗉𝗅𝗂𝖾𝖽 𝖳𝗈 𝖴𝗌𝖾𝗋.
  ✧ `/𝗍𝗆𝗎𝗍𝖾` (𝗎𝗌𝖾𝗋) (𝗑) **:** 𝖬𝗎𝗍𝖾𝗌 𝖠 𝖴𝗌𝖾𝗋 𝖥𝗈𝗋 𝗑 𝖬𝗂𝗇𝗎𝗍𝖾𝗌. (𝗏𝗂𝖺 𝗁𝖺𝗇𝖽𝗅𝖾, 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒).
  ✧ `/𝗌𝗆𝗎𝗍𝖾` (𝗎𝗌𝖾𝗋) **:** 𝖲𝗂𝗅𝖾𝗇𝗍𝗅𝗒 𝖬𝗎𝗍𝖾 𝖠 𝖴𝗌𝖾𝗋. 𝖣𝖾𝗅𝖾𝗍𝖾𝗌 𝖢𝗈𝗆𝗆𝖺𝗇𝖽, 𝖱𝖾𝗉𝗅𝗂𝖾𝖽 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖠𝗇𝖽 𝖣𝗈𝖾𝗌𝗇'𝗍 𝖱𝖾𝗉𝗅𝗒. (𝗏𝗂𝖺 𝗁𝖺𝗇𝖽𝗅𝖾, 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒)
  ✧ `/𝗎𝗇𝗆𝗎𝗍𝖾` (𝗎𝗌𝖾𝗋) **:** 𝖴𝗇𝗆𝗎𝗍𝖾𝗌 𝖠 𝖴𝗌𝖾𝗋. 𝖢𝖺𝗇 𝖠𝗅𝗌𝗈 𝖡𝖾 𝖴𝗌𝖾𝖽 𝖠𝗌 𝖺 𝖱𝖾𝗉𝗅𝗒, 𝖬𝗎𝗍𝗂𝗇𝗀 𝖳𝗁𝖾 𝖱𝖾𝗉𝗅𝗂𝖾𝖽 𝖳𝗈 𝖴𝗌𝖾𝗋.
 """