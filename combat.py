from hoshino import Service, util, priv
from hoshino.typing import MessageSegment, NoticeSession, CQEvent
import random
from .ma import *
from .lib import *
import operator

BASE = os.path.split(os.path.realpath(__file__))
dat = dat(DATA_PATH)
style_dict = {'stab': '穿刺', 'slash': '斩击', 'block': '格挡', 'accurate': '精准', 'rapid': '速射', 'longranged': '远距离射击','magic attack':'进攻型魔法','defensive attack':'防御型魔法'}
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
arrow=['262','263','264','265','266','267','268','378','503','684','685','686','687','688','935']
spelllist=dat.get_all_spells()
player_bufflist={
    "max_hit_linearmodifier":0,"max_hit_multiplexmodifier":0.00,"min_hit_linearmodifier":0,"min_hit_multiplexmodifier":0.00,
    "hit_chance_linearmodifier":0,"hit_chance_multiplexmodifier":0.00,"mob_hit_chance_linearmodifier":0,"mob_hit_chance_multiplexmodifier":0.00,
    "damage_reduction_linearmodifier":0,"damage_reduction_multiplexmodifier":0.00,
    "melee_evasion_linearmodifier":0,"melee_evasion_multiplexmodifier":0.00,"ranged_evasion_linearmodifier":0,"ranged_evasion_multiplexmodifier":0,"magic_evasion_linearmodifier":0,"magic_evasion_multiplexmodifier":0.00,
    "melee_defence_linearmodifier":0,"melee_defence_multiplexmodifier":0.00,
    "melee_accuracy_linearmodifier":0,"melee_accuracy_multiplexmodifier":0.00,"ranged_accuracy_linearmodifier":0,"ranged_accuracy_multiplexmodifier":0.00,"magic_accuracy_linearmodifier":0,"magic_accuracy_multiplexmodifier":0.00,
    "stab_bonus_linearmodifier":0,
    "slash_bonus_linearmodifier":0,
    "block_bonus_linearmodifier":0,
    "melee_style_bonus_linearmodifier":0,
    "ranged_bonus_linearmodifier":0,
    "magic_bonus_linearmodifier":0,
    "melee_max_hit_linearmodifier":0,"melee_min_hit_linearmodifier":0,
    "ranged_max_hit_linearmodifier":0,"ranged_min_hit_linearmodifier":0,
    "magic_max_hit_linearmodifier":0,"magic_min_hit_linearmodifier":0,
    "attack_speed_linearmodifier":0,"attack_speed_multiplexmodifier":0.00,
    "rune_restore_chance":0.00,
    "arrow_restore_chance":0.00,
    "slayerxp_linearmodifier":0,"slayerxp_multiplexmodifier":0.00,
    "loot_bonus_linearmodifier":0,"loot_bonus_multiplexmodifier":0.00
}
monster_bufflist={
    "damage_reduction_linearmodifier":0,
    "attack_speed_linear_modifier":0,"attack_speed_multiplexmodifier":0.00
    }
monster_status={}

