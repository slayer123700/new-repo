import random
from shigaraki.database import couple_collection , waifu_collection
from datetime import datetime, timedelta
from pytz import timezone
from pyrogram import Client, filters
from pyrogram.types import Message
from shigaraki.database.couple_db import save_couple , save_waifu
from shigaraki import app
from config import config

# Define IST timezone
IST = timezone('Asia/Kolkata')
time_format = "%Y-%m-%d %H:%M:%S"

OWNER_ID = 5630057244
SPECIAL_FEMALE_ID = 7834395897
SPECIAL_FEMALE_NAME = "𝘔𝘢𝘱𝘭𝘦<3"

# List of image URLs
IMAGE_URLS = [
    "https://files.catbox.moe/5zsvmu.jpg",
    "https://files.catbox.moe/wte8ko.jpg",
    "https://files.catbox.moe/uy4ydt.jpg",
    "https://files.catbox.moe/37uyq0.jpg",
    "https://files.catbox.moe/gikzhy.jpg"
]

async def choose_couple(chat_id: int, members: list) -> tuple:
    """Choose a random male and female member from the chat members."""
    humans = [member for member in members if not member['is_bot']]
    if len(humans) < 2:
        return None, None

    male = random.choice(humans)
    female = random.choice([m for m in humans if m != male])
    return male, female

@app.on_message(filters.command("couple" , config.COMMAND_PREFIXES) & filters.group)
@app.on_message(filters.regex(r"^(?i)Nibba Nibbi$") & filters.group)
async def couple_handler(client: Client, message: Message):
    chat_id = message.chat.id

    # Choose a random image
    img_url = random.choice(IMAGE_URLS)

    # Check if the command is used by OWNER_ID
    if message.from_user.id == OWNER_ID:
        male_mention = f"[{message.from_user.first_name}](tg://user?id={OWNER_ID})"
        female_mention = f"[{SPECIAL_FEMALE_NAME}](tg://user?id={SPECIAL_FEMALE_ID})"
        await client.send_photo(
            chat_id,
            photo=img_url,
            caption=(
                f"🎀  𝒞❁𝓊𝓅𝓁𝑒 ❀𝒻 𝒯𝒽𝑒 𝒟𝒶𝓎  🎀\n"
                f"╭──────────────\n"
                f"┊•➢ {male_mention} + {female_mention} = 💞\n"
                f"╰───•➢♡"
            )
        )
        return

    # Check if a couple is already chosen and within 24 hours
    couple = await couple_collection.find_one({"chat_id": chat_id})
    if couple:
        date_chosen = IST.localize(datetime.strptime(couple["date"], time_format))
        if datetime.now(IST) - date_chosen < timedelta(hours=24):
            male_mention = f"[{couple['couple_first_name']}](tg://user?id={couple['couple_id']})"
            female_mention = f"[{couple['couple_first_name_2']}](tg://user?id={couple['couple_id_2']})"
            await client.send_photo(
                chat_id,
                photo=img_url,
                caption=(
                    f"🎀  𝒞❁𝓊𝓅𝓁𝑒 ❀𝒻 𝒯𝒽𝑒 𝒟𝒶𝓎  🎀\n"
                    f"╭──────────────\n"
                    f"┊•➢ {male_mention} + {female_mention} = 💞\n"
                    f"╰───•➢♡"
                )
            )
            return

    members = [
        {
            "user_id": member.user.id,
            "first_name": member.user.first_name,
            "is_bot": member.user.is_bot,
        }
        async for member in client.get_chat_members(chat_id)
        if not member.user.is_bot and member.user.first_name  # Exclude bots and deleted accounts
    ]


    # Choose a new couple
    male, female = await choose_couple(chat_id, members)
    if not male or not female:
        await message.reply_text("Couldn't find enough human members to form a couple.")
        return

    # Save the new couple in the database
    male_mention = f"[{male['first_name']}](tg://user?id={male['user_id']})"
    female_mention = f"[{female['first_name']}](tg://user?id={female['user_id']})"
    await save_couple(chat_id, male["user_id"], male["first_name"], female["user_id"], female["first_name"])

    # Send the couple of the day message with an image
    await client.send_photo(
        chat_id,
        photo=img_url,
        caption=(
            f"🎀  𝒞❁𝓊𝓅𝓁𝑒 ❀𝒻 𝒯𝒽𝑒 𝒟𝒶𝓎  🎀\n"
            f"╭──────────────\n"
            f"┊•➢ {male_mention} + {female_mention} = 💞\n"
            f"╰───•➢♡"
        )
    )
    
