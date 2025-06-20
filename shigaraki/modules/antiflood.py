from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, filters, MessageHandler
from shigaraki import ptb , ANTI_FLOOD_GROUP
from shigaraki.database.anti_flooddb import (
    get_antiflood_settings,
    set_flood_threshold,
    set_flood_timer,
    set_flood_action,
    set_delete_flood_messages,
    get_flood_action_duration,
    set_flood_action_duration
)
from datetime import timedelta
from shigaraki.helper.user import is_user_admin  # Import the function that checks admin status
from shigaraki.helper.anti_flood_helper import *
from shigaraki.helper.handler import MultiCommandHandler
from shigaraki.database.approve_db import is_user_approved

async def flood_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = await get_antiflood_settings(update.effective_chat.id)
    user = update.effective_user  # Assign user directly, even if None

    # Check if user exists
    if not user:
        return  # Exit if no user is associated with the update

    # Check if the command issuer is an admin
    if not await is_user_admin(update, context, user.id):
        await update.message.reply_text(
            "*𝖧𝗈𝗅𝖽 𝗎𝗉!* 𝖮𝗇𝗅𝗒 𝖺𝖽𝗆𝗂𝗇𝗌 𝖼𝖺𝗇 𝗎𝗌𝖾 𝗍𝗁𝗂𝗌 𝖼𝗈𝗆𝗆𝖺𝗇𝖽.",
            parse_mode="Markdown"
        )
        return

    # Check if antiflood is disabled
    if settings.get("flood_threshold", 0) == 0:
        await update.message.reply_text(
            "𝖳𝗁𝗂𝗌 𝖼𝗁𝖺𝗍 𝗂𝗌 𝗇𝗈𝗍 𝖼𝗎𝗋𝗋𝖾𝗇𝗍𝗅𝗒 𝖾𝗇𝖿𝗈𝗋𝖼𝗂𝗇𝗀 𝖿𝗅𝗈𝗈𝖽 𝖼𝗈𝗇𝗍𝗋𝗈𝗅.",
            parse_mode="Markdown"
        )
        return

    # Convert the action duration from seconds into a human-readable format
    action_duration_seconds = settings.get("action_duration", 86400)  # Default: 1 day
    readable_duration = str(timedelta(seconds=action_duration_seconds))

    await update.message.reply_text(
        f"**𝖠𝗇𝗍𝗂-𝖥𝗅𝗈𝗈𝖽 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌**\n"
        f"• **𝖳𝗁𝗋𝖾𝗌𝗁𝗈𝗅𝖽:** {settings['flood_threshold']} messages\n"
        f"• **𝖳𝗂𝗆𝖾𝖽 𝖥𝗅𝗈𝗈𝖽:** {settings['flood_timer_count']} messages in {settings['flood_timer_duration']} seconds\n"
        f"• **𝖠𝖼𝗍𝗂𝗈𝗇:** {settings['flood_action'].capitalize()}\n"
        f"• **𝖠𝖼𝗍𝗂𝗈𝗇 𝖣𝗎𝗋𝖺𝗍𝗂𝗈𝗇:** {readable_duration}\n"
        f"• **𝖣𝖾𝗅𝖾𝗍𝖾 𝖥𝗅𝗈𝗈𝖽 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌:** {'Enabled' if settings['delete_flood_messages'] else 'Disabled'}",
        parse_mode="Markdown"
    )

