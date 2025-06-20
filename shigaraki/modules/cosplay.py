from pyrogram import filters
import aiohttp
from shigaraki import app
from config import config 

async def get_cosplay_data():
    cosplay_url = "https://sugoi-api.vercel.app/cosplay"
    async with aiohttp.ClientSession() as session:
        async with session.get(cosplay_url) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception("Failed to fetch data from the API.")


@app.on_message(filters.command("cosplay", prefixes=config.COMMAND_PREFIXES))
async def cosplay(client, message):
    try:
        data = await get_cosplay_data()
        photo_url = data.get("url")  # Corrected key: "url" instead of "cosplay_url"
        if photo_url:
            await message.reply_photo(photo=photo_url)
        else:
            await message.reply_text("Could not fetch photo URL.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

__module__ = "𝖢𝗈𝗌𝗉𝗅𝖺𝗒"
__help__ = """✧ /𝖼𝗈𝗌𝗉𝗅𝖺𝗒 : 𝖥𝖾𝗍𝖼𝗁 𝖺 𝖼𝗈𝗌𝗉𝗅𝖺𝗒 𝗉𝗁𝗈𝗍𝗈 𝖿𝗋𝗈𝗆 𝖺𝗇 𝖠𝖯𝖨 𝗌𝗈𝗎𝗋𝖼𝖾.
 ✧ 𝖠𝖿𝗍𝖾𝗋 𝗉𝗋𝗈𝗏𝗂𝖽𝗂𝗇𝗀 𝖺 𝖽𝗂𝗌𝗍𝗂𝗇𝖼𝗍 𝖼𝗈𝗌𝗉𝗅𝖺𝗒 𝗉𝗁𝗈𝗍𝗈, 𝗒𝗈𝗎 𝖼𝖺𝗇 𝖾𝗌𝗍𝖺𝖻𝗅𝗂𝗌𝗁 𝗂𝗍 𝗍𝗈 𝖺𝗇𝗒 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗂𝗇 𝗍𝗁𝖾 𝖼𝗁𝖺𝗍.
 """
