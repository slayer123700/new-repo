from html import escape
from secrets import choice
from typing import List
from shigaraki.helper.welcome_helper import *
from pyrogram import emoji, enums, filters , Client
from pyrogram.errors import ChannelPrivate, ChatAdminRequired, RPCError
from pyrogram.types import Message, User
from shigaraki import app
from shigaraki.database.welcome_db import Greetings
from shigaraki.decorator.chatadmin import can_change_info , chatadmin
from config import config 

ChatType = enums.ChatType

async def escape_mentions_using_curly_brackets_wl(
        user: User,
        m: Message,
        text: str,
        parse_words: list,
) -> str:
    teks = await escape_invalid_curly_brackets(text, parse_words)
    if teks:
        teks = teks.format(
            first=escape(user.first_name),
            last=escape(user.last_name or user.first_name),
            fullname=" ".join(
                [
                    escape(user.first_name),
                    escape(user.last_name),
                ]
                if user.last_name
                else [escape(user.first_name)],
            ),
            username=(
                "@" + (await escape_markdown(escape(user.username)))
                if user.username
                else (await (mention_html(escape(user.first_name), user.id)))
            ),
            mention=await (mention_html(escape(user.first_name), user.id)),
            chatname=escape(m.chat.title)
            if m.chat.type != ChatType.PRIVATE
            else escape(user.first_name),
            id=user.id,
        )
    else:
        teks = ""

    return teks


@app.on_message(filters.command("cleanwelcome" , config.COMMAND_PREFIXES))
@can_change_info
async def cleanwlcm(_, m: Message):
    db = Greetings(m.chat.id)
    status = db.get_current_cleanwelcome_settings()
    args = m.text.split(" ", 1)

    if len(args) >= 2:
        if args[1].lower() == "on":
            db.set_current_cleanwelcome_settings(True)
            await m.reply_text("Turned on!")
            return
        if args[1].lower() == "off":
            db.set_current_cleanwelcome_settings(False)
            await m.reply_text("Turned off!")
            return
        await m.reply_text("what are you trying to do ??")
        return
    await m.reply_text(f"Current settings:- {status}")
    return


@app.on_message(filters.command("cleangoodbye" , config.COMMAND_PREFIXES))
@can_change_info
async def cleangdbye(_, m: Message):
    db = Greetings(m.chat.id)
    status = db.get_current_cleangoodbye_settings()
    args = m.text.split(" ", 1)

    if len(args) >= 2:
        if args[1].lower() == "on":
            db.set_current_cleangoodbye_settings(True)
            await m.reply_text("Turned on!")
            return
        if args[1].lower() == "off":
            db.set_current_cleangoodbye_settings(False)
            await m.reply_text("Turned off!")
            return
        await m.reply_text("what are you trying to do ??")
        return
    await m.reply_text(f"Current settings:- {status}")
    return


@app.on_message(filters.command("setwelcome" , config.COMMAND_PREFIXES))
@can_change_info
async def save_wlcm(_, m: Message):
    db = Greetings(m.chat.id)
    if m and not m.from_user:
        return
    args = m.text.split(None, 1)

    if len(args) >= 4096:
        await m.reply_text(
            "Word limit exceed !!",
        )
        return
    if not (m.reply_to_message and m.reply_to_message.text) and len(m.command) == 0:
        await m.reply_text(
            "Error: There is no text in here! and only text with buttons are supported currently !",
        )
        return
    text, msgtype, file = await get_wlcm_type(m)
    if not m.reply_to_message and msgtype == Types.TEXT and len(m.command) <= 2:
        await m.reply_text(f"<code>{m.text}</code>\n\nError: There is no data in here!")
        return

    if not text and not file:
        await m.reply_text(
            "Please provide some data!",
        )
        return

    if not msgtype:
        await m.reply_text("Please provide some data for this to reply with!")
        return

    db.set_welcome_text(text, msgtype, file)
    await m.reply_text("Saved welcome!")
    return


@app.on_message(filters.command("setgoodbye" , config.COMMAND_PREFIXES))
@can_change_info
async def save_gdbye(_, m: Message):
    db = Greetings(m.chat.id)
    if m and not m.from_user:
        return
    args = m.text.split(None, 1)

    if len(args) >= 4096:
        await m.reply_text(
            "Word limit exceeds !!",
        )
        return
    if not (m.reply_to_message and m.reply_to_message.text) and len(m.command) == 0:
        await m.reply_text(
            "Error: There is no text in here! and only text with buttons are supported currently !",
        )
        return
    text, msgtype, file = await get_wlcm_type(m)

    if not m.reply_to_message and msgtype == Types.TEXT and len(m.command) <= 2:
        await m.reply_text(f"<code>{m.text}</code>\n\nError: There is no data in here!")
        return

    if not text and not file:
        await m.reply_text(
            "Please provide some data!",
        )
        return

    if not msgtype:
        await m.reply_text("Please provide some data for this to reply with!")
        return

    db.set_goodbye_text(text, msgtype, file)
    await m.reply_text("Saved goodbye!")
    return


