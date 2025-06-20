from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message , CallbackQuery , ChatPrivileges
from shigaraki.decorator.chatadmin import fetch_admin_privileges ,  chatadmin , can_pin_messages , can_delete_messages , can_promote_members
from pyrogram.enums import ChatMembersFilter , ChatMemberStatus , ChatType , ParseMode
from config import config as c
import time
from shigaraki import app , admin_cache , admin_cache_reload , log
from pyrogram.errors import ChatAdminRequired, ChatInvalid , MessageDeleteForbidden , RPCError , UserNotParticipant
from shigaraki.helper.user import resolve_user , LOWPROMOTE , PROMOTE , FULLPROMOTE , UNMUTE , MUTE
from shigaraki.database.rules_db import get_rules , set_rules ,  clear_rules
import os , asyncio
from shigaraki.helper.log_helper import send_log, format_log
from shigaraki.decorator.errors import error 
from shigaraki.decorator.save import save 
from shigaraki.shigaraki import CHAT_ADMIN_REQUIRED , USER_ALREADY_PROMOTED , USER_ALREADY_DEMOTED , USER_IS_OWNER 


@app.on_message(filters.command(["reload" , "admincache"] , prefixes=c.COMMAND_PREFIXES) & filters.group)
@chatadmin
@error
@save
async def update_all_admin_cache(client, message: Message):
    chat_id = message.chat.id
    chat_name = message.chat.title
    current_time = time.time()  # Current time in seconds

    # Check if the chat has a cooldown entry and if 10 minutes have passed
    if chat_id in admin_cache_reload:
        time_diff = current_time - admin_cache_reload[chat_id]
        if time_diff < 600:  # 600 seconds = 10 minutes
            await message.reply(f"𝖯𝗅𝖾𝖺𝗌𝖾 𝖶𝖺𝗂𝗍 {int(600 - time_diff)} 𝖲𝖾𝖼𝗈𝗇𝖽𝗌 𝖡𝖾𝖿𝗈𝗋𝖾 𝖱𝖾𝗅𝗈𝖺𝖽𝗂𝗇𝗀 𝖳𝗁𝖾 𝖠𝖽𝗆𝗂𝗇 𝖢𝖺𝖼𝗁𝖾 𝖠𝗀𝖺𝗂𝗇.")
            return

    try:
        # Fetch all administrators in the chat
        admins = [admin async for admin in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS)]
        
        # Update privileges from admin data
        for admin in admins:
            user_id = admin.user.id
            # Extract and cache privileges directly from the admin object
            privileges = {
                "is_admin": admin.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER],
                "is_owner": admin.status == ChatMemberStatus.OWNER,
                "privileges": admin.privileges if admin.privileges else None,
            }
            admin_cache[(chat_id, user_id)] = privileges
        # Update last reload time for this chat
        admin_cache_reload[chat_id] = current_time

        await message.reply(f"𝖨 𝖧𝖺𝗏𝖾 U𝗉𝖽𝖺𝗍𝖾𝖽 𝖬𝗒 𝖠𝖽𝗆𝗂𝗇 𝖢𝖺𝖼𝗁𝖾 𝖥𝗈𝗋 {𝖼𝗁𝖺𝗍_𝗇𝖺𝗆𝖾}.")

        await send_log(
            chat_id,
            await format_log(
                action="Admin Cache Reloaded",
                chat=chat_name,
                admin=message.from_user.first_name
            )
        )

    except ChatAdminRequired:
        await message.reply(CHAT_ADMIN_REQUIRED)

@app.on_message(filters.command("pin", prefixes=c.COMMAND_PREFIXES) & filters.group)
@app.on_message(filters.regex(r"^(?i)Pin It$") & filters.group & filters.reply)
@can_pin_messages
@error
@save
async def pin_message(client, message: Message):
    try:
        if message.reply_to_message:
            # Pin the replied-to message
            await app.pin_chat_message(chat_id=message.chat.id, message_id=message.reply_to_message.id)
            chat_id = str(message.chat.id).removeprefix("-100")  # Remove the -100 prefix
            
            # Generate the pinned message link
            if message.chat.username:
                pinned_link = f"https://t.me/{message.chat.username}/{message.reply_to_message.id}"
            else:
                pinned_link = f"https://t.me/c/{chat_id}/{message.reply_to_message.id}"
            
            await message.reply_text(
                f"[𝖬𝖾𝗌𝗌𝖺𝗀𝖾]({pinned_link}) 𝖯𝗂𝗇𝗇𝖾𝖽 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 𝖨𝗇 {message.chat.title}!",
                disable_web_page_preview=True,
            )

            # Log the action
            await send_log(
                message.chat.id,
                await format_log(
                    action="Message Pinned",
                    chat=message.chat.title,
                    admin=message.from_user.first_name,
                    pinned_link=pinned_link,
                ),
            )

        elif len(message.command) > 1:
            # Pin a new message with provided text
            msg_text = message.text.split(None, 1)[1]
            sent_message = await message.reply(msg_text)
            await message.delete()
            await app.pin_chat_message(chat_id=sent_message.chat.id, message_id=sent_message.id)
            chat_id = str(message.chat.id).removeprefix("-100")  # Remove the -100 prefix

            # Generate the pinned message link
            if sent_message.chat.username:
                pinned_link = f"https://t.me/{sent_message.chat.username}/{sent_message.id}"
            else:
                pinned_link = f"https://t.me/c/{chat_id}/{sent_message.id}"

            await message.reply_text(
                f"[𝖬𝖾𝗌𝗌𝖺𝗀𝖾]({pinned_link}) 𝖯𝗂𝗇𝗇𝖾𝖽 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 𝖨𝗇 {message.chat.title}!",
                disable_web_page_preview=True,
            )

            # Log the action
            await send_log(
                message.chat.id,
                await format_log(
                    action="Message Pinned",
                    chat=message.chat.title,
                    admin=message.from_user.first_name,
                    pinned_link=pinned_link,
                ),
            )

        else:
            # No message to pin
            await message.reply_text("𝖱𝖾𝗉𝗅𝗒 𝖳𝗈 𝖠 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖮𝗋 𝖯𝗋𝗈𝗏𝗂𝖽𝖾 𝖳𝖾𝗑𝗍 𝖳𝗈 𝖯𝗂𝗇.")
    except ChatAdminRequired:
        await message.reply(CHAT_ADMIN_REQUIRED)
    except Exception as e:
        print(f"Error in pin_message: {e}")

# Unpin a specific message
@app.on_message(filters.command("unpin" , prefixes=c.COMMAND_PREFIXES) & filters.group)
@app.on_message(filters.regex(r"^(?i)Unpin It$") & filters.group & filters.reply)
@can_pin_messages
@error
@save
async def unpin_message(client, message: Message):
    
    try :
        if message.reply_to_message:
            await app.unpin_chat_message(chat_id= message.chat.id , message_id = message.reply_to_message.id)
            await message.reply_text(f"𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖴𝗇𝗉𝗂𝗇𝗇𝖾𝖽 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 𝖨𝗇 {message.chat.title}!")
        
        elif len(message.command) > 1:
            # Pin a new message with provided text
            msg_text = message.text.split(None, 1)[1]
            if msg_text.lower() == "all":
                await message.chat.unpin_all_messages()
                await message.reply_text(f"𝖠𝗅𝗅 𝖯𝗂𝗇𝗇𝖾𝖽 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖧𝖺𝗏𝖾 𝖡𝖾𝖾𝗇 𝖴𝗇𝗉𝗂𝗇𝗇𝖾𝖽 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 𝖨𝗇 {message.chat.title}!")

            await send_log(
                message.chat.id,
                await format_log(
                    action="Message Unpinned",
                    chat=message.chat.title,
                    admin=message.from_user.first_name
                )
            )

        else:
            await message.reply_text("𝖱𝖾𝗉𝗅𝗒 𝖳𝗈 𝖺 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖳𝗈 𝖴𝗇𝗉𝗂𝗇.")
    except ChatAdminRequired:
        await message.reply(CHAT_ADMIN_REQUIRED)


