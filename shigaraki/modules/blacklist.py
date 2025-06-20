from pyrogram import Client, filters
from pyrogram.types import Message
from shigaraki.database.blacklistdb import (
    add_blacklisted_word,
    remove_blacklisted_word,
    get_blacklisted_words,
    set_blacklist_mode,
    get_blacklist_mode,
    add_blacklisted_sticker,
    remove_blacklisted_sticker,
    get_blacklisted_stickers,
)
from shigaraki.database.approve_db import is_user_approved
from shigaraki import app , BLACKLIST_GROUP
from pyrogram.enums import ParseMode
from pyrogram import types 
import time
import re
from shigaraki.decorator.chatadmin import chatadmin , can_restrict_members
from config import config 
from shigaraki.database.warn_db import add_warn , MAX_WARNS
from pyrogram.errors import ChatAdminRequired
from shigaraki.helper.log_helper import send_log, format_log
from shigaraki.decorator.save import save 
from shigaraki.decorator.errors import error 

@app.on_message(filters.command("blacklist" , config.COMMAND_PREFIXES) & filters.group)
@chatadmin
@error
@save
async def blacklist_command(client: Client, message: Message):
    chat_id = message.chat.id
    words = await get_blacklisted_words(chat_id)
    if not words:
        await message.reply(f"𝖭𝗈 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽 𝗐𝗈𝗋𝖽𝗌 𝖿𝗈𝗎𝗇𝖽 𝖿𝗈𝗋 {message.chat.title}.")
    else:
        word_list = "\n".join(f"- <code>{word}</code>" for word in words)
        await message.reply(f"𝖠𝗅𝗅 𝖡𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽 𝖶𝗈𝗋𝖽𝗌 𝖠𝖼𝗍𝗂𝗏𝖾 𝖨𝗇 {message.chat.title}:\n{word_list}", parse_mode=ParseMode.HTML)


@app.on_message(filters.command("addblacklist" , config.COMMAND_PREFIXES) & filters.group)
@chatadmin
@error
@save
async def add_blacklist_command(client: Client, message: Message):
    chat_id = message.chat.id
    words = message.text.split()[1:]
    if not words:
        await message.reply("𝖸𝗈𝗎 𝗆𝗎𝗌𝗍 𝗌𝗉𝖾𝖼𝗂𝖿𝗒 𝗐𝗈𝗋𝖽𝗌 𝗍𝗈 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍!")
        return

    already_blacklisted = []
    newly_added = []
    for word in words:
        if word in await get_blacklisted_words(chat_id):
            already_blacklisted.append(word)
        else:
            await add_blacklisted_word(chat_id, word)
            newly_added.append(word)
    
    response = ""
    if newly_added:
        response += f"𝖠𝖽𝖽𝖾𝖽 𝖺 𝗐𝗈𝗋𝖽 𝗍𝗈 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍 𝗂𝗇 {message.chat.title}: {', '.join(newly_added)}.\n"
    if already_blacklisted:
        response += f"𝖠𝗅𝗋𝖾𝖺𝖽𝗒 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽: {', '.join(already_blacklisted)}."
    await message.reply(response)


@app.on_message(filters.command("unblacklist" , config.COMMAND_PREFIXES) & filters.group)
@chatadmin
@error
@save
async def remove_blacklist_command(client: Client, message: Message):
    chat_id = message.chat.id
    words = message.text.split()[1:]
    if not words:
        await message.reply("𝖸𝗈𝗎 𝗆𝗎𝗌𝗍 𝗌𝗉𝖾𝖼𝗂𝖿𝗒 𝗐𝗈𝗋𝖽𝗌 𝗍𝗈 𝗋𝖾𝗆𝗈𝗏𝖾 𝖿𝗋𝗈𝗆 𝗍𝗁𝖾 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍!")
        return

    not_blacklisted = []
    removed = []
    for word in words:
        if word not in await get_blacklisted_words(chat_id):
            not_blacklisted.append(word)
        else:
            await remove_blacklisted_word(chat_id, word)
            removed.append(word)
    
    response = ""
    if removed:
        response += f"𝖱𝖾𝗆𝗈𝗏𝖾𝖽 𝖺 𝗐𝗈𝗋𝖽 𝖿𝗋𝗈𝗆 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍 𝗂𝗇 {message.chat.title}: {', '.join(removed)}.\n"
    if not_blacklisted:
        response += f"Not blacklisted: {', '.join(not_blacklisted)}."
    await message.reply(response)


