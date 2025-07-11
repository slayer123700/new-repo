import json
import requests
import asyncio
import os
import shlex
from traceback import format_exc as err
from time import time
from datetime import datetime
from os.path import basename
from typing import Tuple, Optional
from uuid import uuid4
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import (
    InlineKeyboardButton,
    CallbackQuery,
    Message,
    InlineKeyboardMarkup
)

from shigaraki import app
from .db import get_collection
from config import config

OWNER = config.OWNER_ID
LOG_CHANNEL_ID = config.LOG_CHANNEL

DOWN_PATH = "shigaraki/downloads/"

AUTH_USERS = get_collection("AUTH_USERS")
IGNORE = get_collection("IGNORED_USERS")
PIC_DB = get_collection("PIC_DB")
GROUPS = get_collection("GROUPS")
CC = get_collection('CONNECTED_CHANNELS')
USER_JSON = {}
USER_WC = {}


def rand_key():
    return str(uuid4())[:8]


def control_user(func):
    async def wrapper(_, message: Message):
        msg = json.loads(str(message))
        gid = msg['chat']['id']
        gidtype = msg['chat']['type']
        if gidtype in [ChatType.SUPERGROUP, ChatType.GROUP] and not (
            await GROUPS.find_one({"_id": gid})
        ):
            try:
                gidtitle = msg['chat']['username']
            except KeyError:
                gidtitle = msg['chat']['title']
            await GROUPS.insert_one({"_id": gid, "grp": gidtitle})
            await clog(
                "#shigaraki",
                f"Bot added to a new group\n\n{gidtitle}\nID: `{gid}`",
                "NEW_GROUP"
            )
        try:
            user = msg['from_user']['id']
        except KeyError:
            user = msg['chat']['id']
        if await IGNORE.find_one({'_id': user}):
            return
        nut = time()
        if user != OWNER:
            try:
                out = USER_JSON[user]
                if nut-out<1.2:
                    USER_WC[user] += 1
                    if USER_WC[user] == 3:
                        await message.reply_text(
                            (
                                "Stop spamming bot!!!"
                                +"\nElse you will be blacklisted"
                            ),
                        )
                        await clog('shigaraki', f'UserID: {user}', 'SPAM')
                    if USER_WC[user] == 5:
                        await IGNORE.insert_one({'_id': user})
                        await message.reply_text(
                            (
                                "You have been exempted from using this bot "
                                +"now due to spamming 5 times consecutively!!!"
                                +"\nTo remove restriction plead to "
                                +"@shigarakiXSupportGc"
                            )
                        )
                        await clog('shigaraki', f'UserID: {user}', 'BAN')
                        return
                    await asyncio.sleep(USER_WC[user])
                else:
                    USER_WC[user] = 0
            except KeyError:
                pass
            USER_JSON[user] = nut
        try:
            await func(_, message, msg)
        except FloodWait as e:
            await asyncio.sleep(e.x + 5)
        except MessageNotModified:
            pass
        except Exception:
            e = err()
            reply_msg = None
            if func.__name__ == "trace_bek":
                reply_msg = message.reply_to_message
            try:
                await clog(
                    'shigaraki',
                    'Message:\n'+msg['text']+'\n\n'+"```"+e+"```", 'COMMAND',
                    msg=message,
                    replied=reply_msg
                )
            except Exception:
                await clog('shigaraki', e, 'FAILURE', msg=message)
    return wrapper