@app.on_message(filters.command("resetgoodbye" , config.COMMAND_PREFIXES))
@can_change_info
async def resetgb(_, m: Message):
    db = Greetings(m.chat.id)
    if m and not m.from_user:
        return
    text = "Sad to see you leaving {first}.\nTake Care!"
    db.set_goodbye_text(text, None)
    await m.reply_text("Ok Done!")
    return


@app.on_message(filters.command("resetwelcome"))
@can_change_info
async def resetwlcm(_, m: Message):
    db = Greetings(m.chat.id)
    if m and not m.from_user:
        return
    text = "Hey {first}, welcome to {chatname}!"
    db.set_welcome_text(text, None)
    await m.reply_text("Done!")
    return


@app.on_message(filters.group & filters.new_chat_members, group=69)
async def member_has_joined(c: Client, m: Message):
    users: List[User] = m.new_chat_members
    db = Greetings(m.chat.id)
    for user in users:
        try:
            if user.id == c.me.id:
                continue
            if user.is_bot:
                continue  # ignore bots
        except ChatAdminRequired:
            continue
        status = db.get_welcome_status()
        oo = db.get_welcome_text()
        UwU = db.get_welcome_media()
        mtype = db.get_welcome_msgtype()
        parse_words = [
            "first",
            "last",
            "fullname",
            "username",
            "mention",
            "id",
            "chatname",
        ]
        hmm = await escape_mentions_using_curly_brackets_wl(user, m, oo, parse_words)
        if not status:
            continue
        tek, button = await parse_button(hmm)
        button = await build_keyboard(button)
        button = ikb(button) if button else None

        if "%%%" in tek:
            filter_reply = tek.split("%%%")
            teks = choice(filter_reply)
        else:
            teks = tek

        if not teks:
            teks = f"A wild {user.mention} appeared in {m.chat.title}! Everyone be aware."

        ifff = db.get_current_cleanwelcome_id()
        gg = db.get_current_cleanwelcome_settings()
        if ifff and gg:
            try:
                await c.delete_messages(m.chat.id, int(ifff))
            except RPCError:
                pass
        if not teks:
            teks = "Hey {first}, welcome to {chatname}"
        try:
            if not UwU:
                jj = await c.send_message(
                    m.chat.id,
                    text=teks,
                    reply_markup=button,
                    disable_web_page_preview=True,
                )
            else:
                jj = await (await send_cmd(c, mtype))(
                    m.chat.id,
                    UwU,
                    caption=teks,
                    reply_markup=button,
                )

            if jj:
                db.set_cleanwlcm_id(int(jj.id))
        except ChannelPrivate:
            continue
        except RPCError as e:
            return


@app.on_message(filters.group & filters.left_chat_member, group=99)
async def member_has_left(c: Client, m: Message):
    db = Greetings(m.chat.id)
    status = db.get_goodbye_status()
    oo = db.get_goodbye_text()
    UwU = db.get_goodbye_media()
    mtype = db.get_goodbye_msgtype()
    parse_words = [
        "first",
        "last",
        "fullname",
        "id",
        "username",
        "mention",
        "chatname",
    ]

    user = m.left_chat_member or m.from_user

    hmm = await escape_mentions_using_curly_brackets_wl(user, m, oo, parse_words)
    if not status:
        return
    tek, button = await parse_button(hmm)
    button = await build_keyboard(button)
    button = ikb(button) if button else None

    if "%%%" in tek:
        filter_reply = tek.split("%%%")
        teks = choice(filter_reply)
    else:
        teks = tek

    if not teks:  # Just in case
        teks = f"Thanks for being part of this group {user.mention}. But I don't like your arrogance and leaving the group {emoji.EYES}"

    ifff = db.get_current_cleangoodbye_id()
    iii = db.get_current_cleangoodbye_settings()
    if ifff and iii:
        try:
            await c.delete_messages(m.chat.id, int(ifff))
        except RPCError:
            pass
    if not teks:
        teks = "Sad to see you leaving {first}\nTake Care!"
    try:
        ooo = (
            await (await send_cmd(c, mtype))(
                m.chat.id,
                UwU,
                caption=teks,
                reply_markup=button,
            ) if UwU else await c.send_message(
                m.chat.id,
                text=teks,
                reply_markup=button,
                disable_web_page_preview=True,
            )
        )
        if ooo:
            db.set_cleangoodbye_id(int(ooo.id))
        return
    except ChannelPrivate:
        pass
    except RPCError as e:
        return


