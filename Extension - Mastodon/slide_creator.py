from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

def split_string_into_chunks(text, chunk_size=25):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def fetch_and_resize_image(url, target_size):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))

    image = image.convert("RGB")
    resized_image = image.resize(target_size)

    return resized_image

def place_pp(slide, pp, position):
    slide.paste(pp, position)
    return slide

def slide_creator(toot):
    image = Image.open("slide.png")
    draw = ImageDraw.Draw(image)

    username = toot['account']['username']
    date = toot['created_at'].strftime('%d.%m.%y-%H:%M')
    content_chunks = split_string_into_chunks(toot['content'])
    tags = "#" + toot['tags'][0]['name']

    font = ImageFont.truetype("consola.ttf", 128)
    content_font = ImageFont.truetype("consola.ttf", 104)

    username_position = (800,300)
    date_position = (800, 435)
    content_position = (800, 635)
    tag_position = (800, 739)

    draw.text(username_position, username, fill="white", font=font)
    draw.text(date_position, date, fill="white", font=font)

    for content in content_chunks:
        draw.text(content_position, content, fill="white", font=content_font)
        content_position = (content_position[0], content_position[1] + 104)
        tag_position = (tag_position[0], tag_position[1] + 104)
    draw.text(tag_position, tags, fill="white", font=content_font)


    pp = fetch_and_resize_image(toot['account']['avatar'], (400,400))
    image = place_pp(image, pp, (300, 300))

    image.save("./toots/1.png")