# Command: /setflood - Set message count to trigger flood action
async def setflood_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user  # Assign user directly, even if None

    # Check if user exists
    if not user:
        return  # Exit if no user is associated with the update

    # Check if the command issuer is an admin
    if not await is_user_admin(update, context, user.id):
        await update.message.reply_text(
            "*𝖧𝗈𝗅𝖽 𝗎𝗉!* 𝖮𝗇𝗅𝗒 𝖺𝖽𝗆𝗂𝗇𝗌 𝖼𝖺𝗇 𝗎𝗌𝖾 𝗍𝗁𝗂𝗌 𝖼𝗈𝗆𝗆𝖺𝗇𝖽.",
            parse_mode="Markdown"
        )
        return    

    if len(context.args) != 1:
        await update.message.reply_text("𝖴𝗌𝖺𝗀𝖾: `/𝗌𝖾𝗍𝖿𝗅𝗈𝗈𝖽 <𝗇𝗎𝗆𝖻a𝖾𝗋/𝗈𝖿𝖿>`", parse_mode="Markdown")
        return
    arg = context.args[0].lower()
    if arg in ["off", "no", "0"]:
        await set_flood_threshold(update.effective_chat.id, 0)
        await update.message.reply_text("𝖠𝗇𝗍𝗂-𝖥𝗅𝗈𝗈𝖽 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 **𝖽𝗂𝗌𝖺𝖻𝗅𝖾𝖽**.", parse_mode="Markdown")
    else:
        try:
            threshold = int(arg)
            await set_flood_threshold(update.effective_chat.id, threshold)
            await update.message.reply_text(
                f"𝖠𝗇𝗍𝗂-𝖥𝗅𝗈𝗈𝖽 𝗂𝗌 𝗇𝗈𝗐 𝗍𝗋𝗂𝗀𝗀𝖾𝗋𝖾𝖽 𝖺𝖿𝗍𝖾𝗋 **{𝗍𝗁𝗋𝖾𝗌𝗁𝗈𝗅𝖽} 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌**.", parse_mode="Markdown"
            )
        except ValueError:
            await update.message.reply_text("𝖯𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 **𝗏𝖺𝗅𝗂𝖽 𝗇𝗎𝗆𝖻𝖾𝗋** 𝖿𝗈𝗋 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗍𝗁𝗋𝖾𝗌𝗁𝗈𝗅𝖽.", parse_mode="Markdown")

# Command: /actionduration - Set the duration for tban or tmute
async def actionduration_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    user = update.effective_user  # Assign user directly, even if None

    # Check if user exists
    if not user:
        return  # Exit if no user is associated with the update

    # Check if the command issuer is an admin
    if not await is_user_admin(update, context, user.id):
        await update.message.reply_text(
            "*𝖧𝗈𝗅𝖽 𝗎𝗉!* 𝖮𝗇𝗅𝗒 𝖺𝖽𝗆𝗂𝗇𝗌 𝖼𝖺𝗇 𝗎𝗌𝖾 𝗍𝗁𝗂𝗌 𝖼𝗈𝗆𝗆𝖺𝗇𝖽.",
            parse_mode="Markdown"
        )
        return

    if not context.args:
        await update.message.reply_text(
            "𝖴𝗌𝖺𝗀𝖾: `/𝖺𝖼𝗍𝗂𝗈𝗇𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇 <𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇>`\n"
            "𝖤𝗑𝖺𝗆𝗉𝗅𝖾: `/𝖺𝖼𝗍𝗂𝗈𝗇𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇 𝟣𝖽 𝟤𝗁 𝟥𝗆 𝟦𝗌`",
            parse_mode="Markdown",
        )
        return

    try:
        duration = parse_duration(" ".join(context.args))
        await set_flood_action_duration(update.effective_chat.id, duration.total_seconds())
        await update.message.reply_text(
            f"𝖠𝖼𝗍𝗂𝗈𝗇 𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇 𝗌𝖾𝗍 𝗍𝗈 **{str(duration)}**.",
            parse_mode="Markdown",
        )
    except ValueError as e:
        await update.message.reply_text(str(e), parse_mode="Markdown")