def check_user(func):
    async def wrapper(_, c_q: CallbackQuery):
        cq = json.loads(str(c_q))
        user = cq['from_user']['id']
        if await IGNORE.find_one({'_id': user}):
            return
        cqowner_is_ch = False
        cqowner = cq['data'].split("_").pop()
        if "-100" in cqowner:
            cqowner_is_ch = True
            ccdata = await CC.find_one({"_id": cqowner})
            if ccdata and ccdata['usr'] == user:
                user_valid = True
            else:
                user_valid = False
        if user == OWNER or user==int(cqowner):
            if user != OWNER:
                nt = time()
                try:
                    ot = USER_JSON[user]
                    if nt-ot<1.4:
                        await c_q.answer(
                            (
                                "Stop spamming bot!!!\n"
                                +"Else you will be blacklisted"
                            ),
                            show_alert=True
                        )
                        await clog('shigaraki', f'UserID: {user}', 'SPAM')
                except KeyError:
                    pass
                USER_JSON[user] = nt
            try:
                await func(_, c_q, cq)
            except FloodWait as e:
                await asyncio.sleep(e.x + 5)
            except MessageNotModified:
                pass
            except Exception:
                e = err()
                reply_msg = None
                if func.__name__ == "tracemoe_btn":
                    reply_msg = c_q.message.reply_to_message
                try:
                    await clog(
                        'shigaraki',
                        'Callback:\n'+cq['data']+'\n\n'+"```"+e+"```",
                        'CALLBACK',
                        cq=c_q,
                        replied=reply_msg
                    )
                except Exception:
                    await clog('shigaraki', e, 'FAILURE', cq=c_q)
        else:
            if cqowner_is_ch:
                if user_valid:
                    try:
                        await func(_, c_q, cq)
                    except FloodWait as e:
                        await asyncio.sleep(e.x + 5)
                    except MessageNotModified:
                        pass
                    except Exception:
                        e = err()
                        reply_msg = None
                        if func.__name__ == "tracemoe_btn":
                            reply_msg = c_q.message.reply_to_message
                        try:
                            await clog(
                                'shigaraki',
                                'Callback:\n'+cq['data']+'\n\n'+"```"+e+"```",
                                'CALLBACK_ANON',
                                cq=c_q,
                                replied=reply_msg
                            )
                        except Exception:
                            await clog('shigaraki', e, 'FAILURE', cq=c_q)
                else:
                    await c_q.answer(
                        (
                            "No one can click buttons on queries made by "
                            +"channels unless connected with /aniconnect!!!"
                        ),
                        show_alert=True,
                    )
            else:
                await c_q.answer(
                    "Not your query!!!",
                    show_alert=True,
                )
    return wrapper


async def media_to_image(
    client: app, message: Message, x: Message, replied: Message # type: ignore
):
    if not (
        replied.photo
        or replied.sticker
        or replied.animation
        or replied.video
    ):
        await x.edit_text("Media Type Is Invalid !")
        await asyncio.sleep(5)
        await x.delete()
        return
    media = (
        replied.photo 
        or replied.sticker 
        or replied.animation 
        or replied.video
    )
    if not os.path.isdir(DOWN_PATH):
        os.makedirs(DOWN_PATH)
    dls = await client.download_media(
        media,
        file_name=DOWN_PATH + rand_key(),
    )
    dls_loc = os.path.join(DOWN_PATH, os.path.basename(dls))
    if replied.sticker and replied.sticker.file_name.endswith(".tgs"):
        png_file = os.path.join(DOWN_PATH, f"{rand_key()}.png")
        cmd = (
            f"lottie_convert.py --frame 0 -if lottie "
            +f"-of png {dls_loc} {png_file}"
        )
        stdout, stderr = (await runcmd(cmd))[:2]
        os.remove(dls_loc)
        if not os.path.lexists(png_file):
            await x.edit_text(
                "This sticker is Gey, Task Failed Successfully ≧ω≦"
            )
            await asyncio.sleep(5)
            await x.delete()
            raise Exception(stdout + stderr)
        dls_loc = png_file
    elif replied.sticker and replied.sticker.file_name.endswith(".webp"):
        stkr_file = os.path.join(DOWN_PATH, f"{rand_key()}.png")
        os.rename(dls_loc, stkr_file)
        if not os.path.lexists(stkr_file):
            await x.edit_text("```Sticker not found...```")
            await asyncio.sleep(5)
            await x.delete()
            return
        dls_loc = stkr_file
    elif replied.animation or replied.video:
        await x.edit_text("`Converting Media To Image ...`")
        jpg_file = os.path.join(DOWN_PATH, f"{rand_key()}.jpg")
        await take_screen_shot(dls_loc, 0, jpg_file)
        os.remove(dls_loc)
        if not os.path.lexists(jpg_file):
            await x.edit_text(
                "This Gif is Gey (｡ì _ í｡), Task Failed Successfully !"
            )
            await asyncio.sleep(5)
            await x.delete()
            return
        dls_loc = jpg_file
    return dls_loc


async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    """ run command in terminal """
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )


async def take_screen_shot(
    video_file: str, duration: int, path: str = ""
) -> Optional[str]:
    """ take a screenshot """
    print(
        "[[[Extracting a frame from %s ||| Video duration => %s]]]",
        video_file,
        duration,
    )
    thumb_image_path = path or os.path.join(
        DOWN_PATH, f"{basename(video_file)}.jpg"
    )
    command = (
        f"ffmpeg -ss {duration} "
        +f'-i "{video_file}" -vframes 1 "{thumb_image_path}"'
    )
    err = (await runcmd(command))[1]
    if err:
        print(err)
    return thumb_image_path if os.path.exists(thumb_image_path) else None



async def get_user_from_channel(cid):
    try:
        k = (await CC.find_one({"_id": str(cid)}))['usr']
        return k
    except TypeError:
        return None


