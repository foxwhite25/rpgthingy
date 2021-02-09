from li import *

DB_PATH = os.path.expanduser("~/.hoshino/rpg.db")
db = RecordDAO(DB_PATH)
DATA_PATH = os.path.expanduser("~/.hoshino/data.db")
dat = dat(DATA_PATH)


def add(dict1, dict2):
    for key in dict2:
        if key in dict1:
            if not isinstance(dict1[key],dict):
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
            print(temp)
            print(ini)
            add(temp, ini)
            print(ini)
        else:
            pass
    if not ini["type"]:
        ini["type"] = "Melee"
    if not ini["attack_speed"]:
        ini["attack_speed"] = 2400
    print(ini)
    return ini



def get_skill_level(x):
    for level, xp in exp:
        if x >= xp:
            return level


def base_combat_level(uid):
    skill = db.get_player_skill(uid)[1]
    skill = json.load(skill)
    return (skill["defence"] + skill["hitpoints"] + skill["prayer"] / 2) * 0.25


def melee_combat_level(uid):
    skill = db.get_player_skill(uid)[1]
    skill = json.load(skill)
    return (skill["attack"] + skill["strength"]) * 0.325


def magic_combat_level(uid):
    skill = db.get_player_skill(uid)[1]
    skill = json.load(skill)
    return skill["magic"] * 0.4875


def ranged_combat_level(uid):
    skill = db.get_player_skill(uid)[1]
    skill = json.load(skill)
    return skill["ranged"] * 0.4875


def combat_level(uid):
    offensiv_skill_level = [melee_combat_level(uid), magic_combat_level(uid), ranged_combat_level(uid)]
    return base_combat_level(uid) + max(offensiv_skill_level)


db.ini_player(114514)
combine_stat(114514)
