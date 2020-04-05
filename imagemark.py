from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

def watermark_text(input_image_path,
                   output_image_path,
                   text, pos):
    photo = Image.open(input_image_path)
    logo = Image.open('cubadata.jpg')
    W, H = photo.size

    wl, hl = logo.size

    photo.paste(logo, (5,H-hl-10))

    # make the image editable
    drawing = ImageDraw.Draw(photo)
    black = (112, 128, 144)
    font = ImageFont.truetype("./font.ttf", 15)
    w, h = drawing.textsize(text)
    drawing.text((wl+5,H-h-12), text, fill=black, font=font)
    #photo.show()
    photo.save(output_image_path)