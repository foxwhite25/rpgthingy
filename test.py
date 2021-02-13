import math
import os

from PIL import Image, ImageFont, ImageDraw

mining_mastery = {45: 0, 46: 0, 47: 0, 48: 0, 49: 0, 50: 0, 51: 0, 52: 0, 53: 0, 54: 0, 388: 0}
skill = {"mxp": 0, "mlv": 1, "sxp": 0, "slv": 1, 'nmxp': 10, 'nsxp': 10}
__BASE = os.path.split(os.path.realpath(__file__))
ore = [{'id': 45, 'level': 1, 'exp': 7}, {'id': 46, 'level': 1, 'exp': 7}, {'id': 47, 'level': 15, 'exp': 14},
       {'id': 48, 'level': 49, 'exp': 18}, {'id': 49, 'level': 30, 'exp': 25}, {'id': 50, 'level': 40, 'exp': 28},
       {'id': 51, 'level': 50, 'exp': 65}, {'id': 52, 'level': 70, 'exp': 71}, {'id': 53, 'level': 80, 'exp': 86},
       {'id': 54, 'level': 95, 'exp': 101}, {'id': 388, 'level': 1, 'exp': 5}]
millnames = ['', 'K', 'M', 'B', 'T']


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
    draw.text(((W - w) / 2 - 48, (H - h) / 2 - 15), msg, font=fnt, fill="black")
    return rectangle


a = [{'from': {'45': '1', '46': '1'}, 'to': {'55': '1'}, 'level': '1', 'exp': '5'}, {'from': {'47': '1'}, 'to': {'56': '1'}, 'level': '10', 'exp': '8'}, {'from': {'47': '1', '48': '2'}, 'to': {'57': '1'}, 'level': '25', 'exp': '12'}, {'from': {'49': '1'}, 'to': {'133': '1'}, 'level': '30', 'exp': '15'}, {'from': {'50': '1'}, 'to': {'58': '1'}, 'level': '40', 'exp': '20'}, {'from': {'51': '1', '48': '4'}, 'to': {'59': '1'}, 'level': '40', 'exp': '35'}, {'from': {'52': '1', '48': '6'}, 'to': {'60': '1'}, 'level': '55', 'exp': '42'}, {'from': {'53': '1', '48': '8'}, 'to': {'61': '1'}, 'level': '70', 'exp': '50'}, {'from': {'54': '1', '53': '2', '48': '12'}, 'to': {'62': '1'}, 'level': '85', 'exp': '60'}]
b = []
for item in a:
    for key , value in item.items():
        if isinstance(value,dict):
            for k , v in value.items():
                value[k] = int(v)
            item[key] = value
        else:
            item[key] = int(value)
    b.append(item)
print(b)
b = [{'from': {'45': 1, '46': 1}, 'to': {'55': 1}, 'level': 1, 'exp': 5}, {'from': {'47': 1}, 'to': {'56': 1}, 'level': 10, 'exp': 8}, {'from': {'47': 1, '48': 2}, 'to': {'57': 1}, 'level': 25, 'exp': 12}, {'from': {'49': 1}, 'to': {'133': 1}, 'level': 30, 'exp': 15}, {'from': {'50': 1}, 'to': {'58': 1}, 'level': 40, 'exp': 20}, {'from': {'51': 1, '48': 4}, 'to': {'59': 1}, 'level': 40, 'exp': 35}, {'from': {'52': 1, '48': 6}, 'to': {'60': 1}, 'level': 55, 'exp': 42}, {'from': {'53': 1, '48': 8}, 'to': {'61': 1}, 'level': 70, 'exp': 50}, {'from': {'54': 1, '53': 2, '48': 12}, 'to': {'62': 1}, 'level': 85, 'exp': 60}]
