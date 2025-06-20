from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from html import escape
from re import compile as compilere
from re import sub
import base64
from datetime import datetime, timedelta
from html import escape
from re import compile as compile_re
from typing import List
from pyrogram.enums import ChatType
from pyrogram.types import Message
from shigaraki import ist
from pyrogram import Client

def ikb(rows=None, back=False, todo="start_back"):
    """
    rows = pass the rows
    back - if want to make back button
    todo - callback data of back button
    """
    if rows is None:
        rows = []
    lines = []
    try:
        for row in rows:
            line = []
            for button in row:
                btn_text = button.split(".")[1].capitalize()
                button = btn(btn_text, button)  # InlineKeyboardButton
                line.append(button)
            lines.append(line)
    except AttributeError:
        for row in rows:
            line = []
            for button in row:
                # Will make the kb which don't have "." in them
                button = btn(*button)
                line.append(button)
            lines.append(line)
    except TypeError:
        # make a code to handel that error
        line = []
        for button in rows:
            button = btn(*button)  # InlineKeyboardButton
            line.append(button)
        lines.append(line)
    if back:
        back_btn = [(btn("« Back", todo))]
        lines.append(back_btn)
    return InlineKeyboardMarkup(inline_keyboard=lines)


def btn(text, value, type="callback_data"):
    return InlineKeyboardButton(text, **{type: value})

async def cleanhtml(raw_html: str) -> str:
    """Clean html data."""
    cleanr = compilere("<.*?>")
    return sub(cleanr, "", raw_html)


async def escape_markdown(text: str) -> str:
    """Escape markdown data."""
    escape_chars = r"\*_`\["
    return sub(f"([{escape_chars}])", r"\\\1", text)


async def mention_html(name: str, user_id: int) -> str:
    """Mention user in html format."""
    name = escape(name)
    return f'<a href="tg://user?id={user_id}">{name}</a>'


async def mention_markdown(name: str, user_id: int) -> str:
    """Mention user in markdown format."""
    return f"[{(await escape_markdown(name))}](tg://user?id={user_id})"


BTN_URL_REGEX = compile_re(
    r"(\[([^\[]+?)\]\(buttonurl:(?:/{0,2})(.+?)(:same)?\))")


async def extract_time(m: Message, time_val: str):
    """Extract time from message."""
    if any(time_val.endswith(unit) for unit in ("m", "h", "d")):
        unit = time_val[-1]
        time_num = time_val[:-1]  # type: str
        if not time_num.isdigit():
            await m.reply("Unspecified amount of time.")
            return ""
        initial_time = datetime.now(ist)
        if unit == "m":
            bantime = initial_time + timedelta(minutes=int(time_num))
        elif unit == "h":
            bantime = initial_time + timedelta(hours=int(time_num))
        elif unit == "d":
            bantime = initial_time + timedelta(days=int(time_num))
        else:
            # how even...?
            return ""
        return bantime
    await m.reply(
        f"Invalid time type specified. Needed m, h, or s. got: {time_val[-1]}",
    )
    return ""