@app.on_message(filters.command("welcome" , config.COMMAND_PREFIXES))
@chatadmin
async def welcome(c: Client, m: Message):
    db = Greetings(m.chat.id)
    status = db.get_welcome_status()
    oo = db.get_welcome_text()
    args = m.text.split(" ", 1)

    if m and not m.from_user:
        return

    if len(args) >= 2:
        if args[1].lower() == "noformat":
            await m.reply_text(
                f"""Current welcome settings:-
            Welcome : {status}
            Clean Welcome: {db.get_current_cleanwelcome_settings()}
            Cleaning service: {db.get_current_cleanservice_settings()}
            Welcome text in no formating:
            """,
            )
            await c.send_message(
                m.chat.id, text=oo, parse_mode=enums.ParseMode.DISABLED
            )
            return
        if args[1].lower() == "on":
            db.set_current_welcome_settings(True)
            await m.reply_text("I will greet newly joined member from now on.")
            return
        if args[1].lower() == "off":
            db.set_current_welcome_settings(False)
            await m.reply_text("I will stay quiet when someone joins.")
            return
        await m.reply_text("what are you trying to do ??")
        return
    await m.reply_text(
        f"""Current welcome settings:-
    Welcome : {status}
    Clean Welcome: {db.get_current_cleanwelcome_settings()}
    Cleaning service: {db.get_current_cleanservice_settings()}
    Welcome text:
    """,
    )
    UwU = db.get_welcome_media()
    mtype = db.get_welcome_msgtype()
    tek, button = await parse_button(oo)
    button = await build_keyboard(button)
    button = ikb(button) if button else None
    if not UwU:
        await c.send_message(
            m.chat.id,
            text=tek,
            reply_markup=button,
            disable_web_page_preview=True,
        )
    else:
        await (await send_cmd(c, mtype))(
            m.chat.id,
            UwU,
            caption=tek,
            reply_markup=button,
        )
    return


@app.on_message(filters.command("goodbye" , config.COMMAND_PREFIXES))
@chatadmin
async def goodbye(c: Client, m: Message):
    db = Greetings(m.chat.id)
    status = db.get_goodbye_status()
    oo = db.get_goodbye_text()
    args = m.text.split(" ", 1)
    if m and not m.from_user:
        return
    if len(args) >= 2:
        if args[1].lower() == "noformat":
            await m.reply_text(
                f"""Current goodbye settings:-
            Goodbye : {status}
            Clean Goodbye: {db.get_current_cleangoodbye_settings()}
            Cleaning service: {db.get_current_cleanservice_settings()}
            Goodbye text in no formating:
            """,
            )
            await c.send_message(
                m.chat.id, text=oo, parse_mode=enums.ParseMode.DISABLED
            )
            return
        if args[1].lower() == "on":
            db.set_current_goodbye_settings(True)
            await m.reply_text("I don't want but I will say goodbye to the fugitives")
            return
        if args[1].lower() == "off":
            db.set_current_goodbye_settings(False)
            await m.reply_text("I will stay quiet for fugitives")
            return
        await m.reply_text("what are you trying to do ??")
        return
    await m.reply_text(
        f"""Current Goodbye settings:-
    Goodbye : {status}
    Clean Goodbye: {db.get_current_cleangoodbye_settings()}
    Cleaning service: {db.get_current_cleanservice_settings()}
    Goodbye text:
    """,
    )
    UwU = db.get_goodbye_media()
    mtype = db.get_goodbye_msgtype()
    tek, button = await parse_button(oo)
    button = await build_keyboard(button)
    button = ikb(button) if button else None
    if not UwU:
        await c.send_message(
            m.chat.id,
            text=tek,
            reply_markup=button,
            disable_web_page_preview=True,
        )
    else:
        await (await send_cmd(c, mtype))(
            m.chat.id,
            UwU,
            caption=tek,
            reply_markup=button,
        )
    return


__module__ = "𝖦𝗋𝖾𝖾𝗍𝗂𝗇𝗀𝗌"


