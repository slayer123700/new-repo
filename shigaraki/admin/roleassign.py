import json
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from shigaraki import app as pgram
from config import config
from shigaraki.decorator.errors import error
from shigaraki.decorator.save import save

OWNER_ID = config.OWNER_ID

# Path to the sudoers.json file
sudoers_file = "sudoers.json"

# Ensure the JSON file exists
if not os.path.exists(sudoers_file):
    with open(sudoers_file, "w") as f:
        json.dump({"Hokages": [], "Jonins": [], "Chunins": [], "Genins": []}, f, indent=4)

# Function to load roles from the file
def load_roles():
    with open(sudoers_file, "r") as f:
        return json.load(f)

# Function to save roles to the file
def save_roles(data):
    with open(sudoers_file, "w") as f:
        json.dump(data, f, indent=4)

# Ensure OWNER_ID is in Hokages
def ensure_owner_is_hokage():
    roles = load_roles()
    if OWNER_ID not in roles["Hokages"]:
        roles["Hokages"].append(OWNER_ID)
        save_roles(roles)
        

# Check if user has sufficient permissions
def has_permission(user_id):
    roles = load_roles()
    return user_id == OWNER_ID or user_id in roles["Hokages"] or user_id in roles["Jonins"]

# Command to assign roles
@pgram.on_message(filters.command("assign" , prefixes=config.COMMAND_PREFIXES))
@error
@save
async def assign_role(client: Client, message: Message):
    if not has_permission(message.from_user.id):
        await message.reply("𝖸𝗈𝗎 𝖽𝗈𝗇'𝗍 𝗁𝖺𝗏𝖾 𝗉𝖾𝗋𝗆𝗂𝗌𝗌𝗂𝗈𝗇 𝗍𝗈 𝗎𝗌𝖾 𝗍𝗁𝗂𝗌 𝖼𝗈𝗆𝗆𝖺𝗇𝖽.")
        return

    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) == 2 and message.command[1].isdigit():
        user_id = int(message.command[1])
    else:
        await message.reply("𝖯𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 𝗏𝖺𝗅𝗂𝖽 𝖴𝗌𝖾𝗋𝖨𝖣 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗎𝗌𝖾𝗋'𝗌 𝗆𝖾𝗌𝗌𝖺𝗀𝖾.")
        return

    roles = load_roles()
    role_buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(role, callback_data=f"assign:{role}:{user_id}:{message.from_user.id}")]
            for role in ["Hokage", "Jonin", "Chunin", "Genin"]
        ]
    )
    await message.reply(
        "𝖢𝗁𝗈𝗈𝗌𝖾 𝖺 𝗋𝗈𝗅𝖾 𝗍𝗈 𝖺𝗌𝗌𝗂𝗀𝗇:",
        reply_markup=role_buttons
    )

