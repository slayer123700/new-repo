from gtts import gTTS
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from shigaraki import app
from config import config
from shigaraki.decorator.save import save 
from shigaraki.decorator.errors import error

AUDIO_FILE = "shigaraki.mp3"

@app.on_message(filters.command("tts" , prefixes=config.COMMAND_PREFIXES))
@error
@save
async def gtts_handler(client: Client, message: Message):
    reply = ""

    # Get text from the command arguments or reply
    if len(message.command) > 1:
        reply = " ".join(message.command[1:])
    elif message.reply_to_message and message.reply_to_message.text:
        reply = message.reply_to_message.text

    if not reply:
        await message.reply_text(
            "𝖤𝗇𝗍𝖾𝗋 𝖺𝗇𝗒 𝗍𝖾𝗑𝗍 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗍𝖾𝗑𝗍 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗍𝗈 𝖼𝗈𝗇𝗏𝖾𝗋𝗍 𝗂𝗍 𝗍𝗈 𝖺𝗎𝖽𝗂𝗈."
        )
        return

    # Remove newlines from the text
    reply = reply.replace("\n", "")

    try:
        # Convert text to speech
        tts = gTTS(reply, lang="en", tld="co.in")
        tts.save(AUDIO_FILE)

        # Send the audio file
        await client.send_audio(
            chat_id=message.chat.id,
            audio=AUDIO_FILE,
            caption="𝖧𝖾𝗋𝖾 𝗂𝗌 𝗒𝗈𝗎𝗋 𝗍𝖾𝗑𝗍-𝗍𝗈-𝗌𝗉𝖾𝖾𝖼𝗁 𝖺𝗎𝖽𝗂𝗈."
        )
    except Exception as e:
        await message.reply_text(f"❌ 𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝖼𝗈𝗇𝗏𝖾𝗋𝗍 𝗍𝖾𝗑𝗍 𝗍𝗈 𝗌𝗉𝖾𝖾𝖼𝗁. 𝖤𝗋𝗋𝗈𝗋: {e}")
    finally:
        # Clean up the audio file
        if os.path.isfile(AUDIO_FILE):
            os.remove(AUDIO_FILE)

__module__ = "𝖳𝖳𝖲"


__help__ = """ ✧ `/𝗍𝗍𝗌` (𝗋𝖾𝗉𝗅𝗒 𝗈𝗋 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝗍𝖾𝗑𝗍) *:* 𝖢𝗈𝗇𝗏𝖾𝗋𝗍𝗌 𝖳𝖾𝗑𝗍 𝖳𝗈 𝖠𝗎𝖽𝗂𝗈.
 """