@app.on_message(filters.command("pinned" , prefixes=c.COMMAND_PREFIXES) & filters.group)
@can_pin_messages
@error
@save
async def get_last_pinned(client, message: Message):
    try:
        # Fetch chat details including pinned_message
        chat = await client.get_chat(message.chat.id)
        pinned_message = chat.pinned_message

        if pinned_message:
            chat_id = str(message.chat.id).removeprefix("-100")  # Remove the -100 prefix
            if message.chat.username:
                await message.reply_text(
                    f"𝖯𝗂𝗇𝗇𝖾𝖽 [𝖬𝖾𝗌𝗌𝖺𝗀𝖾](https://t.me/{message.chat.username}/{pinned_message.id}) 𝖨𝗇 {message.chat.title}",
                    disable_web_page_preview=True,
                )
            else:
                await message.reply_text(
                    f"𝖯𝗂𝗇𝗇𝖾𝖽 [𝖬𝖾𝗌𝗌𝖺𝗀𝖾](https://t.me/c/{chat_id}/{pinned_message.id}) 𝖨𝗇 {message.chat.title}",
                    disable_web_page_preview=True,
                )
        else:
            await message.reply_text(f"𝖭𝗈 𝖯𝗂𝗇𝗇𝖾𝖽 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖨𝗇 {message.chat.id}.")
    except ChatAdminRequired:
        await message.reply(CHAT_ADMIN_REQUIRED)

@app.on_message(filters.command(["invitelink" , "link"] , prefixes=c.COMMAND_PREFIXES) & filters.group)
@chatadmin
@error
@save
async def invite_link(client: app, message: Message):  # type: ignore
    try:
        # Get the chat details
        chat = await app.get_chat(message.chat.id)
        
        # Ensure the bot is an admin to fetch the invite link
        if not chat.permissions.can_invite_users:
            await message.reply("𝖨 𝖭𝖾𝖾𝖽 𝖳𝗈 𝖡𝖾 𝖠𝗇 𝖠𝖽𝗆𝗂𝗇 𝖶𝗂𝗍𝗁 𝖨𝗇𝗏𝗂𝗍𝖾 𝖴𝗌𝖾𝗋 𝖯𝖾𝗋𝗆𝗂𝗌𝗌𝗂𝗈𝗇𝗌 𝖳𝗈 𝖦𝖾𝗍 𝖳𝗁𝖾 𝖨𝗇𝗏𝗂𝗍𝖾 𝖫𝗂𝗇𝗄!")
            return
        
        # Get or create the invite link
        invite_link = await app.export_chat_invite_link(message.chat.id)
        link = f"https://telegram.me/share/url?url={invite_link}"
        
        # Inline keyboard with a "Share Link" button
        share_button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔗 𝖲𝗁𝖺𝗋𝖾 𝖫𝗂𝗇𝗄", url=link)]]
        )
        
        await message.reply(
            f"𝖧𝖾𝗋𝖾 𝖨𝗌 𝖳𝗁𝖾 𝖨𝗇𝗏𝗂𝗍𝖾 𝖫𝗂𝗇𝗄 𝖥𝗈𝗋 𝖳𝗁𝗂𝗌 𝖢𝗁𝖺𝗍:\n{invite_link}",
            reply_markup=share_button
        )
        
        # Log the action
        await send_log(
            message.chat.id,
            await format_log(
                action="Generated Invite Link",
                chat=message.chat.title,
                admin=message.from_user.first_name,
            ),
        )

    except ChatAdminRequired:
        await message.reply(CHAT_ADMIN_REQUIRED)
    except ChatInvalid:
        await message.reply("𝖨 𝖢𝗈𝗎𝗅𝖽𝗇'𝗍 𝖥𝖾𝗍𝖼𝗁 𝖳𝗁𝖾 𝖨𝗇𝗏𝗂𝗍𝖾 𝖫𝗂𝗇𝗄 𝖥𝗈𝗋 𝖳𝗁𝗂𝗌 𝖢𝗁𝖺𝗍.")
    except Exception as e:
        await message.reply(f"𝖠𝗇 𝖤𝗋𝗋𝗈𝗋 𝖮𝖼𝖼𝗎𝗋𝗋𝖾𝖽: {e}")

#==============================================================================================================================================#

@app.on_message(filters.command(["del" , "delete"] , prefixes=c.COMMAND_PREFIXES) & filters.group)
@app.on_message(filters.regex(r"^(del|delete)$") & filters.group & filters.reply)
@can_delete_messages
@error
@save
async def delete_message(client, message: Message):
    try:
        if message.reply_to_message:
            await message.delete()

            # Log deletion
            log_message = await format_log(
                action="Message Deleted",
                chat=message.chat.title,
                admin=message.from_user.first_name,
                user=message.reply_to_message.from_user.first_name,
            )
            log_message += f"\nMessage : {message.reply_to_message.text}"
            await message.reply_to_message.delete()
            await send_log(message.chat.id, log_message)
        else:
            await message.reply_text("𝖱𝖾𝗉𝗅𝗒 𝖳𝗈 𝖠 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖳𝗈 𝖣𝖾𝗅𝖾𝗍𝖾.")
    except ChatAdminRequired:
        await message.reply(CHAT_ADMIN_REQUIRED)

@app.on_message(filters.command("purge" , prefixes=c.COMMAND_PREFIXES) & filters.group & filters.reply)
@app.on_message(filters.regex(r"^(purge)$") & filters.group & filters.reply)
@can_delete_messages
@error
@save
async def purge(c: app, m: Message): # type: ignore

    if m.chat.type != ChatType.SUPERGROUP:
        await m.reply_text(text="𝖢𝖺𝗇𝗇𝗈𝗍 𝗉𝗎𝗋𝗀𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝗂𝗇 𝖺 𝖻𝖺𝗌𝗂𝖼 𝗀𝗋𝗈𝗎𝗉")
        return

    if m.reply_to_message:
        message_ids = list(range(m.reply_to_message.id, m.id))

        def divide_chunks(l: list, n: int = 100):
            for i in range(0, len(l), n):
                yield l[i : i + n]

        # Dielete messages in chunks of 100 messages
        m_list = list(divide_chunks(message_ids))

        try:
            for plist in m_list:
                await c.delete_messages(
                    chat_id=m.chat.id,
                    message_ids=plist,
                    revoke=True,
                )

            log_message = await format_log(
                action="Purge",
                chat=m.chat.title,
                admin=m.from_user.first_name,
            )
            await send_log(m.chat.id, log_message)

            a = await m.reply_text(f"𝖯𝗎𝗋𝗀𝖾𝖽 `{len(message_ids)}` 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖨𝗇 {m.chat.title}!")
            await asyncio.sleep(10)
            await a.delete()
            await m.delete()
        except MessageDeleteForbidden:
            await m.reply_text(
                text="𝖢𝖺𝗇𝗇𝗈𝗍 𝖽𝖾𝗅𝖾𝗍𝖾 𝖺𝗅𝗅 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌. 𝖳𝗁𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝗆𝖺𝗒 𝖻𝖾 𝗍𝗈𝗈 𝗈𝗅𝖽, 𝖨 𝗆𝗂𝗀𝗁𝗍 𝗇𝗈𝗍 𝗁𝖺𝗏𝖾 𝖽𝖾𝗅𝖾𝗍𝖾 𝗋𝗂𝗀𝗁𝗍𝗌, 𝗈𝗋 𝗍𝗁𝗂𝗌 𝗆𝗂𝗀𝗁𝗍 𝗇𝗈𝗍 𝖻𝖾 𝖺 𝗌𝗎𝗉𝖾𝗋𝗀𝗋𝗈𝗎𝗉."
            )
            return
        except RPCError:
            return