class Combat_Handler:
    def __init__(self, uid, mob):
        self.uid = uid
        self.mob = mob
        self.tab = 'equipment'
        self.inventory=json.loads(db.get_player_inv(uid)[1])
        self.effective_inventory={}
        for item, number in self.inventory.items():
            if number>0:
                self.effective_inventory[item]=number
        self.effective_inventory=json.dumps(self.effective_inventory,indent=4)
        # ================================================================= #
        self.mob_name = dat.get_monster_name(mob)
        self.mob_stat = dat.get_monster_stat(str(mob))
        self.mob_loot = json.dumps(dat.get_monster_loot(mob))
        mob_attack_stat = {'melee': self.mob_stat['skill']['atk'], 'ranged': self.mob_stat['skill']['rag'],
                           'magic': self.mob_stat['skill']['mag']}
        self.mob_attack_type = max(mob_attack_stat.items(), key=operator.itemgetter(1))[0]
        if self.mob in monster_dict:
            self.mob_location = monster_dict[self.mob]
        else:
            self.mob_location = ('combat', 'question', '')
        self.mob_damage_reduction, self.mob_attack_speed = 0, float(self.mob_stat['attack_speed'])
        # ================================================================= #
        self.equipment = json.loads(db.get_player_inv(uid)[2])
        self.portion=json.loads(db.get_player_inv(uid)[7])
        self.effective_potion={}
        self.prayer=json.loads(db.get_player_inv(uid)[8])
        self.effective_prayer={}
        self.skill_xp, self.skill = json.loads(db.get_player_skill(uid)[1]), {}
        self.combat_level, self.max_hit, self.min_hit, self.accuracy_rating, self.style = combat_level(uid), 0, 1, 0, '' #combat_lvl not style?
        self.hit_chance, self.mob_hit_chance, self.damage_reduction, self.effective_damage_reduction = 0, 0, 0, 0
        # ================================================================= #

        self.max_hit_linearmodifier, self.max_hit_multiplexmodifier=0,0.00
        self.min_hit_linearmodifier,self.min_hit_multiplexmodifier=0,0.00
        self.hit_chance_linearmodifier,self.hit_chance_multiplexmodifier=0,0.00
        self.mob_hit_chance_linearmodifier, self.mob_hit_chance_multiplexmodifier=0,0.00
        self.damage_reduction_linearmodifier, self.damage_reduction_multiplexmodifier=0,0.00
        self.effective_damage_reduction_linearmodifier, self.effective_damage_reduction_multiplexmodifier=0,0.00

        # ================================================================= #
        self.effective_melee_defence, self.effective_ranged_defence, self.effective_magic_defence = 0, 0, 0
        self.melee_evasion, self.ranged_evasion, self.magic_evasion = 0, 0, 0
        self.melee_defence_bonus, self.ranged_defence_bonus, self.magic_defence_bonus = 0, 0, 0
        # ================================================================= #

        self.effective_melee_defence_linearmodifier, self.effective_melee_defence_multiplexmodifier=0,0.00
        self.effective_ranged_defence_linearmodifier, self.effective_ranged_defence_multiplexmodifier=0,0.00
        self.effective_magic_defence_linearmodifier, self.effective_magic_defence_multiplexmodifier=0,0.00

        self.melee_evasion_linearmodifier,self.melee_evasion_multiplexmodifier=0,0.00
        self.ranged_evasion_linearmodifier,self.ranged_evasion_multiplexmodifier=0,0.00
        self.magic_evasion_linearmodifier,self.magic_evasion_multiplexmodifier=0,00

        self.melee_defence_bonus_linearmodifier,self.melee_defence_bonus_multiplexmodifier=0,0.00
        self.ranged_defence_bonus_linearmodifier, self.ranged_defence_bonus_multiplexmodifier=0,0.00
        self.magic_defence_bonus_linearmodifier, self.magic_defence_bonus_multiplexmodifier=0,0.00

        # ================================================================== #

        self.effective_melee_attack, self.effective_ranged_attack, self.effective_magic_attack = 0, 0, 0
        self.melee_accuracy, self.ranged_accuracy, self.magic_accuracy = 0, 0, 0
        self.stab_bonus, self.slash_bonus, self.block_bonus, self.melee_style_bonus = 0, 0, 0, {}
        self.melee_style, self.ranged_style = 'stab', 'accurate'
        self.ranged_bonus, self.magic_bonus = 0, 0
        # ================================================================= #

        self.effective_melee_attack_linearmodifier,self.effective_melee_attack_multiplexmodifier=0,0.00
        self.effective_ranged_attack_linearmodifier,self.effective_ranged_attack_multiplexmodifier=0,0.00
        self.effective_magic_attack_linearmodifier,self.effective_magic_attack_multiplexmodifier=0,0.00

        self.melee_accuracy_linearmodifier, self.melee_accuracy_multiplexmodifier=0,0.00
        self.ranged_accuracy_linearmodifier, self.ranged_accuracy_multiplexmodifier=0,0.00
        self.magic_accuracy_linearmodifier, self.magic_accuracy_multiplexmodifier=0,0.00

        self.stab_bonus_linearmodifier, self.stab_bonus_multiplexmodifier=0,0.00
        self.slash_bonus_linearmodifier, self.slash_bonus_multiplexmodifier=0,0.00
        self.block_bonus_linearmodifier, self.bolck_bonus_multiplexmodifier=0,0.00
        self.melee_style_bonus_linearmodifier, self.melee_style_bonus_multiplexmodifier=0,0.00

        self.ranged_bonus_linearmodifier, self.ranged_bonus_multiplexmodifier=0,0.00
        self.magic_bonus_linearmodifier, self.magic_bonus_multiplexmodifier=0,0.00

        # ================================================================= #
        self.melee_max_hit, self.ranged_max_hit, self.magic_max_hit = 0, 0, 0
        self.melee_strength_bonus, self.ranged_strength_bonus = 0, 0
        self.effective_ranged_strength = 0
        # ================================================================= #

        self.melee_max_hit_linearmodifier, self.melee_max_hit_multiplexmodifier=0,0.00
        self.melee_min_hit_linearmodifier, self.melee_min_hit_multiplexmodifier=0,0.00
        self.ranged_max_hit_linearmodifier, self.ranged_max_hit_multiplexmodifier=0,0.00
        self.ranged_min_hit_linearmodifier, self.ranged_min_hit_multiplexmodifier=0,0.00
        self.magic_max_hit_linearmodifier, self.magic_max_hit_multiplexmodifier=0,0.00
        self.magic_min_hit_linearmodifier, self.magic_min_hit_multiplexmodifier=0,0.00

        self.melee_strength_bonus_linearmodifier, self.melee_strength_bonus_multiplexmodifier=0,0.00
        self.ranged_strength_bonus_linearmodifier, self.ranged_strength_bonus_multiplexmodifier=0,0.00
        self.effective_ranged_strength_linearmodifier, self.effective_ranged_strength_multiplexmodifier=0,0.00

        # ================================================================= #

        self.attack_speed_linear_modifier=0.0

        self.rune_reservation=0
        self.rune_restore_chance=0.00
        self.arrow_reservation=0
        self.arrow_restore_chance=0.00

        self.xp_linearmodifier,self.xp_multiplexmodifier=0,0.00
        self.slayerxp_linearmodifier,self.slayerxp_multiplexmodifier=0,0.00
        self.xp_pool={
            "hitpoints":0,
            "attack":0,
            "strength":0,
            "defence":0,
            "magic":0,
            "ranged":0,
            "prayer":0
        }
        self.item_looted={}

        self.loot_bonus_linearmodifier, self.loot_bonus_multiplexmodifier=0,0.00

        self.ranged_ammo='262'
        self.spellid='0'

        # ================================================================= #
        if self.skill_xp['hitpoints'] < 1155:
            db.set_combat_xp(uid, 'hitpoints', 1155)
        self.get_equipment_total_stat()
        # ================================================================= #
        self.mob_max_hp, self.max_hp = self.mob_stat['hp'], self.skill['hitpoints'] * 10
        if self.equipment['shield'] == '883':
            self.max_hp += 30
        self.mob_hp, self.hp = self.mob_max_hp, self.max_hp
        # ================================================================= #
        self.item_used, self.time_taken, self.time_since_last_mob_attack = {}, 0, 0.0
        # ================================================================= #
        try:
            weapon_stat = dat.get_equipment_stat(self.equipment['weapon'])
            self.attack_type = weapon_stat['type'].strip().lower()
            self.attack_speed = weapon_stat['attack_speed'] / 1000
        except Exception:
            self.attack_type = 'melee'
            self.attack_speed = 2.4
        # ================================================================ #
        self.setup_melee()
        self.setup_ranged()
        self.setup_magic()
        # ================================================================ #

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
            self.ranged_bonus += stat['atk_bonus']['ranged']
            self.magic_bonus += stat['atk_bonus']['magic']
            self.melee_defence_bonus += stat['def_bonus']['melee']
            self.ranged_defence_bonus += stat['def_bonus']['ranged']
            self.magic_defence_bonus += stat['def_bonus']['magic']
            self.damage_reduction += stat['damage_reduction']
            self.melee_style_bonus = {
            'stab': self.stab_bonus, 
            'slash': self.slash_bonus, 
            'block': self.block_bonus
            }

        for skill, xp in self.skill_xp.items():
            if isinstance(xp, int):
                self.skill[skill] = get_skill_level(xp)

    def get_player_potion(self):
        for portion, charge in self.portion.items():
            if(charge>0):
                self.effective_potion[portion]=charge
        self.effective_potion=json.dumps(self.effective_potion, indent=4)

    def get_player_prayer(self):
        for prayer, charge in self.prayer.items():
            if(charge>0):
                self.effective_prayer[prayer]=charge
        self.effective_prayer=json.dumps(self.effective_prayer,indent=4)

    def setup_potion(self):
        for potion,charge in self.effective_potion.items():
            if(charge>0):
                charge=charge-1
                for entry, number in dat.get_potion_buff(potion).items():
                    player_bufflist[entry]+=number
            else:
                continue

    def setup_others(self):
        self.effective_damage_reduction=self.damage_reduction+player_bufflist["damage_reduction_linearmodifier"]
        self.mob_damage_reduction=monster_bufflist["damage_reduction_linearmodifier"]
        self.effective_attack_speed=(self.attack_speed+player_bufflist["attack_speed_linearmodifier"])*(1-player_bufflist["attack_speed_multiplexmodifier"])
        self.mob_effective_attack_speed=(self.mob_attack_speed+monster_bufflist["attack_speed_linear_modifier"])*(1-monster_bufflist["attack_speed_multiplexmodifier"])
        
    def setup_melee(self):
        
        #serve agility

        if(self.style=='stab'):attack_style_bonus=player_bufflist['stab_bonus_linearmodifier']
        elif(self.style=='slash'):attack_style_bonus=player_bufflist['slash_bonus_linearmodifier']
        else:attack_style_bonus=player_bufflist['block_bonus_linearmodifier']

        self.effective_melee_attack = self.skill["attack"] + 8 + attack_style_bonus 

        self.effective_melee_defence = self.skill['defence'] + 8
        self.melee_evasion = self.effective_melee_defence * (self.melee_defence_bonus + 64 )*(1+player_bufflist['melee_defence_linearmodifier']/100)*(1+player_bufflist["melee_defence_multiplexmodifier"])
        self.melee_accuracy = self.effective_melee_attack * (   #melee style bonus also related to atk styles(from corresponding bonus from equipments)
                self.melee_style_bonus[self.melee_style] + 64 )*(1+ player_bufflist["melee_accuracy_linearmodifier"]/100) * (1+player_bufflist["melee_accuracy_multiplexmodifier"])
        self.melee_max_hit = \
            (22 + self.skill["strength"] + ((17 + self.skill["strength"]) / 64)
             * self.melee_strength_bonus)*(1+player_bufflist["melee_max_hit_linearmodifier"]/100)  # * Potion and prayer
        if self.attack_type == 'melee':
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
            self.style = self.melee_style

    def setup_ranged(self):
        #serve agility
        self.ranged_bonus+=dat.get_equipment_stat(str(self.ranged_ammo))
        self.effective_ranged_attack = self.skill["ranged"] + 8 + player_bufflist['ranged_bonus_linearmodifier'] 
        self.effective_ranged_defence = self.skill['defence'] + 9
        if self.ranged_style == 'accurate':
            bonus = 4
        else:
            if self.ranged_style=='rapid':
                self.attack_speed-=0.4
            bonus = 1
        self.effective_ranged_strength = self.skill["ranged"] + bonus
        self.ranged_evasion = self.effective_ranged_defence * (self.ranged_defence_bonus + 64) *(1+player_bufflist["ranged_evasion_linearmodifier"]/100)
        self.ranged_accuracy = self.effective_ranged_attack * (self.ranged_bonus + 64) *(1+player_bufflist["ranged_accuracy_linearmodifier"]/100)
        self.ranged_max_hit = \
            10 * \
            (1.3 + self.effective_ranged_strength / 10 + self.ranged_bonus / 80
             + self.effective_ranged_strength * self.ranged_bonus / 640)*(1+player_bufflist["ranged_max_hit_linearmodifier"]/100)
        if self.attack_type == 'ranged':
            if self.ranged_accuracy < self.mob_stat['evasion']['range']:
                self.hit_chance = 0.5 * self.ranged_accuracy / self.mob_stat['evasion']['range']
            else:
                self.hit_chance = 1 - 0.5 * self.mob_stat['evasion']['range'] / self.ranged_accuracy
            if self.mob_stat['accuracy'] < self.ranged_evasion:
                self.mob_hit_chance = 0.5 * self.mob_stat['accuracy'] / self.ranged_evasion
            else:
                self.mob_hit_chance = 1 - 0.5 * self.ranged_evasion / self.mob_stat['accuracy']
            if self.mob_attack_type == 'magic':
                self.effective_damage_reduction = self.damage_reduction * 1.25
                self.ranged_max_hit = self.ranged_max_hit * 1.1
            elif self.mob_attack_type == 'melee':
                self.effective_damage_reduction = self.damage_reduction * 0.5
                self.ranged_max_hit = self.ranged_max_hit * 0.9
            self.max_hit = self.ranged_max_hit
            self.accuracy_rating = self.ranged_accuracy
            self.style = self.ranged_style

    def setup_magic(self):
        #serve agility
        self.effective_magic_attack = self.skill["magic"] + 8 +player_bufflist["magic_bonus_linearmodifier"] 
        self.effective_magic_defence = self.skill['defence'] * 0.3 + self.skill['magic'] * 0.7 + 9
        spell_hit = dat.get_spell_dmg(self.spellid) 
        self.magic_evasion = self.effective_magic_defence * (self.magic_defence_bonus + 64) *(1+player_bufflist["magic_evasion_linearmodifier"]/100)
        self.magic_accuracy = self.effective_magic_attack * (self.magic_bonus + 64) *(1+player_bufflist["magic_accuracy_linearmodifier"]/100)
        self.magic_max_hit = spell_hit * (1 + (self.skill['magic'] + 1) / 200 *
                                          (1 + self.magic_bonus / 100)) *(1+player_bufflist["magic_max_hit_linearmodifier"]/100)
        if self.attack_type == 'magic':
            if self.magic_accuracy < self.mob_stat['evasion']['magic']:
                self.hit_chance = 0.5 * self.magic_accuracy / self.mob_stat['evasion']['magic']
            else:
                self.hit_chance = 1 - 0.5 * self.mob_stat['evasion']['magic'] / self.magic_accuracy
            if self.mob_stat['accuracy'] < self.magic_evasion:
                self.mob_hit_chance = 0.5 * self.mob_stat['accuracy'] / self.magic_evasion
            else:
                self.mob_hit_chance = 1 - 0.5 * self.magic_evasion / self.mob_stat['accuracy']
            if self.mob_attack_type == 'melee':
                self.effective_damage_reduction = self.damage_reduction * 1.25
                self.magic_max_hit = self.magic_max_hit * 1.1
            elif self.mob_attack_type == 'ranged':
                self.effective_damage_reduction = self.damage_reduction * 0.5
                self.magic_max_hit = self.magic_max_hit * 0.9
            self.max_hit = self.magic_max_hit
            self.min_hit = 1 + player_bufflist["magic_min_hit_linearmodifier"]
            self.accuracy_rating = self.magic_accuracy
            self.style = '(WIP)'

    def use_item(itemid,num=1):
        effect=dat.get_item_effect(itemid)
        # caution: external json codes
        return

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
        temp = ''
        if self.attack_type == 'melee':
            temp = f'近战类型: {style_dict[self.melee_style]}\n'
        elif self.attack_type == 'ranged':
            temp = f'远程类型: {style_dict[self.ranged_style]}\n'
        msg = f'''伤害: {round(self.min_hit)}-{round(self.max_hit)}
攻速: {self.attack_speed}s
命中几率: {round(self.hit_chance * 100)}%
命中评分: {self.accuracy_rating}
伤害减免: {round(self.damage_reduction * 100)}%
伤害类型: {attack_dict[self.attack_type]}
{temp}
近战闪避评分: {round(self.melee_evasion)}
远程闪避评分: {round(self.ranged_evasion)}
魔法闪避评分: {round(self.magic_evasion)}

祝福点数: Place holder
启用祝福: Place holder'''
        d.text((380, 110), msg, fill="black", font=ImageFont.truetype(font_path, 15))
        # ================================================================= #
        attack_speed_bar = progressBar((219, 222, 225), (92, 172, 229), 0, 0, 600, 15, 0)
        img.paste(attack_speed_bar, (50, 757), attack_speed_bar)
        msg = f"0.0/{self.attack_speed} s"
        w, h = d.textsize(msg, ImageFont.truetype(font_path, 15))
        d.text(((W - w) / 2 + 10, 775), msg, fill="black", font=ImageFont.truetype(font_path, 10))
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
        msg = f"{self.mob_hp}/{self.mob_max_hp} HP"
        w, h = d.textsize(msg, ImageFont.truetype(font_path, 15))
        d.text(((W - w) / 2 + 10, 35), msg, fill="black", font=ImageFont.truetype(font_path, 10))
        # ================================================================= #
        im = round_rectangle((600, 390), 10, (219, 222, 225), '')
        img.paste(im, (50, 50), im)
        msg_list = [(f'icons/{self.mob_location[0]}/{self.mob_location[1]}.png', self.mob_location[2]),
                    ('icons/combat/combat.png', self.mob_stat['combat_level']),
                    ('icons/skill/atta.png', self.mob_stat['skill']['atk']),
                    ('icons/skill/stre.png', self.mob_stat['skill']['str']),
                    ('icons/skill/defe.png', self.mob_stat['skill']['def']),
                    ('icons/skill/rang.png', self.mob_stat['skill']['rag']),
                    ('icons/skill/magi.png', self.mob_stat['skill']['mag'])]
        temp = 70
        for path, value in msg_list:
            im = Image.open(os.path.join(BASE[0], path)).resize((40, 40), Image.ANTIALIAS).convert("RGBA")
            img.paste(im, (70, temp), im)
            d.text((120, temp + 20), str(value), fill="black", font=ImageFont.truetype(font_path, 20))
            temp += 50
        # ================================================================= #
        im = Image.open(os.path.join(BASE[0], f'icons/monster/{self.mob}.png'))
        im.thumbnail((290, 290), Image.ANTIALIAS)
        img.paste(im, (290, 130), im)
        d.text((260, 70), str(self.mob_name), fill="black", font=ImageFont.truetype(font_path, 50))
        # ================================================================= #
        im = round_rectangle((290, 250), 10, (219, 222, 225), '')
        img.paste(im, (50, 450), im)
        img.paste(im, (360, 450), im)
        d.text((130, 460), '攻击属性:', fill="black", font=ImageFont.truetype(font_path, 30))
        d.text((440, 460), '防御属性:', fill="black", font=ImageFont.truetype(font_path, 30))
        offensive_msg = f'''攻击类型:{attack_dict[self.mob_attack_type]}
伤害: 1 - {self.mob_stat['max_hit']}
攻速: {self.mob_attack_speed}s
命中几率: {round(self.mob_hit_chance * 100)}%
命中评分: {self.mob_stat["accuracy"]}'''
        defensive_msg = f'''近战闪避评分: {self.mob_stat['evasion']['melee']}
远程闪避评分: {self.mob_stat['evasion']['range']}
魔法闪避评分: {self.mob_stat['evasion']['magic']}
伤害减免: {round(self.mob_damage_reduction * 100)}%'''
        d.text((70, 500), offensive_msg, fill="black", font=ImageFont.truetype(font_path, 15))
        d.text((380, 500), defensive_msg, fill="black", font=ImageFont.truetype(font_path, 15))
        # ================================================================= #
        attack_speed_bar = progressBar((219, 222, 225), (92, 172, 229), 0, 0, 600, 15,
                                       self.time_since_last_mob_attack / self.mob_attack_speed)
        img.paste(attack_speed_bar, (50, 757), attack_speed_bar)
        msg = f"{self.time_since_last_mob_attack}/{self.mob_attack_speed} s"
        w, h = d.textsize(msg, ImageFont.truetype(font_path, 15))
        d.text(((W - w) / 2 + 10, 775), msg, fill="black", font=ImageFont.truetype(font_path, 10))
        return MessageSegment.image(util.pic2b64(img))

    def mob_normal_attack(self):
        attack_speed = self.mob_effective_attack_speed
        attack_count = 0
        time = self.effective_attack_speed
        while time >= (attack_speed - self.time_since_last_mob_attack):
            time += -attack_speed + self.time_since_last_mob_attack
            self.time_since_last_mob_attack = 0
            attack_count += 1
        self.time_since_last_mob_attack = round(time, 1)
        if not attack_count:
            return f'{self.mob_name}并没有对你发动攻击', False
        total_dmg = 0
        for each in range(attack_count):
            if decision(self.mob_hit_chance):
                damage = random.randint(1, round(self.mob_stat['max_hit']))
                damage = round(damage * (1 - self.effective_damage_reduction))
                if self.hp > damage:
                    self.hp += -damage
                    total_dmg += damage
                else:
                    self.hp = 0
                    return f'你被{self.mob_name}以{damage}伤害杀死了', True
        if not total_dmg:
            return f'{self.mob_name}对你造成了{attack_count}次攻击，但一次都没有命中。', False
        return f'{self.mob_name}对你造成了{attack_count}次总共{total_dmg}伤害。', False

    def player_normal_attack(self):
        self.setup_potion()
        self.setup_others()
        damage = random.randint(round(self.min_hit+player_bufflist["min_hit_linearmodifier"]+player_bufflist["melee_min_hit_linearmodifier"]), round(self.max_hit+player_bufflist["max_hit_linearmodifier"]))
        damage = round(damage * (1 - self.mob_damage_reduction))
        self.time_taken += self.effective_attack_speed
        msg, is_dead = self.mob_normal_attack()
        if is_dead:
            return msg, True
        if decision(self.hit_chance):
            if self.mob_hp > damage:
                self.mob_hp += -damage
                return f'{msg}\n你对{self.mob_name}发动了{style_dict[self.style]}{attack_dict[self.attack_type]}攻击，并造成了{damage}点伤害。', False
            else:
                self.mob_hp = 0
                return f'{msg}\n你对{self.mob_name}发动了{style_dict[self.style]}{attack_dict[self.attack_type]}攻击，并造成了{damage}点的最后一击。', True
        else:
            return f'{msg}\n你对{self.mob_name}发动了{style_dict[self.style]}{attack_dict[self.attack_type]}攻击，但没有击中。', False

    def player_ranged_attack(self):
        self.setup_potion()
        self.setup_others()
        damage = random.randint(round(self.min_hit+player_bufflist["min_hit_linearmodifier"]+player_bufflist["ranged_min_hit_linearmodifier"]), round(self.max_hit+player_bufflist["max_hit_linearmodifier"]))
        damage = round(damage * (1 - self.mob_damage_reduction))
        self.time_taken += self.effective_attack_speed
        msg, is_dead = self.mob_normal_attack()
        if is_dead:
            return msg, True
        if decision(self.hit_chance):
            if self.mob_hp > damage:
                self.mob_hp += -damage
                self.calculate_experience(self.attack_type,self.style,damage)
                return f'{msg}\n你对{self.mob_name}发动了{style_dict[self.style]}{attack_dict[self.attack_type]}攻击，并造成了{damage}点伤害。', False
            else:
                self.calculate_experience(self.attack_type,self.style,damage-self.mob_hp)
                self.mob_hp = 0
                return f'{msg}\n你对{self.mob_name}发动了{style_dict[self.style]}{attack_dict[self.attack_type]}攻击，并造成了{damage}点的最后一击。', True
        else:
            return f'{msg}\n你对{self.mob_name}发动了{style_dict[self.style]}{attack_dict[self.attack_type]}攻击，但没有击中。', False

    def calculate_experience(self,atk_mode,atk_style,dmg_dealt):
        if atk_mode=='melee':
            if atk_style=='stab':
                self.xp_pool['attack']+=dmg_dealt*0.4
            elif atk_style=='slash':
                self.xp_pool['strength']+=dmg_dealt*0.4
            else: 
                self.xp_pool['defence']+=dmg_dealt*0.4
        elif atk_mode=='ranged':
            if atk_style=='longranged':
                self.xp_pool['ranged']+=dmg_dealt*0.2
                self.xp_pool['defence']+=dmg_dealt*0.2
            else:
                self.xp_pool['ranged']+=dmg_dealt*0.4
        else:
            if atk_style=='magic attack':
                self.xp_pool['magic']+=dmg_dealt*0.4
            else:
                self.xp_pool['magic']+=dmg_dealt*0.2
                self.xp_pool['defence']+=dmg_dealt*0.2
    
    def warp_up(self):                    #update prayer(might not here)
        db.update_player_potion(self.uid,self.effective_potion)
        msg='战斗结束：\n'
        msg+='你获得了:\n'
        for skill,amount in self.xp_pool.items():
            db.add_combat_xp(self.uid,skill,amount)
            msg+=f'{amount} exp in {skill}\n'
        
        msg+='你消耗了:\n'
        for item, amount in self.item_used.items():
            msg+=f'{item} {amount};'
        msg+='\n'
        self.loot_item()
        msg+='你捡到了：\n'
        for item,amount in self.item_looted.items():
            msg+=f'{amount} {item};'
            self.effective_inventory[item]+=amount
        db.update_player_items(self.uid,self.effective_inventory)


    def loot_item(self):
        bonus=self.loot_bonus_multiplexmodifier
        for item in self.mob_loot.items():
            if(item=='coin'):
                self.item_looted['coin']+=random.randint(self.mob_loot['coin']['from'],self.mob_loot['coin']['to'])
            if(random.random()*(1+bonus)<=self.mob_loot[item]['chance']):
                self.item_looted[item]+=random.randint(self.mob_loot[item]['quantity']['from'],self.mob_loot[item]['quantity']['to'])
        self.item_looted=json.dumps(self.item_looted,indent=4)

