from pyrogram import filters , Client
import lyricsgenius
from pyrogram.types import Message 
from shigaraki import app 
from config import config
import requests
 

genius = lyricsgenius.Genius(config.LYRICS_GENIUS_TOKEN , remove_section_headers = True , verbose=False)

def fetch_lyrics(song_name):
    """Fetch lyrics for a song using the Genius API."""
    try:
        song = genius.search_song(song_name)
        if song:
            return f"**{song.title} by {song.artist}**\n\n{song.lyrics}"
        else:
            return "Sorry, I couldn't find the lyrics for that song."
    except Exception as e:
        return f"An error occurred while fetching lyrics: {e}"

def fetch_song_info(song_name):
    """Fetch song information and image from Genius API."""
    try:
        song = genius.search_song(song_name)
        if song:
            return {
                "title": song.title,
                "artist": song.artist,
                "album": song.album.name,
                "image_url": song.song_art_image_url,
                "url": song.url
            }
        else:
            return None
    except Exception as e:
        return {"error": str(e)}


# Function to fetch gender information
def fetch_gender(name):
    """Fetch gender prediction from Genderize API."""
    try:
        response = requests.get(f"https://api.genderize.io/?name={name}")
        if response.status_code == 200:
            data = response.json()
            return {
                "gender": data.get("gender"),
                "probability": data.get("probability"),
                "count": data.get("count")
            }
        else:
            return {"error": f"API returned status code {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


@app.on_message(filters.command("lyrics" , config.COMMAND_PREFIXES))
async def send_lyrics(client : Client , message : Message):

    if len(message.command) < 2:
        await message.reply_text("𝖴𝗌𝖺𝗀𝖾: /𝗅𝗒𝗋𝗂𝖼𝗌 [𝗌𝗈𝗇𝗀 𝗇𝖺𝗆𝖾]")
        return

    song_name = " ".join(message.command[1:])
    x = await message.reply_text("𝖥𝖾𝗍𝖼𝗁𝗂𝗇𝗀 𝗅𝗒𝗋𝗂𝖼𝗌... 𝖯𝗅𝖾𝖺𝗌𝖾 𝗐𝖺𝗂𝗍.")

    song_info = fetch_song_info(song_name)
    lyrics = fetch_lyrics(song_name)
    if len(lyrics) > 4096:
        for chunk in [lyrics[i:i + 4096] for i in range(0, len(lyrics), 4096)]:
            await message.reply_text(f"[🎶]({song_info['image_url']}) {chunk}")
            await x.delete()
    else:
        await x.edit_text(f"[🎶]({song_info['image_url']}) {lyrics}" , invert_media=True)
    
    
@app.on_message(filters.command("searchsong" , config.COMMAND_PREFIXES))
async def search_song(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("𝖴𝗌𝖺𝗀𝖾: /𝗌𝖾𝖺𝗋𝖼𝗁𝗌𝗈𝗇𝗀 [𝗌𝗈𝗇𝗀 𝗇𝖺𝗆𝖾]")
        return

    song_name = " ".join(message.command[1:])
    x = await message.reply_text("𝖲𝖾𝖺𝗋𝖼𝗁𝗂𝗇𝗀 𝖿𝗈𝗋 𝗌𝗈𝗇𝗀... 𝖯𝗅𝖾𝖺𝗌𝖾 𝗐𝖺𝗂𝗍.")

    song_info = fetch_song_info(song_name)
    if song_info is None:
        await x.edit("𝖲𝗈𝗋𝗋𝗒, 𝖨 𝖼𝗈𝗎𝗅𝖽𝗇'𝗍 𝖿𝗂𝗇𝖽 𝖺𝗇𝗒 𝗂𝗇𝖿𝗈𝗋𝗆𝖺𝗍𝗂𝗈𝗇 𝖿𝗈𝗋 𝗍𝗁𝖺𝗍 𝗌𝗈𝗇𝗀.s")
        return

    if "error" in song_info:
        await x.edit(f"An error occurred while searching for the song: {song_info['error']}")
        return

    caption = (
        f"🎵 **𝖲𝗈𝗇𝗀:** {song_info['title']}\n"
        f"🎤 **𝖠𝗋𝗍𝗂𝗌𝗍:** {song_info['artist']}\n"
        f"💿 **𝖠𝗅𝖻𝗎𝗆:** {song_info['album'] or 'N/A'}\n"
        f"🔗 [𝖬𝗈𝗋𝖾 𝖨𝗇𝖿𝗈]({song_info['url']})"
    )

    if song_info["image_url"]:
        await message.reply_photo(photo=song_info["image_url"], caption=caption , invert_media=True)
    else:
        await message.reply_text(caption)

    await x.delete()
    
@app.on_message(filters.command("gender" , config.COMMAND_PREFIXES))
async def gender_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("**𝖴𝗌𝖺𝗀𝖾:** `/𝗀𝖾𝗇𝖽𝖾𝗋 [𝗇𝖺𝗆𝖾]`")
        return

    name = message.command[1]
    x = await message.reply_text("🔍 𝖢𝗁𝖾𝖼𝗄𝗂𝗇𝗀 𝗀𝖾𝗇𝖽𝖾𝗋... 𝖯𝗅𝖾𝖺𝗌𝖾 𝗐𝖺𝗂𝗍.")

    gender_info = fetch_gender(name)

    if "error" in gender_info:
        await x.edit(f"**𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽:** `{gender_info['error']}`")
        return

    if gender_info["gender"] is None:
        await x.edit("**𝖲𝗈𝗋𝗋𝗒, 𝖨 𝖼𝗈𝗎𝗅𝖽𝗇'𝗍 𝗉𝗋𝖾𝖽𝗂𝖼𝗍 𝗍𝗁𝖾 𝗀𝖾𝗇𝖽𝖾𝗋 𝖿𝗈𝗋 𝗍𝗁𝗂𝗌 𝗇𝖺𝗆𝖾.**")
        return

    gender = gender_info["gender"].capitalize()
    probability = gender_info["probability"] * 100
    count = gender_info["count"]

    response = (
        f"👤 **𝖭𝖺𝗆𝖾:** {name}\n"
        f"🧭 **𝖯𝗋𝖾𝖽𝗂𝖼𝗍𝖾𝖽 𝖦𝖾𝗇𝖽𝖾𝗋:** {gender}\n"
        f"📊 **𝖯𝗋𝗈𝖻𝖺𝖻𝗂𝗅𝗂𝗍𝗒:** {probability:.2f}%\n"
        f"🧮 **𝖲𝖺𝗆𝗉𝗅𝖾 𝖲𝗂𝗓𝖾:** {count} occurrences"
    )

    await x.edit(response)

__module__ = "𝖬𝖨𝖢𝖲"

__help__ = """**𝖬𝗎𝗌𝗂𝖼 𝖠𝗇𝖽 𝖦𝖾𝗇𝖽𝖾𝗋 𝖳𝗈𝗈𝗅𝗌:**

✧ **Lyrics Finder:**
   - `/lyrics <song name>`: 𝖥𝗂𝗇𝖽 𝗅𝗒𝗋𝗂𝖼𝗌 𝖿𝗈𝗋 𝖺 𝗀𝗂𝗏𝖾𝗇 𝗌𝗈𝗇𝗀.

✧ **Song Search:**
   - `/searchsong <song name>`: 𝖲𝖾𝖺𝗋𝖼𝗁 𝗍𝗈 𝖿𝗂𝗇𝖽 𝗌𝗈𝗇𝗀 𝗂𝗇𝖿𝗈𝗋𝗆𝖺𝗍𝗂𝗈𝗇 𝗅𝗂𝗄𝖾 𝗍𝗂𝗍𝗅𝖾, 𝖺𝗋𝗍𝗂𝗌𝗍, 𝖺𝗅𝖻𝗎𝗆, 𝖺𝗇𝖽 𝗆𝗈𝗋𝖾.

✧ **Gender Prediction:**
   - `/gender <name>`: 𝖢𝗁𝖾𝖼𝗄 𝗀𝖾𝗇𝖽𝖾𝗋 𝗉𝗋𝖾𝖽𝗂𝖼𝗍𝗂𝗈𝗇 𝖿𝗈𝗋 𝖺 𝗇𝖺𝗆𝖾.

"""
