from hoshino import Service, util, priv
from hoshino.typing import MessageSegment, NoticeSession, CQEvent
import random
from .ma import *
from .lib import *
import operator

BASE = os.path.split(os.path.realpath(__file__))
dat = dat(DATA_PATH)
style_dict = {'stab': '穿刺', 'slash': '斩击', 'block': '格挡'}
attack_dict = {'melee': '近战', 'ranged': '远程', 'magic': '魔法'}
a = {"str_bonus": {"melee": 3, "ranged": 0},
     "atk_bonus": {"melee": {"stab": 0, "slash": 0, "block": 0}, "ranged": -2, "magic": -6}, "magic_bonus": 0.0,
     "def_bonus": {"melee": 9, "ranged": 9, "magic": -1}, "damage_reduction": 0.0, "slayer_xp": 0.05,
     "level": {"def": 0, "rag": 0, "mag": 0}, "slot": "Helmet"}
b = {"combat_level": 23, "hp": 200, "attack_speed": "2.6", "max_hit": 42, "accuracy": 2146,
     "evasion": {"melee": 2436, "range": 2436, "magic": 960},
     "skill": {"atk": 20, "str": 20, "def": 20, "rag": 1, "mag": 1}}
combat_dict = {}
monster_dict = dat.get_monster_dict()