__help__ = """**𝖢𝗎𝗌𝗍𝗈𝗆𝗂𝗓𝖾 𝖶𝖾𝗅𝖼𝗈𝗆𝖾/𝖦𝗈𝗈𝖽𝖻𝗒𝖾 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌:**

  ✧ `/𝗌𝖾𝗍𝗐𝖾𝗅𝖼𝗈𝗆𝖾 <𝗋𝖾𝗉𝗅𝗒>` **:** 𝖲𝖾𝗍𝗌 𝖺 𝖼𝗎𝗌𝗍𝗈𝗆 𝗐𝖾𝗅𝖼𝗈𝗆𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾.
   ✧ `/𝗌𝖾𝗍𝗀𝗈𝗈𝖽𝖻𝗒𝖾 <𝗋𝖾𝗉𝗅𝗒>` **:** 𝖲𝖾𝗍𝗌 𝖺 𝖼𝗎𝗌𝗍𝗈𝗆 𝗀𝗈𝗈𝖽𝖻𝗒𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾.
   ✧ `/𝗋𝖾𝗌𝖾𝗍𝗐𝖾𝗅𝖼𝗈𝗆𝖾` **:** 𝖱𝖾𝗌𝖾𝗍𝗌 𝗍𝗈 𝖽𝖾𝖿𝖺𝗎𝗅𝗍 𝗐𝖾𝗅𝖼𝗈𝗆𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾.
   ✧ `/𝗋𝖾𝗌𝖾𝗍𝗀𝗈𝗈𝖽𝖻𝗒𝖾` **:** 𝖱𝖾𝗌𝖾𝗍𝗌 𝗍𝗈 𝖽𝖾𝖿𝖺𝗎𝗅𝗍 𝗀𝗈𝗈𝖽𝖻𝗒𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾.

**𝖤𝗇𝖺𝖻𝗅𝖾/𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌:**
   ✧ `/𝗐𝖾𝗅𝖼𝗈𝗆𝖾 <𝗈𝗇/𝗈𝖿𝖿>` **:** 𝖤𝗇𝖺𝖻𝗅𝖾𝗌/𝖣𝗂𝗌𝖺𝖻𝗅𝖾𝗌 𝗐𝖾𝗅𝖼𝗈𝗆𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌.
   ✧ `/𝗀𝗈𝗈𝖽𝖻𝗒𝖾 <𝗈𝗇/𝗈𝖿𝖿>` **:** 𝖤𝗇𝖺𝖻𝗅𝖾𝗌/𝖣𝗂𝗌𝖺𝖻𝗅𝖾𝗌 𝗀𝗈𝗈𝖽𝖻𝗒𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌.

**𝖢𝗅𝖾𝖺𝗇 𝖬𝖾𝗌𝗌𝖺𝗀𝖾𝗌:**
   ✧ `/𝖼𝗅𝖾𝖺𝗇𝗐𝖾𝗅𝖼𝗈𝗆𝖾 <𝗈𝗇/𝗈𝖿𝖿>` **:** 𝖤𝗇𝖺𝖻𝗅𝖾𝗌/𝖽𝗂𝗌𝖺𝖻𝗅𝖾𝗌 𝖼𝗅𝖾𝖺𝗇𝗂𝗇𝗀 𝗈𝖿 𝗐𝖾𝗅𝖼𝗈𝗆𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌.
   ✧ `/𝖼𝗅𝖾𝖺𝗇𝗀𝗈𝗈𝖽𝖻𝗒𝖾 <𝗈𝗇/𝗈𝖿𝖿>` **:** 𝖤𝗇𝖺𝖻𝗅𝖾𝗌/𝖽𝗂𝗌𝖺𝖻𝗅𝖾𝗌 𝖼𝗅𝖾𝖺𝗇𝗂𝗇𝗀 𝗈𝖿 𝗀𝗈𝗈𝖽𝖻𝗒𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌.

**𝖭𝗈𝗍𝖾𝗌:**
  ✧ 𝖢𝗎𝗋𝗋𝖾𝗇𝗍𝗅𝗒 𝗌𝗎𝗉𝗉𝗈𝗋𝗍𝗌 𝗈𝗇𝗅𝗒 𝗍𝖾𝗑𝗍 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌.
   ✧ 𝖸𝗎𝗆𝖾𝗄𝗈 𝗆𝗎𝗌𝗍 𝖻𝖾 𝖺𝗇 𝖺𝖽𝗆𝗂𝗇 𝗍𝗈 𝗀𝗋𝖾𝖾𝗍 𝖺𝗇𝖽 𝗀𝗈𝗈𝖽𝖻𝗒𝖾 𝗎𝗌𝖾𝗋𝗌.
 """