async def return_json_senpai(
    query: str,
    vars_: dict,
    auth: bool = False,
    user: int = None
):
    url = "https://graphql.anilist.co"
    headers = None
    if auth:
        headers = {
            'Authorization': (
                'Bearer ' 
                +str((await AUTH_USERS.find_one({"id": int(user)}))['token'])
            ),
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
    return requests.post(
        url,
        json={"query": query, "variables": vars_},
        headers=headers
    ).json()


def cflag(country):
    if country == "JP":
        return "\U0001F1EF\U0001F1F5"
    if country == "CN":
        return "\U0001F1E8\U0001F1F3"
    if country == "KR":
        return "\U0001F1F0\U0001F1F7"
    if country == "TW":
        return "\U0001F1F9\U0001F1FC"


def pos_no(no):
    ep_ = list(str(no))
    x = ep_.pop()
    if ep_ != [] and ep_.pop()=='1':
        return 'th'
    th = (
        "st" if x == "1" 
        else "nd" if x == "2" 
        else "rd" if x == "3" 
        else "th"
    )
    return th


def make_it_rw(time_stamp):
    """Converting Time Stamp to Readable Format"""
    seconds, milliseconds = divmod(int(time_stamp), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + " Days, ") if days else "")
        + ((str(hours) + " Hours, ") if hours else "")
        + ((str(minutes) + " Minutes, ") if minutes else "")
        + ((str(seconds) + " Seconds, ") if seconds else "")
        + ((str(milliseconds) + " ms, ") if milliseconds else "")
    )
    return tmp[:-2]


async def clog(
    name: str,
    text: str,
    tag: str,
    msg: Message = None,
    cq: CallbackQuery = None,
    replied: Message = None,
    file: str = None,
    send_as_file: str = None
):
    log = f"#{name.upper()}  #{tag.upper()}\n\n{text}"
    data = ""
    if msg:
        data += str(msg)
        data += "\n\n\n\n"
    if cq:
        data += str(cq)
        data += "\n\n\n\n"
    await app.send_message(chat_id=LOG_CHANNEL_ID, text=log)
    if msg or cq:
        with open("query_data.txt", "x") as output:
            output.write(data)
        await app.send_document(LOG_CHANNEL_ID, "query_data.txt")
        os.remove("query_data.txt")
    if replied:
        media = (
            replied.photo 
            or replied.sticker 
            or replied.animation 
            or replied.video
        )
        media_path = await app.download_media(media)
        await app.send_document(LOG_CHANNEL_ID, media_path)
    if file:
        await app.send_document(LOG_CHANNEL_ID, file)
    if send_as_file:
        with open("dataInQuestio.txt", "x") as text_file:
            text_file.write()
        await app.send_document(LOG_CHANNEL_ID, "dataInQuestio.txt")
        os.remove("dataInQuestio.txt")


