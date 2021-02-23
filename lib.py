import datetime
from typing import List, Callable, Dict
import os
import sqlite3
import os
import ujson as json
from .ma import *

cmds: Dict[str, Callable] = {}
RPG_DB_PATH = os.path.expanduser("~/.hoshino/rpg.db")
DATA_PATH = os.path.dirname(os.path.realpath(__file__))

try:
    from hoshino.typing import *
    from hoshino import Service

    sv = Service('random_idle', bundle='pcr娱乐')


    @sv.on_prefix('?')  # 指令执行
    async def exec_cmd(bot: HoshinoBot, ev: CQEvent):
        # if ev['message_type'] != 'group':
        #     await bot.send(ev, '请在QQ群中使用本插件')
        #     return
        plain_cmd = ev.message.extract_plain_text()
        cmd, *args = plain_cmd.split(' ')  # 分割指令与参数
        if cmd in cmds:
            func = cmds[cmd]
            for each in args:
                if each.isnumeric():
                    args[args.index(each)] = int(each)
            await func(bot, ev, args)
        elif cmd != '':
            sv.logger.info('指令列表' + str(cmds))
            await bot.send(ev, '未知指令\n输入?说明或?help查看说明')


    def reg_cmd(names) -> Callable:
        if type(names) == str:
            names = [names, ]
        elif not type(names) == list:
            err_str = '指令名必须是字符串(str)或列表(list), 但却是' + str(type(names))
            raise ValueError(err_str)

        def reg(func) -> Callable:
            for name in names:
                if name in cmds:
                    sv.logger.warning('命名冲突')
                else:
                    cmds[name] = func
                    sv.logger.info(f'[RPG]指令{name}已注册')
            return func

        return reg
except:
    pass


