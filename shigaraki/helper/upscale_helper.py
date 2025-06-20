from pyrogram.types import Message
from lexica import Client as LexicaClient

async def getFile(message: Message):

    if not message.reply_to_message:
        return None

    # Check if the reply contains a photo or a document of valid image types
    if message.reply_to_message.photo:
        image = await message.reply_to_message.download()
        return image
    elif message.reply_to_message.document and message.reply_to_message.document.mime_type in ['image/png', 'image/jpg', 'image/jpeg']:
        image = await message.reply_to_message.download()
        return image
    else:
        return None

async def UpscaleImages(image: bytes) -> str:

    try:
        # Initialize the Lexica client and upscale the image
        client = LexicaClient()
        content = client.upscale(image)
        
        # Save the upscaled image to a file
        upscaled_file_path = "upscaled.png"
        with open(upscaled_file_path, "wb") as output_file:
            output_file.write(content)
        
        return upscaled_file_path
    except Exception as e:
        raise Exception(f"Failed to upscale the image: {e}")
    
