from pyrogram import filters
import requests
from shigaraki import app as pbot
from pytz import timezone
from datetime import datetime
from pyrogram.enums import ParseMode
from shigaraki.decorator.errors import error
from shigaraki.decorator.save import save

def get_indian_tz_time(hour, minutes):
    current_time = datetime.now()
    date_converted = datetime(current_time.year, current_time.month, current_time.day, int(hour), int(minutes),
                              tzinfo=timezone("Japan")).astimezone(timezone("Asia/Kolkata"))
    return date_converted.strftime("%I:%M %p")


@pbot.on_message(filters.command('latest'))
@pbot.on_message(filters.command('schedule'))
@error
@save
async def schedule(_, message):
    results = requests.get('https://subsplease.org/api/?f=schedule&h=true&tz=Japan').json()
    text = None
    for result in results['schedule']:
        title = result['title']
        hours, minutes = result['time'].split(':')
        time = get_indian_tz_time(hours, minutes)
        aired = bool(result['aired'])
        title = f"**[{title}](https://subsplease.org/shows/{result['page']})**" if not aired else f"**~~[{title}](https://subsplease.org/shows/{result['page']})~~**"
        data = f"{title} - **{time}**"

        if text:
            text = f"{text}\n{data}"
        else:
            text = data

    await message.reply_text(f"**𝖳𝗈𝖽𝖺𝗒'𝗌 𝖲𝖼𝗁𝖾𝖽𝗎𝗅𝖾:**\n𝖳𝗂𝗆𝖾-𝖹𝗈𝗇𝖾: 𝖨𝗇𝖽𝗂𝖺𝗇 (GMT +9)\n\n{text}", parse_mode=ParseMode.MARKDOWN)


__module__ = "𝖠𝗇𝗂𝗆𝖾 𝖲𝖼𝗁𝖾𝖽𝗎𝗅𝖾"


__help__ = """✧ `/𝗅𝖺𝗍𝖾𝗌𝗍` 𝗈𝗋 `/𝗌𝖼𝗁𝖾𝖽𝗎𝗅𝖾`: 𝗍𝗈 𝗌𝖾𝖾 𝗅𝖺𝗍𝖾𝗌𝗍 𝖺𝗇𝗂𝗆𝖾 𝖾𝗉𝗂𝗌𝗈𝖽𝖾𝗌 𝗌𝖼𝗁𝖾𝖽𝗎𝗅𝖾 𝗍𝗂𝗆𝖾 𝗂𝗇 𝖨𝖲𝖳 (𝖨𝗇𝖽𝗂𝖺𝗇 𝖲𝗍𝖺𝗇𝖽𝖺𝗋𝖽 𝖳𝗂𝗆𝖾) 𝖹𝗈𝗇𝖾.
 𝖭𝗈𝗍𝖾: 𝖸𝗈𝗎 𝖼𝖺𝗇 𝗎𝗌𝖾 𝗍𝗁𝗂𝗌 𝖼𝗈𝗆𝗆𝖺𝗇𝖽 𝗈𝗇𝗅𝗒 𝗂𝗇 𝗀𝗋𝗈𝗎𝗉𝗌.
 """