def get_btns(
    media,
    user: int,
    result: list,
    lsqry: str = None,
    lspage: int = None,
    auth: bool = False,
    sfw: str = "False"
):
    buttons = []
    qry = f"_{lsqry}" if lsqry is not None else ""
    pg = f"_{lspage}" if lspage is not None else ""
    if media == "ANIME" and sfw == "False":
        buttons.append([
            InlineKeyboardButton(
                text="Characters",
                callback_data=(
                    f"char_{result[2][0]}_ANI" + f"{qry}{pg}_{str(auth)}_1_{user}"
                )
            ),
            InlineKeyboardButton(
                text="Description",
                callback_data=(
                    f"desc_{result[2][0]}_ANI" + f"{qry}{pg}_{str(auth)}_{user}"
                )
            ),
            InlineKeyboardButton(
                text="List Series",
                callback_data=(
                    f"ls_{result[2][0]}_ANI" + f"{qry}{pg}_{str(auth)}_{user}"
                )
            ),
        ])
    if media == "CHARACTER":
        buttons.append([
            InlineKeyboardButton(
                "Description",
                callback_data=(
                    f"desc_{result[2][0]}_CHAR"
                    +f"{qry}{pg}_{str(auth)}_{user}"
                )
            )
        ])
        buttons.append([
            InlineKeyboardButton(
                "List Series",
                callback_data=f"lsc_{result[2][0]}{qry}{pg}_{str(auth)}_{user}"
            )
        ])
    if media == "SCHEDULED":
        if result[0]!=0 and result[0]!=6:
            buttons.append([
                InlineKeyboardButton(
                    str(day_(result[0]-1)),
                    callback_data=f"sched_{result[0]-1}_{user}"
                ),
                InlineKeyboardButton(
                    str(day_(result[0]+1)),
                    callback_data=f"sched_{result[0]+1}_{user}"
                )
            ])
        if result[0] == 0:
            buttons.append([
                InlineKeyboardButton(
                    str(day_(result[0]+1)),
                    callback_data=f"sched_{result[0]+1}_{user}"
                )
            ])
        if result[0] == 6:
            buttons.append([
                InlineKeyboardButton(
                    str(day_(result[0]-1)),
                    callback_data=f"sched_{result[0]-1}_{user}"
                )
            ])
    if media == "MANGA" and sfw == "False":
        buttons.append([
            InlineKeyboardButton("More Info", url=result[1][2])
        ])
    if media == "AIRING" and sfw == "False":
        buttons.append([
            InlineKeyboardButton("More Info", url=result[1][0])
        ])
    if auth is True and media!="SCHEDULED" and sfw == "False":
        auth_btns = get_auth_btns(
            media,user, result[2], lspage=lspage, lsqry=lsqry
        )
        buttons.append(auth_btns)
    if len(result)>3:
        if result[3] == "None":
            if result[4] != "None":
                buttons.append([
                    InlineKeyboardButton(
                        text="Sequel",
                        callback_data=f"btn_{result[4]}_{str(auth)}_{user}"
                    )
                ])
        else:
            if result[4] != "None":
                buttons.append([
                    InlineKeyboardButton(
                        text="Prequel",
                        callback_data=f"btn_{result[3]}_{str(auth)}_{user}"
                    ),
                    InlineKeyboardButton(
                        text="Sequel",
                        callback_data=f"btn_{result[4]}_{str(auth)}_{user}"
                    ),
                ])
            else:
                buttons.append([
                    InlineKeyboardButton(
                        text="Prequel",
                        callback_data=f"btn_{result[3]}_{str(auth)}_{user}"
                    )
                ])
    if (lsqry is not None) and (len(result)!=1):
        if lspage==1:
            if result[1][1] is True:
                buttons.append([
                    InlineKeyboardButton(
                        text="Next",
                        callback_data=(
                            f"page_{media}{qry}_{int(lspage)+1}_{str(auth)}_{user}"
                        )
                    )
                ])
            else:
                pass
        elif lspage!=1:
            if result[1][1] is False:
                buttons.append([
                    InlineKeyboardButton(
                        text="Prev",
                        callback_data=(
                            f"page_{media}{qry}_{int(lspage)-1}_{str(auth)}_{user}"
                        )
                    )
                ])
            else:
                buttons.append([
                    InlineKeyboardButton(
                        text="Prev",
                        callback_data=(
                            f"page_{media}{qry}_{int(lspage)-1}_{str(auth)}_{user}"
                        )
                    ),
                    InlineKeyboardButton(
                        text="Next",
                        callback_data=(
                            f"page_{media}{qry}_{int(lspage)+1}_{str(auth)}_{user}"
                        )
                    )
                ])
    return InlineKeyboardMarkup(buttons)


def get_auth_btns(media, user, data, lsqry: str = None, lspage: int = None):
    btn = []
    qry = f"_{lsqry}" if lsqry is not None else ""
    pg = f"_{lspage}" if lspage is not None else ""
    if media=="CHARACTER":
        btn.append(
            InlineKeyboardButton(
                text=(
                    "Add to Favs" if data[1] is not True
                    else "Remove from Favs"
                ),
                callback_data=f"fav_{media}_{data[0]}{qry}{pg}_{user}"
            )
        )
    else:
        btn.append(
            InlineKeyboardButton(
                text=(
                    "Add to Favs" if data[3] is not True 
                    else "Remove from Favs"
                ),
                callback_data=f"fav_{media}_{data[0]}{qry}{pg}_{user}"
            )
        )
        btn.append(InlineKeyboardButton(
            text="Add to List" if data[1] is False else "Update in List",
            callback_data=(
                f"lsadd_{media}_{data[0]}{qry}{pg}_{user}" if data[1] is False 
                else f"lsupdt_{media}_{data[0]}_{data[2]}{qry}{pg}_{user}"
            )
        ))
    return btn


def day_(x: int):
    if x == 0: return "Monday"
    if x == 1: return "Tuesday"
    if x == 2: return "Wednesday"
    if x == 3: return "Thursday"
    if x == 4: return "Friday"
    if x == 5: return "Saturday"
    if x == 6: return "Sunday"


def season_(future: bool = False):
    k = datetime.now()
    m = k.month
    if future:
        m = m+3
    y = k.year
    if m > 12:
        y = y+1
    if m in [1, 2, 3] or m > 12:
        return 'WINTER', y
    if m in [4, 5, 6]:
        return 'SPRING', y
    if m in [7, 8, 9]:
        return 'SUMMER', y
    if m in [10, 11, 12]:
        return 'FALL', y