# Command: /setfloodtimer - Set timed flood settings
async def setfloodtimer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    user = update.effective_user  # Assign user directly, even if None

    # Check if user exists
    if not user:
        return  # Exit if no user is associated with the update

    # Check if the command issuer is an admin
    if not await is_user_admin(update, context, user.id):
        await update.message.reply_text(
            "*𝖧𝗈𝗅𝖽 𝗎𝗉!* 𝖮𝗇𝗅𝗒 𝖺𝖽𝗆𝗂𝗇𝗌 𝖼𝖺𝗇 𝗎𝗌𝖾 𝗍𝗁𝗂𝗌 𝖼𝗈𝗆𝗆𝖺𝗇𝖽.",
            parse_mode="Markdown"
        )
        return

    if len(context.args) != 2:
        await update.message.reply_text(
            "𝖴𝗌𝖺𝗀𝖾: `/𝗌𝖾𝗍𝖿𝗅𝗈𝗈𝖽𝗍𝗂𝗆𝖾𝗋 <𝖼𝗈𝗎𝗇𝗍> <𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇 𝗂𝗇 𝗌𝖾𝖼𝗈𝗇𝖽𝗌>`", parse_mode="Markdown"
        )
        return
    try:
        count = int(context.args[0])
        duration = int(context.args[1])
        await set_flood_timer(update.effective_chat.id, count, duration)
        await update.message.reply_text(
            f"𝖳𝗂𝗆𝖾𝖽 𝖠𝗇𝗍𝗂-𝖥𝗅𝗈𝗈𝖽 𝗌𝖾𝗍 𝗍𝗈 **{𝖼𝗈𝗎𝗇𝗍} 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝗂𝗇 {𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇} 𝗌𝖾𝖼𝗈𝗇𝖽𝗌**.", parse_mode="Markdown"
        )
    except ValueError:
        await update.message.reply_text("𝖯𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 **𝗏𝖺𝗅𝗂𝖽 𝗇𝗎𝗆𝖻𝖾𝗋𝗌** 𝖿𝗈𝗋 𝖼𝗈𝗎𝗇𝗍 𝖺𝗇𝖽 𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇.", parse_mode="Markdown")

# Command: /floodmode - Set action for flood detection
async def floodmode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user  # Assign user directly, even if None

    # Check if user exists
    if not user:
        return  # Exit if no user is associated with the update

    # Check if the command issuer is an admin
    if not await is_user_admin(update, context, user.id):
        await update.message.reply_text(
            "*𝖧𝗈𝗅𝖽 𝗎𝗉!* 𝖮𝗇𝗅𝗒 𝖺𝖽𝗆𝗂𝗇𝗌 𝖼𝖺𝗇 𝗎𝗌𝖾 𝗍𝗁𝗂𝗌 𝖼𝗈𝗆𝗆𝖺𝗇𝖽.",
            parse_mode="Markdown"
        )
        return

    if not context.args:
        await update.message.reply_text(
            "𝖴𝗌𝖺𝗀𝖾: `/𝖿𝗅𝗈𝗈𝖽𝗆𝗈𝖽𝖾 <𝖻𝖺𝗇/𝗆𝗎𝗍𝖾/𝗄𝗂𝖼𝗄/𝗍𝖻𝖺𝗇/𝗍𝗆𝗎𝗍𝖾>`", parse_mode="Markdown"
        )
        return
    action = context.args[0].lower()
    if action not in ["ban", "mute", "kick", "tban", "tmute"]:
        await update.message.reply_text(
            "𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖺𝖼𝗍𝗂𝗈𝗇. 𝖴𝗌𝖾 **𝖻𝖺𝗇/𝗆𝗎𝗍𝖾/𝗄𝗂𝖼𝗄/𝗍𝖻𝖺𝗇/𝗍𝗆𝗎𝗍𝖾**.", parse_mode="Markdown"
        )
        return
    await set_flood_action(update.effective_chat.id, action)
    await update.message.reply_text(f"𝖥𝗅𝗈𝗈𝖽 𝗆𝗈𝖽𝖾 𝗌𝖾𝗍 𝗍𝗈 **{action}**.", parse_mode="Markdown")