#ammo and rune reservation not implemented yet


@reg_cmd("开始战斗")
async def cmd_test(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    combat_dict[uid] = Combat_Handler(uid, str(args[0]))
    combat = combat_dict[uid]
    combat.get_player_potion()
    combat.get_player_prayer()
    if combat.attack_type == 'melee':
        style = "(穿刺,斩击,格挡)"
    elif combat.attack_type == 'ranged':
        style = "(精准,速射,远距离射击)"
    else:
        style = '(魔法ID)'
    cmd_list = [f'{attack_dict[combat.attack_type]}攻击', f'转换攻击方式 {style}', '治疗', '装备', '祝福 (WIP)', '魔法 (WIP)', '逃跑']
    msg = '\n可用指令:'
    for each in cmd_list:
        msg += f'\n?{each}'
    await bot.send(ev, str(combat.image_gen_player()) + str(combat.image_gen_mob()) + '\n' + msg)


@reg_cmd('近战攻击')
async def cmd_attack_melee(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    if uid not in combat_dict:
        await bot.send(ev, '你并没有在战斗之中')
        return
    combat = combat_dict[uid]
    combat.setup_melee()
    msg, is_done = combat.player_normal_attack()
    if is_done:
        combat.warp_up()
        del combat_dict[uid]
    await bot.send(ev, str(combat.image_gen_player()) + str(combat.image_gen_mob()) + '\n' + msg)


@reg_cmd('远程攻击')
async def cmd_attack_ranged(bot: HoshinoBot, ev: CQEvent,args):
    uid = ev['user_id']
    if uid not in combat_dict:
        await bot.send(ev,'你并没有在战斗之中')
        return
    combat = combat_dict[uid]
    if combat.effective_inventory[combat.ranged_ammo]==1:
        await bot.send(ev,'warning，所选的箭即将用尽')
    elif combat.effective_inventory[combat.ranged_ammo]==0:
        await bot.send(ev,'箭已用尽，请换箭')
        return
    combat.effective_inventory[combat.ranged_ammo]-=1
    combat.item_used[combat.ranged_ammo]+=1
    combat.setup_ranged()
    msg, is_done= combat.player_ranged_attack()
    if is_done:
        combat.warp_up()
        del combat_dict[uid]
    await bot.send(ev, str(combat.image_gen_player()) + str(combat.image_gen_mob()) + '\n' + msg)

@sv.on_prefix('换箭')
async def cmd_switch_ranged_ammo(bot: HoshinoBot, ev: CQEvent,args):
    uid = ev['user_id']
    if uid not in combat_dict:
        await bot.send(ev,'你并没有在战斗之中')
        return
    combat = combat_dict[uid]
    ammo=ev.message.extract_plain_text()
    if ammo not in arrow:
        await bot.send(ev,'denied,不是可以射出去的东西')
    if combat.effective_inventory[ammo]>0:
        combat.ranged_ammo=ammo
        await bot.send(ev,'切换成功')
        return
    else:
        await bot.send(ev,'对应物品不足，切换失败')

@reg_cmd('魔法攻击')
async def cmd_attack_magic(bot: HoshinoBot,ev:CQEvent,args):
    uid = ev['user_id']
    if uid not in combat_dict:
        await bot.send(ev,'你并没有在战斗之中')
        return
    combat = combat_dict[uid]
    spellcost=dat.get_spell_cost(combat.spellid)
    for item,amount in spellcost.items():
        if combat.effective_inventory[item]<amount:
            await bot.send(ev,'魔法消耗品不足，请换一种魔法')
            return
    for item,amount in spellcost.items():
        combat.effective_inventory[item]-=amount
        combat.item_used[item]+=amount
    combat.setup_magic()
    msg, is_done= combat.player_ranged_attack()
    if is_done:
        combat.warp_up()
        del combat_dict[uid]
    await bot.send(ev, str(combat.image_gen_player()) + str(combat.image_gen_mob()) + '\n' + msg)    
        
@sv.on_prefix('切换魔法')
async def cmd_switch_magic_spell(bot: HoshinoBot, ev: CQEvent,args):
    uid = ev['user_id']
    if uid not in combat_dict:
        await bot.send(ev,'你并没有在战斗之中')
        return
    combat = combat_dict[uid]
    spell=ev.message.extract_plain_text()
    if spell not in spelllist:
        await bot.send(ev,'这不是个可施放的法术')
        return
    for item, num in combat.get_spell_cost(spell):
        if item not in combat.effective_inventory:
            await bot.send(ev,'denied,消耗品不足')
            return
        if num>combat.effective_inventory[item]:
            await bot.send(ev,'denied,消耗品不足')
            return
    combat.spellid=spell
    await bot.send(ev,'切换成功')

@sv.on_prefix('查看物品')
async def cmd_item_check(bot: HoshinoBot, ev:CQEvent,args):
    uid = ev['user_id']
    if uid not in combat_dict:
        await bot.send(ev,'你并没有在战斗之中')
        return
    combat = combat_dict[uid]
    itemid=ev.message.extract_plain_text()
    itemnum=combat.effective_inventory[itemid]
    await bot.send(ev,f'所选物品的存量为{itemnum}')    

@sv.on_prefix('使用物品')
async def cmd_item_use(bot: HoshinoBot, ev:CQEvent, args):
    uid = ev['user_id']
    if uid not in combat_dict:
        await bot.send(ev,'你并没有在战斗之中')
        return
    combat=combat_dict[uid]
    itemid=ev.message.extract_plain_text()
    if combat.effective_inventory[itemid]>0:
        combat.effective_inventory[itemid]-=1
        combat.item_used[itemid]+=1
        combat.use_item(itemid) #not finished
        await bot.send(ev,'使用成功')
    else:
        await bot.send(ev,'物品不足')
        return

@sv.on_prefix('转换攻击方式')
async def cmd_switch_atk_style(bot: HoshinoBot, ev:CQEvent,args):
    uid = ev['user_id']
    if uid not in combat_dict:
        await bot.send(ev,'你并没有在战斗之中')
        return
    combat=combat_dict[uid]
    style=style_dict[ev.message.extract_plain_text()]
    combat.style=style
    await bot.send(ev,'切换成功')

# log:
#
# UNstable! all the new codes are not tested yet!
# a more muture combat system
# implemented most features: different atk style, using comsumables(include insufficient detection), xp and loot, 
#                            generalized buffing (potion and prayer and others), used item count, update battle result
# reserved most variables to be used in the future 
# added necessary entries in lib.py
#
# to do:
# implement ammo and rune reservation function
# use item in combat(how to run json codes)
# implement prayer in use(the count down part)
# loot function outside combat(open chests)
# more flexible player commands("use item{id} {target}")
# agility
# other comments in file
# preview battle status(recalculate with buff and show player, not in combat)
# might split into different files( )