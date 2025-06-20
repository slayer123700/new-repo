from shigaraki import app , admin_cache_ptb , ptb
from pyrogram.errors import RPCError
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message , ChatPrivileges , ChatPermissions
from pyrogram.errors import PeerIdInvalid
from telegram import Update, ChatMember
from telegram.ext import ContextTypes 
from telegram.error import BadRequest , Forbidden
from pyrogram.types import ChatPermissions
from threading import RLock
from time import perf_counter
from cachetools import TTLCache

# stores admemes in memory for 10 min.
ADMIN_CACHE = TTLCache(maxsize=512, ttl=60 * 10, timer=perf_counter)
THREAD_LOCK = RLock()

async def resolve_user(client: app, message: Message):  # type: ignore
    try:
        if message.reply_to_message and message.reply_to_message.from_user:
            return message.reply_to_message.from_user

        if message.command:
            args = message.command[1:]
            if args:
                query = args[0]

                if query.isdigit():
                    try:
                        return await app.get_users(int(query))
                    except RPCError:
                        return None

                if query.startswith("@"):
                    try:
                        return await app.get_users(query)
                    except RPCError:
                        return None

        if message.entities:
            for entity in message.entities:
                if entity.type == MessageEntityType.TEXT_MENTION and entity.user:
                    return entity.user

        return None

    except PeerIdInvalid:
        return None


DEMOTE = ChatPrivileges(
                            can_delete_messages = False,
                            can_manage_video_chats = False,
                            can_restrict_members = False,
                            can_promote_members = False,
                            can_change_info = False,
                            can_edit_messages = False,
                            can_invite_users = False,
                            can_pin_messages = False,
                            can_post_stories = False,
                            can_edit_stories = False,
                            can_delete_stories = False,
                            is_anonymous = False
            )

PROMOTE = ChatPrivileges(
                            can_delete_messages = True,
                            can_manage_video_chats = True,
                            can_restrict_members = False,
                            can_promote_members = False,
                            can_change_info = False,
                            can_invite_users = True,
                            can_pin_messages = True,
                            can_post_stories = True,
                            can_edit_stories = False,
                            can_delete_stories = False,
                            is_anonymous = False
            )

FULLPROMOTE = ChatPrivileges(
                            can_delete_messages = True,
                            can_manage_video_chats = True,
                            can_restrict_members = True,
                            can_promote_members = True,
                            can_change_info = True,
                            can_invite_users = True,
                            can_pin_messages = True,
                            can_post_stories = True,
                            can_edit_stories = True,
                            can_delete_stories = True,
                            is_anonymous = False
            )

LOWPROMOTE = ChatPrivileges(
                            can_delete_messages = False,
                            can_manage_video_chats = False,
                            can_restrict_members = False,
                            can_promote_members = False,
                            can_change_info = False,
                            can_invite_users = True,
                            can_pin_messages = True,
                            can_post_stories = False,
                            can_edit_stories = False,
                            can_delete_stories = False,
                            is_anonymous = False
            )

async def resolve_user_for_afk(client: app, message: Message):  # type: ignore
    try:
        if message.reply_to_message and message.reply_to_message.from_user:
            return message.reply_to_message.from_user

        if message.command:
            args = message.command[1:]
            if args:
                query = args[0]

                if query.isdigit():
                    try:
                        return await app.get_users(int(query))
                    except RPCError:
                        return None

                if query.startswith("@"):
                    try:
                        return await app.get_users(query)
                    except RPCError:
                        return None

        if message.entities:
            for entity in message.entities:
                if entity.type == MessageEntityType.TEXT_MENTION and entity.user:
                    return entity.user
                elif entity.type == MessageEntityType.MENTION and entity.user:
                    return entity.user

        return None

    except PeerIdInvalid:
        return None