# Command: /clearflood - Set whether to delete flood messages
async def clearflood_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user  # Assign user directly, even if None

    # Check if user exists
    if not user:
        return  # Exit if no user is associated with the update

    # Check if the command issuer is an admin
    if not await is_user_admin(update, context, user.id):
        await update.message.reply_text(
            "**𝖧𝗈𝗅𝖽 𝗎𝗉!* 𝖮𝗇𝗅𝗒 𝖺𝖽𝗆𝗂𝗇𝗌 𝖼𝖺𝗇 𝗎𝗌𝖾 𝗍𝗁𝗂𝗌 𝖼𝗈𝗆𝗆𝖺𝗇𝖽.",
            parse_mode="Markdown"
        )
        return

    if not context.args or context.args[0].lower() not in ["yes", "no", "on", "off"]:
        await update.message.reply_text("𝖴𝗌𝖺𝗀𝖾: `/𝖼𝗅𝖾𝖺𝗋𝖿𝗅𝗈𝗈𝖽 <𝗒𝖾𝗌/𝗇𝗈>`", parse_mode="Markdown")
        return
    delete = context.args[0].lower() in ["yes", "on"]
    await set_delete_flood_messages(update.effective_chat.id, delete)
    await update.message.reply_text(
        f"𝖥𝗅𝗈𝗈𝖽 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝗐𝗂𝗅𝗅 **{'𝖻𝖾 𝖽𝖾𝗅𝖾𝗍𝖾𝖽' if delete else '𝗇𝗈𝗍 𝖻𝖾 𝖽𝖾𝗅𝖾𝗍𝖾𝖽'}**.", parse_mode="Markdown"
    )

# Flood detection logic
async def flood_detection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user  # Assign user directly, even if None

    settings = await get_antiflood_settings(chat_id)
    if settings["flood_threshold"] == 0:
        return  # Antiflood disabled

    # Check if user exists
    if not user:
        return  # Exit if no user is associated with the update
    
    user_id = user.id
    
    if await is_user_approved(chat_id , user_id):
        return

    # Skip flood detection for admins
    if await is_user_admin(update, context, user_id):
        return


    # Update user message count and track messages
    flood_tracker[user_id]["count"] += 1
    flood_tracker[user_id]["timestamps"].append(update.message.date)
    flood_tracker[user_id]["messages"].append(update.message)

    # Check regular flood
    if flood_tracker[user_id]["count"] >= settings["flood_threshold"]:
        await take_flood_action(update, context, settings, user_id)
        flood_tracker[user_id] = {"count": 0, "timestamps": [], "messages": []}

    # Check timed flood
    elif settings["flood_timer_count"] > 0:
        timestamps = flood_tracker[user_id]["timestamps"]
        if len(timestamps) >= settings["flood_timer_count"] and \
           (timestamps[-1] - timestamps[-settings["flood_timer_count"]]).total_seconds() <= settings["flood_timer_duration"]:
            await take_flood_action(update, context, settings, user_id)
            flood_tracker[user_id] = {"count": 0, "timestamps": [], "messages": []}

# Updated take_flood_action to use custom duration
async def take_flood_action(update: Update, context: ContextTypes.DEFAULT_TYPE, settings, user_id):
    action = settings["flood_action"]
    chat_id = update.effective_chat.id
    duration_seconds = await get_flood_action_duration(chat_id)
    duration = timedelta(seconds=duration_seconds) if duration_seconds else timedelta(days=3)

    # Announcement message
    user_mention = update.effective_user.mention_html()
    announcement = (
        f" <b>Anti-Flood Alert</b> \n\n"
        f"User {user_mention} has been <b>{action.capitalize()}ed</b> for violating the anti-flood rules."
    )
    await update.effective_chat.send_message(announcement, parse_mode="HTML")

    # Execute the chosen action
    if action == "ban":
        await context.bot.ban_chat_member(chat_id, user_id)
    elif action == "mute":
        await context.bot.restrict_chat_member(chat_id, user_id, ChatPermissions())
    elif action == "kick":
        await context.bot.ban_chat_member(chat_id, user_id)
        await context.bot.unban_chat_member(chat_id, user_id)
    elif action == "tban":
        await context.bot.ban_chat_member(chat_id, user_id, until_date=update.message.date + duration)
    elif action == "tmute":
        await context.bot.restrict_chat_member(chat_id, user_id, ChatPermissions(), until_date=update.message.date + duration)

    # Delete all flood messages if enabled
    if settings["delete_flood_messages"]:
        for msg in flood_tracker[user_id]["messages"]:
            try:
                await msg.delete()
            except:
                pass