class Combat_Handler:
    def __init__(self, uid, mob):
        self.uid = uid
        self.mob = mob
        self.tab = 'equipment'
        # ================================================================= #
        self.mob_name = dat.get_monster_name(mob)
        self.mob_stat = dat.get_monster_stat(str(mob))
        mob_attack_stat = {'melee': self.mob_stat['skill']['atk'], 'ranged': self.mob_stat['skill']['rag'],
                           'magic': self.mob_stat['skill']['mag']}
        self.mob_attack_type = max(mob_attack_stat.items(), key=operator.itemgetter(1))[0]
        # ================================================================= #
        self.equipment = json.loads(db.get_player_inv(uid)[2])
        self.skill_xp, self.skill = json.loads(db.get_player_skill(uid)[1]), {}
        self.combat_level, self.max_hit, self.min_hit, self.accuracy_rating = combat_level(uid), 0, 1, 0
        self.hit_chance, self.mob_hit_chance, self.damage_reduction, self.effective_damage_reduction = 0, 0, 0, 0
        # ================================================================= #
        self.effective_melee_defence, self.effective_ranged_defence, self.effective_magic_defence = 0, 0, 0
        self.melee_evasion, self.ranged_evasion, self.magic_evasion = 0, 0, 0
        self.melee_defence_bonus, self.ranged_defence_bonus, self.magic_defence_bonus = 0, 0, 0
        # ================================================================= #
        self.effective_melee_attack, self.effective_ranged_attack, self.effective_magic_attack = 0, 0, 0
        self.melee_accuracy, self.ranged_accuracy, self.magic_accuracy = 0, 0, 0
        self.stab_bonus, self.slash_bonus, self.block_bonus, self.melee_style_bonus = 0, 0, 0, {}
        self.melee_style = 'stab'
        self.ranged_bonus, self.magic_bonus = 0, 0
        # ================================================================= #
        self.melee_max_hit, self.ranged_max_hit, self.magic_max_hit = 0, 0, 0
        self.melee_strength_bonus, self.ranged_strength_bonus = 0, 0
        # ================================================================= #
        self.get_equipment_total_stat()
        if self.skill['hitpoints'] < 10:
            db.set_combat_xp(uid, 'hitpoints', 1155)
        # ================================================================= #
        self.mob_max_hp, self.max_hp = self.mob_stat['hp'], self.skill['hitpoints'] * 10
        if self.equipment['shield'] == '883':
            self.max_hp += 30
        self.mob_hp, self.hp = self.mob_max_hp, self.max_hp
        self.item_used, self.time_taken = {}, 0
        # ================================================================= #
        weapon_stat = dat.get_equipment_stat(self.equipment['weapon'])
        attack_stat = {'melee': cal_average(weapon_stat["atk_bonus"]["melee"]),
                       'ranged': weapon_stat["atk_bonus"]['ranged'],
                       'magic': weapon_stat["atk_bonus"]['magic']}
        if attack_stat['melee'] == attack_stat['ranged'] == attack_stat['magic']:
            self.attack_type = 'melee'
        else:
            self.attack_type = max(attack_stat.items(), key=operator.itemgetter(1))[0]

    def get_equipment_total_stat(self):
        for slot, item in self.equipment.items():
            try:
                stat = dat.get_equipment_stat(str(item))
            except IndexError:
                continue
            self.melee_strength_bonus += stat['str_bonus']['melee']
            self.ranged_strength_bonus += stat['str_bonus']['ranged']
            self.stab_bonus += stat['atk_bonus']['melee']['stab']
            self.slash_bonus += stat['atk_bonus']['melee']['slash']
            self.block_bonus += stat['atk_bonus']['melee']['block']
            self.melee_defence_bonus = stat['def_bonus']['melee']
            self.damage_reduction += stat['damage_reduction']
        self.melee_style_bonus = {'stab': self.stab_bonus, 'slash': self.slash_bonus, 'block': self.block_bonus}
        for skill, xp in self.skill_xp.items():
            if isinstance(xp, int):
                self.skill[skill] = get_skill_level(xp)

    def setup_melee(self, style):
        self.effective_melee_attack = self.skill["attack"] + 8  # + Attack style bonus (from agility apparently)
        self.effective_melee_defence = self.skill['defence'] + 8
        self.melee_evasion = self.effective_melee_defence * (self.melee_style_bonus[style] + 64)  # * Potion and prayer
        self.melee_accuracy = self.effective_melee_attack * (self.melee_style_bonus[style] + 64)  # * Potion and prayer
        self.melee_max_hit = \
            (22 + self.skill["strength"] + ((17 + self.skill["strength"]) / 64)
             * self.melee_strength_bonus)  # * Potion and prayer
        if self.melee_accuracy < self.mob_stat['evasion']['melee']:
            self.hit_chance = 0.5 * self.melee_accuracy / self.mob_stat['evasion']['melee']
        else:
            self.hit_chance = 1 - 0.5 * self.mob_stat['evasion']['melee'] / self.melee_accuracy
        if self.mob_stat['accuracy'] < self.melee_evasion:
            self.mob_hit_chance = 0.5 * self.mob_stat['accuracy'] / self.melee_evasion
        else:
            self.mob_hit_chance = 1 - 0.5 * self.melee_evasion / self.mob_stat['accuracy']
        if self.mob_attack_type == 'ranged':
            self.effective_damage_reduction = self.damage_reduction * 1.25
            self.melee_max_hit = self.melee_max_hit * 1.1
        elif self.mob_attack_type == 'magic':
            self.effective_damage_reduction = self.damage_reduction * 0.5
            self.melee_max_hit = self.melee_max_hit * 0.9
        self.max_hit = self.melee_max_hit
        self.accuracy_rating = self.melee_accuracy
        self.melee_style = style

    def image_gen_player(self):
        W, H = (700, 800)
        font_path = os.path.join(BASE[0], 'random.ttf')
        img = Image.new('RGBA', (W, H), (255, 249, 249, 250))
        d = ImageDraw.Draw(img)
        d.rectangle((0, 0, 700, 2), fill=(70, 195, 123))
        # ================================================================= #
        Health_bar = progressBar((210, 106, 92), (48, 199, 141), 0, 0, 600, 15, self.hp / self.max_hp)
        img.paste(Health_bar, (50, 17), Health_bar)
        msg = f"{self.hp}/{self.max_hp} HP"
        w, h = d.textsize(msg, ImageFont.truetype(font_path, 15))
        d.text(((W - w) / 2 + 10, 35), msg, fill="black", font=ImageFont.truetype(font_path, 10))
        # ================================================================= #
        im = round_rectangle((290, 550), 10, (219, 222, 225), '')
        img.paste(im, (50, 50), im)
        if self.tab == 'equipment':
            im = armour(self.uid, False).resize((250, 500), Image.ANTIALIAS)
            img.paste(im, (70, 110), im)
            d.text((160, 60), '装备:', fill="black", font=ImageFont.truetype(font_path, 30))
        # ================================================================= #
        im = round_rectangle((290, 550), 10, (219, 222, 225), '')
        img.paste(im, (360, 50), im)
        d.text((460, 60), '属性:', fill="black", font=ImageFont.truetype(font_path, 30))
        if self.attack_type == 'melee':
            temp = f'近战类型: {style_dict[self.melee_style]}\n'
        else:
            temp = ''
        msg = f'''伤害: {round(self.min_hit)}-{round(self.max_hit)}
命中几率: {round(self.hit_chance * 100)}%
命中评分: {self.accuracy_rating}
伤害减免: {round(self.damage_reduction * 100)}%
伤害类型: {attack_dict[self.attack_type]}
{temp}
近战闪避评分: {self.melee_evasion}
远程闪避评分: {self.ranged_evasion}
魔法闪避评分: {self.magic_evasion}

祝福点数: Place holder
启用祝福: Place holder'''
        d.text((380, 110), msg, fill="black", font=ImageFont.truetype(font_path, 15))
        return MessageSegment.image(util.pic2b64(img))

    def image_gen_mob(self):
        W, H = (700, 800)
        font_path = os.path.join(BASE[0], 'random.ttf')
        img = Image.new('RGBA', (W, H), (255, 249, 249, 250))
        d = ImageDraw.Draw(img)
        d.rectangle((0, 0, 700, 2), fill=(229, 103, 103))
        # ================================================================= #
        Health_bar = progressBar((210, 106, 92), (48, 199, 141), 0, 0, 600, 15, self.mob_hp / self.mob_max_hp)
        img.paste(Health_bar, (50, 17), Health_bar)
        msg = f"{self.hp}/{self.max_hp} HP"
        w, h = d.textsize(msg, ImageFont.truetype(font_path, 15))
        d.text(((W - w) / 2 + 10, 35), msg, fill="black", font=ImageFont.truetype(font_path, 10))
        return MessageSegment.image(util.pic2b64(img))


@reg_cmd("测试输出")
async def cmd_test(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    combat_dict[uid] = Combat_Handler(uid, str(args[0]))
    combat = combat_dict[uid]
    combat.setup_melee('stab')
    await bot.send(ev,
                   f'怪物名字:{combat.mob_name},命中几率:{round(combat.hit_chance * 100)}%,怪物命中几率:{round(combat.mob_hit_chance * 100)}%')
    await bot.send(ev, combat.image_gen_player())
    await bot.send(ev, combat.image_gen_mob())