@app.on_message(filters.command("spurge" , prefixes=c.COMMAND_PREFIXES) & filters.group & filters.reply)
@app.on_message(filters.regex(r"^(spurge)$") & filters.group & filters.reply)
@can_delete_messages
@error
@save
async def spurge(c: app, m: Message): # type: ignore

    if m.chat.type != ChatType.SUPERGROUP:
        await m.reply_text(text="𝖢𝖺𝗇𝗇𝗈𝗍 𝗉𝗎𝗋𝗀𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝗂𝗇 𝖺 𝖻𝖺𝗌𝗂𝖼 𝗀𝗋𝗈𝗎𝗉")
        return

    if m.reply_to_message:
        message_ids = list(range(m.reply_to_message.id, m.id))

        def divide_chunks(l: list, n: int = 100):
            for i in range(0, len(l), n):
                yield l[i : i + n]

        # Dielete messages in chunks of 100 messages
        m_list = list(divide_chunks(message_ids))

        try:
            for plist in m_list:
                await c.delete_messages(
                    chat_id=m.chat.id,
                    message_ids=plist,
                    revoke=True,
                )

            log_message = await format_log(
                action="Silent Purge",
                chat=m.chat.title,
                admin=m.from_user.first_name,
            )
            await send_log(m.chat.id, log_message)

            await m.delete()
        except MessageDeleteForbidden:
            await m.reply_text(
                text="𝖢𝖺𝗇𝗇𝗈𝗍 𝖽𝖾𝗅𝖾𝗍𝖾 𝖺𝗅𝗅 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌. 𝖳𝗁𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝗆𝖺𝗒 𝖻𝖾 𝗍𝗈𝗈 𝗈𝗅𝖽, 𝖨 𝗆𝗂𝗀𝗁𝗍 𝗇𝗈𝗍 𝗁𝖺𝗏𝖾 𝖽𝖾𝗅𝖾𝗍𝖾 𝗋𝗂𝗀𝗁𝗍𝗌, 𝗈𝗋 𝗍𝗁𝗂𝗌 𝗆𝗂𝗀𝗁𝗍 𝗇𝗈𝗍 𝖻𝖾 𝖺 𝗌𝗎𝗉𝖾𝗋𝗀𝗋𝗈𝗎𝗉."
            )
            return
        except RPCError:
            return

#==============================================================================================================================================#

@app.on_message(filters.command(["promote" , "makeadmin"], prefixes=c.COMMAND_PREFIXES) & filters.group)
@app.on_message(filters.regex(r"^(?i)Promote (him|her)$") & filters.group & filters.reply)
@can_promote_members
@error
@save
async def promote_user(client: app, message: Message):  # type: ignore
    chat_id = message.chat.id

    if not message.from_user:
        return

    title = "Admin"  # Default admin title
    target_user = None

    # Case 1: Command is a reply
    if message.reply_to_message:
        target_user = await resolve_user(client, message)
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            title = args[1]  # Use the second argument as the title

    # Case 2: Command with username/ID and title
    else:
        args = message.text.split(maxsplit=2)
        if len(args) > 1:
            # Resolve the username or user ID
            target_user = await resolve_user(client, message)
        if len(args) > 2:
            title = args[2]  # Use the third argument as the title

    if not target_user:
        await message.reply(
            "𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖿𝗂𝗇𝖽 𝗍𝗁𝖾 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖾𝖽 𝗎𝗌𝖾𝗋. 𝖯𝗅𝖾𝖺𝗌𝖾 𝗆𝖺𝗄𝖾 𝗌𝗎𝗋𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾/𝗂𝖽 𝗂𝗌 𝗏𝖺𝗅𝗂𝖽 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾."
        )
        return

    if len(title) > 16:
        await message.reply("𝖳𝗂𝗍𝗅𝖾 𝗆𝗎𝗌𝗍 𝖻𝖾 𝗅𝖾𝗌𝗌 𝗍𝗁𝖺𝗇 16 𝖼𝗁𝖺𝗋𝖺𝖼𝗍𝖾𝗋𝗌.")
        return



    # Promote the user with the provided title
    try:

        # Check the user's current status in the chat
        x = await app.get_chat_member(chat_id, target_user.id)
    
        if x.status == ChatMemberStatus.OWNER:
            await message.reply(USER_IS_OWNER)
            return
    
        if x.status == ChatMemberStatus.ADMINISTRATOR:
            await message.reply(USER_ALREADY_PROMOTED)
            return

        # Fetch the bot's privileges from the cache or API
        cached_privileges = admin_cache.get((chat_id, app.me.id))
        if not cached_privileges:
            cached_privileges = await fetch_admin_privileges(chat_id, app.me.id)

        bot_privileges = cached_privileges.get("privileges") if cached_privileges else None

        # Adjust the promotion rights based on the bot's capabilities

        adjusted_privileges = ChatPrivileges(
                can_delete_messages=bot_privileges.can_delete_messages and PROMOTE.can_delete_messages,
                can_manage_video_chats=bot_privileges.can_manage_video_chats and PROMOTE.can_manage_video_chats,
                can_restrict_members=bot_privileges.can_restrict_members and PROMOTE.can_restrict_members,
                can_promote_members=bot_privileges.can_promote_members and PROMOTE.can_promote_members,
                can_change_info=bot_privileges.can_change_info and PROMOTE.can_change_info,
                can_invite_users=bot_privileges.can_invite_users and PROMOTE.can_invite_users,
                can_pin_messages=bot_privileges.can_pin_messages and PROMOTE.can_pin_messages,
                can_post_stories=bot_privileges.can_post_stories and PROMOTE.can_post_stories,
                can_edit_stories=bot_privileges.can_edit_stories and PROMOTE.can_edit_stories,
                can_delete_stories=bot_privileges.can_delete_stories and PROMOTE.can_delete_stories,
                is_anonymous=bot_privileges.is_anonymous and PROMOTE.is_anonymous,
            )
            
        await app.promote_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            privileges=adjusted_privileges,
            title=title,
        )

        # Construct promotion message
        promotion_message = (
            f"✪ **𝖯𝖱𝖮𝖬𝖮𝖳𝖤 𝖤𝖵𝖤𝖭𝖳**\n\n"
            f"👤 **𝖴𝗌𝖾𝗋:** {target_user.mention()} (`{target_user.id}`)\n"
            f"⬆️ **𝖯𝗋𝗈𝗆𝗈𝗍𝖾𝖽 𝖡𝗒:** {message.from_user.mention()}\n"
            f"🏷️ **𝖳𝗂𝗍𝗅𝖾:** `{title}`\n"
        )

        # Send promotion message with inline buttons
        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("𝖣𝖾𝗆𝗈𝗍𝖾", callback_data=f"demote:{target_user.id}")],
                [InlineKeyboardButton("🗑️", callback_data="delete")],
            ]
        )
        await message.reply(promotion_message, reply_markup=buttons)

        # Log the promotion event
        log_message = await format_log(
            action="Promoted User",
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
        await message.reply(f"𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖯𝗋𝗈𝗆𝗈𝗍𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋:")


@app.on_callback_query(filters.regex("^demote:(\d+)$"))
@can_promote_members
@error
async def demote_user(client: app, callback_query: CallbackQuery): # type: ignore
    if not callback_query.from_user:
        return

    user_id = int(callback_query.data.split(":")[1])
    chat_id = callback_query.message.chat.id
    d_user = await app.get_users(user_id)




    try:
        d = await app.get_chat_member(chat_id , user_id)
    
        if d.status != ChatMemberStatus.ADMINISTRATOR:
            await callback_query.message.edit_text(USER_ALREADY_DEMOTED)
            return

        await app.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=MUTE
        )

        # Demote the user
        await app.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=UNMUTE
        )
        await callback_query.answer("𝖴𝗌𝖾𝗋 𝖽𝖾𝗆𝗈𝗍𝖾𝖽 𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒.")
        await callback_query.message.edit_text(f"{d_user.mention()} 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝖽𝖾𝗆𝗈𝗍𝖾𝖽 𝖻𝗒 {callback_query.from_user.mention()}")

        # Log the promotion event
        log_message = await format_log(
            action="Demoted User",
            chat=callback_query.message.chat.title,
            admin=callback_query.message.from_user.mention(),
            user=d_user.mention(),
        )
        await send_log(chat_id, log_message)

    except ChatAdminRequired:
        await callback_query.message.edit_text(CHAT_ADMIN_REQUIRED)
    except Exception as e:
        await callback_query.answer(f"𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝖽𝖾𝗆𝗈𝗍𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋: 𝖬𝖺𝗒𝖻𝖾 𝖳𝗁𝖾𝗒 𝖠𝗋𝖾 𝖭𝗈𝗍 𝖯𝗋𝗈𝗆𝗈𝗍𝖾𝖽 𝖡𝗒 𝖬𝖾", show_alert=True)