async def parse_button(text: str):
    """Parse button from text."""
    markdown_note = text
    prev = 0
    note_data = ""
    buttons = []
    for match in BTN_URL_REGEX.finditer(markdown_note):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and markdown_note[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        # if even, not escaped -> create button
        if n_escapes % 2 == 0:
            # create a thruple with button label, url, and newline status
            buttons.append(
                (match.group(2), match.group(3), bool(match.group(4))))
            note_data += markdown_note[prev: match.start(1)]
            prev = match.end(1)
        # if odd, escaped -> move along
        else:
            note_data += markdown_note[prev:to_check]
            prev = match.start(1) - 1
    note_data += markdown_note[prev:]
    return note_data, buttons


async def build_keyboard(buttons):
    """Build keyboards from provided buttons."""
    keyb = []
    for btn in buttons:
        if btn[-1] and keyb:
            keyb[-1].append((btn[0], btn[1], "url"))
        else:
            keyb.append([(btn[0], btn[1], "url")])

    return keyb


SMART_OPEN = "“"
SMART_CLOSE = "”"
START_CHAR = ("'", '"', SMART_OPEN)


async def escape_invalid_curly_brackets(text: str, valids: List[str]) -> str:
    new_text = ""
    idx = 0
    while idx < len(text):
        if text[idx] == "{":
            if idx + 1 < len(text) and text[idx + 1] == "{":
                idx += 2
                new_text += "{{{{"
                continue
            success = False
            for v in valids:
                if text[idx:].startswith("{" + v + "}"):
                    success = True
                    break
            if success:
                new_text += text[idx: idx + len(v) + 2]
                idx += len(v) + 2
                continue
            new_text += "{{"

        elif text[idx] == "}":
            if idx + 1 < len(text) and text[idx + 1] == "}":
                idx += 2
                new_text += "}}}}"
                continue
            new_text += "}}"

        else:
            new_text += text[idx]
        idx += 1

    return new_text


async def escape_mentions_using_curly_brackets(
        m: Message,
        text: str,
        parse_words: list,
) -> str:
    if m.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP, ChatType.CHANNEL]:
        chat_name = escape(m.chat.title)
    else:
        chat_name = escape(m.from_user.first_name)
    teks = await escape_invalid_curly_brackets(text, parse_words)
    if teks:
        teks = teks.format(
            first=escape(m.from_user.first_name),
            last=escape(m.from_user.last_name or m.from_user.first_name),
            mention=m.from_user.mention,
            username=(
                "@" + (await escape_markdown(escape(m.from_user.username)))
                if m.from_user.username
                else m.from_user.mention
            ),
            fullname=" ".join(
                [
                    escape(m.from_user.first_name),
                    escape(m.from_user.last_name),
                ]
                if m.from_user.last_name
                else [escape(m.from_user.first_name)],
            ),
            chatname=chat_name,
            id=m.from_user.id,
        )
    else:
        teks = ""

    return teks


async def split_quotes(text: str):
    """Split quotes in text."""
    if not any(text.startswith(char) for char in START_CHAR):
        return text.split(None, 1)
    counter = 1  # ignore first char -> is some kind of quote
    while counter < len(text):
        if text[counter] == "\\":
            counter += 1
        elif text[counter] == text[0] or (
                text[0] == SMART_OPEN and text[counter] == SMART_CLOSE
        ):
            break
        counter += 1
    else:
        return text.split(None, 1)

    # 1 to avoid starting quote, and counter is exclusive so avoids ending
    key = await remove_escapes(text[1:counter].strip())
    # index will be in range, or `else` would have been executed and returned
    rest = text[counter + 1:].strip()
    if not key:
        key = text[0] + text[0]
    return list(filter(None, [key, rest]))


async def remove_escapes(text: str) -> str:
    """Remove the escaped from message."""
    res = ""
    is_escaped = False
    for counter in range(len(text)):
        if is_escaped:
            res += text[counter]
            is_escaped = False
        elif text[counter] == "\\":
            is_escaped = True
        else:
            res += text[counter]
    return res


async def encode_decode(string: str, to_do="encode"):
    """
    Function to encode or decode strings
    string: string to be decoded or encoded
    to_do: encode to encode the string or decode to decode the string
    """
    if to_do.lower() == "encode":
        encodee = string.encode("ascii")
        base64_ = base64.b64encode(encodee)
        return base64_.decode("ascii")

    elif to_do.lower() == "decode":
        decodee = string.encode("ascii")
        base64_ = base64.b64decode(decodee)
        return base64_.decode("ascii")

    else:
        return None
    
from enum import IntEnum, unique

from pyrogram.types import Message


@unique
class Types(IntEnum):
    TEXT = 1
    DOCUMENT = 2
    PHOTO = 3
    VIDEO = 4
    STICKER = 5
    AUDIO = 6
    VOICE = 7
    VIDEO_NOTE = 8
    ANIMATION = 9
    ANIMATED_STICKER = 10
    CONTACT = 11


