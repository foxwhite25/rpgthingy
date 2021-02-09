import requests
from PIL import Image, ImageFont, ImageDraw
import random
from io import StringIO
import math

millnames = ['', ' K', ' M', ' B', ' T']


def millify(n):
    n = float(n)
    millidx = max(0, min(len(millnames) - 1,
                         int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

    return '{:.0f}{}'.format(n / 10 ** (3 * millidx), millnames[millidx])



def progressBar(bgcolor, color, x, y, w, h, progress):
    im = Image.new('RGBA', (w, h), color='black')
    drawObject = ImageDraw.Draw(im)

    '''BG'''
    drawObject.ellipse((x + w, y, x + h + w, y + h), fill=bgcolor)
    drawObject.ellipse((x, y, x + h, y + h), fill=bgcolor)
    drawObject.rectangle((x + (h / 2), y, x + w + (h / 2), y + h), fill=bgcolor)

    '''PROGRESS'''
    if (progress <= 0):
        progress = 0.01
    if (progress > 1):
        progress = 1
    w = w * progress
    drawObject.ellipse((x + w, y, x + h + w, y + h), fill=color)
    drawObject.ellipse((x, y, x + h, y + h), fill=color)
    drawObject.rectangle((x + (h / 2), y, x + w + (h / 2), y + h), fill=color)

    '''SAVE'''
    return im


def get_pic(qq):
    apiPath = f'http://q1.qlogo.cn/g?b=qq&nk={qq}&s=100'
    return Image.open(requests.get(apiPath, stream=True).raw)


def profile(uid):
    placeholder = Image.open("./icons/placeholder.png")
    r = get_pic(uid)
    r = r.resize((280, 280), Image.ANTIALIAS)
    img = Image.new('RGBA', (900, 1340), (255, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype('./random.ttf', 70)
    d.text((450, 100), f"名字:{NAME}", font=fnt, fill=(0, 0, 0))
    d.text((450, 170), f"战斗等级:{CLEVEL}", font=fnt, fill=(0, 0, 0))
    d.text((450, 240), f"金钱:{COIN}", font=fnt, fill=(0, 0, 0))
    d.text((450, 310), f"背包:{BACKPACK}", font=fnt, fill=(0, 0, 0))
    img.paste(r, (100, 100))
    placeholder = placeholder.resize((70, 70), Image.ANTIALIAS)
    fnt = ImageFont.truetype('./random.ttf', 25)
    n = 0
    for skill, lv in level.items():
        d.text((180, 480 + 100 * n), skill, font=fnt, fill=(0, 0, 0))
        img.paste(progressBar("white", "black", 0, 0, 620, 10, lv / 100), (180, 505 + 100 * n))
        d.text((180, 515 + 100 * n), f"{lv}/100", font=fnt, fill=(0, 0, 0))
        img.paste(placeholder, (100, 480 + 100 * n))
        n += 1
    im = Image.open("./border.png")
    im = im.convert('RGBA')
    im = im.resize((1080, 1920), Image.ANTIALIAS)
    im.paste(img, (100, 150), img)
    im.save('white.png')
