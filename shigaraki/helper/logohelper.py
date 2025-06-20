from PIL import Image, ImageDraw, ImageFont


font=ImageFont.truetype("shigaraki/fonts/IronFont.otf",110)
def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im
    
def Gabung(fun):
    def gabung(arg):
        im, text1 = add_corners(arg[0], 17), arg[1]

        # Load font
        font_path = "./shigaraki/fonts/default.ttf"  # Replace with your font's path
        font_size = 120
        font = ImageFont.truetype(font_path, font_size)

        # Measure the text size using textbbox()
        text_bbox = font.getbbox(text1)  # Returns (x_min, y_min, x_max, y_max)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Create a new black rectangle
        op = Image.new("RGB", (40, 20), color=(0, 0, 0))

        # Create a new image with enough space for text and the provided image
        baru = Image.new(
            "RGB",
            (im.width + text_width + 210 + 20 + 130, 600),
            color=(0, 0, 0)
        )

        # Draw the text onto the image
        draw = ImageDraw.Draw(baru)
        draw.text((150, 250), text1, (255, 255, 255), font=font)

        # Paste the processed image onto the new image
        baru.paste(im, (150 + text_width + 20, 230 + 10), im.convert("RGBA"))
        return baru

    return gabung(fun)

    
def generate(text1, text2):
    # Load the font
    font_path = "./shigaraki/fonts/default.ttf"  # Update this to the correct font path
    font_size = 120  # Adjust font size as needed
    font = ImageFont.truetype(font_path, font_size)

    # Get the size of the text using getbbox()
    text_bbox = font.getbbox(text2)  # Returns (x_min, y_min, x_max, y_max)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Create a new image for the text
    oren = Image.new("RGBA", (text_width + 20, 140), color=(240, 152, 0))
    draw = ImageDraw.Draw(oren)

    # Center the text vertically
    text_x = 10  # Padding on the left
    text_y = (oren.height - text_height) // 2 - 10
    draw.text((text_x, text_y), text2, (0, 0, 0), font=font)

    # Combine the generated text image with `text1`
    return Gabung([oren, text1])


def blackpink(teks):
    # Load the font and determine text dimensions
    font_path = "./shigaraki/fonts/blackpink.otf"  # Update this to the correct font path
    font_size = 120  # Adjust font size as needed
    font = ImageFont.truetype(font_path, font_size)

    # Calculate text dimensions using getbbox()
    text_bbox = font.getbbox(teks)  # (x_min, y_min, x_max, y_max)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Create the initial image
    img = Image.new("RGB", (text_width + 100, text_height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Center the text and draw it
    x = (img.width - text_width) // 2
    y = -25  # Adjust y position as required
    draw.text((x, y), teks, fill=(255, 148, 224), font=font)

    # Create the second image (with padding)
    padded_width = img.width + 400
    padded_height = img.height + 400
    img2 = Image.new("RGB", (padded_width, padded_height), color=(0, 0, 0))

    # Center the first image on the padded image
    paste_x = (img2.width - img.width) // 2
    paste_y = (img2.height - img.height) // 2
    img2.paste(img, (paste_x, paste_y))

    return img2