@app.on_callback_query(filters.regex("^delete$"))
@error
async def delete_promotion_message(client: app, callback_query: CallbackQuery): # type: ignore
    try:
        await callback_query.message.delete()
        await callback_query.answer("𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖣𝖾𝗅𝖾𝗍𝖾𝖽.")
    except Exception as e:
        await callback_query.answer(f"𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝖽𝖾𝗅𝖾𝗍𝖾 𝗍𝗁𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾: {e}", show_alert=True)

@app.on_message(filters.command("demote", prefixes=c.COMMAND_PREFIXES) & filters.group)
@app.on_message(filters.regex(r"^(?i)Demote (him|her)$") & filters.group & filters.reply)
@can_promote_members
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
    
        if x.status != ChatMemberStatus.ADMINISTRATOR:
            await message.reply(USER_ALREADY_DEMOTED)
            return
        
        await app.restrict_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            permissions=MUTE
        )

        await app.restrict_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            permissions=UNMUTE
        )

        # Construct the promotion message
        promotion_message = (
            f"✪ **𝖣𝖾𝗆𝗈𝗍𝖾 𝖤𝖵𝖤𝖭𝖳**\n\n"
            f"👤 **𝖴𝗌𝖾𝗋:** {target_user.mention()} (`{target_user.id}`)\n"
            f"⬆️ **𝖣𝖾𝗆𝗈𝗍𝖾𝖽 𝖡𝗒:** {user.mention()}\n"
        )

        await message.reply(promotion_message)

        # Log the promotion event
        log_message = await format_log(
            action="Demoted User",
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
        await message.reply(f"𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝖣𝖾𝗆𝗈𝗍𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋: 𝖬𝖺𝗒𝖻𝖾 𝖳𝗁𝖾𝗒 𝖠𝗋𝖾 𝖭𝗈𝗍 𝖯𝗋𝗈𝗆𝗈𝗍𝖾𝖽 𝖡𝗒 𝖬𝖾")

@app.on_message(filters.command("lowpromote", prefixes=c.COMMAND_PREFIXES) & filters.group)
@app.on_message(filters.regex(r"^(?i)Lowpromote (him|her)$") & filters.group & filters.reply)
@can_promote_members
@error
@save
async def promote_user(client: app, message: Message):  # type: ignore
    chat_id = message.chat.id

    if not message.from_user:
        return

    title = "Admin"  # Default admin title
    target_user = None

    # Case 1: Command is a reply
    if message.reply_to_message:
        target_user = await resolve_user(client, message)
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            title = args[1]  # Use the second argument as the title

    # Case 2: Command with username/ID and title
    else:
        args = message.text.split(maxsplit=2)
        if len(args) > 1:
            # Resolve the username or user ID
            target_user = await resolve_user(client, message)
        if len(args) > 2:
            title = args[2]  # Use the third argument as the title

    if not target_user:
        await message.reply(
            "𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖿𝗂𝗇𝖽 𝗍𝗁𝖾 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖾𝖽 𝗎𝗌𝖾𝗋. 𝖯𝗅𝖾𝖺𝗌𝖾 𝗆𝖺𝗄𝖾 𝗌𝗎𝗋𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾/𝗂𝖽 𝗂𝗌 𝗏𝖺𝗅𝗂𝖽 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾."
        )
        return

    if len(title) > 16:
        await message.reply("𝖳𝗂𝗍𝗅𝖾 𝗆𝗎𝗌𝗍 𝖻𝖾 𝗅𝖾𝗌𝗌 𝗍𝗁𝖺𝗇 16 𝖼𝗁𝖺𝗋𝖺𝖼𝗍𝖾𝗋𝗌.")
        return



    # Promote the user with the provided title
    try:

        # Check the user's current status in the chat
        x = await app.get_chat_member(chat_id, target_user.id)
    
        if x.status == ChatMemberStatus.OWNER:
            await message.reply(USER_IS_OWNER)
            return
    
        if x.status == ChatMemberStatus.ADMINISTRATOR:
            await message.reply(USER_ALREADY_PROMOTED)
            return

        # Fetch the bot's privileges from the cache or API
        cached_privileges = admin_cache.get((chat_id, app.me.id))
        if not cached_privileges:
            cached_privileges = await fetch_admin_privileges(chat_id, app.me.id)

        bot_privileges = cached_privileges.get("privileges") if cached_privileges else None

        # Adjust the promotion rights based on the bot's capabilities

        adjusted_privileges = ChatPrivileges(
                can_delete_messages=bot_privileges.can_delete_messages and LOWPROMOTE.can_delete_messages,
                can_manage_video_chats=bot_privileges.can_manage_video_chats and LOWPROMOTE.can_manage_video_chats,
                can_restrict_members=bot_privileges.can_restrict_members and LOWPROMOTE.can_restrict_members,
                can_promote_members=bot_privileges.can_promote_members and LOWPROMOTE.can_promote_members,
                can_change_info=bot_privileges.can_change_info and LOWPROMOTE.can_change_info,
                can_invite_users=bot_privileges.can_invite_users and LOWPROMOTE.can_invite_users,
                can_pin_messages=bot_privileges.can_pin_messages and LOWPROMOTE.can_pin_messages,
                can_post_stories=bot_privileges.can_post_stories and LOWPROMOTE.can_post_stories,
                can_edit_stories=bot_privileges.can_edit_stories and LOWPROMOTE.can_edit_stories,
                can_delete_stories=bot_privileges.can_delete_stories and LOWPROMOTE.can_delete_stories,
                is_anonymous=bot_privileges.is_anonymous and LOWPROMOTE.is_anonymous,
            )


        await app.promote_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            privileges=adjusted_privileges,
            title=title,
        )

        # Construct promotion message
        promotion_message = (
            f"✪ **𝖫𝖮𝖶-𝖯𝖱𝖮𝖬𝖮𝖳𝖤 𝖤𝖵𝖤𝖭𝖳**\n\n"
            f"👤 **𝖴𝗌𝖾𝗋:** {target_user.mention()} (`{target_user.id}`)\n"
            f"⬆️ **𝖯𝗋𝗈𝗆𝗈𝗍𝖾𝖽 𝖡𝗒:** {message.from_user.mention()}\n"
            f"🏷️ **𝖳𝗂𝗍𝗅𝖾:** `{title}`\n"
        )

        # Send promotion message with inline buttons
        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("𝖣𝖾𝗆𝗈𝗍𝖾", callback_data=f"demote:{target_user.id}")],
                [InlineKeyboardButton("🗑️", callback_data="delete")],
            ]
        )
        await message.reply(promotion_message, reply_markup=buttons)

        # Log the promotion event
        log_message = await format_log(
            action="Low Promoted User",
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
        await message.reply(f"𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖯𝗋𝗈𝗆𝗈𝗍𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋: {e}")


@app.on_message(filters.command("fullpromote", prefixes=c.COMMAND_PREFIXES) & filters.group)
@app.on_message(filters.regex(r"^(?i)Fullpromote (him|her)$") & filters.group & filters.reply)
@can_promote_members
@error
@save
async def promote_user(client: app, message: Message):  # type: ignore
    chat_id = message.chat.id

    if not message.from_user:
        return

    title = "Admin"  # Default admin title
    target_user = None

    # Case 1: Command is a reply
    if message.reply_to_message:
        target_user = await resolve_user(client, message)
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            title = args[1]  # Use the second argument as the title

    # Case 2: Command with username/ID and title
    else:
        args = message.text.split(maxsplit=2)
        if len(args) > 1:
            # Resolve the username or user ID
            target_user = await resolve_user(client, message)
        if len(args) > 2:
            title = args[2]  # Use the third argument as the title

    if not target_user:
        await message.reply(
            "𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖿𝗂𝗇𝖽 𝗍𝗁𝖾 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖾𝖽 𝗎𝗌𝖾𝗋. 𝖯𝗅𝖾𝖺𝗌𝖾 𝗆𝖺𝗄𝖾 𝗌𝗎𝗋𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾/𝗂𝖽 𝗂𝗌 𝗏𝖺𝗅𝗂𝖽 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾."
        )
        return

    if len(title) > 16:
        await message.reply("𝖳𝗂𝗍𝗅𝖾 𝗆𝗎𝗌𝗍 𝖻𝖾 𝗅𝖾𝗌𝗌 𝗍𝗁𝖺𝗇 16 𝖼𝗁𝖺𝗋𝖺𝖼𝗍𝖾𝗋𝗌.")
        return



    # Promote the user with the provided title
    try:

        # Check the user's current status in the chat
        x = await app.get_chat_member(chat_id, target_user.id)
    
        if x.status == ChatMemberStatus.OWNER:
            await message.reply(USER_IS_OWNER)
            return
    
        if x.status == ChatMemberStatus.ADMINISTRATOR:
            await message.reply(USER_ALREADY_PROMOTED)
            return



        # Fetch the bot's privileges from the cache or API
        cached_privileges = admin_cache.get((chat_id, app.me.id))
        if not cached_privileges:
            cached_privileges = await fetch_admin_privileges(chat_id, app.me.id)

        bot_privileges = cached_privileges.get("privileges") if cached_privileges else None

        # Adjust the promotion rights based on the bot's capabilities

        adjusted_privileges = ChatPrivileges(
                can_delete_messages=bot_privileges.can_delete_messages and FULLPROMOTE.can_delete_messages,
                can_manage_video_chats=bot_privileges.can_manage_video_chats and FULLPROMOTE.can_manage_video_chats,
                can_restrict_members=bot_privileges.can_restrict_members and FULLPROMOTE.can_restrict_members,
                can_promote_members=bot_privileges.can_promote_members and FULLPROMOTE.can_promote_members,
                can_change_info=bot_privileges.can_change_info and FULLPROMOTE.can_change_info,
                can_invite_users=bot_privileges.can_invite_users and FULLPROMOTE.can_invite_users,
                can_pin_messages=bot_privileges.can_pin_messages and FULLPROMOTE.can_pin_messages,
                can_post_stories=bot_privileges.can_post_stories and FULLPROMOTE.can_post_stories,
                can_edit_stories=bot_privileges.can_edit_stories and FULLPROMOTE.can_edit_stories,
                can_delete_stories=bot_privileges.can_delete_stories and FULLPROMOTE.can_delete_stories,
                is_anonymous=bot_privileges.is_anonymous and FULLPROMOTE.is_anonymous,
            )

        await app.promote_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            privileges=adjusted_privileges,
            title=title,
        )

        # Construct promotion message
        promotion_message = (
            f"✪ **𝖥𝖴𝖫𝖫-𝖯𝖱𝖮𝖬𝖮𝖳𝖤 𝖤𝖵𝖤𝖭𝖳**\n\n"
            f"👤 **𝖴𝗌𝖾𝗋:** {target_user.mention()} (`{target_user.id}`)\n"
            f"⬆️ **𝖯𝗋𝗈𝗆𝗈𝗍𝖾𝖽 𝖡𝗒:** {message.from_user.mention()}\n"
            f"🏷️ **𝖳𝗂𝗍𝗅𝖾:** `{title}`\n"
        )

        # Send promotion message with inline buttons
        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("𝖣𝖾𝗆𝗈𝗍𝖾", callback_data=f"demote:{target_user.id}")],
                [InlineKeyboardButton("🗑️", callback_data="delete")],
            ]
        )
        await message.reply(promotion_message, reply_markup=buttons)

        # Log the promotion event
        log_message = await format_log(
            action="Full Promoted User",
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
        await message.reply(f"𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖯𝗋𝗈𝗆𝗈𝗍𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋: {e}")


@app.on_message(filters.command("title", prefixes=c.COMMAND_PREFIXES) & filters.group & filters.reply)
@can_promote_members
@error
@save
async def set_admin_title(client: app, message: Message):  # type: ignore
    chat_id = message.chat.id

    if not message.from_user:
        return

    title = "Admin"
    target_user = None

    # Case 1: Command is a reply
    if message.reply_to_message:
        target_user = await resolve_user(client, message)
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            title = args[1]  # Use the second argument as the title

    # Case 2: Command with username/ID and title
    else:
        args = message.text.split(maxsplit=2)
        if len(args) > 1:
            # Resolve the username or user ID
            target_user = await resolve_user(client, message)
        if len(args) > 2:
            title = args[2]  # Use the third argument as the title

    if not target_user:
        await message.reply(
            "𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝖿𝗂𝗇𝖽 𝗍𝗁𝖾 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖾𝖽 𝗎𝗌𝖾𝗋. 𝖯𝗅𝖾𝖺𝗌𝖾 𝗆𝖺𝗄𝖾 𝗌𝗎𝗋𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾/𝗂𝖽 𝗂𝗌 𝗏𝖺𝗅𝗂𝖽 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾."
        )
        return

    if len(title) > 16:
        await message.reply("𝖳𝗂𝗍𝗅𝖾 𝗆𝗎𝗌𝗍 𝖻𝖾 𝗅𝖾𝗌𝗌 𝗍𝗁𝖺𝗇 16 𝖼𝗁𝖺𝗋𝖺𝖼𝗍𝖾𝗋𝗌.")
        return

    # Check the user's current status in the chat
    try:
        x = await app.get_chat_member(chat_id, target_user.id)

        if x.status != ChatMemberStatus.ADMINISTRATOR:
            await message.reply("𝖳𝗁𝖾 𝗎𝗌𝖾𝗋 𝗂𝗌 𝗇𝗈𝗍 𝖺𝗇 𝖺𝖽𝗆𝗂𝗇.")
            return

        # Set the custom title for the admin
        await app.set_administrator_title(chat_id, target_user.id, title)

        await message.reply(f"𝖳𝗁𝖾 𝖠𝖽𝗆𝗂𝗇 𝗍𝗂𝗍𝗅𝖾 𝖿𝗈𝗋 {target_user.mention()} 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗎𝗉𝖽𝖺𝗍𝖾𝖽 𝗍𝗈: `{title}`")
    except ChatAdminRequired:
        await message.reply(CHAT_ADMIN_REQUIRED)
    except UserNotParticipant:
        await message.reply("𝖴𝗌𝖾𝗋 𝖨𝗌 𝖭𝗈𝗍 𝖯𝗋𝖾𝗌𝖾𝗇𝗍 𝖨𝗇 𝖳𝗁𝗂𝗌 𝖢𝗁𝖺𝗍 !!")
    except Exception as e:
        await message.reply(f"𝖴𝗇𝖺𝖻𝗅𝖾 𝗍𝗈 𝗎𝗉𝖽𝖺𝗍𝖾 𝗍𝗁𝖾 𝗍𝗂𝗍𝗅𝖾: {e}")

#==============================================================================================================================================#

@app.on_message(filters.command("adminlist") & filters.group)
@app.on_message(filters.regex(r"^(?i)Yaha Ke Majdoor$") & filters.group)
@chatadmin
@error
@save
async def admin_list(client: app, message: Message):  # type: ignore
    chat_id = message.chat.id
    
    sent = await message.reply("𝖣𝖾𝗍𝖾𝖼𝗍𝗂𝗇𝗀 𝖺𝗅𝗅 𝖺𝖽𝗆𝗂𝗇𝗌...")

    try:
        # `get_chat_members` returns an async generator, no `await` here
        admins = app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS)

        owner = None
        admins_list = []

        async for member in admins:
            user = member.user
            title = member.custom_title if member.custom_title else "Admin"

            if member.status == ChatMemberStatus.OWNER:
                owner = user.mention  # Format the Owner separately
            else:
                admins_list.append(f"• {user.mention} - `{title}`")

        # Construct the message text
        text = "**👮 Admin List:**\n"
        if owner:
            text += f"\n👑 **Owner :** {owner}\n\n"

        if admins_list:
            text += "\n".join(admins_list)
        else:
            text += "\n"

        await sent.edit_text((text))

    except ChatAdminRequired:
        await message.reply_text(CHAT_ADMIN_REQUIRED)

    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