async def get_note_type(m: Message):
    """Get type of note."""
    if len(m.text.split()) <= 1:
        return None, None, None, None

    data_type = None
    content = None
    raw_text = m.text.markdown if m.text else m.caption.markdown
    args = raw_text.split(None, 2)
    note_name = args[1]

    if len(args) >= 3:
        text = args[2]
        data_type = Types.TEXT

    elif m.reply_to_message:

        if m.reply_to_message.text:
            text = m.reply_to_message.text.markdown
        elif m.reply_to_message.caption:
            text = m.reply_to_message.caption.markdown
        else:
            text = ""

        if len(args) >= 2 and m.reply_to_message.text:  # not caption, text
            data_type = Types.TEXT

        elif m.reply_to_message.sticker:
            content = m.reply_to_message.sticker.file_id
            data_type = Types.STICKER

        elif m.reply_to_message.document:
            if m.reply_to_message.document.mime_type in ["application/x-bad-tgsticker", "application/x-tgsticker"]:
                data_type = Types.ANIMATED_STICKER
            else:
                data_type = Types.DOCUMENT
            content = m.reply_to_message.document.file_id

        elif m.reply_to_message.photo:
            content = m.reply_to_message.photo.file_id  # last elem = best quality
            data_type = Types.PHOTO

        elif m.reply_to_message.audio:
            content = m.reply_to_message.audio.file_id
            data_type = Types.AUDIO

        elif m.reply_to_message.voice:
            content = m.reply_to_message.voice.file_id
            data_type = Types.VOICE

        elif m.reply_to_message.video:
            content = m.reply_to_message.video.file_id
            data_type = Types.VIDEO

        elif m.reply_to_message.video_note:
            content = m.reply_to_message.video_note.file_id
            data_type = Types.VIDEO_NOTE

        elif m.reply_to_message.animation:
            content = m.reply_to_message.animation.file_id
            data_type = Types.ANIMATION

    else:
        return None, None, None, None

    return note_name, text, data_type, content


async def get_filter_type(m: Message):
    """Get filter type."""
    if len(m.text.split()) <= 1:
        return None, None, None

    data_type = None
    content = None
    raw_text = m.text.markdown if m.text else m.caption.markdown
    args = raw_text.split(None, 2)

    if not m.reply_to_message and m.text and len(m.text.split()) >= 3:
        content = None
        text = m.text.markdown.split(None, 2)[2]
        data_type = Types.TEXT

    elif m.reply_to_message:

        if m.reply_to_message.text:
            text = m.reply_to_message.text.markdown
        elif m.reply_to_message.caption:
            text = m.reply_to_message.caption.markdown
        else:
            text = ""

        if len(args) >= 2 and m.reply_to_message.text:  # not caption, text
            data_type = Types.TEXT

        elif m.reply_to_message.sticker:
            content = m.reply_to_message.sticker.file_id
            data_type = Types.STICKER

        elif m.reply_to_message.document:
            if m.reply_to_message.document.mime_type in ["application/x-bad-tgsticker", "application/x-tgsticker"]:
                data_type = Types.ANIMATED_STICKER
            else:
                data_type = Types.DOCUMENT
            content = m.reply_to_message.document.file_id

        elif m.reply_to_message.photo:
            content = m.reply_to_message.photo.file_id  # last elem = best quality
            data_type = Types.PHOTO

        elif m.reply_to_message.audio:
            content = m.reply_to_message.audio.file_id
            data_type = Types.AUDIO

        elif m.reply_to_message.voice:
            content = m.reply_to_message.voice.file_id
            data_type = Types.VOICE

        elif m.reply_to_message.video:
            content = m.reply_to_message.video.file_id
            data_type = Types.VIDEO

        elif m.reply_to_message.video_note:
            content = m.reply_to_message.video_note.file_id
            data_type = Types.VIDEO_NOTE

        elif m.reply_to_message.animation:
            content = m.reply_to_message.animation.file_id
            data_type = Types.ANIMATION

    else:
        text = None
        data_type = None
        content = None

    return text, data_type, content