MUTE = ChatPermissions(all_perms=False)
UNMUTE = ChatPermissions(
    can_send_messages = True ,
    can_send_media_messages = True ,
    can_add_web_page_previews = True ,
    can_send_audios = True ,
    can_send_docs = True ,
    can_send_games = True ,
    can_send_gifs = True ,
    can_send_inline = True ,
    can_send_photos = True ,
    can_send_stickers = True ,
    can_send_videos = True ,
    can_send_voices = True
)
RESTRICT = ChatPermissions(
    can_send_messages = True ,
    can_send_media_messages = False ,
    can_add_web_page_previews = False ,
    can_send_audios = False ,
    can_send_docs = False ,
    can_send_games = False ,
    can_send_gifs = False ,
    can_send_inline = True ,
    can_send_photos = True ,
    can_send_stickers = True ,
    can_send_videos = False ,
    can_send_voices = False
)


async def update_admin_cache(chat_id: int, context: ContextTypes.DEFAULT_TYPE):

    try:
        # Fetch chat administrators
        admins = await context.bot.get_chat_administrators(chat_id)

        # Iterate through all admins and update the cache
        for admin in admins:
            user_id = admin.user.id

            # Cache the admin status (True for OWNER or ADMINISTRATOR)
            admin_cache_ptb[(chat_id, user_id)] = admin.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]

            # Cache specific rights if the admin is not the OWNER
            if admin.status == ChatMember.ADMINISTRATOR:
                rights = [
                    'can_manage_chat',
                    'can_delete_messages',
                    'can_manage_video_chats',
                    'can_restrict_members',
                    'can_promote_members',
                    'can_change_info',
                    'can_invite_users',
                ]
                for right in rights:
                    admin_cache_ptb[(chat_id, user_id, right)] = getattr(admin, right, False)

            # OWNER has all rights, so set them to True
            elif admin.status == ChatMember.OWNER:
                rights = [
                    'can_manage_chat',
                    'can_delete_messages',
                    'can_manage_video_chats',
                    'can_restrict_members',
                    'can_promote_members',
                    'can_change_info',
                    'can_invite_users',
                ]
                for right in rights:
                    admin_cache_ptb[(chat_id, user_id, right)] = True

    except (BadRequest, Forbidden) as e:
        # Handle API errors gracefully
        print(f"Failed to fetch administrators for chat {chat_id}: {e}")



async def is_user_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:

    chat = update.effective_chat

    with THREAD_LOCK:
        # try to fetch from cache first.
        try:
            return user_id in ADMIN_CACHE[chat.id]
        except (KeyError, IndexError):
            # keyerror happend means cache is deleted,
            # so query bot api again and return user status
            # while saving it in cache for future useage...
            chat_admins = await ptb.bot.getChatAdministrators(chat.id)
            admin_list = [x.user.id for x in chat_admins]
            ADMIN_CACHE[chat.id] = admin_list

            return user_id in admin_list

async def has_admin_right(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, right: str) -> bool:
    chat_id = update.effective_chat.id
    cache_key = (chat_id, user_id, right)


    if cache_key in admin_cache_ptb:
        return admin_cache_ptb[cache_key]

    # If not cached, update the cache and check again
    await update_admin_cache(chat_id, context)
    return admin_cache_ptb.get(cache_key, False)


# Define permissions for night mode
NIGHT_MODE_PERMISSIONS = ChatPermissions(
    can_send_messages = True ,
    can_send_media_messages = False,
    can_send_polls = False,
    can_add_web_page_previews = False ,
    can_change_info = False,
    can_invite_users = False,
    can_pin_messages = False,
    can_manage_topics = False,
    can_send_audios = False,
    can_send_docs = False,
    can_send_games = False,
    can_send_gifs = False,
    can_send_inline = False,
    can_send_photos = False,
    can_send_plain = False,
    can_send_roundvideos =False ,
    can_send_stickers = False,
    can_send_videos = False,
    can_send_voices = False
)

DEFAULT_PERMISSIONS = ChatPermissions(
    can_send_messages = True ,
    can_send_media_messages = True,
    can_send_polls = True,
    can_add_web_page_previews = True ,
    can_change_info = False,
    can_invite_users = True,
    can_pin_messages = False,
    can_manage_topics = False,
    can_send_audios = True,
    can_send_docs = True,
    can_send_games = True,
    can_send_gifs = True,
    can_send_inline = True,
    can_send_photos = True,
    can_send_plain = True,
    can_send_roundvideos =True ,
    can_send_stickers = True,
    can_send_videos = True,
    can_send_voices = True
)