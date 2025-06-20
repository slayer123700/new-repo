import asyncio
import random
from telethon import events
from telethon.errors import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from shigaraki import telebot
from shigaraki.vars import emojis

spam_chats = []

@telebot.on(events.NewMessage(pattern="^/(tagall|etagall) ?(.*)"))
@telebot.on(events.NewMessage(pattern="^@(all|eall) ?(.*)"))
async def mentionall(event):
    chat_id = event.chat_id
    if event.is_private:
        return await event.respond("𝖳𝗁𝗂𝗌 𝖼𝗈𝗆𝗆𝖺𝗇𝖽 𝖼𝖺𝗇 𝖻𝖾 𝗎𝗌𝖾𝖽 𝗂𝗇 𝗀𝗋𝗈𝗎𝗉𝗌 𝖺𝗇𝖽 𝖼𝗁𝖺𝗇𝗇𝖾𝗅𝗌!")

    is_admin = False
    try:
        partici_ = await telebot(GetParticipantRequest(chat_id, event.sender_id))
    except UserNotParticipantError:
        is_admin = False
    else:
        if isinstance(partici_.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            is_admin = True

    if not is_admin:
        return await event.respond("𝖮𝗇𝗅𝗒 𝖺𝖽𝗆𝗂𝗇𝗌 𝖼𝖺𝗇 𝗆𝖾𝗇𝗍𝗂𝗈𝗇 𝖺𝗅𝗅!")

    # Determine the mention mode
    command_type = event.pattern_match.group(1)
    msg_text = event.pattern_match.group(2)
    
    if msg_text and event.is_reply:
        return await event.respond("𝖯𝗋𝗈𝗏𝗂𝖽𝖾 𝗈𝗇𝗅𝗒 𝗈𝗇𝖾 𝖺𝗋𝗀𝗎𝗆𝖾𝗇𝗍!")
    elif event.is_reply:
        msg = await event.get_reply_message()
        if msg is None:
            return await event.respond("𝖨 𝖼𝖺𝗇'𝗍 𝗆𝖾𝗇𝗍𝗂𝗈𝗇 𝗆𝖾𝗆𝖻𝖾𝗋𝗌 𝖿𝗈𝗋 𝗈𝗅𝖽𝖾𝗋 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌!")
        mode = "text_on_reply"
    elif msg_text:
        msg = msg_text
        mode = "text_on_cmd"
    else:
        return await event.respond("𝖱𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗈𝗋 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝗍𝖾𝗑𝗍 𝗍𝗈 𝗆𝖾𝗇𝗍𝗂𝗈𝗇 𝗈𝗍𝗁𝖾𝗋𝗌!")

    spam_chats.append(chat_id)
    usrnum = 0
    usrtxt = ""
    
    async for usr in telebot.iter_participants(chat_id):
        if chat_id not in spam_chats:
            break
        usrnum += 1

        if command_type in ["all", "tagall"]:
            usrtxt += f"[{usr.first_name}](tg://user?id={usr.id}), "
        elif command_type in ["eall", "etagall"]:
            random_emoji = random.choice(emojis)
            usrtxt += f"[{random_emoji}](tg://user?id={usr.id}), "
        
        if usrnum == 5:
            if mode == "text_on_cmd":
                txt = f"{msg}\n{usrtxt}"
                await telebot.send_message(chat_id, txt)
            elif mode == "text_on_reply":
                await msg.reply(usrtxt)
            await asyncio.sleep(3)
            usrnum = 0
            usrtxt = ""

    try:
        spam_chats.remove(chat_id)
    except:
        pass

@telebot.on(events.NewMessage(pattern="^/cancel$"))
async def cancel_spam(event):
    if event.chat_id not in spam_chats:
        return await event.respond("𝖭𝗈 𝗈𝗇𝗀𝗈𝗂𝗇𝗀 𝗆𝖾𝗇𝗍𝗂𝗈𝗇 𝗉𝗋𝗈𝖼𝖾𝗌𝗌 𝗍𝗈 𝖼𝖺𝗇𝖼𝖾𝗅.")
    
    is_admin = False
    try:
        partici_ = await telebot(GetParticipantRequest(event.chat_id, event.sender_id))
    except UserNotParticipantError:
        is_admin = False
    else:
        if isinstance(partici_.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
            is_admin = True

    if not is_admin:
        return await event.respond("𝖮𝗇𝗅𝗒 𝖺𝖽𝗆𝗂𝗇𝗌 𝖼𝖺𝗇 𝖾𝗑𝖾𝖼𝗎𝗍𝖾 𝗍𝗁𝗂𝗌 𝖼𝗈𝗆𝗆𝖺𝗇𝖽!")
    
    try:
        spam_chats.remove(event.chat_id)
    except:
        pass
    return await event.respond("𝖬𝖾𝗇𝗍𝗂𝗈𝗇𝗂𝗇𝗀 𝗉𝗋𝗈𝖼𝖾𝗌𝗌 𝗌𝗍𝗈𝗉𝗉𝖾𝖽.")


__module__ = "𝖳𝖺𝗀 𝖠𝗅𝗅"


__help__ = """**𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌 𝖿𝗈𝗋 𝖬𝖾𝗇𝗍𝗂𝗈𝗇𝗂𝗇𝗀 𝖠𝗅𝗅 𝖬𝖾𝗆𝖻𝖾𝗋𝗌:**

  ✧ `/𝗍𝖺𝗀𝖺𝗅𝗅 <𝗍𝖾𝗑𝗍>` 𝗈𝗋 `@𝖺𝗅𝗅 <𝗍𝖾𝗑𝗍>` **:** 𝖬𝖾𝗇𝗍𝗂𝗈𝗇 𝖺𝗅𝗅 𝗎𝗌𝖾𝗋𝗌 𝗂𝗇 𝗍𝗁𝖾 𝗀𝗋𝗈𝗎𝗉 𝗎𝗌𝗂𝗇𝗀 𝗍𝗁𝖾𝗂𝗋 𝗇𝖺𝗆𝖾𝗌.
   ✧ `/𝖾𝗍𝖺𝗀𝖺𝗅𝗅 <𝗍𝖾𝗑𝗍>` 𝗈𝗋 `@𝖾𝖺𝗅𝗅 <𝗍𝖾𝗑𝗍>` **:** 𝖬𝖾𝗇𝗍𝗂𝗈𝗇 𝖺𝗅𝗅 𝗎𝗌𝖾𝗋𝗌 𝗎𝗌𝗂𝗇𝗀 𝗋𝖺𝗇𝖽𝗈𝗆 𝖾𝗆𝗈𝗃𝗂𝗌 𝗂𝗇𝗌𝗍𝖾𝖺𝖽 𝗈𝖿 𝗇𝖺𝗆𝖾𝗌.
   ✧ `/𝗍𝖺𝗀𝖺𝗅𝗅` 𝗈𝗋 `/𝖾𝗍𝖺𝗀𝖺𝗅𝗅` 𝗐𝗂𝗍𝗁𝗈𝗎𝗍 𝗍𝖾𝗑𝗍 𝗐𝗈𝗋𝗄𝗌 𝖺𝗌 𝖺 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝗆𝖾𝗇𝗍𝗂𝗈𝗇 𝗎𝗌𝖾𝗋𝗌 𝖿𝗈𝗋 𝗍𝗁𝖺𝗍 𝗆𝖾𝗌𝗌𝖺𝗀𝖾.
 
**𝖢𝖺𝗇𝖼𝖾𝗅 𝖬𝖾𝗇𝗍𝗂𝗈𝗇𝗂𝗇𝗀:**
  ✧ `/𝖼𝖺𝗇𝖼𝖾𝗅` **:** 𝖲𝗍𝗈𝗉 𝗍𝗁𝖾 𝗈𝗇𝗀𝗈𝗂𝗇𝗀 𝗆𝖾𝗇𝗍𝗂𝗈𝗇 𝗉𝗋𝗈𝖼𝖾𝗌𝗌.
 
**𝖤𝗑𝖺𝗆𝗉𝗅𝖾𝗌:**
  ✧ `/𝗍𝖺𝗀𝖺𝗅𝗅 𝖧𝖾𝗅𝗅𝗈 𝖾𝗏𝖾𝗋𝗒𝗈𝗇𝖾!` **:** 𝖬𝖾𝗇𝗍𝗂𝗈𝗇 𝖺𝗅𝗅 𝗎𝗌𝖾𝗋𝗌 𝗐𝗂𝗍𝗁 "𝖧𝖾𝗅𝗅𝗈 𝖾𝗏𝖾𝗋𝗒𝗈𝗇𝖾!" 𝗎𝗌𝗂𝗇𝗀 𝗍𝗁𝖾𝗂𝗋 𝗇𝖺𝗆𝖾𝗌.
   ✧ `/𝖾𝗍𝖺𝗀𝖺𝗅𝗅 𝖫𝖾𝗍'𝗌 𝗉𝖺𝗋𝗍𝗒!` **:** 𝖬𝖾𝗇𝗍𝗂𝗈𝗇 𝖺𝗅𝗅 𝗎𝗌𝖾𝗋𝗌 𝗐𝗂𝗍𝗁 𝗋𝖺𝗇𝖽𝗈𝗆 𝖾𝗆𝗈𝗃𝗂𝗌 𝗂𝗇𝗌𝗍𝖾𝖺𝖽 𝗈𝖿 𝗇𝖺𝗆𝖾𝗌.
   ✧ 𝖱𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗐𝗂𝗍𝗁 `/𝗍𝖺𝗀𝖺𝗅𝗅` 𝗈𝗋 `/𝖾𝗍𝖺𝗀𝖺𝗅𝗅` 𝗍𝗈 𝗆𝖾𝗇𝗍𝗂𝗈𝗇 𝖺𝗅𝗅 𝗎𝗌𝖾𝗋𝗌 𝖿𝗈𝗋 𝗍𝗁𝖺𝗍 𝗆𝖾𝗌𝗌𝖺𝗀𝖾.
 """