@app.on_message(filters.command("waifu", config.COMMAND_PREFIXES) & filters.group)
@app.on_message(filters.regex(r"^(?i)Waifuu$") & filters.group)
async def waifu_handler(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_first_name = message.from_user.first_name
    user_mention = message.from_user.mention

    x = await message.reply_text("Please Wait And Let Me Find Your Waifu....")
    
    # Check if the user already has a waifu chosen within the last 24 hours in this chat
    waifu = await waifu_collection.find_one({"chat_id": chat_id, "user_id": user_id})
    if waifu:
        date_chosen = IST.localize(datetime.strptime(waifu["date"], time_format))
        if datetime.now(IST) - date_chosen < timedelta(hours=24):
            waifu_mention = f"[{waifu['waifu_first_name']}](tg://user?id={waifu['waifu_id']})"
            bond_percentage = waifu["bond"]
            await x.delete()
            if waifu["waifu_photo"]:
                await client.send_cached_media(
                    chat_id,
                    file_id=waifu["waifu_photo"],
                    caption=(
                        f"✨ **{user_mention}'s Today's Waifu** ✨\n"
                        f"╭──────────────\n"
                        f"┊•➢ {waifu_mention}\n"
                        f"┊•➢ **Bond Percentage:** {bond_percentage}%\n"
                        f"╰───•➢♡"
                    )
                )
            else:
                await message.reply_text(
                    f"✨ **{user_mention}'s Today's Waifu** ✨\n"
                    f"╭──────────────\n"
                    f"┊•➢ {waifu_mention}\n"
                    f"┊•➢ **Bond Percentage:** {bond_percentage}%\n"
                    f"╰───•➢♡"
                )
            return

    # Get all chat members
    members = [
        {"user_id": member.user.id, "first_name": member.user.first_name, "is_bot": member.user.is_bot}
        async for member in client.get_chat_members(chat_id)
    ]

    # Exclude bots and the user themselves
    humans = [
        member
        for member in members
        if not member["is_bot"] and member["user_id"] != user_id and member["first_name"]  # Exclude bots and deleted accounts
    ]
    if not humans:
        await message.reply_text("Couldn't find any eligible waifu for you!")
        return

    # Randomly choose a waifu
    waifu_choice = random.choice(humans)
    waifu_id = waifu_choice["user_id"]
    waifu_first_name = waifu_choice["first_name"]
    waifu_mention = f"[{waifu_first_name}](tg://user?id={waifu_id})"

    waifu_photo = None

    # Get waifu's profile photo
    photo_count = await client.get_chat_photos_count(waifu_id)

    if photo_count == 0 :
        waifu_photo = None        

    async for photo in client.get_chat_photos(waifu_id, limit=1):
        waifu_photo = photo.file_id
        break  #

    # Generate bond percentage
    bond_percentage = random.randint(0, 100)

    # Save the waifu details in the database (with chat_id)
    await save_waifu(chat_id, user_id, user_first_name, bond_percentage, waifu_id, waifu_first_name, waifu_photo)

    await x.delete()
    # Send the response
    if waifu_photo:
        await client.send_cached_media(
            chat_id,
            file_id=waifu_photo,
            caption=(
                f"✨ **{user_mention}'s Today's Waifu** ✨\n"
                f"╭──────────────\n"
                f"┊•➢ {waifu_mention}\n"
                f"┊•➢ **Bond Percentage:** {bond_percentage}%\n"
                f"╰───•➢♡"
            )
        )
    else:
        await message.reply_text(
            f"✨ **{user_mention}'s Today's Waifu** ✨\n"
            f"╭──────────────\n"
            f"┊•➢ {waifu_mention}\n"
            f"┊•➢ **Bond Percentage:** {bond_percentage}%\n"
            f"╰───•➢♡"
        )


__module__ = "𝖢𝗈𝗎𝗉𝗅𝖾"

__help__ = """✧ /𝖼𝗈𝗎𝗉𝗅𝖾 : 𝖱𝖺𝗇𝖽𝗈𝗆𝗅𝗒 𝗌𝖾𝗅𝖾𝖼𝗍𝗌 𝖺𝗇𝖽 𝖽𝗂𝗌𝗉𝗅𝖺𝗒𝗌 𝗍𝗁𝖾 "𝖢𝗈𝗎𝗉𝗅𝖾 𝗈𝖿 𝗍𝗁𝖾 𝖣𝖺𝗒" 𝖿𝗋𝗈𝗆 𝗍𝗁𝖾 𝗀𝗋𝗈𝗎𝗉 𝗆𝖾𝗆𝖻𝖾𝗋𝗌. 
 ✧ /𝗐𝖺𝗂𝖿𝗎 : 𝖥𝗂𝗇𝖽𝗌 𝖺𝗇𝖽 𝖽𝗂𝗌𝗉𝗅𝖺𝗒𝗌 𝗒𝗈𝗎𝗋 "𝖶𝖺𝗂𝖿𝗎 𝗈𝖿 𝗍𝗁𝖾 𝖣𝖺𝗒" 𝗐𝗂𝗍𝗁 𝖺 𝖻𝗈𝗇𝖽 𝗉𝖾𝗋𝖼𝖾𝗇𝗍𝖺𝗀𝖾. 
 """