class RecordDAO:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._create_table()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        with self.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS skill"
                "(uid INT NOT NULL,skill json NOT NULL ,PRIMARY KEY (uid))"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS inventory"
                "(uid INT NOT NULL,inventory json NOT NULL,equipment json NOT NULL , action json NOT NULL ,upgrade json NOT NULL ,PRIMARY KEY (uid))"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS stat"
                "(uid INT NOT NULL,i_slot INT NOT NULL,coin INT NOT NULL , name TEXT NOT NULL ,PRIMARY KEY (uid))"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS mastery"
                "(uid INT NOT NULL, woodcutting json NOT NULL, fishing json NOT NULL, firemaking json NOT NULL, cooking json NOT NULL, mining json NOT NULL, smithing json NOT NULL, thieving json NOT NULL, farming json NOT NULL, fletching json NOT NULL, crafting json NOT NULL, runecrafting json NOT NULL, herblore json NOT NULL, PRIMARY KEY (uid))"
            )

    def get_player_stat(self, uid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT * FROM stat WHERE uid=? ", (uid,)
            ).fetchall()
        return r[0]

    def get_player_skill(self, uid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT * FROM skill WHERE uid=? ", (uid,)
            ).fetchall()
        return r[0]

    def get_player_inv(self, uid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT * FROM inventory WHERE uid=? ", (uid,)
            ).fetchall()
        return r[0]

    def is_player_exist(self, uid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT * FROM inventory WHERE uid=? ", (uid,)
            ).fetchall()
        return r

    def update_player_inv(self, uid, inv):
        inv = json.loads(inv)
        inv2 = {}
        for item, value in inv.items():
            if value != 0:
                inv2[item] = value
        inv2 = json.dumps(inv2, indent=4)
        with self.connect() as conn:
            r = conn.execute(
                "UPDATE inventory SET inventory=? WHERE uid=?", (inv2, uid,)
            ).fetchall()
        return r

    def update_player_stat(self, uid, col, value):
        with self.connect() as conn:
            r = conn.execute(
                "UPDATE stat SET %s=? WHERE uid=?" % col, (value, uid)
            ).fetchall()
        return r

    def update_player_upgrade(self, uid, upgrade):
        with self.connect() as conn:
            r = conn.execute(
                "UPDATE inventory SET upgrade=? WHERE uid=?", (upgrade, uid,)
            ).fetchall()
        return r

    def update_player_equipment(self, uid, equipment):
        with self.connect() as conn:
            r = conn.execute(
                "UPDATE inventory SET equipment=? WHERE uid=?", (equipment, uid,)
            ).fetchall()
        return r

    def update_player_charge(self, uid, charge):
        with self.connect() as conn:
            r = conn.execute(
                "UPDATE inventory SET charge=? WHERE uid=?", (charge, uid,)
            ).fetchall()
        return r

    def get_player_action(self, uid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT action FROM inventory WHERE uid=? ", (uid,)
            ).fetchall()
        return json.loads(r[0][0])

    def add_skill_xp(self, uid, skill, amount):
        with self.connect() as conn:
            r = conn.execute(
                "select skill from skill WHERE uid = ?", (uid,)
            ).fetchall()[0][0]
        r = json.loads(r)
        r[skill][1] += amount
        r = json.dumps(r, indent=4)
        with self.connect() as conn:
            r = conn.execute(
                "UPDATE skill SET skill=? WHERE uid = ?", (r, uid,)
            )

    def add_mastery_pool(self, uid, skill, amount):
        with self.connect() as conn:
            r = conn.execute(
                "select skill from skill WHERE uid = ?", (uid,)
            ).fetchall()[0][0]
        r = json.loads(r)
        r[skill][0] += amount
        r = json.dumps(r, indent=4)
        with self.connect() as conn:
            r = conn.execute(
                "UPDATE skill SET skill=? WHERE uid = ?", (r, uid,)
            )

    def add_master_xp(self, uid, skill, item, amount):
        with self.connect() as conn:
            r = conn.execute(
                "select %s from mastery WHERE uid = ?" % skill, (uid,)
            ).fetchall()[0][0]
        r = json.loads(r)
        r[str(item)] += amount
        r = json.dumps(r, indent=4)
        with self.connect() as conn:
            r = conn.execute(
                "UPDATE mastery SET %s=? WHERE uid = ?" % skill, (r, uid,)
            )

    def update_player_action(self, action, uid):
        now = datetime.datetime.timestamp(datetime.datetime.now())
        act = self.get_player_action(uid)
        act["start_time"] = now
        if not action:
            act['start_time'] = None
        act['action'] = action
        act = json.dumps(act, indent=4)
        with self.connect() as conn:
            r = conn.execute(
                "UPDATE inventory SET action=? WHERE uid=? ", (act, uid,)
            ).fetchall()
        return

    def update_player_name(self, uid, name):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT name FROM stat WHERE uid=? ", (uid,)
            ).fetchall()
        with self.connect() as conn:
            b = conn.execute(
                "UPDATE stat SET name=? WHERE uid=? ", (name, uid,)
            )
        return r[0]

    def get_mastery(self, uid, action):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT %s FROM mastery WHERE uid=?" % action, (uid,)
            ).fetchall()
        return r[0]

    def get_all_skill_level(self, uid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT skill FROM skill WHERE uid=?", (uid,)
            ).fetchall()[0][0]
        r = json.loads(r)
        return r

    def get_upgrade(self, uid):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT upgrade FROM inventory WHERE uid=?", (uid,)
            ).fetchall()[0][0]
        r = json.loads(r)
        return r

    def ini_player(self, uid, name):
        if not self.is_player_exist(uid):
            skill = {"attack": 0, "strength": 0, "defence": 0, "hitpoints": 0, "ranged": 0, "magic": 0, "prayer": 0,
                     "slayer": 0,
                     "woodcutting": [0, 0], "fishing": [0, 0], "firemaking": [0, 0], "cooking": [0, 0],
                     "mining": [0, 0], "smithing": [0, 0], "thieving": [0, 0], "farming": [0, 0], "fletching": [0, 0],
                     "crafting": [0, 0], "runecrafting": [0, 0], "herblore": [0, 0], "alternative_magic": [0, 0]}
            inventory = {}
            equipment = {"helmet": None, "platebody": None, "boots": None, "gloves": None, "cape": None, "quiver": None,
                         "ring": None, "amulet": None, "shield": None, "weapon": None}
            action = {"action": None, "start_time": None}
            woodcutting, fishing, firemaking, cooking, mining, smithing, thieving, farming, fletching, crafting, runecrafting, herblore = {}, {}, {}, {}, {
                45: 0, 46: 0, 47: 0, 48: 0, 49: 0, 50: 0, 51: 0, 52: 0, 53: 0, 54: 0,
                388: 0}, {'55': 0, '56': 0, '57': 0, '133': 0, '58': 0, '59': 0, '60': 0, '61': 0, '62': 0, '63': 0,
                          '705': 0, '269': 0, '64': 0, '462': 0, '431': 0, '67': 0, '65': 0, '731': 0, '68': 0,
                          '121': 0, '66': 0, '724': 0, '69': 0, '70': 0, '723': 0, '71': 0, '706': 0, '72': 0, '270': 0,
                          '463': 0, '432': 0, '75': 0, '73': 0, '732': 0, '76': 0, '122': 0, '74': 0, '725': 0, '77': 0,
                          '78': 0, '79': 0, '707': 0, '80': 0, '271': 0, '464': 0, '433': 0, '83': 0, '81': 0, '733': 0,
                          '84': 0, '123': 0, '82': 0, '726': 0, '85': 0, '86': 0, '87': 0, '708': 0, '88': 0, '272': 0,
                          '465': 0, '435': 0, '91': 0, '89': 0, '734': 0, '92': 0, '124': 0, '90': 0, '727': 0, '93': 0,
                          '94': 0, '95': 0, '709': 0, '96': 0, '273': 0, '466': 0, '436': 0, '99': 0, '97': 0, '735': 0,
                          '100': 0, '125': 0, '98': 0, '728': 0, '101': 0, '102': 0, '103': 0, '710': 0, '104': 0,
                          '274': 0, '467': 0, '437': 0, '107': 0, '105': 0, '736': 0, '108': 0, '126': 0, '106': 0,
                          '729': 0, '109': 0, '110': 0, '111': 0, '711': 0, '112': 0, '275': 0, '468': 0, '438': 0,
                          '115': 0, '113': 0, '737': 0, '116': 0, '127': 0, '114': 0, '730': 0, '118': 0,
                          '117': 0}, {}, {}, {}, {'297': 0, '298': 0, '299': 0, '300': 0, '301': 0, '302': 0, '624': 0,
                                                  '625': 0, '626': 0, '627': 0, '628': 0, '629': 0, '303': 0, '304': 0,
                                                  '758': 0, '305': 0, '306': 0, '307': 0, '759': 0, '308': 0, '309': 0,
                                                  '310': 0, '760': 0, '311': 0, '312': 0, '313': 0, '761': 0, '314': 0,
                                                  '315': 0, '320': 0, '316': 0, '321': 0, '317': 0, '322': 0, '318': 0,
                                                  '323': 0, '319': 0, '324': 0, '325': 0, '330': 0, '326': 0, '331': 0,
                                                  '327': 0, '332': 0, '328': 0, '333': 0, '329': 0, '334': 0}, {}, {}
            upgrade = {"pickaxe": 0, "axe": 0, "fishing_rod": 0, "cooking_fire": 0}
            charge = {"335": "None", "336": "None", "337": "None", "338": "None", "339": "None"}
            woodcutting, fishing, firemaking, cooking, mining, smithing, thieving, farming, fletching, crafting, runecrafting, herblore = json.dumps(
                woodcutting, indent=4), json.dumps(fishing, indent=4), json.dumps(firemaking, indent=4), json.dumps(
                cooking, indent=4), json.dumps(mining, indent=4), json.dumps(smithing, indent=4), json.dumps(thieving,
                                                                                                             indent=4), json.dumps(
                farming, indent=4), json.dumps(fletching, indent=4), json.dumps(crafting, indent=4), json.dumps(
                runecrafting, indent=4), json.dumps(herblore, indent=4)
            skill = json.dumps(skill, indent=4)
            inventory = json.dumps(inventory, indent=4)
            equipment = json.dumps(equipment, indent=4)
            action = json.dumps(action, indent=4)
            upgrade = json.dumps(upgrade, indent=4)
            charge = json.dumps(charge, indent=4)
            with self.connect() as conn:
                conn.execute("INSERT OR REPLACE INTO skill (uid,skill) VALUES (?,?)", (uid, skill,), )
            with self.connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO inventory (uid,inventory,equipment,action,upgrade,charge) VALUES (?,?,?,?,?,?)",
                    (uid, inventory, equipment, action, upgrade, charge), )
            with self.connect() as conn:
                conn.execute("INSERT OR REPLACE INTO stat (uid,i_slot,coin,name) VALUES (?,?,?,?)",
                             (uid, 12, 0, name,), )
            with self.connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO mastery (uid,woodcutting, fishing, firemaking, cooking, mining, smithing, thieving, farming, fletching, crafting, runecrafting, herblore) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (uid, woodcutting, fishing, firemaking, cooking, mining, smithing, thieving, farming, fletching,
                     crafting, runecrafting, herblore,), )
            return True
        else:
            return


