import io
import sys
import traceback
from shigaraki import app
from datetime import datetime
from pyrogram import filters
from config import config 
from shigaraki.decorator.errors import error
from shigaraki.decorator.save import save

async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)

@app.on_message(filters.command("eval", prefixes=config.COMMAND_PREFIXES) , config.OWNER_ID)
@error
@save
async def eval(client, message):
    if len(message.text.split()) <2:
          return await message.reply_text("`𝖨𝗇𝗉𝗎𝗍 𝖭𝗈𝗍 𝖥𝗈𝗎𝗇𝖽!`")
    status_message = await message.reply_text("𝖯𝗋𝗈𝖼𝖾𝗌𝗌𝗂𝗇𝗀...")
    cmd = message.text.split(None, 1)[1]
    start = datetime.now()
    reply_to_ = message
    if message.reply_to_message:
        reply_to_ = message.reply_to_message
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    end = datetime.now()
    ping = (end-start).microseconds / 1000
    final_output = "<b>📎 Input</b>: "
    final_output += f"<code>{cmd}</code>\n\n"
    final_output += "<b>📒 Output</b>:\n"
    final_output += f"<code>{evaluation.strip()}</code> \n\n"
    final_output += f"<b>✨ Taken Time</b>: {ping}<b>ms</b>"
    if len(final_output) > 4096:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.text"
            await reply_to_.reply_document(
                document=out_file, caption=cmd, disable_notification=True
            )
    else:
        await status_message.edit_text(final_output)