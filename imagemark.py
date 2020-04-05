from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

def watermark_text(input_image_path,
                   output_image_path,
                   text, pos):
    photo = Image.open(input_image_path)
    # make the image editable
    drawing = ImageDraw.Draw(photo)
    black = (3, 8, 12)
    #font = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 40)
    #drawing.text(pos, text, fill=black, font=font)
    drawing.text(pos, text, fill=black)
    photo.show()
    photo.save(output_image_path)