# Callback handler for role assignment
@pgram.on_callback_query(filters.regex(r"^assign:(.+?):(\d+):(\d+)$"))
@error
@save
async def handle_assign_callback(client: Client, callback: CallbackQuery):
    ensure_owner_is_hokage()
    role, user_id, cmd_user_id = callback.data.split(":")[1:]
    user_id, cmd_user_id = int(user_id), int(cmd_user_id)

    if callback.from_user.id != cmd_user_id:
        await callback.answer("𝖸𝗈𝗎 𝖺𝗋𝖾 𝗇𝗈𝗍 𝖺𝗅𝗅𝗈𝗐𝖾𝖽 𝗍𝗈 𝗉𝖾𝗋𝖿𝗈𝗋𝗆 𝗍𝗁𝗂𝗌 𝖺𝖼𝗍𝗂𝗈𝗇.", show_alert=True)
        return

    roles = load_roles()
    valid_roles = ["Hokage", "Jonin", "Chunin", "Genin"]

    # Check permissions
    if cmd_user_id == OWNER_ID or cmd_user_id in roles["Hokages"]:
        allowed_roles = valid_roles
    elif cmd_user_id in roles["Jonins"]:
        allowed_roles = valid_roles[2:]  # Jonins can only assign Chunin or Genin
    else:
        await callback.answer("𝖸𝗈𝗎 𝖽𝗈𝗇'𝗍 𝗁𝖺𝗏𝖾 𝗉𝖾𝗋𝗆𝗂𝗌𝗌𝗂𝗈𝗇 𝗍𝗈 𝖺𝗌𝗌𝗂𝗀𝗇 𝗋𝗈𝗅𝖾𝗌.", show_alert=True)
        return

    if role not in allowed_roles:
        await callback.answer("𝖸𝗈𝗎 𝖼𝖺𝗇𝗇𝗈𝗍 𝖺𝗌𝗌𝗂𝗀𝗇 𝗍𝗁𝗂𝗌 𝗋𝗈𝗅𝖾.", show_alert=True)
        return

    # Remove the user from all roles first
    for r in valid_roles:
        if user_id in roles[r + "s"]:
            roles[r + "s"].remove(user_id)

    # Assign the new role
    roles[role + "s"].append(user_id)
    save_roles(roles)

    await callback.edit_message_text(f"**𝖠𝗌𝗌𝗂𝗀𝗇𝖾𝖽 {𝗋𝗈𝗅𝖾} 𝗍𝗈 𝗎𝗌𝖾𝗋 𝖨𝖣: {𝗎𝗌𝖾𝗋_𝗂𝖽}**")

# Command to remove users from their roles
@pgram.on_message(filters.command("unassign" , prefixes=config.COMMAND_PREFIXES))
@error
@save
async def remove_role(client: Client, message: Message):
    ensure_owner_is_hokage()

    if not has_permission(message.from_user.id):
        await message.reply("𝖸𝗈𝗎 𝖽𝗈𝗇'𝗍 𝗁𝖺𝗏𝖾 𝗉𝖾𝗋𝗆𝗂𝗌𝗌𝗂𝗈𝗇 𝗍𝗈 𝗎𝗌𝖾 𝗍𝗁𝗂𝗌 𝖼𝗈𝗆𝗆𝖺𝗇𝖽.")
        return

    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) == 2 and message.command[1].isdigit():
        user_id = int(message.command[1])
    else:
        await message.reply("𝖯𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺 𝗏𝖺𝗅𝗂𝖽 𝖴𝗌𝖾𝗋𝖨𝖣 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗎𝗌𝖾𝗋'𝗌 𝗆𝖾𝗌𝗌𝖺𝗀𝖾.")
        return

    roles = load_roles()
    removed = False

    # Remove the user from all roles
    for r in ["Hokages", "Jonins", "Chunins", "Genins"]:
        if user_id in roles[r]:
            roles[r].remove(user_id)
            removed = True

    if removed:
        save_roles(roles)
        await message.reply(f"**𝖱𝖾𝗆𝗈𝗏𝖾𝖽 𝖺𝗅𝗅 𝗋𝗈𝗅𝖾𝗌 𝖿𝗋𝗈𝗆 𝗎𝗌𝖾𝗋 𝖨𝖣 : {user_id}**")
    else:
        await message.reply(f"**𝖴𝗌𝖾𝗋 𝖨𝖣: {𝗎𝗌𝖾𝗋_𝗂𝖽} 𝖽𝗈𝖾𝗌 𝗇𝗈𝗍 𝗁𝖺𝗏𝖾 𝖺𝗇𝗒 𝗋𝗈𝗅𝖾𝗌.**")

# Command to list all users with roles
@pgram.on_message(filters.command("staffs" , prefixes=config.COMMAND_PREFIXES) & filters.user(OWNER_ID))
@error
@save
async def list_staffs(client: Client, message: Message):
    roles = load_roles()
    response = "**𝗟𝗶𝘀𝘁 𝗼𝗳 𝗦𝘁𝗮𝗳𝗳:**\n\n"

    for role, users in roles.items():
        if users:
            response += f"**{role}:**\n"
            response += "\n".join([f"- `{user_id}`" for user_id in users])
            response += "\n\n"
        else:
            response += f"**{role}:** None\n\n"

    await message.reply(response, disable_web_page_preview=True)