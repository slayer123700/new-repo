import aiohttp
from pyrogram import filters
from shigaraki import app
from config import config 
from pyrogram.enums import ParseMode
from shigaraki.decorator.save import save 
from shigaraki.decorator.errors import error

# Define the /news command
@app.on_message(filters.command("news" , prefixes=config.COMMAND_PREFIXES))
@error
@save
async def news_command(client, message):
    if len(message.command) < 2:
        await message.reply_text("𝖯𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 𝗄𝖾𝗒𝗐𝗈𝗋𝖽 𝗍𝗈 𝗌𝖾𝖺𝗋𝖼𝗁 𝖿𝗈𝗋 𝗇𝖾𝗐𝗌. 𝖤𝗑𝖺𝗆𝗉𝗅𝖾: /𝗇𝖾𝗐𝗌 𝖺𝗇𝗂𝗆𝖾")
        return

    keyword = " ".join(message.command[1:])
    api_url = f"https://sugoi-api.vercel.app/news?keyword={keyword}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status != 200:
                    await message.reply_text("𝖥𝖺𝗂𝗅𝖾𝖽 𝗍𝗈 𝖿𝖾𝗍𝖼𝗁 𝗇𝖾𝗐𝗌. 𝖯𝗅𝖾𝖺𝗌𝖾 𝗍𝗋𝗒 𝖺𝗀𝖺𝗂𝗇 𝗅𝖺𝗍𝖾𝗋.")
                    return
                data = await response.json()

        if not data:
            await message.reply_text(f"𝖭𝗈 𝗇𝖾𝗐𝗌 𝖿𝗈𝗎𝗇𝖽 𝖿𝗈𝗋 𝗄𝖾𝗒𝗐𝗈𝗋𝖽: {keyword}")
            return

        news_items = []
        for news in data[:5]:  # Limit to the first 5 results
            title = news.get("title", "No title")
            url = news.get("url", "No URL")
            news_items.append(f"\u2022 [{title}]({url})")

        news_text = "\n".join(news_items)
        await message.reply_text(f"𝖧𝖾𝗋𝖾 𝖺𝗋𝖾 𝗍𝗁𝖾 𝗍𝗈𝗉 𝗇𝖾𝗐𝗌 𝗋𝖾𝗌𝗎𝗅𝗍𝗌 𝖿𝗈𝗋 **{keyword}**:\n\n{news_text}", parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        await message.reply_text("𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽 𝗐𝗁𝗂𝗅𝖾 𝖿𝖾𝗍𝖼𝗁𝗂𝗇𝗀 𝗇𝖾𝗐𝗌. 𝖯𝗅𝖾𝖺𝗌𝖾 𝗍𝗋𝗒 𝖺𝗀𝖺𝗂𝗇 𝗅𝖺𝗍𝖾𝗋.")
        print(f"𝖤𝗋𝗋𝗈𝗋 𝖿𝖾𝗍𝖼𝗁𝗂𝗇𝗀 𝗇𝖾𝗐𝗌: {e}")



__module__ = "𝖭𝖾𝗐𝗌"

__help__ = """𝖳𝗁𝗂𝗌 𝗆𝗈𝖽𝗎𝗅𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾𝗌 𝗌𝖾𝖺𝗋𝖼𝗁 𝖿𝗎𝗇𝖼𝗍𝗂𝗈𝗇𝖺𝗅𝗂𝗍𝗂𝖾𝗌 𝖿𝗈𝗋 𝗇𝖾𝗐𝗌, 𝖡𝗂𝗇𝗀 𝗌𝖾𝖺𝗋𝖼𝗁, 𝖺𝗇𝖽 𝗂𝗆𝖺𝗀𝖾 𝗌𝖾𝖺𝗋𝖼𝗁𝖾𝗌.
  
**𝖠𝗏𝖺𝗂𝗅𝖺𝖻𝗅𝖾 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:**
𝟣. `/𝗇𝖾𝗐𝗌 <𝗄𝖾𝗒𝗐𝗈𝗋𝖽>` - 𝖲𝖾𝖺𝗋𝖼𝗁 𝖿𝗈𝗋 𝗇𝖾𝗐𝗌 𝖺𝗋𝗍𝗂𝖼𝗅𝖾𝗌 𝖻𝖺𝗌𝖾𝖽 𝗈𝗇 𝖺 𝗄𝖾𝗒𝗐𝗈𝗋𝖽. 
     𝖤𝗑𝖺𝗆𝗉𝗅𝖾: `/𝗇𝖾𝗐𝗌 𝖿𝗈𝗈𝗍𝖻𝖺𝗅𝗅`


**𝖭𝗈𝗍𝖾:** 
- 𝖥𝗈𝗋 `/𝗇𝖾𝗐𝗌`, 𝗒𝗈𝗎 𝖼𝖺𝗇 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺𝗇𝗒 𝗄𝖾𝗒𝗐𝗈𝗋𝖽 𝗈𝗋 𝗅𝖾𝖺𝗏𝖾 𝗂𝗍 𝖾𝗆𝗉𝗍𝗒 𝗍𝗈 𝖿𝖾𝗍𝖼𝗁 𝗀𝖾𝗇𝖾𝗋𝖺𝗅 𝗇𝖾𝗐𝗌.
  """