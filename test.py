from collections import Counter

import ujson as json
import math
import os
import sqlite3
import textwrap
from lib import *
from PIL import Image, ImageFont, ImageDraw

__BASE = os.path.split(os.path.realpath(__file__))
RPG_DB_PATH = os.path.expanduser("~/.hoshino/rpg.db")
db = RecordDAO(RPG_DB_PATH)
DATA_PATH = os.path.expanduser("~/.hoshino/data.db")
dat = dat(DATA_PATH)


def get_item_image(iid):
    img_path = os.path.join(__BASE[0], f'icons/item/{iid}.png')
    im = Image.open(img_path)
    return im


def f(x):
    if x == 1:
        return 0
    else:
        y = round(0.25 * (x - 1 + 300 * (2 ** ((x - 1) / 7))))
        y += f(x - 1)
        return y


def g(x):
    if x == 1:
        return 0
    else:
        y = round(0.25 * (x - 1 + 300 * (2 ** ((x - 1) / 7))))
        return y


exp = {}
exp_delta = {}
for n in range(1, 99):
    exp[n] = f(n)
    exp_delta[n] = g(n)


def get_level(x):
    a = 1
    for level, xp in exp.items():
        if x == xp:
            return level
        if x > xp:
            return a
        a = level


def round_corner(radius, fill):
    """Draw a round corner"""
    corner = Image.new('RGBA', (radius, radius), (0, 0, 0, 0))
    draw = ImageDraw.Draw(corner)
    draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=fill)
    return corner


def round_rectangle(size, radius, fill, msg):
    """Draw a rounded rectangle"""
    width, height = size
    W, H = width, height
    rectangle = Image.new('RGBA', size, fill)
    corner = round_corner(radius, fill)
    rectangle.paste(corner, (0, 0))
    rectangle.paste(corner.rotate(90), (0, height - radius))  # Rotate the corner and paste it
    rectangle.paste(corner.rotate(180), (width - radius, height - radius))
    rectangle.paste(corner.rotate(270), (width - radius, 0))
    draw = ImageDraw.Draw(rectangle)
    w, h = draw.textsize(msg)
    font_path = os.path.join(__BASE[0], 'random.ttf')
    fnt = ImageFont.truetype(font_path, 40)
    draw.text(((W - w) / 2 - 48, (H - h) / 2 - 15), msg, font=fnt, fill="white")
    return rectangle


def get_gather_skill_mastery(uid, s_type):
    skill = json.loads(db.get_player_skill(uid)[1])
    mxp, sxp = skill[s_type][0], skill[s_type][1]
    mlv, slv = get_skill_level(mxp), get_skill_level(sxp)
    nmxp, nsxp = skill[s_type][0] - exp[mlv], skill[s_type][1] - exp[slv]
    return {"mxp": mxp, "mlv": mlv, "sxp": sxp, "slv": slv, 'nmxp': nmxp, 'nsxp': nsxp}


def progressBar(bgcolor, color, x, y, w, h, progress):
    im = Image.new('RGBA', (w, h), (255, 0, 0, 0))
    drawObject = ImageDraw.Draw(im)

    '''BG'''
    drawObject.ellipse((x + w, y, x + h + w, y + h), fill=bgcolor)
    drawObject.ellipse((x, y, x + h, y + h), fill=bgcolor)
    drawObject.ellipse((w - h - 1, y, w - 1, h), fill=bgcolor)
    drawObject.rectangle((x + (h / 2), y, x + w + (h / 2) - h * 1.1, y + h), fill=bgcolor)

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


def f(x):
    if x == 1:
        return 0
    else:
        y = round(0.25 * (x - 1 + 300 * (2 ** ((x - 1) / 7))))
        y += f(x - 1)
        return y


def g(x):
    if x == 1:
        return 0
    else:
        y = round(0.25 * (x - 1 + 300 * (2 ** ((x - 1) / 7))))
        return y


exp = {}
exp_delta = {}
for n in range(1, 99):
    exp[n] = f(n)
    exp_delta[n] = g(n)

millnames = ['', 'K', 'M', 'B', 'T']


def get_skill_level(x):
    a = 1
    for level, xp in exp.items():
        if x == xp:
            return level
        if x < xp:
            return a
        a = level


def millify(n):
    n = float(n)
    millidx = max(0, min(len(millnames) - 1,
                         int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

    return '{:.0f}{}'.format(n / 10 ** (3 * millidx), millnames[millidx])


# Get current inv -> get max craft -> get iteration -> calculate bonus ->minus cost from inv-> add loot to inv-> result
