import os
import subprocess
import shutil
from pytz import timezone
from pyrogram import Client, filters
from pyrogram.types import Message
from config import config
from shigaraki import app , log , BACKUP_FILE_JSON , scheduler
import json
from shigaraki.decorator.errors import error
from shigaraki.decorator.save import save


# Database-specific backup function
def backup_db(db_name: str, path: str):
    try:
        subprocess.run(
            ["mongodump", "--uri", config.MONGODB_URI, "--db", db_name, "--out", path],
            check=True
        )
        shutil.make_archive(path, 'zip', path)
        return f"{path}.zip"
    except subprocess.CalledProcessError as e:
        return f"Backup failed: {str(e)}"

def restore_db(zip_path: str):
    try:
        extract_path = zip_path.replace(".zip", "")
        shutil.unpack_archive(zip_path, extract_path)
        subprocess.run(
            ["mongorestore", "--uri", config.MONGODB_URI, extract_path],
            check=True
        )
        return "Restore successful!"
    except (subprocess.CalledProcessError, shutil.ReadError) as e:
        return f"Restore failed: {str(e)}"

async def handle_backup(client: Client, message: Message):
    path = f"./backup/{config.BOT_NAME}"
    db_name = config.DATABASE_NAME  # Database name from config
    zip_path = backup_db(db_name, path)
    if zip_path.endswith(".zip"):
        await client.send_document(chat_id=config.OWNER_ID, document=zip_path)
        shutil.rmtree(path)  # Clean up the backup directory
        os.remove(zip_path)  # Clean up the zip file
        response = "Backup successful!"
    else:
        response = zip_path
    await message.reply_text(response)

async def handle_restore(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        await message.reply_text("Please reply to a backup zip file to restore.")
        return

    document = message.reply_to_message.document
    file_path = await client.download_media(document.file_id)
    response = restore_db(file_path)
    os.remove(file_path)  # Clean up the downloaded zip file
    await message.reply_text(response)

@app.on_message(filters.command("backup", prefixes=config.COMMAND_PREFIXES) & filters.user(config.OWNER_ID))
@error
@save
async def backup_command(client: Client, message: Message):
    await handle_backup(client, message)

@app.on_message(filters.command("restore", prefixes=config.COMMAND_PREFIXES) & filters.user(config.OWNER_ID))
@error
@save
async def restore_command(client: Client, message: Message):
    await handle_restore(client, message)

# Automatic backup function
async def scheduled_backup():
    path = f"./backup/{config.BOT_NAME}"
    db_name = config.DATABASE_NAME
    zip_path = backup_db(db_name, path)
    if zip_path.endswith(".zip"):
        message = await app.send_document(chat_id=config.LOG_CHANNEL, document=zip_path)
        shutil.rmtree(path)  # Clean up the backup directory
        os.remove(zip_path)  # Clean up the zip file

        # Save the file ID to a JSON file
        with open(BACKUP_FILE_JSON, "w") as f:
            json.dump({"file_id": message.document.file_id}, f)

        log.info("Backup completed and file ID saved.")


scheduler.add_job(scheduled_backup, "cron", hour=0, minute=0, timezone=timezone("Asia/Kolkata"))
scheduler.add_job(scheduled_backup, "cron", hour=1, minute=0, timezone=timezone("Asia/Kolkata"))
scheduler.add_job(scheduled_backup, "cron", hour=2, minute=0, timezone=timezone("Asia/Kolkata"))
scheduler.add_job(scheduled_backup, "cron", hour=3, minute=0, timezone=timezone("Asia/Kolkata"))
scheduler.add_job(scheduled_backup, "cron", hour=4, minute=0, timezone=timezone("Asia/Kolkata"))
scheduler.add_job(scheduled_backup, "cron", hour=5, minute=0, timezone=timezone("Asia/Kolkata"))
scheduler.add_job(scheduled_backup, "cron", hour=6, minute=0, timezone=timezone("Asia/Kolkata"))
scheduler.add_job(scheduled_backup, "cron", hour=7, minute=0, timezone=timezone("Asia/Kolkata"))
scheduler.add_job(scheduled_backup, "cron", hour=8, minute=0, timezone=timezone("Asia/Kolkata"))
scheduler.add_job(scheduled_backup, "cron", hour=9, minute=0, timezone=timezone("Asia/Kolkata"))
scheduler.add_job(scheduled_backup, "cron", hour=10, minute=0, timezone=timezone("Asia/Kolkata"))
scheduler.add_job(scheduled_backup, "cron", hour=11, minute=0, timezone=timezone("Asia/Kolkata"))
scheduler.add_job(scheduled_backup, "cron", hour=12, minute=0, timezone=timezone("Asia/Kolkata"))
scheduler.add_job(scheduled_backup, "cron", hour=18, minute=0, timezone=timezone("Asia/Kolkata"))



