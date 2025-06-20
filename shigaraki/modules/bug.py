from pyrogram import filters
from pyrogram.enums import ParseMode
from shigaraki import app
from config import config 

# Define a handler for the /bug command
@app.on_message(filters.command("bug", prefixes=config.COMMAND_PREFIXES))
async def bug_command_handler(client, message):
    # Check if the command is a reply
    if message.reply_to_message:
        # Get the message being replied to
        replied_message = message.reply_to_message

        # Extract message content
        content = replied_message.text or replied_message.caption

        # Check if there is media content
        media_type = (
            "**Media content included**"
            if replied_message.photo
            or replied_message.document
            or replied_message.video
            or replied_message.audio
            or replied_message.animation
            else "**No media content included**"
        )

        # Prepare the report message with message link and media content info
        if message.from_user.username :
            
            report_message = f"**Bug reported by @{message.from_user.username}:**\n\n{content}\n\n{media_type}\n\n**Message Link:** {replied_message.link}"
        else :
            report_message = f"**Bug reported by {message.from_user.mention}:**\n\n{content}\n\n{media_type}\n\n**Message Link:** {replied_message.link}"
        # Send the report message
        await client.send_message(config.LOG_CHANNEL, report_message, parse_mode=ParseMode.MARKDOWN
        )
    else:
        # If not a reply, send a message to reply with /bug command to report a bug
        await client.send_message(
            message.chat.id,
            "To report a bug, please reply to the message with **/ bug** cmd.",
            parse_mode=ParseMode.MARKDOWN,
        )