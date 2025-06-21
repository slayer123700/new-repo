from pyrogram.types import Message, CallbackQuery, ChatMember
from pyrogram.enums import ChatMemberStatus , ChatMembersFilter
from functools import wraps
from shigaraki import app , admin_cache , log
from pyrogram.errors import RPCError
import json
from shigaraki.yumeko import USER_NOT_ADMIN

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

async def cache_all_admin(chat_id):
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

async def fetch_admin_privileges(chat_id, user_id):
    """Fetch admin privileges from the Telegram API and cache them."""
    try :
        await cache_all_admin(chat_id)
        privileges = admin_cache.get((chat_id, user_id))
        return privileges
    except :
        return

def ensure_privilege(privilege_name):
    def decorator(func):
        @wraps(func)
        async def wrapper(client: app, update, *args, **kwargs):  # type: ignore
            if isinstance(update, Message):
                user_id = update.from_user.id
            elif isinstance(update, CallbackQuery):
                user_id = update.from_user.id
            else:
                return

            # Dynamically fetch privileged users
            privileged_users = get_privileged_users()

            # Allow privileged users to bypass checks
            if user_id in privileged_users:
                return await func(client, update, *args, **kwargs)

            # Fetch admin privileges if not privileged
            chat_id = update.chat.id if isinstance(update, Message) else update.message.chat.id
            cached_privileges = admin_cache.get((chat_id, user_id))
            if not cached_privileges:
                cached_privileges = await fetch_admin_privileges(chat_id, user_id)

            member = await app.get_chat_member(chat_id, user_id)
            if not member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                if isinstance(update, Message):
                    await update.reply(USER_NOT_ADMIN)
                elif isinstance(update, CallbackQuery):
                    await update.answer(USER_NOT_ADMIN, show_alert=True)
                return

            privileges_obj = cached_privileges["privileges"]
            if not privileges_obj or not getattr(privileges_obj, privilege_name, False):
                if isinstance(update, Message):
                    await update.reply(f"𝖸𝗈𝗎 𝖭𝖾𝖾𝖽 𝖳𝗁𝖾 `{privilege_name}` 𝖯𝗋𝗂𝗏𝗂𝗅𝖾𝗀𝖾 𝖳𝗈 𝖴𝗌𝖾 𝖳𝗁𝗂𝗌 𝖢𝗈𝗆𝗆𝖺𝗇𝖽.")
                elif isinstance(update, CallbackQuery):
                    await update.answer(f"𝖸𝗈𝗎 𝖭𝖾𝖾𝖽 𝖳𝗁𝖾 '{privilege_name}' 𝖯𝗋𝗂𝗏𝗂𝗅𝖾𝗀𝖾 𝖳𝗈 𝖴𝗌𝖾 𝖳𝗁𝗂𝗌.", show_alert=True)
                return

            return await func(client, update, *args, **kwargs)

        return wrapper
    return decorator

def can_manage_chat(func):
    return ensure_privilege("can_manage_chat")(func)

def can_delete_messages(func):
    return ensure_privilege("can_delete_messages")(func)

def can_manage_video_chats(func):
    return ensure_privilege("can_manage_video_chats")(func)

def can_restrict_members(func):
    return ensure_privilege("can_restrict_members")(func)

def can_promote_members(func):
    return ensure_privilege("can_promote_members")(func)

def can_change_info(func):
    return ensure_privilege("can_change_info")(func)

def can_post_messages(func):
    return ensure_privilege("can_post_messages")(func)

def can_edit_messages(func):
    return ensure_privilege("can_edit_messages")(func)

def can_invite_users(func):
    return ensure_privilege("can_invite_users")(func)

def can_pin_messages(func):
    return ensure_privilege("can_pin_messages")(func)

def is_anonymous(func):
    return ensure_privilege("is_anonymous")(func)

#==================================================================================================================================#

def ensure_admin_or_owner(required_role=None):
    """
    Ensure the user is an admin or owner. Optionally specify required_role ('admin' or 'owner').
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(client, update, *args, **kwargs):
            if isinstance(update, Message):
                chat_id = update.chat.id
                user_id = update.from_user.id
            elif isinstance(update, CallbackQuery):
                chat_id = update.message.chat.id
                user_id = update.from_user.id
            else:
                await update.reply("Unsupported update type.")
                return

            # Dynamically fetch privileged users
            privileged_users = get_privileged_users()

            # Allow privileged users to bypass checks
            if user_id in privileged_users:
                return await func(client, update, *args, **kwargs)

            try:
                member_status = await client.get_chat_member(chat_id, user_id)

                is_admin = member_status.status in [
                    ChatMemberStatus.ADMINISTRATOR,
                    ChatMemberStatus.OWNER,
                ]
                is_owner = member_status.status == ChatMemberStatus.OWNER

                if not is_admin:
                    if isinstance(update, Message):
                        await update.reply(USER_NOT_ADMIN)
                    elif isinstance(update, CallbackQuery):
                        await update.answer(USER_NOT_ADMIN, show_alert=True)
                    return

                if required_role == "owner" and not is_owner:
                    if isinstance(update, Message):
                        await update.reply("𝖸𝗈𝗎 𝖬𝗎𝗌𝗍 𝖡𝖾 𝖳𝗁𝖾 𝖢𝗁𝖺𝗍 𝖮𝗐𝗇𝖾𝗋 𝖳𝗈 𝖴𝗌𝖾 𝖳𝗁𝗂𝗌 𝖢𝗈𝗆𝗆𝖺𝗇𝖽.")
                    elif isinstance(update, CallbackQuery):
                        await update.answer("𝖸𝗈𝗎 𝖬𝗎𝗌𝗍 𝖡𝖾 𝖳𝗁𝖾 𝖢𝗁𝖺𝗍 𝖮𝗐𝗇𝖾𝗋 𝖳𝗈 𝖴𝗌𝖾 𝖳𝗁𝗂𝗌.", show_alert=True)
                    return

                return await func(client, update, *args, **kwargs)

            except RPCError as e:
                log.info(f"Failed to verify privileges: {e}")
                if isinstance(update, Message):
                    return
                elif isinstance(update, CallbackQuery):
                    return

        return wrapper
    return decorator


def chatadmin(func):
    return ensure_admin_or_owner(required_role="admin")(func)

def chatowner(func):
    return ensure_admin_or_owner(required_role="owner")(func)

