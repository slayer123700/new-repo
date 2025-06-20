import os
import io
import random
import glob
from PIL import Image, ImageDraw, ImageFont
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from shigaraki import app as pgram 
from shigaraki.vars import LOGO_LINKS
from pyrogram.enums import ParseMode
import os
from shigaraki.helper.logohelper import generate , blackpink
from config import config
from shigaraki.decorator.save import save 
from shigaraki.decorator.errors import error


BOT_USERNAME = config.BOT_USERNAME
Name = "shigaraki.png"

@pgram.on_message(filters.command("logo", prefixes=config.COMMAND_PREFIXES))
@error
@save
async def generate_logo(client, message):
    try:
        # Ensure the command has the required text
        if len(message.command) < 2:
            await message.reply_text(
                "𝖣𝖺𝗋𝗅𝗂𝗇𝗀, 𝗉𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝗌𝗈𝗆𝖾 𝗍𝖾𝗑𝗍 𝗍𝗈 𝖼𝗋𝖾𝖺𝗍𝖾 𝖺 𝗅𝗈𝗀𝗈!\𝗇\𝗇𝖤𝗑𝖺𝗆𝗉𝗅𝖾: `/𝗅𝗈𝗀𝗈 𝖸𝗎𝗆𝖾𝗄𝗈`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Extract the text to generate the logo
        text = " ".join(message.command[1:])

        # Notify the user that the logo is being generated
        status_message = await message.reply_text("`𝖫𝗈𝗀𝗈 𝗂𝗇 𝖯𝗋𝗈𝖼𝖾𝗌𝗌. 𝖯𝗅𝖾𝖺𝗌𝖾 𝗐𝖺𝗂𝗍 𝖺 𝗌𝖾𝖼...`")

        # Choose a random background image
        random_logo = random.choice(LOGO_LINKS)
        response = requests.get(random_logo)
        response.raise_for_status()  # Ensure the request was successful
        img = Image.open(io.BytesIO(response.content))

        # Draw text on the image
        draw = ImageDraw.Draw(img)
        fnt_files = glob.glob("./shigaraki/fonts/*")  # Update to your font directory
        if not fnt_files:
            await status_message.edit("𝖭𝗈 𝖿𝗈𝗇𝗍𝗌 𝖺𝗏𝖺𝗂𝗅𝖺𝖻𝗅𝖾 𝗂𝗇 𝗍𝗁𝖾 `𝖿𝗈𝗇𝗍𝗌` 𝖽𝗂𝗋𝖾𝖼𝗍𝗈𝗋𝗒.")
            return
        random_font = random.choice(fnt_files)
        font = ImageFont.truetype(random_font, 120)

        # Center the text
        image_width, image_height = img.size
        text_bbox = draw.textbbox((0, 0), text, font=font)  # Calculate text bounding box
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        x, y = (image_width - text_width) / 2, (image_height - text_height) / 2
        draw.text((x, y), text, font=font, fill="white", stroke_width=1, stroke_fill="black")

        # Save the generated logo
        fname = "generated_logo.png"
        img.save(fname, "PNG")

        # Send the generated logo back to the user
        await client.send_photo(
            chat_id=message.chat.id,
            photo=fname,
            caption=f"**𝖫𝗈𝗀𝗈 𝖦𝖾𝗇𝖾𝗋𝖺𝗍𝖾𝖽 𝖻𝗒 @{BOT_USERNAME}**"
        )

        # Clean up the generated file
        os.remove(fname)
        await status_message.delete()

    except requests.exceptions.RequestException as e:
        await message.reply_text(f"𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽 𝗐𝗁𝗂𝗅𝖾 𝖿𝖾𝗍𝖼𝗁𝗂𝗇𝗀 𝗍𝗁𝖾 𝗅𝗈𝗀𝗈 𝖻𝖺𝖼𝗄𝗀𝗋𝗈𝗎𝗇𝖽: {str(e)}")
    except Exception as e:
        await message.reply_text(f"𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽: {str(e)}")

@pgram.on_message(filters.command("clogo", prefixes=config.COMMAND_PREFIXES))
@error
@save
async def make_logog(client: Client, message: Message):
    msg = await message.reply("`𝖯𝗋𝗈𝖼𝖾𝗌𝗌𝗂𝗇𝗀...`")
    try:
        # Extract text from the command
        match = message.text.split(maxsplit=1)[1]
    except IndexError:
        return await msg.edit("`𝖯𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 𝗇𝖺𝗆𝖾 𝗍𝗈 𝗆𝖺𝗄𝖾 𝖺 𝗅𝗈𝗀𝗈...`")
    
    # Split text into two parts (first and last)
    first, last = "", ""
    if len(match.split()) >= 2:
        first, last = match.split()[:2]
    else:
        last = match

    import asyncio

    # Generate the logo
    logo = await generate(first, last) if asyncio.iscoroutinefunction(generate) else generate(first, last)

    # Save the logo
    name = "generated_clogo.png"
    logo.save(name, format="PNG")

    # Send the generated logo
    await client.send_photo(
        chat_id=message.chat.id,
        photo=name,
        reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None
    )

    # Clean up
    os.remove(name)
    await msg.delete()



@pgram.on_message(filters.command("blogo", prefixes=config.COMMAND_PREFIXES))
@error
@save
async def make_blackpink_logo(client: Client, message: Message):
    msg = await message.reply("`𝖯𝗋𝗈𝖼𝖾𝗌𝗌𝗂𝗇𝗀...`")
    try:
        # Extract text
        match = message.text.split(maxsplit=1)[1]
    except IndexError:
        return await msg.edit("`𝖯𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 𝗇𝖺𝗆𝖾 𝗍𝗈 𝗆𝖺𝗄𝖾 𝖺 𝗅𝗈𝗀𝗈...`")

    try:
        # Generate the blackpink logo
        logo = blackpink(match)

        # Save the logo
        logo_path = "generated_blogo.png"
        logo.save(logo_path, format="PNG")

        # Send the logo
        await client.send_photo(
            chat_id=message.chat.id,
            photo=logo_path,
            reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None
        )
        os.remove(logo_path)  # Clean up
        await msg.delete()

    except Exception as e:
        await msg.edit(f"𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽: {str(e)}")


__module__ = "𝖫𝗈𝗀𝗈"


__help__ = """**𝖴𝗌𝖾𝗋 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:**
  ✧ `/𝗅𝗈𝗀𝗈 <𝗍𝖾𝗑𝗍>` **:** 𝖦𝖾𝗇𝖾𝗋𝖺𝗍𝖾𝗌 𝖺 𝗅𝗈𝗀𝗈 𝗐𝗂𝗍𝗁 𝗍𝗁𝖾 𝗀𝗂𝗏𝖾𝗇 𝗍𝖾𝗑𝗍.
   ✧ `/𝖼𝗅𝗈𝗀𝗈 <𝗍𝖾𝗑𝗍>` **:** 𝖢𝗋𝖾𝖺𝗍𝖾𝗌 𝖺 𝖼𝗎𝗌𝗍𝗈𝗆 𝗅𝗈𝗀𝗈 𝗐𝗂𝗍𝗁 𝖺 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖼 𝗌𝗍𝗒𝗅𝖾.
   ✧ `/𝖻𝗅𝗈𝗀𝗈 <𝗍𝖾𝗑𝗍>` **:** 𝖦𝖾𝗇𝖾𝗋𝖺𝗍𝖾𝗌 𝖺 𝗅𝗈𝗀𝗈 𝗐𝗂𝗍𝗁 𝖺 𝖻𝗅𝖺𝖼𝗄-𝗉𝗂𝗇𝗄 𝗍𝗁𝖾𝗆𝖾.
 
*𝖤𝗑𝖺𝗆𝗉𝗅𝖾𝗌:*
  ✧ `/𝗅𝗈𝗀𝗈 𝖸𝗎𝗆𝖾𝗄𝗈`
  ✧ `/𝖼𝗅𝗈𝗀𝗈 𝖢𝗎𝗌𝗍𝗈𝗆 𝖫𝗈𝗀𝗈`
  ✧ `/𝖻𝗅𝗈𝗀𝗈 𝖡𝗅𝗂𝗇𝗄 𝖲𝗍𝗒𝗅𝖾`
"""