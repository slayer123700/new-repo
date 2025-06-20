from pyrogram import filters
from pyrogram.types import Message
from config import config
from shigaraki import app
from shigaraki.decorator.save import save 
from shigaraki.decorator.errors import error

@app.on_message(filters.command("write" , prefixes=config.COMMAND_PREFIXES))
@error
@save
async def handwrite(_, message: Message):
    if not message.reply_to_message:
        name = (
            message.text.split(None, 1)[1]
            if len(message.command) < 3
            else message.text.split(None, 1)[1].replace(" ", "%20")
        )
        m = await app.send_message(message.chat.id, "**𝖯𝗋𝗈𝖼𝖾𝗌𝗌𝗂𝗇𝗀 𝖸𝗈𝗎𝗋 𝖱𝖾𝗊𝗎𝖾𝗌𝗍 𝖯𝗅𝖾𝖺𝗌𝖾 𝖶𝖺𝗂𝗍....**")
        photo = "https://apis.xditya.me/write?text=" + name
        await app.send_photo(message.chat.id, photo=photo, caption=f"✍️ Written By @{config.BOT_USERNAME}")
        await m.delete()
    else:
        lol = message.reply_to_message.text
        name = lol.split(None, 0)[0].replace(" ", "%20")
        m = await app.send_message(message.chat.id, "**𝖯𝗋𝗈𝖼𝖾𝗌𝗌𝗂𝗇𝗀 𝖸𝗈𝗎𝗋 𝖱𝖾𝗊𝗎𝖾𝗌𝗍 𝖯𝗅𝖾𝖺𝗌𝖾 𝖶𝖺𝗂𝗍....**")
        photo = "https://apis.xditya.me/write?text=" + name
        await app.send_photo(message.chat.id, photo=photo, caption=f"✍️ 𝖶𝗋𝗂𝗍𝗍𝖾𝗇 𝖡𝗒 @{config.BOT_USERNAME}")
        await m.delete()


__module__ = "𝖶𝗋𝗂𝗍𝖾"


__help__ = """✧ `/𝗐𝗋𝗂𝗍𝖾` **:** 𝖳𝗈 𝖶𝗋𝗂𝗍𝖾 𝖠𝗇𝗒𝗍𝗁𝗂𝗇𝗀 𝖮𝗇 𝖠 𝖯𝖺𝗉𝖾𝗋.
 """