@app.on_message(filters.command("blacklistmode" , config.COMMAND_PREFIXES) & filters.group)
@can_restrict_members
@error
@save
async def blacklist_mode_command(client: Client, message: Message):
    chat_id = message.chat.id
    args = message.text.split()[1:]
    if not args or args[0] not in ["off", "del", "warn", "ban", "kick", "mute"]:
        await message.reply("𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝗆𝗈𝖽𝖾! 𝖴𝗌𝖺𝗀𝖾: /𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝗆𝗈𝖽𝖾 <𝗈𝖿𝖿/𝗐𝖺𝗋𝗇/𝖻𝖺𝗇/𝗄𝗂𝖼𝗄/𝗆𝗎𝗍𝖾>")
        return

    mode = args[0]
    duration = int(args[1]) if len(args) > 1 and mode in ["tban", "tmute"] else 0
    await set_blacklist_mode(chat_id, mode, duration)
    await message.reply(f"𝖡𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍 𝗆𝗈𝖽𝖾 𝗌𝖾𝗍 𝗍𝗈 {mode} 𝗂𝗇 {message.chat.title}.")


@app.on_message(filters.command("blsticker" , config.COMMAND_PREFIXES) & filters.group)
@chatadmin
@error
@save
async def blsticker_command(client: Client, message: Message):
    chat_id = message.chat.id
    stickers = await get_blacklisted_stickers(chat_id)
    
    if not stickers:
        await message.reply(f"𝖭𝗈 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽 𝗌𝗍𝗂𝖼𝗄𝖾𝗋𝗌 𝖿𝗈𝗎𝗇𝖽 𝗂𝗇 <b>{message.chat.title}</b>.", parse_mode=ParseMode.HTML)
    else:
        sticker_list = "\n".join(f"- <code>{sticker}</code>" for sticker in stickers)
        await message.reply(
            f"<b>𝖡𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽 𝖲𝗍𝗂𝖼𝗄𝖾𝗋𝗌 𝗂𝗇 {message.chat.title}:</b>\n{sticker_list}",
            parse_mode=ParseMode.HTML
        )


@app.on_message(filters.command("addblsticker" , config.COMMAND_PREFIXES) & filters.group)
@chatadmin
@error
@save
async def add_blsticker_command(client: Client, message: Message):
    chat_id = message.chat.id
    if not message.reply_to_message or not message.reply_to_message.sticker:
        await message.reply("𝖱𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗌𝗍𝗂𝖼𝗄𝖾𝗋 𝗍𝗈 𝖺𝖽𝖽 𝗂𝗍 𝗍𝗈 𝗍𝗁𝖾 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍.")
        return

    sticker_id = message.reply_to_message.sticker.file_unique_id
    if sticker_id in await get_blacklisted_stickers(chat_id):
        await message.reply(f"𝖳𝗁𝗂𝗌 𝗌𝗍𝗂𝖼𝗄𝖾𝗋 𝗂𝗌 𝖺𝗅𝗋𝖾𝖺𝖽𝗒 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽 𝗂𝗇 {message.chat.title}.\n- {sticker_id}")
    else:
        await add_blacklisted_sticker(chat_id, sticker_id)
        await message.reply(f"𝖠𝖽𝖽𝖾𝖽 𝖺 𝖲𝗍𝗂𝖼𝗄𝖾𝗋 𝖳𝗈 𝖡𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍 𝖨𝗇 {message.chat.title}.\n- {sticker_id}")


@app.on_message(filters.command("unblsticker" , config.COMMAND_PREFIXES) & filters.group)
@chatadmin
@error
@save
async def remove_blsticker_command(client: Client, message: Message):
    chat_id = message.chat.id
    args = message.text.split()[1:]
    
    # Get sticker ID from reply or command argument
    sticker_id = None
    if message.reply_to_message and message.reply_to_message.sticker:
        sticker_id = message.reply_to_message.sticker.file_id
    elif args:
        sticker_id = args[0]
    
    if not sticker_id:
        await message.reply("𝖸𝗈𝗎 𝗆𝗎𝗌𝗍 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗌𝗍𝗂𝖼𝗄𝖾𝗋 𝗈𝗋 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 𝗌𝗍𝗂𝖼𝗄𝖾𝗋 𝖨𝖣 𝗍𝗈 𝗋𝖾𝗆𝗈𝗏𝖾 𝗂𝗍 𝖿𝗋𝗈𝗆 𝗍𝗁𝖾 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍.")
        return

    # Check if the sticker is blacklisted
    if sticker_id not in await get_blacklisted_stickers(chat_id):
        await message.reply(f"𝖳𝗁𝗂𝗌 𝗌𝗍𝗂𝖼𝗄𝖾𝗋 𝗂𝗌 𝗇𝗈𝗍 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽 𝗂𝗇 <b>{message.chat.title}</b>.\n- <code>{sticker_id}</code>", parse_mode=ParseMode.HTML)
    else:
        await remove_blacklisted_sticker(chat_id, sticker_id)
        await message.reply(f"𝖱𝖾𝗆𝗈𝗏𝖾𝖽 𝗍𝗁𝖾 𝗌𝗍𝗂𝖼𝗄𝖾𝗋 𝖿𝗋𝗈𝗆 𝗍𝗁𝖾 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍 𝗂𝗇 <b>{message.chat.title}</b>.\n- <code>{sticker_id}</code>", parse_mode=ParseMode.HTML)