#==============================================================================================================================================#

# /setgtitle command
@app.on_message(filters.command("setgtitle") & filters.group)
@error
@save
async def set_group_title(client: app, message: Message): # type: ignore

    new_title = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not new_title:
        return await message.reply_text("𝖯𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 𝗍𝗂𝗍𝗅𝖾 𝗍𝗈 𝗌𝖾𝗍. 𝖤𝗑𝖺𝗆𝗉𝗅𝖾: `/setgtitle New Title`")

    try:
        await app.set_chat_title(message.chat.id, new_title)
        await message.reply_text(f"𝖦𝗋𝗈𝗎𝗉 𝗍𝗂𝗍𝗅𝖾 𝗎𝗉𝖽𝖺𝗍𝖾𝖽 𝗍𝗈: **{new_title}**")
    except ChatAdminRequired:
        await message.reply_text(CHAT_ADMIN_REQUIRED)
    except Exception as e:
        await message.reply_text(f"𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽: {e}")

# /setgpic command
@app.on_message(filters.command("setgpic") & filters.group & filters.reply)
@error
@save
async def set_group_photo(client: app, message: Message): # type: ignore

    if not message.reply_to_message.photo:
        return await message.reply_text("𝖯𝗅𝖾𝖺𝗌𝖾 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺𝗇 𝗂𝗆𝖺𝗀𝖾 𝗍𝗈 𝗌𝖾𝗍 𝖺𝗌 𝗍𝗁𝖾 𝗀𝗋𝗈𝗎𝗉 𝗉𝗁𝗈𝗍𝗈.")

    try:
        photo = await message.reply_to_message.download()
        await app.set_chat_photo(message.chat.id, photo)
        await message.reply_text("𝖦𝗋𝗈𝗎𝗉 𝗉𝗁𝗈𝗍𝗈 𝗎𝗉𝖽𝖺𝗍𝖾𝖽 𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒.")

    except ChatAdminRequired:
        await message.reply_text(CHAT_ADMIN_REQUIRED)
    except Exception as e:
        await message.reply_text(f"𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽: {e}")

# /rmgpic command
@app.on_message(filters.command("rmgpic") & filters.group)
@error
@save
async def remove_group_photo(client: app, message: Message): # type: ignore
    try:
        await app.delete_chat_photo(message.chat.id)
        await message.reply_text("𝖦𝗋𝗈𝗎𝗉 𝗉𝗁𝗈𝗍𝗈 𝗋𝖾𝗆𝗈𝗏𝖾𝖽 𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒.")
    except Exception as e:
        await message.reply_text(f"𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽: {e}")

# /setdesc command
@app.on_message(filters.command("setdesc") & filters.group)
@error
@save
async def set_group_description(client: app, message: Message): # type: ignore

    new_description = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not new_description:
        return await message.reply_text("𝖯𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 𝖽𝖾𝗌𝖼𝗋𝗂𝗉𝗍𝗂𝗈𝗇 𝗍𝗈 𝗌𝖾𝗍. 𝖤𝗑𝖺𝗆𝗉𝗅𝖾: `/setdesc New Description`")

    try:
        await app.set_chat_description(message.chat.id, new_description)
        await message.reply_text("𝖦𝗋𝗈𝗎𝗉 𝖽𝖾𝗌𝖼𝗋𝗂𝗉𝗍𝗂𝗈𝗇 𝗎𝗉𝖽𝖺𝗍𝖾𝖽 𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒.")
    except ChatAdminRequired:
        await message.reply_text(CHAT_ADMIN_REQUIRED)
    except Exception as e:
        await message.reply_text(f"𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽: {e}")

#==============================================================================================================================================#

# Command: /setrule
@app.on_message(filters.command("setrule") & filters.group)
@chatadmin
@error
@save
async def set_rule(client: app, message: Message): # type: ignore
    chat_id = message.chat.id
    text = message.text.split(None, 1)  # Split command and rest of the text

    if len(text) < 2:
        await message.reply_text(
            "𝖯𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝗍𝗁𝖾 𝗋𝗎𝗅𝖾𝗌. 𝖴𝗌𝖺𝗀𝖾: /setrule <rules>",
            quote=True
        )
        return

    rules = text[1].strip()

    # Check if rules already exist
    existing_rules = await get_rules(chat_id)

    if existing_rules:
        await message.reply_text(
            "𝖱𝗎𝗅𝖾𝗌 𝖺𝗋𝖾 𝖺𝗅𝗋𝖾𝖺𝖽𝗒 𝗌𝖾𝗍 𝖿𝗈𝗋 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍. 𝖯𝗅𝖾𝖺𝗌𝖾 𝖼𝗅𝖾𝖺𝗋 𝗍𝗁𝖾𝗆 𝖿𝗂𝗋𝗌𝗍 𝗂𝖿 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗍𝗈 𝗌𝖾𝗍 𝗇𝖾𝗐 𝗋𝗎𝗅𝖾𝗌.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("𝖢𝗅𝖾𝖺𝗋 𝖱𝗎𝗅𝖾𝗌 🧹", callback_data=f"clear_rules|{chat_id}")]
            ]),
            quote=True
        )
    else:
        await set_rules(chat_id, rules)
        await message.reply_text(
            "𝖱𝗎𝗅𝖾𝗌 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 𝗌𝖾𝗍!",
            quote=True
        )

# Command: /rules
@app.on_message(filters.command("rules") & filters.group)
@error
@save
async def get_rules_command(client: app, message: Message): # type: ignore
    chat_id = message.chat.id
    chat_name = message.chat.title

    # Fetch rules
    rules = await get_rules(chat_id)

    if rules:
        await message.reply_text(
            f"<b>{chat_name}'𝗌 𝖠𝗅𝗅 𝖱𝗎𝗅𝖾𝗌:</b>\n<pre>{rules}</pre>",
            parse_mode=ParseMode.HTML,
            quote=True
        )
    else:
        await message.reply_text(
            "𝖭𝗈 𝗋𝗎𝗅𝖾𝗌 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝗌𝖾𝗍 𝖿𝗈𝗋 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.",
            quote=True
        )

# Command: /clearrule
@app.on_message(filters.command("clearrule") & filters.group)
@chatadmin
@error
@save
async def clear_rules_command(client: app, message: Message): # type: ignore
    chat_id = message.chat.id

    # Clear rules
    await clear_rules(chat_id)
    await message.reply_text(
        "𝖱𝗎𝗅𝖾𝗌 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝖼𝗅𝖾𝖺𝗋𝖾𝖽 𝖿𝗈𝗋 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.",
        quote=True
    )

# Callback query handler for clearing rules
@app.on_callback_query(filters.regex("^clear_rules\|"))
@chatadmin
@error
async def clear_rules_callback(client: app, callback_query): # type: ignore
    chat_id = int(callback_query.data.split("|")[1])

    # Clear rules
    await clear_rules(chat_id)
    await callback_query.message.edit_text(
        "𝖱𝗎𝗅𝖾𝗌 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝖼𝗅𝖾𝖺𝗋𝖾𝖽 𝖿𝗈𝗋 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍.",
    )

#==============================================================================================================================================#

@app.on_message(filters.command("userlist") & filters.group)
@chatadmin
@error
@save
async def userlist(client: app, message: Message):  # type: ignore
    chat = message.chat

    try:
        # Collect all members into a list
        members = []
        async for member in app.get_chat_members(chat.id):
            members.append(member)
        
        total_members = len(members)

        # Create a list of user details
        user_data = [
            f"{member.user.first_name or '𝖴𝗇𝗄𝗇𝗈𝗐𝗇'} : {member.user.id}"
            for member in members
        ]

        # Save user data to a file
        file_name = f"{chat.title}_𝗎𝗌𝖾𝗋𝗅𝗂𝗌𝗍.txt"
        with open(file_name, "w") as file:
            file.write("\n".join(user_data))

        # Send the file with caption
        caption = (
            f"𝖳𝗈𝗍𝖺𝗅 𝖬𝖾𝗆𝖻𝖾𝗋𝗌: {total_members}\n"
            f"𝖧𝖾𝗋𝖾 𝗂𝗌 𝗍𝗁𝖾 𝗅𝗂𝗌𝗍 𝗈𝖿 𝗎𝗌𝖾𝗋𝗌 𝗂𝗇 𝗍𝗁𝗂𝗌 𝖼𝗁𝖺𝗍."
        )

        await app.send_document(
            chat_id=chat.id,
            document=file_name,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN
        )

        # Clean up the file
        os.remove(file_name)

    except ChatAdminRequired:
        await message.reply_text(CHAT_ADMIN_REQUIRED)
    except Exception as e:
        await message.reply_text("𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽!")
        log.error(f"𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽 𝗐𝗁𝗂𝗅𝖾 𝖿𝖾𝗍𝖼𝗁𝗂𝗇𝗀 𝗎𝗌𝖾𝗋 𝗅𝗂𝗌𝗍: {e}")



__module__ = "𝖠𝖽𝗆𝗂𝗇"