async def get_wlcm_type(m: Message):
    """Get wlcm type."""
    data_type = None
    content = None
    raw_text = m.text.markdown if m.text else m.caption.markdown
    args = raw_text.split(None, 1)

    if not m.reply_to_message and m.text and len(m.text.strip().split()) >= 2:
        content = None
        text = m.text.markdown.split(None, 1)[1]
        data_type = Types.TEXT

    elif m.reply_to_message:

        if m.reply_to_message.text:
            text = m.reply_to_message.text.markdown
        elif m.reply_to_message.caption:
            text = m.reply_to_message.caption.markdown
        else:
            text = ""

        if len(args) >= 1 and m.reply_to_message.text:  # not caption, text
            data_type = Types.TEXT

        elif m.reply_to_message.document:
            data_type = Types.DOCUMENT
            content = m.reply_to_message.document.file_id

        elif m.reply_to_message.photo:
            content = m.reply_to_message.photo.file_id  # last elem = best quality
            data_type = Types.PHOTO

        elif m.reply_to_message.audio:
            content = m.reply_to_message.audio.file_id
            data_type = Types.AUDIO

        elif m.reply_to_message.voice:
            content = m.reply_to_message.voice.file_id
            data_type = Types.VOICE

        elif m.reply_to_message.video:
            content = m.reply_to_message.video.file_id
            data_type = Types.VIDEO

        elif m.reply_to_message.video_note:
            content = m.reply_to_message.video_note.file_id
            data_type = Types.VIDEO_NOTE

        elif m.reply_to_message.animation:
            content = m.reply_to_message.animation.file_id
            data_type = Types.ANIMATION

    else:
        text = None
        data_type = None
        content = None

    return text, data_type, content


async def get_afk_type(m: Message):
    data_type = None
    content = None
    raw_text = m.text.markdown if m.text else m.caption.markdown
    args = raw_text.split(None, 1)

    if not m.reply_to_message and m.text and len(m.text.strip().split()) >= 2:
        content = None
        text = m.text.markdown.split(None, 1)[1]
        data_type = Types.TEXT

    elif m.reply_to_message:

        if m.reply_to_message.text:
            text = m.reply_to_message.text.markdown
        elif m.reply_to_message.caption:
            text = m.reply_to_message.caption.markdown
        else:
            text = ""

        if len(args) >= 1 and m.reply_to_message.text:  # not caption, text
            data_type = Types.TEXT

        elif m.reply_to_message.document:
            data_type = Types.DOCUMENT
            content = m.reply_to_message.document.file_id

        elif m.reply_to_message.photo:
            content = m.reply_to_message.photo.file_id  # last elem = best quality
            data_type = Types.PHOTO

        elif m.reply_to_message.audio:
            content = m.reply_to_message.audio.file_id
            data_type = Types.AUDIO

        elif m.reply_to_message.voice:
            content = m.reply_to_message.voice.file_id
            data_type = Types.VOICE

        elif m.reply_to_message.video:
            content = m.reply_to_message.video.file_id
            data_type = Types.VIDEO

        elif m.reply_to_message.video_note:
            content = m.reply_to_message.video_note.file_id
            data_type = Types.VIDEO_NOTE

        elif m.reply_to_message.animation:
            content = m.reply_to_message.animation.file_id
            data_type = Types.ANIMATION

    else:
        text = None
        data_type = None
        content = None

    return text, data_type, content


async def send_cmd(client: Client, msgtype: int):
    GET_FORMAT = {
        Types.TEXT.value: client.send_message,
        Types.DOCUMENT.value: client.send_document,
        Types.PHOTO.value: client.send_photo,
        Types.VIDEO.value: client.send_video,
        Types.STICKER.value: client.send_sticker,
        Types.AUDIO.value: client.send_audio,
        Types.VOICE.value: client.send_voice,
        Types.VIDEO_NOTE.value: client.send_video_note,
        Types.ANIMATION.value: client.send_animation,
        Types.ANIMATED_STICKER.value: client.send_sticker,
        Types.CONTACT: client.send_contact,
    }
    return GET_FORMAT[msgtype]