# Add handlers
ptb.add_handler(MultiCommandHandler("flood", flood_command , filters.ChatType.GROUPS | filters.ChatType.SUPERGROUP))
ptb.add_handler(MultiCommandHandler("setflood", setflood_command , filters.ChatType.GROUPS | filters.ChatType.SUPERGROUP))
ptb.add_handler(MultiCommandHandler("setfloodtimer", setfloodtimer_command , filters.ChatType.GROUPS | filters.ChatType.SUPERGROUP))
ptb.add_handler(MultiCommandHandler("floodmode", floodmode_command , filters.ChatType.GROUPS | filters.ChatType.SUPERGROUP))
ptb.add_handler(MultiCommandHandler("clearflood", clearflood_command , filters.ChatType.GROUPS | filters.ChatType.SUPERGROUP))
antiflood = MessageHandler(filters.ALL & ~filters.COMMAND, flood_detection)
ptb.add_handler(MultiCommandHandler("actionduration", actionduration_command , filters.ChatType.GROUPS | filters.ChatType.SUPERGROUP))
ptb.add_handler(antiflood, group=ANTI_FLOOD_GROUP)


__module__ = "𝖠𝗇𝗍𝗂𝖥𝗅𝗈𝗈𝖽"


__help__ = """**𝖠𝖽𝗆𝗂𝗇𝗌 𝗈𝗇𝗅𝗒:**
  ✧ `/𝖿𝗅𝗈𝗈𝖽` **:** 𝖣𝗂𝗌𝗉𝗅𝖺𝗒 𝖼𝗎𝗋𝗋𝖾𝗇𝗍 𝖺𝗇𝗍𝗂-𝖿𝗅𝗈𝗈𝖽 𝗌𝖾𝗍𝗍𝗂𝗇𝗀𝗌.
   ✧ `/𝗌𝖾𝗍𝖿𝗅𝗈𝗈𝖽 <𝗇𝗎𝗆𝖻𝖾𝗋/𝗈𝖿𝖿>` **:** 𝖲𝖾𝗍 𝗍𝗁𝖾 𝗇𝗎𝗆𝖻𝖾𝗋 𝗈𝖿 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝗍𝗈 𝗍𝗋𝗂𝗀𝗀𝖾𝗋 𝖿𝗅𝗈𝗈𝖽 𝖺𝖼𝗍𝗂𝗈𝗇, 𝗈𝗋 𝖽𝗂𝗌𝖺𝖻𝗅𝖾 𝖺𝗇𝗍𝗂-𝖿𝗅𝗈𝗈𝖽.
   ✧ `/𝗌𝖾𝗍𝖿𝗅𝗈𝗈𝖽𝗍𝗂𝗆𝖾𝗋 <𝖼𝗈𝗎𝗇𝗍> <𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇>` **:** 𝖲𝖾𝗍 𝗍𝗂𝗆𝖾𝖽 𝖿𝗅𝗈𝗈𝖽 𝗌𝖾𝗍𝗍𝗂𝗇𝗀𝗌 (𝖾.𝗀., `𝟥 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝗂𝗇 𝟣𝟢 𝗌𝖾𝖼𝗈𝗇𝖽𝗌`).
   ✧ `/𝖿𝗅𝗈𝗈𝖽𝗆𝗈𝖽𝖾 <𝖻𝖺𝗇/𝗆𝗎𝗍𝖾/𝗄𝗂𝖼𝗄/𝗍𝖻𝖺𝗇/𝗍𝗆𝗎𝗍𝖾>` **:** 𝖲𝖾𝗍 𝗍𝗁𝖾 𝖺𝖼𝗍𝗂𝗈𝗇 𝗍𝗈 𝗍𝖺𝗄𝖾 𝗐𝗁𝖾𝗇 𝖿𝗅𝗈𝗈𝖽 𝖼𝗈𝗇𝗍𝗋𝗈𝗅 𝗂𝗌 𝗍𝗋𝗂𝗀𝗀𝖾𝗋𝖾𝖽.
   ✧ `/𝖺𝖼𝗍𝗂𝗈𝗇𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇 <𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇>` **:** 𝖲𝖾𝗍 𝗍𝗁𝖾 𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇 𝗈𝖿 `𝗍𝗆𝗎𝗍𝖾` 𝗈𝗋 `𝗍𝖻𝖺𝗇` 𝖺𝖼𝗍𝗂𝗈𝗇𝗌 (𝖾.𝗀., `𝟣𝗁`, `𝟤𝖽 𝟥𝗁`, 𝖾𝗍𝖼.).
   ✧ `/𝖼𝗅𝖾𝖺𝗋𝖿𝗅𝗈𝗈𝖽 <𝗒𝖾𝗌/𝗇𝗈>` **:** 𝖤𝗇𝖺𝖻𝗅𝖾 𝗈𝗋 𝖽𝗂𝗌𝖺𝖻𝗅𝖾 𝗍𝗁𝖾 𝖽𝖾𝗅𝖾𝗍𝗂𝗈𝗇 𝗈𝖿 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝗍𝗁𝖺𝗍 𝗍𝗋𝗂𝗀𝗀𝖾𝗋𝖾𝖽 𝗍𝗁𝖾 𝖺𝗇𝗍𝗂-𝖿𝗅𝗈𝗈𝖽.
 
*𝖤𝗑𝖺𝗆𝗉𝗅𝖾𝗌:*
  ✧ `/𝗌𝖾𝗍𝖿𝗅𝗈𝗈𝖽 𝟧` **:** 𝖳𝗋𝗂𝗀𝗀𝖾𝗋 𝖿𝗅𝗈𝗈𝖽 𝖺𝖼𝗍𝗂𝗈𝗇 𝖺𝖿𝗍𝖾𝗋 𝟧 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌.
   ✧ `/𝗌𝖾𝗍𝖿𝗅𝗈𝗈𝖽 𝗈𝖿𝖿` **:** 𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖿𝗅𝗈𝗈𝖽 𝖼𝗈𝗇𝗍𝗋𝗈𝗅.
   ✧ `/𝗌𝖾𝗍𝖿𝗅𝗈𝗈𝖽𝗍𝗂𝗆𝖾𝗋 𝟥 𝟣𝟢` **:** 𝖳𝗋𝗂𝗀𝗀𝖾𝗋 𝖿𝗅𝗈𝗈𝖽 𝖺𝖼𝗍𝗂𝗈𝗇 𝗂𝖿 𝟥 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖺𝗋𝖾 𝗌𝖾𝗇𝗍 𝗐𝗂𝗍𝗁𝗂𝗇 𝟣𝟢 𝗌𝖾𝖼𝗈𝗇𝖽𝗌.
   ✧ `/𝖿𝗅𝗈𝗈𝖽𝗆𝗈𝖽𝖾 𝖻𝖺𝗇` **:** 𝖡𝖺𝗇 𝗎𝗌𝖾𝗋𝗌 𝗐𝗁𝗈 𝗍𝗋𝗂𝗀𝗀𝖾𝗋 𝖿𝗅𝗈𝗈𝖽 𝖼𝗈𝗇𝗍𝗋𝗈𝗅.
   ✧ `/𝖺𝖼𝗍𝗂𝗈𝗇𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇 𝟤𝖽` **:** 𝖳𝖾𝗆𝗉𝗈𝗋𝖺𝗋𝗂𝗅𝗒 𝖻𝖺𝗇/𝗆𝗎𝗍𝖾 𝗎𝗌𝖾𝗋𝗌 𝖿𝗈𝗋 𝟤 𝖽𝖺𝗒𝗌 𝗐𝗁𝖾𝗇 𝖿𝗅𝗈𝗈𝖽 𝖼𝗈𝗇𝗍𝗋𝗈𝗅 𝗂𝗌 𝗍𝗋𝗂𝗀𝗀𝖾𝗋𝖾𝖽.
   ✧ `/𝖼𝗅𝖾𝖺𝗋𝖿𝗅𝗈𝗈𝖽 𝗒𝖾𝗌` **:** 𝖠𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖽𝖾𝗅𝖾𝗍𝖾 𝖿𝗅𝗈𝗈𝖽-𝗍𝗋𝗂𝗀𝗀𝖾𝗋𝗂𝗇𝗀 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌.
 """