from shigaraki.database.log_channel_db import get_log_channel
from shigaraki import app


# Helper function to send logs to the log channel
async def send_log(chat_id: int, log_message: str):
    log_channel_id = await get_log_channel(chat_id)
    if log_channel_id:
        try:
            await app.send_message(log_channel_id, log_message, disable_web_page_preview=True)
        except Exception as e:
            print(f"Error sending log: {e}")

# Log format helper
async def format_log(action: str, chat: str, admin: str = None, user: str = None, pinned_link: str = None):
    log = f"**Action:** {action}\n**Chat:** {chat}"
    if admin:
        log += f"\n**Admin:** {admin}"
    if user:
        log += f"\n**User:** {user}"
    if pinned_link:
        log += f"\n**Pinned Message:** [View Message]({pinned_link})"
    return log

