from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
import aiohttp
from shigaraki import app
from config import config 
from pyrogram.enums import ParseMode
from shigaraki.decorator.save import save 
from shigaraki.decorator.errors import error

class MatchManager:
    def __init__(self, api_url):
        self.api_url = api_url
        self.matches = []
        self.match_count = 0

    async def fetch_matches(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url) as response:
                self.matches = await response.json()

    def get_next_matches(self, count):
        next_matches = self.matches[self.match_count : self.match_count + count]
        self.match_count += count
        return next_matches

    def reset_matches(self):
        self.matches = []
        self.match_count = 0


async def get_match_text(match, sport):
    match_text = f"{'🏏' if sport == 'cricket' else '⚽️'} **{match['title']}**\n\n"
    match_text += f"🗓 **𝖣𝖺𝗍𝖾:** {match['date']}\n"
    match_text += f"🏆 **𝖳𝖾𝖺𝗆 1:** {match['team1']}\n"
    match_text += f"🏆 **𝖳𝖾𝖺𝗆 2:** {match['team2']}\n"
    match_text += f"🏟️ **𝖵𝖾𝗇𝗎𝖾:** {match['venue']}"
    return match_text


def create_inline_keyboard(sport):
    inline_keyboard = [
        [
            InlineKeyboardButton(
                f"𝖭𝖾𝗑𝗍 {sport.capitalize()} 𝖬𝖺𝗍𝖼𝗁 ➡️",
                callback_data=f"next_{sport}_match",
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard)


cricket_manager = MatchManager(config.CRICKET_API_URL)
football_manager = MatchManager(config.FOOTBALL_API_URL)


@app.on_message(filters.command("cricket"  , prefixes=config.COMMAND_PREFIXES))
@error
@save
async def get_cricket_matches(client: Client, message: Message):
    try:
        cricket_manager.reset_matches()
        await cricket_manager.fetch_matches()

        if not cricket_manager.matches:
            await message.reply_text("𝖭𝗈 𝖼𝗋𝗂𝖼𝗄𝖾𝗍 𝗆𝖺𝗍𝖼𝗁𝖾𝗌 𝖿𝗈𝗎𝗇𝖽.")
            return

        next_matches = cricket_manager.get_next_matches(1)
        match = next_matches[0]

        match_text = await get_match_text(match, "cricket")
        reply_markup = create_inline_keyboard("cricket")

        await message.reply_text(
            match_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        await message.reply_text(f"𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽: {str(e)}")


@app.on_message(filters.command("football"  , prefixes=config.COMMAND_PREFIXES))
@error
@save
async def get_football_matches(client: Client, message: Message):
    try:
        football_manager.reset_matches()
        await football_manager.fetch_matches()

        if not football_manager.matches:
            await message.reply_text("𝖭𝗈 𝖿𝗈𝗈𝗍𝖻𝖺𝗅𝗅 𝗆𝖺𝗍𝖼𝗁𝖾𝗌 𝖿𝗈𝗎𝗇𝖽.")
            return

        next_matches = football_manager.get_next_matches(1)
        match = next_matches[0]

        match_text = await get_match_text(match, "football")
        reply_markup = create_inline_keyboard("football")

        await message.reply_text(
            match_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        await message.reply_text(f"𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽: {str(e)}")


@app.on_callback_query(filters.regex(r"^next_(cricket|football)_match$"))
@error
async def show_next_match(client: Client, query: CallbackQuery):
    try:
        sport = query.data.split("_")[1]
        manager = cricket_manager if sport == "cricket" else football_manager

        if not manager.matches:
            await query.answer(f"𝖭𝗈 𝗆𝗈𝗋𝖾 {sport} 𝗆𝖺𝗍𝖼𝗁𝖾𝗌 𝖺𝗏𝖺𝗂𝗅𝖺𝖻𝗅𝖾.")
            return

        next_matches = manager.get_next_matches(3)

        if not next_matches:
            await query.answer(f"𝖭𝗈 𝗆𝗈𝗋𝖾 {sport} 𝗆𝖺𝗍𝖼𝗁𝖾𝗌 𝖺𝗏𝖺𝗂𝗅𝖺𝖻𝗅𝖾.")
            return

        match_text = ""
        for match in next_matches:
            match_text += await get_match_text(match, sport) + "\n\n"

        reply_markup = create_inline_keyboard(sport)

        await query.message.edit_text(
            match_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        await query.answer()

    except Exception as e:
        await query.message.reply_text(f"𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽: {str(e)}")


__module__ = "𝖲𝗉𝗈𝗋𝗍𝗌"

__help__ = """𝖳𝗁𝗂𝗌 𝗆𝗈𝖽𝗎𝗅𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾𝗌 𝗅𝗂𝗏𝖾 𝗆𝖺𝗍𝖼𝗁 𝗎𝗉𝖽𝖺𝗍𝖾𝗌 𝖿𝗈𝗋 𝖢𝗋𝗂𝖼𝗄𝖾𝗍 𝖺𝗇𝖽 𝖥𝗈𝗈𝗍𝖻𝖺𝗅𝗅.
 
**𝖠𝗏𝖺𝗂𝗅𝖺𝖻𝗅𝖾 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:**
- `/𝖼𝗋𝗂𝖼𝗄𝖾𝗍` - 𝖦𝖾𝗍 𝗍𝗁𝖾 𝖽𝖾𝗍𝖺𝗂𝗅𝗌 𝗈𝖿 𝗎𝗉𝖼𝗈𝗆𝗂𝗇𝗀 𝖼𝗋𝗂𝖼𝗄𝖾𝗍 𝗆𝖺𝗍𝖼𝗁𝖾𝗌.
 - `/𝖿𝗈𝗈𝗍𝖻𝖺𝗅𝗅` - 𝖦𝖾𝗍 𝗍𝗁𝖾 𝖽𝖾𝗍𝖺𝗂𝗅𝗌 𝗈𝖿 𝗎𝗉𝖼𝗈𝗆𝗂𝗇𝗀 𝖿𝗈𝗈𝗍𝖻𝖺𝗅𝗅 𝗆𝖺𝗍𝖼𝗁𝖾𝗌.
 
**𝖨𝗇𝗅𝗂𝗇𝖾 𝖥𝖾𝖺𝗍𝗎𝗋𝖾𝗌:**
- 𝖭𝖺𝗏𝗂𝗀𝖺𝗍𝖾 𝗍𝗁𝗋𝗈𝗎𝗀𝗁 𝗆𝖺𝗍𝖼𝗁𝖾𝗌 𝗎𝗌𝗂𝗇𝗀 𝗂𝗇𝗅𝗂𝗇𝖾 𝖻𝗎𝗍𝗍𝗈𝗇𝗌:
  - "𝖭𝖾𝗑𝗍 𝖢𝗋𝗂𝖼𝗄𝖾𝗍 𝖬𝖺𝗍𝖼𝗁 ➡️"
  - "𝖭𝖾𝗑𝗍 𝖥𝗈𝗈𝗍𝖻𝖺𝗅𝗅 𝖬𝖺𝗍𝖼𝗁 ➡️"
"""
