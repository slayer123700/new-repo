# import random
# import time
# from pyrogram import filters
# from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
# from shigaraki import app
# from pyrogram.enums import ParseMode
# from shigaraki.decorator.save import save

# IMAGE_URLS = [
#     "https://files.catbox.moe/k3orsl.jpg"]



# @app.on_message(filters.command("start") & filters.private)
# @save
# async def handle_start(client, message):

#     await send_start_message(client, message.chat.id)



# @app.on_callback_query(filters.regex("back_to_start"))
# async def handle_callback(client, callback_query):
#     await callback_query.answer()  # Acknowledge the callback query to avoid timeout issues
#     await send_start_message(client, callback_query.message.chat.id, callback_query.message)

# @app.on_callback_query(filters.regex("refresh"))
# async def refresh_ping_uptime(client, callback_query):
#     await callback_query.answer()  # Acknowledge the callback query to avoid timeout issues
#     await send_start_message(client, callback_query.message.chat.id, callback_query.message)

# async def calculate_ping(client, chat_id):
#     start_time = time.time()
#     sent_message = await client.send_message(chat_id, "Wait...")
#     end_time = time.time()
#     await sent_message.delete()
#     ping = round((end_time - start_time) * 1000, 3)
#     return ping

# async def send_start_message(client, chat_id, message_to_edit=None):
#     """
#     Function to send or edit the start message.
#     If message_to_edit is provided, it edits that message with updated ping and uptime.
#     """


#     # Get bot's mention using Markdown
#     bot_user = await client.get_me()
#     mention_bot = f"[{bot_user.first_name}](tg://user?id={bot_user.id})"

#     # Randomly select an image URL
#     img_url = random.choice(IMAGE_URLS)

#     ca ="""[Download all your favorite anime here!](https://t.me/boinker_bot/boinkapp?startapp=boink5630057244)
# [🎥✨ Don't miss out on the latest episodes and classic series – grab them now!](https://t.me/boinker_bot/boinkapp?startapp=boink5630057244)
    
# [Anime Upload Here ⬇️](https://t.me/boinker_bot/boinkapp?startapp=boink5630057244)
    
# [:-https://t.me/+BuggWawASWtlYTJl](https://t.me/PAWSOG_bot/PAWS?startapp=m5eBzU4U)
# [:-https://t.me/+BuggWawASWtlYTJl](https://t.me/PAWSOG_bot/PAWS?startapp=m5eBzU4U)
# [:-https://t.me/+BuggWawASWtlYTJl](https://t.me/PAWSOG_bot/PAWS?startapp=m5eBzU4U)
# [Get Them Now](https://t.me/boinker_bot/boinkapp?startapp=boink5630057244)"""
#     keyboard = InlineKeyboardMarkup(
#         [
#             [
#                 InlineKeyboardButton(
#                     "Add Me To Your Group",
#                     url=f"https://t.me/{bot_user.username}?startgroup=true",
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     "Download All Anime Free!!",
#                     url=f"https://t.me/PAWSOG_bot/PAWS?startapp=m5eBzU4U",
#                 )
#             ],
#             [InlineKeyboardButton("Download Blue Box!!" , url="https://t.me/+qFcr7Hw_RaI3NDJl")],
#             [InlineKeyboardButton("Download Dr Stone!!" , url="https://t.me/+ZADU2yOd2b84YTQ1")],
#             [
#                 InlineKeyboardButton("Download One Piece" , url="https://t.me/+xsuErnqUX_A5YzE1"),
#                 InlineKeyboardButton(
#                     "Support Group", url="https://t.me/GODL_FC"
#                 ),
#             ],
#         ]
#     )

#     if message_to_edit:
#         # Edit the existing message with updated ping and uptime
#         await message_to_edit.edit_caption(
#             caption=ca,
#             reply_markup=keyboard,
#             parse_mode=ParseMode.MARKDOWN  # Ensure you set Markdown for hyperlinks
#         )
#     else:
#         await client.send_photo(
#             chat_id=chat_id,
#             photo=img_url,
#             caption=ca,
#             reply_markup=keyboard,
#             parse_mode=ParseMode.MARKDOWN  # Ensure you set Markdown for hyperlinks
#         )