__help__ = """**𝖠𝖽𝗆𝗂𝗇𝗌 𝗈𝗇𝗅𝗒:**
  ✧ `/𝗉𝗂𝗇` **:** 𝖲𝗂𝗅𝖾𝗇𝗍𝗅𝗒 𝗉𝗂𝗇𝗌 𝗍𝗁𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗋𝖾𝗉𝗅𝗂𝖾𝖽 𝗍𝗈
  ✧ `/𝗉𝗂𝗇𝗇𝖾𝖽` **:** 𝖦𝖾𝗍 𝖳𝗁𝖾 𝖫𝗂𝗇𝗄 𝖮𝖿 𝖫𝖺𝗌𝗍 𝖯𝗂𝗇𝗇𝖾𝖽 𝖬𝗌𝗀.
  ✧ `/𝗎𝗇𝗉𝗂𝗇` **:** 𝖴𝗇𝗉𝗂𝗇𝗌 𝗍𝗁𝖾 𝖼𝗎𝗋𝗋𝖾𝗇𝗍𝗅𝗒 𝗉𝗂𝗇𝗇𝖾𝖽 𝗆𝖾𝗌𝗌𝖺𝗀𝖾. (𝗏𝗂𝖺 𝗋𝖾𝗉𝗅𝗒)
  ✧ `/𝗉𝗋𝗈𝗆𝗈𝗍𝖾` (𝗎𝗌𝖾𝗋) **:** 𝖯𝗋𝗈𝗆𝗈𝗍𝖾𝗌 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋 𝗋𝖾𝗉𝗅𝗂𝖾𝖽 𝗍𝗈. (𝗏𝗂𝖺 𝗁𝖺𝗇𝖽𝗅𝖾, 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒).
  ✧ `/𝖽𝖾𝗆𝗈𝗍𝖾` (𝗎𝗌𝖾𝗋) **:** 𝖣𝖾𝗆𝗈𝗍𝖾𝗌 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋 𝗋𝖾𝗉𝗅𝗂𝖾𝖽 𝗍𝗈. (𝗏𝗂𝖺 𝗁𝖺𝗇𝖽𝗅𝖾, 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒)
  ✧ `/𝗅𝗈𝗐𝗉𝗋𝗈𝗆𝗈𝗍𝖾` (𝗎𝗌𝖾𝗋) **:** 𝖯𝗋𝗈𝗆𝗈𝗍𝖾𝗌 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋 𝗋𝖾𝗉𝗅𝗂𝖾𝖽 𝗍𝗈 𝗐𝗂𝗍𝗁 𝖿𝖾𝗐 𝗋𝗂𝗀𝗁𝗍𝗌 , (𝗏𝗂𝖺 𝗁𝖺𝗇𝖽𝗅𝖾, 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒)
  ✧ `/𝖿𝗎𝗅𝗅𝗉𝗋𝗈𝗆𝗈𝗍𝖾` (𝗎𝗌𝖾𝗋) **:** 𝖯𝗋𝗈𝗆𝗈𝗍𝖾𝗌 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋 𝗋𝖾𝗉𝗅𝗂𝖾𝖽 𝗍𝗈 𝗐𝗂𝗍𝗁 𝖿𝗎𝗅𝗅 𝗋𝗂𝗀𝗁𝗍𝗌.
  ✧ `/𝗂𝗇𝗏𝗂𝗍𝖾𝗅𝗂𝗇𝗄` **:**  𝖦𝖾𝗍𝗌 𝗂𝗇𝗏𝗂𝗍𝖾𝗅𝗂𝗇𝗄.
  ✧ `/𝗍𝗂𝗍𝗅𝖾` (𝗍𝗂𝗍𝗅𝖾) **:** 𝖲𝖾𝗍𝗌 𝖺 𝖼𝗎𝗌𝗍𝗈𝗆 𝗍𝗂𝗍𝗅𝖾 𝖿𝗈𝗋 𝖺𝗇 𝖺𝖽𝗆𝗂𝗇 𝗍𝗁𝖺𝗍 𝗍𝗁𝖾 𝖻𝗈𝗍 𝗉𝗋𝗈𝗆𝗈𝗍𝖾𝖽
  ✧ `/𝖽𝖾𝗅` **:** 𝖣𝖾𝗅𝖾𝗍𝖾𝗌 𝗍𝗁𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗒𝗈𝗎 𝗋𝖾𝗉𝗅𝗂𝖾𝖽 𝗍𝗈
  ✧ `/𝖺𝖽𝗆𝗂𝗇𝗅𝗂𝗌𝗍` **:** 𝖦𝖾𝗍 𝖳𝗁𝖾 𝖫𝗂𝗌𝗍 𝖮𝖿 𝖠𝗅𝗅 𝖠𝖽𝗆𝗂𝗇𝗌 𝖨𝗇 𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖢𝗁𝖺𝗍.
  ✧ `/𝗌𝖾𝗍𝗀𝗍𝗂𝗍𝗅𝖾` (𝗍𝗂𝗍𝗅𝖾)**:** 𝖲𝖾𝗍 𝗀𝗋𝗈𝗎𝗉 𝗍𝗂𝗍𝗅𝖾.
  ✧ `/𝗌𝖾𝗍𝗀𝗉𝗂𝖼` **:** 𝖱𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺𝗇 𝗂𝗆𝖺𝗀𝖾 𝗍𝗈 𝗌𝖾𝗍 𝖺𝗌 𝗀𝗋𝗈𝗎𝗉 𝗉𝗁𝗈𝗍𝗈.
  ✧ `/𝗋𝗆𝗀𝗉𝗂𝖼` **:** 𝖱𝖾𝗆𝗈𝗏𝖾 𝖦𝗋𝗈𝗎𝗉 𝖯𝗂𝖼.
  ✧ `/𝗌𝖾𝗍𝖽𝖾𝗌𝖼` (𝖽𝖾𝗌𝖼) **:** 𝖲𝖾𝗍 𝗀𝗋𝗈𝗎𝗉 𝖽𝖾𝗌𝖼𝗋𝗂𝗉𝗍𝗂𝗈𝗇.
  ✧ `/𝗋𝗎𝗅𝖾𝗌` **:** 𝖲𝗁𝗈𝗐 𝖱𝗎𝗅𝖾𝗌 𝖮𝖿 𝖳𝗁𝗂𝗌 𝖢𝗁𝖺𝗍.
  ✧ `/𝗌𝖾𝗍𝗋𝗎𝗅𝖾𝗌` (𝗋𝗎𝗅𝖾𝗌) **:** 𝖲𝖾𝗍 𝖱𝗎𝗅𝖾𝗌 𝖥𝗈𝗋 𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖢𝗁𝖺𝗍.
  ✧ `/𝖼𝗅𝖾𝖺𝗋𝗋𝗎𝗅𝖾𝗌` **:** 𝖱𝖾𝗌𝖾𝗍 𝖳𝗁𝖾 𝖱𝗎𝗅𝖾𝗌 𝖥𝗈𝗋 𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖢𝗁𝖺𝗍.
  ✧ `/𝗉𝗎𝗋𝗀𝖾` **:** 𝖣𝖾𝗅𝖾𝗍𝖾𝗌 𝖺𝗅𝗅 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖻𝖾𝗍𝗐𝖾𝖾𝗇 𝗍𝗁𝗂𝗌 𝖺𝗇𝖽 𝗍𝗁𝖾 𝗋𝖾𝗉𝗅𝗂𝖾𝖽 𝗍𝗈 𝗆𝖾𝗌𝗌𝖺𝗀𝖾.
  ✧ `/𝗌𝗉𝗎𝗋𝗀𝖾` **:** 𝖣𝖾𝗅𝖾𝗍𝖾𝗌 𝗍𝗁𝖾 𝗋𝖾𝗉𝗅𝗂𝖾𝖽 𝗆𝖾𝗌𝗌𝖺𝗀𝖾, 𝖺𝗇𝖽 𝖷 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖿𝗈𝗅𝗅𝗈𝗐𝗂𝗇𝗀 𝗂𝗍 𝗂𝖿 𝗋𝖾𝗉𝗅𝗂𝖾𝖽 𝗍𝗈 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾.
  ✧ `/𝗎𝗌𝖾𝗋𝗅𝗂𝗌𝗍` **:** 𝖦𝖾𝗍 𝖳𝗁𝖾 𝖫𝗂𝗌𝗍 𝖮𝖿 𝖠𝗅𝗅 𝖴𝗌𝖾𝗋𝗌 𝖨𝗇 𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖢𝗁𝖺𝗍.
"""