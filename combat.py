from hoshino import Service, util, priv
from hoshino.typing import MessageSegment, NoticeSession, CQEvent
import random
from .ma import *
from .lib import *

dat = dat(DATA_PATH)
a = {"str_bonus": {"melee": 3, "ranged": 0},
     "atk_bonus": {"melee": {"stab": 0, "slash": 0, "block": 0}, "ranged": -2, "magic": -6}, "magic_bonus": 0.0,
     "def_bonus": {"melee": 9, "ranged": 9, "magic": -1}, "damage_reduction": 0.0, "slayer_xp": 0.05,
     "level": {"def": 0, "rag": 0, "mag": 0}, "slot": "Helmet"}
b = {"combat_level": 23, "hp": 200, "attack_speed": "2.6", "max_hit": 42, "accuracy": 2146,
     "evasion": {"melee": 2436, "range": 2436, "magic": 960},
     "skill": {"atk": 20, "str": 20, "def": 20, "rag": 1, "mag": 1}}


class Combat_Handler:
    def __init__(self, uid, mob):
        self.uid = uid
        self.mob = mob
        self.mob_name = dat.get_monster_name(mob)
        self.mob_stat = dat.get_monster_stat(str(mob))
        self.equipment = json.loads(db.get_player_inv(uid)[2])
        self.skill_xp, self.skill = json.loads(db.get_player_skill(uid)[1]), {}
        self.combat_level = combat_level(uid)
        self.hit_chance, self.mob_hit_chance = 0, 0
        # ================================================================= #
        self.effective_melee_defence, self.effective_ranged_defence, self.effective_magic_defence = 0, 0, 0
        self.melee_evasion, self.ranged_evasion, self.magic_evasion = 0, 0, 0
        self.melee_defence_bonus, self.ranged_defence_bonus, self.magic_defence_bonus = 0, 0, 0
        # ================================================================= #
        self.effective_melee_attack, self.effective_ranged_attack, self.effective_magic_attack = 0, 0, 0
        self.melee_accuracy, self.ranged_accuracy, self.magic_accuracy = 0, 0, 0
        self.stab_bonus, self.slash_bonus, self.block_bonus, self.melee_style_bonus = 0, 0, 0, {}
        self.ranged_bonus, self.magic_bonus = 0, 0
        # ================================================================= #
        self.melee_max_hit, self.ranged_max_hit, self.magic_max_hit = 0, 0, 0
        self.melee_strength_bonus, self.ranged_strength_bonus = 0, 0
        # ================================================================= #
        self.get_equipment_total_stat()

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


@reg_cmd("测试输出")
async def cmd_test(bot: HoshinoBot, ev: CQEvent, args):
    combat = Combat_Handler(ev['user_id'], str(args[0]))
    combat.setup_melee('stab')
    await bot.send(ev, f'{combat.mob_name},{combat.hit_chance},{combat.mob_hit_chance}')