class dat:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def connect(self):
        return sqlite3.connect(self.db_path)

    def get_equ_stat(self, id):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT * FROM equipment WHERE ID=? ", (id,)
            ).fetchall()
        return json.loads(r[0][1])

    def get_item_from_col(self, col, value):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT * FROM itemlist WHERE %s=? " % col, (value,)
            ).fetchall()
        return r[0]

    def get_name_from_id(self, id):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT name FROM itemlist WHERE id=? ", (id,)
            ).fetchall()
        return r[0]

    def get_recipes(self, id):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT * FROM recipes WHERE id=? ", (id,)
            ).fetchall()
        return r[0]

    def get_all_recipes(self, skill):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT id FROM recipes WHERE skill=? ", (skill,)
            ).fetchall()
        a = []
        for each in r:
            a.append(each[0])
        return a

    def get_all_recipes_level(self, skill):
        with self.connect() as conn:
            r = conn.execute(
                "SELECT level FROM recipes WHERE skill=? ", (skill,)
            ).fetchall()
        a = []
        for each in r:
            a.append(each[0])
        return a

    def get_shop(self):
        with self.connect() as conn:
            pickaxe = conn.execute(
                "SELECT * FROM pickaxe ",
            ).fetchall()
            axe = conn.execute(
                "SELECT * FROM axe ",
            ).fetchall()
            fish = conn.execute(
                "SELECT * FROM fishing_rod ",
            ).fetchall()
            cook = conn.execute(
                "SELECT * FROM cooking_fire ",
            ).fetchall()
            gloves = conn.execute(
                "SELECT * FROM gloves ",
            ).fetchall()
            shop = conn.execute(
                "SELECT * FROM shop ",
            ).fetchall()
            skillcapes = conn.execute(
                "SELECT * FROM skillcape ",
            ).fetchall()
            a = {}
            for i, s in skillcapes:
                a[s] = i
            skillcapes = a
        return {"pickaxe": pickaxe, "axe": axe, "fish": fish, "cook": cook, "gloves": gloves, "shop": shop,
                "skillcapes": skillcapes}
