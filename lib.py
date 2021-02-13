import datetime
from typing import List, Callable, Dict
import os
import sqlite3
import os
import ujson as json

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
        with self.connect() as conn:
            r = conn.execute(
                "UPDATE inventory SET inventory=? WHERE uid=?", (inv, uid,)
            ).fetchall()
        return r

    def update_player_stat(self, uid, col, value):
        with self.connect() as conn:
            r = conn.execute(
                "UPDATE stat SET %s=? WHERE uid=?" % col, (value, uid)
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
                388: 0}, {}, {}, {}, {}, {}, {}, {}
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
            with self.connect() as conn:
                conn.execute("INSERT OR REPLACE INTO skill (uid,skill) VALUES (?,?)", (uid, skill,), )
            with self.connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO inventory (uid,inventory,equipment,action,upgrade) VALUES (?,?,?,?,?)",
                    (uid, inventory, equipment, action, inventory,), )
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