@app.on_message(filters.group & ~filters.me, BLACKLIST_GROUP)
@error
@save
async def blacklist_handler(client: Client, message: Message):
    
    if not message.from_user:
        return

    chat_id = message.chat.id
    blacklist_mode = await get_blacklist_mode(chat_id)
    blacklisted_words = await get_blacklisted_words(chat_id)
    blacklisted_stickers = await get_blacklisted_stickers(chat_id)



    if await is_user_approved(chat_id , message.from_user.id):
        return

    if message.text:
        for word in blacklisted_words:
            # Use regex to match whole words only
            if re.search(rf"\\b{re.escape(word)}\\b", message.text, flags=re.IGNORECASE):
                await message.delete()
                await take_action(client, message, blacklist_mode)
                return

    if message.sticker and message.sticker.file_unique_id in blacklisted_stickers:
        await message.delete()
        await take_action(client, message, blacklist_mode)
        return


async def take_action(client: Client, message: Message, blacklist_mode: dict):
    try:
        mode = blacklist_mode["mode"]
        duration = blacklist_mode.get("duration", 0)
        if duration == 0:
            d = "Permanent"
        else:
            d = duration

        log_message = None  # Initialize log_message

        if mode == "del":
            log_message = await format_log("Deleted Blacklisted Content", message.chat.title, admin=message.from_user.mention)
            await send_log(message.chat.id, log_message)
            return

        elif mode == "warn":
            warn_count = await add_warn(message.chat.id, message.from_user.id, "Blacklisted content", client)
            await message.reply(f"{message.from_user.mention}, you've been warned. Current warnings: {warn_count}/{MAX_WARNS}.")
            log_message = await format_log("Warned User", message.chat.title, admin=message.from_user.mention, user=message.from_user.mention)

        elif mode == "ban":
            await client.ban_chat_member(message.chat.id, message.from_user.id)
            await message.reply(f"{message.from_user.mention} 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝖻𝖺𝗇𝗇𝖾𝖽 𝖿𝗈𝗋 𝗎𝗌𝗂𝗇𝗀 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽 𝖼𝗈𝗇𝗍𝖾𝗇𝗍.")
            log_message = await format_log("Banned User", message.chat.title, admin=message.from_user.mention, user=message.from_user.mention)

        elif mode == "kick":
            await client.ban_chat_member(message.chat.id, message.from_user.id)
            await client.unban_chat_member(message.chat.id, message.from_user.id)
            await message.reply(f"{message.from_user.mention} 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗄𝗂𝗰𝗄𝖾𝖽 𝖿𝗈𝗋 𝗎𝗌𝗂𝗇𝗀 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽 𝖼𝗈𝗇𝗍𝖾𝗇𝗍.")
            log_message = await format_log("Kicked User", message.chat.title, admin=message.from_user.mention, user=message.from_user.mention)

        elif mode == "mute":
            await client.restrict_chat_member(
                message.chat.id,
                message.from_user.id,
                permissions=types.ChatPermissions(),
            )
            await message.reply(f"{message.from_user.mention} 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗆𝗎𝗍𝖾𝖽 𝖿𝗈𝗋 𝗎𝗌𝗂𝗇𝗀 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽 𝖼𝗈𝗇𝗍𝖾𝗇𝗍.")
            log_message = await format_log("Muted User", message.chat.title, admin=message.from_user.mention, user=message.from_user.mention)

        elif mode == "tban":
            until_date = int(time.time()) + duration
            await client.ban_chat_member(message.chat.id, message.from_user.id, until_date=until_date)
            await message.reply(f"{message.from_user.mention} 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗍𝖾𝗆𝗉𝗈𝗋𝖺𝗋𝗂𝗅𝗒 𝖻𝖺𝗇𝗇𝖾𝖽 𝖿𝗈𝗋 {duration} 𝗌𝖾𝖼𝗈𝗇𝖽𝗌 𝖿𝗈𝗋 𝗎𝗌𝗂𝗇𝗀 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽 𝖼𝗈𝗇𝗍𝖾𝗇𝗍.")
            log_message = await format_log("Temporarily Banned User", message.chat.title, admin=message.from_user.mention, user=message.from_user.mention)

        elif mode == "tmute":
            until_date = int(time.time()) + duration
            await client.restrict_chat_member(
                message.chat.id,
                message.from_user.id,
                permissions=types.ChatPermissions(),
                until_date=until_date,
            )
            await message.reply(f"{message.from_user.mention} 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗍𝖾𝗆𝗉𝗈𝗋𝖺𝗋𝗂𝗅𝗒 𝗆𝗎𝗍𝖾𝖽 𝖿𝗈𝗋 {𝖽} 𝗌𝖾𝖼𝗈𝗇𝖽𝗌 𝖿𝗈𝗋 𝗎𝗌𝗂𝗇𝗀 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽 𝖼𝗈𝗇𝗍𝖾𝗇𝗍.")
            log_message = await format_log("Temporarily Muted User", message.chat.title, admin=message.from_user.mention, user=message.from_user.mention)

        if log_message:
            await send_log(message.chat.id, log_message)

    except ChatAdminRequired:
        return
    except Exception as e:
        print(f"Error in take_action: {e}")


