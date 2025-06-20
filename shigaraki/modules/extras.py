from pyrogram import Client, filters
from pyrogram.types import Message
import aiohttp
import random
from shigaraki import app
from shigaraki.vars import FLIRT as FLIRT_STRINGS , TOSS as TOSS_STRINGS , EYES , MOUTHS , EARS , DECIDE as DECIDE_STRINGS , weebyfont , normiefont 
from config import config
from pyrogram.enums import ParseMode
from shigaraki.decorator.save import save 
from shigaraki.decorator.errors import error


async def fetch_from_api(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()

@app.on_message(filters.command("pickwinner" , config.COMMAND_PREFIXES))
@error
@save
async def pick_winner(client: Client, message: Message):
    participants = message.text.split()[1:]
    if participants:
        winner = random.choice(participants)
        await message.reply_text(f"\ud83c\udf89 𝖳𝗁𝖾 𝗐𝗂𝗇𝗇𝖾𝗋 𝗂𝗌: {winner}")
    else:
        await message.reply_text("𝖯𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 𝗅𝗂𝗌𝗍 𝗈𝖿 𝗉𝖺𝗋𝗍𝗂𝖼𝗂𝗉𝖺𝗇𝗍𝗌.")

@app.on_message(filters.command("hyperlink" , config.COMMAND_PREFIXES))
@error
@save
async def hyperlink_command(client: Client, message: Message):
    args = message.text.split()[1:]
    if len(args) >= 2:
        text = " ".join(args[:-1])
        link = args[-1]
        hyperlink = f"[{text}]({link})"
        await message.reply_text(hyperlink, disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)
    else:
        await message.reply_text("𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖿𝗈𝗋𝗆𝖺𝗍! 𝖴𝗌𝖾: /𝗁𝗒𝗉𝖾𝗋𝗅𝗂𝗇𝗄 <𝗍𝖾𝗑𝗍> <𝗅𝗂𝗇𝗄>")

@app.on_message(filters.command("joke" , config.COMMAND_PREFIXES))
@app.on_message(filters.regex(r"^(?i)shigaraki Ek Joke Sunao$"))
@error
@save
async def joke(client: Client, message: Message):
    joke = await fetch_from_api("https://official-joke-api.appspot.com/random_joke")
    await message.reply_text(f"{joke['setup']} - {joke['punchline']}")

@app.on_message(filters.command("truth" , config.COMMAND_PREFIXES))
@error
@save
async def truth(client: Client, message: Message):
    truth_question = await fetch_from_api("https://api.truthordarebot.xyz/v1/truth")
    await message.reply_text(truth_question["question"])

@app.on_message(filters.command("dare" , config.COMMAND_PREFIXES))
@error
@save
async def dare(client: Client, message: Message):
    dare_question = await fetch_from_api("https://api.truthordarebot.xyz/v1/dare")
    await message.reply_text(dare_question["question"])

@app.on_message(filters.command("roll" , config.COMMAND_PREFIXES) & filters.private)
@error
@save
async def roll(client: Client, message: Message):
    await message.reply_text(random.randint(1, 6))

@app.on_message(filters.command("flirt" , config.COMMAND_PREFIXES))
@app.on_message(filters.regex(r"^(?i)shigaraki flirt$"))
@error
@save
async def flirt(client: Client, message: Message):
    await message.reply_text(random.choice(FLIRT_STRINGS))

@app.on_message(filters.command("toss" , config.COMMAND_PREFIXES))
@app.on_message(filters.regex(r"^(?i)shigaraki toss$"))
@error
@save
async def toss(client: Client, message: Message):
    await message.reply_text(random.choice(TOSS_STRINGS))

@app.on_message(filters.command("shrug" , config.COMMAND_PREFIXES))
@error
@save
async def shrug(client: Client, message: Message):
    await message.reply_text(r"¯\_(ツ)_/¯")

@app.on_message(filters.command("bluetext" , config.COMMAND_PREFIXES))
@error
@save
async def bluetext(client: Client, message: Message):
    await message.reply_text("/BLUE /TEXT\n/MUST /CLICK\n/I /AM /A /STUPID /ANIMAL /THAT /IS /ATTRACTED /TO /COLORS")

@app.on_message(filters.command("rlg" , config.COMMAND_PREFIXES))
@error
@save
async def rlg(client: Client, message: Message):
    eyes = random.choice(EYES)
    mouth = random.choice(MOUTHS)
    ears = random.choice(EARS)
    face = f"{ears[0]}{eyes}{mouth}{eyes}{ears[1]}"
    await message.reply_text(face)

@app.on_message(filters.command("decide" , config.COMMAND_PREFIXES))
@app.on_message(filters.regex(r"^(?i)shigaraki decide$"))
@error
@save
async def decide(client: Client, message: Message):
    await message.reply_text(random.choice(DECIDE_STRINGS))

@app.on_message(filters.command("weebify" , config.COMMAND_PREFIXES))
@error
@save
async def webify(client: Client, message: Message):
    args = message.command[1:]  # Extract arguments from the command
    string = ""

    if message.reply_to_message and message.reply_to_message.text:
        string = message.reply_to_message.text.lower().replace(" ", "  ")

    if args:
        string = "  ".join(args).lower()

    if not string:
        await message.reply_text(
            "𝖴𝗌𝖺𝗀𝖾: `/𝗐𝖾𝖾𝖻𝗂𝖿𝗒 <𝗍𝖾𝗑𝗍>`",
        )
        return

    for normiecharacter in string:
        if normiecharacter in normiefont:
            weebycharacter = weebyfont[normiefont.index(normiecharacter)]
            string = string.replace(normiecharacter, weebycharacter)

    if message.reply_to_message:
        await message.reply_to_message.reply_text(string)
    else:
        await message.reply_text(string)

__module__ = "𝖤𝗑𝗍𝗋𝖺𝗌"


__help__ = """**𝖥𝗎𝗇 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:**

- **𝖯𝗂𝖼𝗄 𝖺 𝖶𝗂𝗇𝗇𝖾𝗋:**
  ✧ `/𝗉𝗂𝖼𝗄𝗐𝗂𝗇𝗇𝖾𝗋 <𝗉𝖺𝗋𝗍𝗂𝖼𝗂𝗉𝖺𝗇𝗍𝟣> <𝗉𝖺𝗋𝗍𝗂𝖼𝗂𝗉𝖺𝗇𝗍𝟤>...` **:** 𝖲𝖾𝗅𝖾𝖼𝗍 𝖺 𝗋𝖺𝗇𝖽𝗈𝗆 𝗐𝗂𝗇𝗇𝖾𝗋 𝖿𝗋𝗈𝗆 𝗍𝗁𝖾 𝗅𝗂𝗌𝗍 𝗈𝖿 𝗉𝖺𝗋𝗍𝗂𝖼𝗂𝗉𝖺𝗇𝗍𝗌.
 
- **𝖧𝗒𝗉𝖾𝗋𝗅𝗂𝗇𝗄 𝖢𝗋𝖾𝖺𝗍𝗂𝗈𝗇:**
  ✧ `/𝗁𝗒𝗉𝖾𝗋𝗅𝗂𝗇𝗄 <𝗍𝖾𝗑𝗍> <𝗅𝗂𝗇𝗄>` **:** 𝖢𝗋𝖾𝖺𝗍𝖾 𝖺 𝖼𝗅𝗂𝖼𝗄𝖺𝖻𝗅𝖾 𝗁𝗒𝗉𝖾𝗋𝗅𝗂𝗇𝗄 𝗂𝗇 𝗍𝗁𝖾 𝖿𝗈𝗋𝗆𝖺𝗍 `[𝗍𝖾𝗑𝗍](𝗅𝗂𝗇𝗄)`.
 
- **𝖩𝗈𝗄𝖾𝗌:**
  ✧ `/𝗃𝗈𝗄𝖾` **:** 𝖦𝖾𝗍 𝖺 𝗋𝖺𝗇𝖽𝗈𝗆 𝗃𝗈𝗄𝖾.
 
- **𝖣𝗂𝖼𝖾 𝖱𝗈𝗅𝗅:**
  ✧ `/𝗋𝗈𝗅𝗅` **:** 𝖱𝗈𝗅𝗅 𝖺 𝖽𝗂𝖼𝖾 𝖺𝗇𝖽 𝗀𝖾𝗍 𝖺 𝗋𝖺𝗇𝖽𝗈𝗆 𝗇𝗎𝗆𝖻𝖾𝗋 𝖻𝖾𝗍𝗐𝖾𝖾𝗇 𝟣 𝖺𝗇𝖽 𝟨.
 
- **𝖥𝗅𝗂𝗋𝗍:**
  ✧ `/𝖿𝗅𝗂𝗋𝗍` **:** 𝖦𝖾𝗍 𝖺 𝗋𝖺𝗇𝖽𝗈𝗆 𝖿𝗅𝗂𝗋𝗍𝖺𝗍𝗂𝗈𝗎𝗌 𝗋𝖾𝗌𝗉𝗈𝗇𝗌𝖾.
 
- **𝖳𝗈𝗌𝗌:**
  ✧ `/𝗍𝗈𝗌𝗌` **:** 𝖳𝗈𝗌𝗌 𝖺 𝖼𝗈𝗂𝗇 𝖺𝗇𝖽 𝗀𝖾𝗍 𝖾𝗂𝗍𝗁𝖾𝗋 "𝖧𝖾𝖺𝖽𝗌" 𝗈𝗋 "𝖳𝖺𝗂𝗅𝗌."

- **𝖲𝗁𝗋𝗎𝗀 𝖤𝗆𝗈𝗃𝗂:**
  ✧ `/𝗌𝗁𝗋𝗎𝗀` **:** 𝖦𝖾𝗍 𝗍𝗁𝖾 𝗌𝗁𝗋𝗎𝗀 𝖾𝗆𝗈𝗃𝗂 (¯\\_(ツ)_/¯).
 
- **𝖡𝗅𝗎𝖾 𝖳𝖾𝗑𝗍:**
  ✧ `/𝖻𝗅𝗎𝖾𝗍𝖾𝗑𝗍` **:** 𝖦𝖾𝗍 𝖺 𝗋𝖺𝗇𝖽𝗈𝗆 "𝖻𝗅𝗎𝖾 𝗍𝖾𝗑𝗍" 𝗋𝖾𝗌𝗉𝗈𝗇𝗌𝖾.
 
- **𝖱𝖺𝗇𝖽𝗈𝗆 𝖫𝖾𝗍𝗍𝖾𝗋𝗌 𝖦𝖾𝗇𝖾𝗋𝖺𝗍𝗈𝗋 (𝖱𝖫𝖦):**
  ✧ `/𝗋𝗅𝗀` **:** 𝖦𝖾𝗇𝖾𝗋𝖺𝗍𝖾 𝖺 𝗋𝖺𝗇𝖽𝗈𝗆 𝖼𝗈𝗆𝖻𝗂𝗇𝖺𝗍𝗂𝗈𝗇 𝗈𝖿 𝖾𝗒𝖾𝗌, 𝗆𝗈𝗎𝗍𝗁, 𝖺𝗇𝖽 𝖾𝖺𝗋𝗌 𝗍𝗈 𝖼𝗋𝖾𝖺𝗍𝖾 𝖺 𝖿𝖺𝖼𝖾.
 
- **𝖣𝖾𝖼𝗂𝗌𝗂𝗈𝗇 𝖬𝖺𝗄𝗂𝗇𝗀:**
  ✧ `/𝖽𝖾𝖼𝗂𝖽𝖾` **:** 𝖦𝖾𝗍 𝖺 𝗋𝖺𝗇𝖽𝗈𝗆 𝖽𝖾𝖼𝗂𝗌𝗂𝗈𝗇-𝗆𝖺𝗄𝗂𝗇𝗀 𝗋𝖾𝗌𝗉𝗈𝗇𝗌𝖾 (𝖾.𝗀., "𝖸𝖾𝗌", "𝖭𝗈", 𝖾𝗍𝖼.).
 
- **𝖶𝖾𝖾𝖻𝗂𝖿𝗒 𝖳𝖾𝗑𝗍:**
  ✧ `/𝗐𝖾𝖾𝖻𝗂𝖿𝗒 <𝗍𝖾𝗑𝗍>` **:** 𝖢𝗈𝗇𝗏𝖾𝗋𝗍 𝗍𝖾𝗑𝗍 𝗂𝗇𝗍𝗈 𝖺 "𝗐𝖾𝖾𝖻𝗂𝖿𝗂𝖾𝖽" 𝖿𝗈𝗇𝗍.
 
- **𝖳𝗋𝗎𝗍𝗁:**
  ✧ `/𝗍𝗋𝗎𝗍𝗁` **:** 𝖦𝖾𝗍 𝖺 𝗋𝖺𝗇𝖽𝗈𝗆 𝗍𝗋𝗎𝗍𝗁 𝗊𝗎𝖾𝗌𝗍𝗂𝗈𝗇.
 
- **𝖣𝖺𝗋𝖾:**
  ✧ `/𝖽𝖺𝗋𝖾` **:** 𝖦𝖾𝗍 𝖺 𝗋𝖺𝗇𝖽𝗈𝗆 𝖽𝖺𝗋𝖾 𝗊𝗎𝖾𝗌𝗍𝗂𝗈𝗇.
 
**𝖧𝗈𝗐 𝗍𝗈 𝖴𝗌𝖾:**
  𝟣. 𝖴𝗌𝖾 𝗍𝗁𝖾 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌 𝖺𝗌 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖾𝖽 𝗐𝗂𝗍𝗁 𝗈𝗋 𝗐𝗂𝗍𝗁𝗈𝗎𝗍 𝖺𝗋𝗀𝗎𝗆𝖾𝗇𝗍𝗌.
   𝟤. 𝖲𝗈𝗆𝖾 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌 𝗋𝖾𝗊𝗎𝗂𝗋𝖾 𝗋𝖾𝗉𝗅𝗒𝗂𝗇𝗀 𝗍𝗈 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 (𝗅𝗂𝗄𝖾 `/𝗌𝗁𝗋𝗎𝗀`, `/𝖻𝗅𝗎𝖾𝗍𝖾𝗑𝗍`, 𝖺𝗇𝖽 `/𝗐𝖾𝖾𝖻𝗂𝖿𝗒`).
   𝟥. 𝖥𝗈𝗋 𝖼𝗈𝗆𝗆𝖺𝗇𝖽𝗌 𝗐𝗂𝗍𝗁 𝗆𝗎𝗅𝗍𝗂𝗉𝗅𝖾 𝗉𝖺𝗋𝗍𝗂𝖼𝗂𝗉𝖺𝗇𝗍𝗌 (𝖾.𝗀., `/𝗉𝗂𝖼𝗄𝗐𝗂𝗇𝗇𝖾𝗋`), 𝗅𝗂𝗌𝗍 𝖺𝗅𝗅 𝗍𝗁𝖾 𝗉𝖺𝗋𝗍𝗂𝖼𝗂𝗉𝖺𝗇𝗍𝗌 𝗌𝖾𝗉𝖺𝗋𝖺𝗍𝖾𝖽 𝖻𝗒 𝗌𝗉𝖺𝖼𝖾𝗌.
   𝟦. 𝖥𝗈𝗋 `/𝗁𝗒𝗉𝖾𝗋𝗅𝗂𝗇𝗄`, 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 𝗍𝖾𝗑𝗍 𝖺𝗇𝖽 𝖺 𝗅𝗂𝗇𝗄 𝗍𝗈 𝖼𝗋𝖾𝖺𝗍𝖾 𝖺 𝗁𝗒𝗉𝖾𝗋𝗅𝗂𝗇𝗄.
   𝟧. `/𝗋𝗈𝗅𝗅` 𝗀𝗂𝗏𝖾𝗌 𝖺 𝗋𝖺𝗇𝖽𝗈𝗆 𝗇𝗎𝗆𝖻𝖾𝗋 𝖿𝗋𝗈𝗆 𝟣 𝗍𝗈 𝟨, 𝗐𝗁𝗂𝗅𝖾 `/𝗍𝗈𝗌𝗌` 𝗀𝗂𝗏𝖾𝗌 𝖾𝗂𝗍𝗁𝖾𝗋 "𝖧𝖾𝖺𝖽𝗌" 𝗈𝗋 "𝖳𝖺𝗂𝗅𝗌".
   𝟨. `/𝗍𝗋𝗎𝗍𝗁` 𝖺𝗇𝖽 `/𝖽𝖺𝗋𝖾` 𝗀𝗂𝗏𝖾 𝖺 𝗋𝖺𝗇𝖽𝗈𝗆 𝗊𝗎𝖾𝗌𝗍𝗂𝗈𝗇 𝖿𝗋𝗈𝗆 𝗍𝗁𝖾 𝗋𝖾𝗌𝗉𝖾𝖼𝗍𝗂𝗏𝖾 𝖼𝖺𝗍𝖾𝗀𝗈𝗋𝗒.
 
"""