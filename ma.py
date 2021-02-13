import base64
from io import BytesIO
from collections import Counter
import numpy

from .lib import *
import requests
from PIL import Image, ImageFont, ImageDraw
import math
from hoshino import Service, util
from hoshino.typing import MessageSegment, NoticeSession, CQEvent
from numpy.random import choice

__BASE = os.path.split(os.path.realpath(__file__))
RPG_DB_PATH = os.path.expanduser("~/.hoshino/rpg.db")
db = RecordDAO(RPG_DB_PATH)
DATA_PATH = os.path.expanduser("~/.hoshino/data.db")
dat = dat(DATA_PATH)
millnames = ['', 'K', 'M', 'B', 'T']


def millify(n):
    n = float(n)
    millidx = max(0, min(len(millnames) - 1,
                         int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

    return '{:.0f}{}'.format(n / 10 ** (3 * millidx), millnames[millidx])


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


def get_pic(qq):
    apiPath = f'http://q1.qlogo.cn/g?b=qq&nk={qq}&s=100'
    return Image.open(requests.get(apiPath, stream=True).raw)


def add(dict1, dict2):
    for key in dict2:
        if key in dict1:
            if not isinstance(dict1[key], dict):
                dict2[key] = dict2[key] + dict1[key]
            else:
                add(dict1[key], dict2[key])


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


def get_bp_cost(x):
    return (132728500 * (x + 2)) / (142015 ** (163 / (122 + x)))


def mxpd(uid, action, item, spa, iteration):
    milestone = mining_milestone(uid)
    mastery = db.get_mastery(uid, action)[0]
    mastery = json.loads(mastery)
    total_mastery = len(mastery) * 99
    player_mastery = 0
    for item, xp in mastery.items():
        level = get_skill_level(xp)
        player_mastery += level
    item_mastery_level = get_skill_level(mastery[item])
    return int(((milestone * (player_mastery / total_mastery)) + (
            item_mastery_level * len(mastery) / 10)) * spa * 0.5 * iteration)


ore = [{'id': 45, 'level': 1, 'exp': 7}, {'id': 46, 'level': 1, 'exp': 7}, {'id': 47, 'level': 15, 'exp': 14},
       {'id': 48, 'level': 30, 'exp': 18}, {'id': 49, 'level': 30, 'exp': 25}, {'id': 50, 'level': 40, 'exp': 28},
       {'id': 51, 'level': 50, 'exp': 65}, {'id': 52, 'level': 70, 'exp': 71}, {'id': 53, 'level': 80, 'exp': 86},
       {'id': 54, 'level': 95, 'exp': 101}, {'id': 388, 'level': 1, 'exp': 5}]
pickaxe = [{'id': 1, 'name': '铁镐', 'level': 1, 'chance': 0.01, 'speed': 0.05, 'coin': 250},
           {'id': 2, 'name': '钢镐', 'level': 10, 'chance': 0.02, 'speed': 0.1, 'coin': 2000},
           {'id': 3, 'name': '黑钢镐', 'level': 20, 'chance': 0.03, 'speed': 0.15, 'coin': 10000},
           {'id': 4, 'name': '秘银镐', 'level': 35, 'chance': 0.04, 'speed': 0.2, 'coin': 50000},
           {'id': 5, 'name': '精金镐', 'level': 50, 'chance': 0.05, 'speed': 0.3, 'coin': 200000},
           {'id': 6, 'name': '符文镐', 'level': 60, 'chance': 0.06, 'speed': 0.4, 'coin': 1000000},
           {'id': 7, 'name': '飞龙镐', 'level': 80, 'chance': 0.07, 'speed': 0.5, 'coin': 5000000}]
gem = [{'id': "128", 'weight': 0.5}, {'id': "129", 'weight': 0.175}, {'id': "130", 'weight': 0.175},
       {'id': "131", 'weight': 0.1},
       {'id': "132", 'weight': 0.05}]
exp = {}
exp_delta = {}
for n in range(1, 99):
    exp[n] = f(n)
    exp_delta[n] = g(n)


def combine_stat(uid):
    ini = {"attack_speed": 0, "type": "", "str_bonus": {"melee": 0, "ranged": 0},
           "atk_bonus": {"melee": {"stab": 0, "slash": 1, "block": 0}, "ranged": 0, "magic": 0}, "magic_bonus": 0.0,
           "def_bonus": {"melee": 0, "ranged": 0, "magic": 0}, "damage_reduction": 0.0, "slayer_xp": 0.0,
           }
    equipment = db.get_player_inv(uid)[2]
    equipment = json.loads(equipment)
    for slot, id in equipment.items():
        if id:
            temp = dat.get_equ_stat(id)
            add(temp, ini)
        else:
            pass
    if not ini["type"]:
        ini["type"] = "Melee"
    if not ini["attack_speed"]:
        ini["attack_speed"] = 2400
    return ini


def get_skill_level(x):
    a = 1
    for level, xp in exp.items():
        if x == xp:
            return level
        if x < xp:
            return a
        a = level


def base_combat_level(uid):
    skill = db.get_player_skill(uid)[1]
    skill = json.loads(skill)
    return (skill["defence"] + skill["hitpoints"] + skill["prayer"] / 2) * 0.25


def melee_combat_level(uid):
    skill = db.get_player_skill(uid)[1]
    skill = json.loads(skill)
    return (skill["attack"] + skill["strength"]) * 0.325


def magic_combat_level(uid):
    skill = db.get_player_skill(uid)[1]
    skill = json.loads(skill)
    return skill["magic"] * 0.4875


def ranged_combat_level(uid):
    skill = db.get_player_skill(uid)[1]
    skill = json.loads(skill)
    return skill["ranged"] * 0.4875


def change_item_num(uid, item, value):
    inv = json.loads(db.get_player_inv(uid)[1])
    name = dat.get_item_from_col("id", item)[1]
    try:
        inv[item] += value
    except KeyError:
        inv[item] = value
    if inv[item] == 0:
        del inv[item]
    inv = json.dumps(inv, indent=4)
    db.update_player_inv(uid, inv)
    return name


def combat_level(uid):
    offensiv_skill_level = [melee_combat_level(uid), magic_combat_level(uid), ranged_combat_level(uid)]
    return base_combat_level(uid) + max(offensiv_skill_level)


def profile(uid):
    placeholder_path = os.path.join(__BASE[0], 'icons/placeholder.png')
    placeholder = Image.open(placeholder_path)
    NAME = db.get_player_stat(uid)[3]
    CLEVEL = combat_level(uid)
    COIN = db.get_player_stat(uid)[2]
    backpack_max = db.get_player_stat(uid)[1]
    backpack_now = len(json.loads(db.get_player_inv(uid)[1]))
    skill = db.get_player_skill(uid)[1]
    skill = json.loads(skill)
    level = {"攻击等级": get_skill_level(skill["attack"]), "力量等级": get_skill_level(skill["strength"]),
             "防御等级": get_skill_level(skill["defence"]), "血量等级": get_skill_level(skill["hitpoints"]),
             "远程等级": get_skill_level(skill["ranged"]), "魔法等级": get_skill_level(skill["magic"]),
             "祷告等级": get_skill_level(skill["prayer"]), "斩杀等级": get_skill_level(skill["slayer"])}
    r = get_pic(uid)
    r = r.resize((280, 280), Image.ANTIALIAS)
    img = Image.new('RGBA', (900, 1340), (255, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font_path = os.path.join(__BASE[0], 'random.ttf')
    fnt = ImageFont.truetype(font_path, 70)
    d.text((450, 100), f"名字:{NAME}", font=fnt, fill=(0, 0, 0))
    d.text((450, 170), f"战斗等级:{CLEVEL}", font=fnt, fill=(0, 0, 0))
    d.text((450, 240), f"金钱:{COIN}", font=fnt, fill=(0, 0, 0))
    d.text((450, 310), f"背包:{backpack_now}/{backpack_max}", font=fnt, fill=(0, 0, 0))
    img.paste(r, (100, 100))
    placeholder = placeholder.resize((70, 70), Image.ANTIALIAS)
    font_path = os.path.join(__BASE[0], 'random.ttf')
    fnt = ImageFont.truetype(font_path, 25)
    n = 0
    for skill, lv in level.items():
        d.text((180, 480 + 100 * n), skill, font=fnt, fill=(0, 0, 0))
        img.paste(progressBar("white", "black", 0, 0, 620, 10, lv / 100), (180, 505 + 100 * n))
        d.text((180, 515 + 100 * n), f"{lv}/100", font=fnt, fill=(0, 0, 0))
        img.paste(placeholder, (100, 480 + 100 * n))
        n += 1
        if n == 8:
            break
    img_path = os.path.join(__BASE[0], 'border.png')
    im = Image.open(img_path)
    im = im.convert('RGBA')
    im = im.resize((1080, 1920), Image.ANTIALIAS)
    im.paste(img, (100, 150), img)
    return MessageSegment.image(util.pic2b64(im))


def inventory(uid, page=1, reverse=True, per_page=20, user_loot=False, loot={}):
    if user_loot:
        inv = loot
    else:
        inv = db.get_player_inv(uid)[1]
        inv = json.loads(inv)
    inv = dict(sorted(inv.items(), key=lambda item: item[1], reverse=reverse))
    if per_page > len(inv):
        per_page = len(inv)
    img = Image.new('RGBA', (900, per_page * 140), (255, 0, 0, 0))  # 单行宽度<440 , 单个高度<130
    font_path = os.path.join(__BASE[0], 'random.ttf')
    fnt = ImageFont.truetype(font_path, 40)
    d = ImageDraw.Draw(img)
    i, a, t, n = (page - 1) * per_page, page * per_page - 1, 0, 0
    for item, count in inv.items():
        if i <= t <= a:
            im = get_item_image(item)
            im = im.resize((130, 130), Image.ANTIALIAS)
            img.paste(im, (0, n * 140))
            d.text((140, n * 140), f"{dat.get_item_from_col('id', item)[1]}", font=fnt, fill=(0, 0, 0))
            d.text((140, n * 140 + 65), f"x{count}个", font=fnt, fill=(0, 0, 0))
            d.text((540, n * 140 + 65), f"ID:{item}", font=fnt, fill=(0, 0, 0))
            n += 1
        t += 1
    h, w = per_page * 140 + 200, 1100
    im = Image.new('RGB', (w, h), (0, 0, 0, 0))
    im2 = Image.new('RGB', (w - 50, h - 50), (255, 255, 255))
    im.convert("RGBA")
    im.paste(im2, (25, 25))
    im.paste(img, (100, 100), img)
    return MessageSegment.image(util.pic2b64(im))


def get_item_image(iid):
    img_path = os.path.join(__BASE[0], f'icons/item/{iid}.png')
    im = Image.open(img_path)
    return im


def default_arg(default, args, num):
    try:
        a = args[num]
    except IndexError:
        a = default
    return a


def get_gather_skill_mastery(uid, s_type):
    skill = json.loads(db.get_player_skill(uid)[1])
    mxp, sxp = skill[s_type][0], skill[s_type][1]
    mlv, slv = get_skill_level(mxp), get_skill_level(sxp)
    nmxp, nsxp = skill[s_type][0] - exp[mlv], skill[s_type][1] - exp[slv]
    return {"mxp": mxp, "mlv": mlv, "sxp": sxp, "slv": slv, 'nmxp': nmxp, 'nsxp': nsxp}


def is_player_in_action(uid):
    try:
        action = db.get_player_action(uid)
        return action["action"]
    except IndexError:
        return None


def get_ore_from_id(r):
    for each in ore:
        if each["id"] == int(r):
            return each


def get_gem_num(r):
    gem_list = []
    gem_weight = []
    for item in gem:
        gem_list.append(item["id"])
        gem_weight.append(item["weight"])
    d = choice(gem_list, r, p=gem_weight)
    unique, counts = numpy.unique(d, return_counts=True)
    return dict(zip(unique, counts))


def is_str_in_list(l, s):
    for each in l:
        if each == s:
            return True
    return False


def mining_milestone(uid):
    skill = get_gather_skill_mastery(uid, "mining")
    yes = []
    for ores in ore:
        if ores["level"] <= skill["slv"]:
            yes.append(ores["id"])
    r = len(yes)
    if skill['slv'] >= 99:
        r += 1
    return r


def cal_mining(action, uid):
    sk = json.loads(db.get_player_skill(uid)[1])
    time = 3
    mastery_pool = sk['mining'][0]
    if mastery_pool >= 2750000:
        time = 2.8
    start_time = action['start_time']
    o = action['action'][1]
    now = datetime.datetime.timestamp(datetime.datetime.now())
    seconds = math.floor(now - start_time)
    if seconds >= 43200:
        seconds = 43200
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    time_str = ("%d小时%02d分%02d秒" % (h, m, s))
    iteration = math.floor(seconds / time)
    loot = get_gem_num(math.floor(iteration / 100))
    bonus_level = {10: 0.01, 20: 0.02, 30: 0.03, 40: 0.04, 50: 0.05, 60: 0.06, 70: 0.07, 80: 0.08, 90: 0.09, 99: 0.15}
    skill = db.get_mastery(uid, 'mining')[0]
    skill = json.loads(skill)
    print(skill)
    bonus = 0
    for level, bs in bonus_level.items():
        if skill[str(o)] > level:
            bonus = bs
    loot[o] = int(iteration * (bonus + 1))
    add_loot_to_inv(loot, uid)
    o = get_ore_from_id(o)
    mxp = mxpd(uid, 'mining', o['id'], time, iteration)
    if mastery_pool >= 550000:
        mxp = int(mxp * 1.05)
    msg = f'经过了{time_str}，进行了{iteration}次挖掘，你获得了{o["exp"] * iteration}点经验值和{mxp}点{dat.get_name_from_id(o["id"])[0]}熟练度以及:\n'
    db.add_skill_xp(uid, 'mining', o['exp'] * iteration)
    db.add_master_xp(uid, 'mining', o['id'], mxp)
    db.add_mastery_pool(uid, 'mining', int(mxp * 0.25))
    msg += str(inventory(0, user_loot=True, loot=loot))
    return msg


def add_loot_to_inv(loot, uid):
    new = {}
    current_inv = json.loads(db.get_player_inv(uid)[1])
    for a, b in loot.items():
        new[str(a)] = int(b)
    new_inv = Counter(new) + Counter(current_inv)
    for a, b in dict(new_inv).items():
        new[str(a)] = int(b)
    a = json.dumps(dict(new), indent=4)
    db.update_player_inv(uid, a)


def mining(uid):
    mastery = db.get_mastery(uid, 'mining')[0]
    mastery = json.loads(mastery)
    sk = get_gather_skill_mastery(uid, 'mining')
    img = Image.new('RGBA', (900, 1820), (255, 0, 0, 0))
    mining_path = os.path.join(__BASE[0], 'icons/skill/mini.png')
    im = Image.open(mining_path)
    im = im.resize((340, 340), Image.ANTIALIAS)
    img.paste(im, (0, 0), im)
    font_path = os.path.join(__BASE[0], 'random.ttf')
    header_fnt = ImageFont.truetype(font_path, 100)
    fnt = ImageFont.truetype(font_path, 30)
    d = ImageDraw.Draw(img)
    d.text((340, 0), f"采矿系统:", font=header_fnt, fill=(0, 0, 0))
    d.text((280, 70), '''
    采矿用于采集矿石，符文精华和宝石。 
    每次采矿行动需要3秒，通过购买镐升级减少
    5-50％，通过购买自然大师升级可降低20％
    而达到50％采矿熟练度则可以降低0.2秒。

    每次采矿行动都有1％的宝石发现几率，
    如果装备了线索追赶者徽章，则增加10％
    （至1.10％），而戴上宝石手套保证掉落。''', font=fnt, fill=(0, 0, 0))
    if sk['slv'] >= 99:
        color = (48, 199, 141)
    else:
        color = (92, 172, 229)
    pbar = progressBar((45, 53, 66), color, 0, 0, 800, 20, sk['slv'] / 100)
    box = round_rectangle((150, 50), 10, (48, 199, 141), f"{sk['slv']}/99")
    box2 = round_rectangle((150, 50), 10, (92, 172, 229), f"{millify(sk['sxp'])}")
    d.text((100, 390), f"等级:", font=ImageFont.truetype(font_path, 45), fill=(0, 0, 0))
    d.text((500, 390), f"经验:", font=ImageFont.truetype(font_path, 45), fill=(0, 0, 0))
    img.paste(box, (200, 390), box)
    img.paste(box2, (600, 390), box2)
    img.paste(pbar, (50, 450), pbar)
    n = 1
    for item, skil in sorted(mastery.items()):
        im = get_item_image(item)
        im = im.resize((100, 100), Image.ANTIALIAS)
        img.paste(im, (0, 400 + n * 120), im)
        level = get_skill_level(skil)
        d.text((110, 400 + n * 120), f"{dat.get_name_from_id(item)[0]}的熟练度:{level}/99", font=fnt, fill=(0, 0, 0))
        if level >= 99:
            color = (48, 199, 141)
        else:
            color = (92, 172, 229)
        pbar = progressBar((45, 53, 66), color, 0, 0, 700, 10, level / 99)
        img.paste(pbar, (110, 440 + n * 120), pbar)
        o = get_ore_from_id(item)
        d.text((110, 470 + n * 120), f"所需等级:{o['level']} 每一次获得经验:{o['exp']} ID:{o['id']}", font=fnt, fill=(0, 0, 0))
        n += 1
    im = Image.new('RGB', (1000, 1920), (0, 0, 0, 0))
    im2 = Image.new('RGB', (950, 1920 - 50), (255, 255, 255))
    im.convert("RGBA")
    im.paste(im2, (25, 25))
    im.paste(img, (50, 50), img)
    im.paste(Image.new('RGBA', (1000, 20), (0, 0, 0)), (0, 400))
    im.paste(Image.new('RGBA', (1000, 20), (0, 0, 0)), (0, 530))
    return MessageSegment.image(util.pic2b64(im))