__module__ = "𝖡𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍"

__help__ = """𝖳𝗁𝗂𝗌 𝗆𝗈𝖽𝗎𝗅𝖾 𝖺𝗅𝗅𝗈𝗐𝗌 𝗀𝗋𝗈𝗎𝗉 𝖺𝖽𝗆𝗂𝗇𝗂𝗌𝗍𝗋𝖺𝗍𝗈𝗋𝗌 𝗍𝗈 𝗆𝖺𝗇𝖺𝗀𝖾 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽 𝗐𝗈𝗋𝖽𝗌 𝖺𝗇𝖽 𝗌𝗍𝗂𝖼𝗄𝖾𝗋𝗌 𝗂𝗇 𝗍𝗁𝖾𝗂𝗋 𝖼𝗁𝖺𝗍. 
 
𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:
𝟣. **/𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍** - 𝖫𝗂𝗌𝗍𝗌 𝖺𝗅𝗅 𝖺𝖼𝗍𝗂𝗏𝖾 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽 𝗐𝗈𝗋𝖽𝗌 𝗂𝗇 𝗍𝗁𝖾 𝗀𝗋𝗈𝗎𝗉.
 𝟤. **/𝖺𝖽𝖽𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍 [𝗐𝗈𝗋𝖽𝟣] [𝗐𝗈𝗋𝖽𝟤]...** - 𝖠𝖽𝖽𝗌 𝗐𝗈𝗋𝖽𝗌 𝗍𝗈 𝗍𝗁𝖾 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍. 𝖱𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗈𝗋 𝗎𝗌𝖾 𝗂𝗇 𝖼𝗈𝗆𝗆𝖺𝗇𝖽.
 𝟥. **/𝗎𝗇𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍 [𝗐𝗈𝗋𝖽𝟣] [𝗐𝗈𝗋𝖽𝟤]...** - 𝖱𝖾𝗆𝗈𝗏𝖾𝗌 𝗐𝗈𝗋𝖽𝗌 𝖿𝗋𝗈𝗆 𝗍𝗁𝖾 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍.
 𝟦. **/𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝗆𝗈𝖽𝖾 <𝗈𝖿𝖿/𝖽𝖾𝗅/𝗐𝖺𝗋𝗇/𝖻𝖺𝗇/𝗄𝗂𝖼𝗄/𝗆𝗎𝗍𝖾/𝗍𝖻𝖺𝗇/𝗍𝗆𝗎𝗍𝖾> [𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇]** - 𝖲𝖾𝗍𝗌 𝗍𝗁𝖾 𝖺𝖼𝗍𝗂𝗈𝗇 𝗍𝗈 𝗍𝖺𝗄𝖾 𝗐𝗁𝖾𝗇 𝖺 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽 𝗂𝗍𝖾𝗆 𝗂𝗌 𝗎𝗌𝖾𝖽.
    - 𝖬𝗈𝖽𝖾𝗌:
       - **𝗈𝖿𝖿**: 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍.
        - **𝖽𝖾𝗅**: 𝖣𝖾𝗅𝖾𝗍𝖾 𝗍𝗁𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾.
        - **𝗐𝖺𝗋𝗇**: 𝖶𝖺𝗋𝗇 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋.
        - **𝖻𝖺𝗇**: 𝖡𝖺𝗇 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋.
        - **𝗄𝗂𝖼𝗄**: 𝖪𝗂𝖼𝗄 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋.
        - **𝗆𝗎𝗍𝖾**: 𝖬𝗎𝗍𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋.
        - **𝗍𝖻𝖺𝗇/𝗍𝗆𝗎𝗍𝖾**: 𝖳𝖾𝗆𝗉𝗈𝗋𝖺𝗋𝗂𝗅𝗒 𝖻𝖺𝗇/𝗆𝗎𝗍𝖾 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋 𝖿𝗈𝗋 𝖺 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖾𝖽 𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇.
 𝟧. **/𝖻𝗅𝗌𝗍𝗂𝖼𝗄𝖾𝗋** - 𝖫𝗂𝗌𝗍𝗌 𝖺𝗅𝗅 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽 𝗌𝗍𝗂𝖼𝗄𝖾𝗋𝗌 𝗂𝗇 𝗍𝗁𝖾 𝗀𝗋𝗈𝗎𝗉.
 𝟨. **/𝖺𝖽𝖽𝖻𝗅𝗌𝗍𝗂𝖼𝗄𝖾𝗋** - 𝖠𝖽𝖽𝗌 𝖺 𝗌𝗍𝗂𝖼𝗄𝖾𝗋 𝗍𝗈 𝗍𝗁𝖾 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍 (𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗌𝗍𝗂𝖼𝗄𝖾𝗋).
 𝟩. **/𝗎𝗇𝖻𝗅𝗌𝗍𝗂𝖼𝗄𝖾𝗋** - 𝖱𝖾𝗆𝗈𝗏𝖾𝗌 𝖺 𝗌𝗍𝗂𝖼𝗄𝖾𝗋 𝖿𝗋𝗈𝗆 𝗍𝗁𝖾 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍 (𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗌𝗍𝗂𝖼𝗄𝖾𝗋 𝗈𝗋 𝗎𝗌𝖾 𝗍𝗁𝖾 𝗌𝗍𝗂𝖼𝗄𝖾𝗋 𝖨𝖣).
 
𝖠𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼 𝖣𝖾𝗍𝖾𝖼𝗍𝗂𝗈𝗇:
- 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖼𝗈𝗇𝗍𝖺𝗂𝗇𝗂𝗇𝗀 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽 𝗐𝗈𝗋𝖽𝗌 𝗈𝗋 𝗌𝗍𝗂𝖼𝗄𝖾𝗋𝗌 𝗐𝗂𝗅𝗅 𝗍𝗋𝗂𝗀𝗀𝖾𝗋 𝗍𝗁𝖾 𝖼𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾𝖽 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍 𝖺𝖼𝗍𝗂𝗈𝗇.
 - 𝖠𝗉𝗉𝗋𝗈𝗏𝖾𝖽 𝗎𝗌𝖾𝗋𝗌 𝖺𝗋𝖾 𝖾𝗑𝖾𝗆𝗉𝗍 𝖿𝗋𝗈𝗆 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍 𝖾𝗇𝖿𝗈𝗋𝖼𝖾𝗆𝖾𝗇𝗍.
 
𝖴𝗌𝖺𝗀𝖾 𝖤𝗑𝖺𝗆𝗉𝗅𝖾:
- `/𝖺𝖽𝖽𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍 𝗌𝗉𝖺𝗆 𝗋𝗎𝖽𝖾` - 𝖠𝖽𝖽𝗌 "𝗌𝗉𝖺𝗆" 𝖺𝗇𝖽 "𝗋𝗎𝖽𝖾" 𝗍𝗈 𝗍𝗁𝖾 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍.
 - `/𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝗆𝗈𝖽𝖾 𝗐𝖺𝗋𝗇` - 𝖶𝖺𝗋𝗇 𝗎𝗌𝖾𝗋𝗌 𝖿𝗈𝗋 𝗎𝗌𝗂𝗇𝗀 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍𝖾𝖽 𝖼𝗈𝗇𝗍𝖾𝗇𝗍.
 - 𝖱𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗌𝗍𝗂𝖼𝗄𝖾𝗋 𝗐𝗂𝗍𝗁 `/𝖺𝖽𝖽𝖻𝗅𝗌𝗍𝗂𝖼𝗄𝖾𝗋` 𝗍𝗈 𝖻𝗅𝖺𝖼𝗄𝗅𝗂𝗌𝗍 𝗍𝗁𝖺𝗍 𝗌𝗍𝗂𝖼𝗄𝖾𝗋.
 """

