from typing import List, Callable
import sqlite3
import os
import ujson as json

DB_PATH = os.path.expanduser("~/.hoshino/rpg.db")
DATA_PATH = os.path.dirname(os.path.realpath(__file__))


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
                "(uid INT NOT NULL,inventory json NOT NULL,equipment json NOT NULL , action json NOT NULL ,PRIMARY KEY (uid))"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS stat"
                "(uid INT NOT NULL,i_slot INT NOT NULL,coin INT NOT NULL , name TEXT NOT NULL ,PRIMARY KEY (uid))"
            )

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

    def ini_player(self, uid):
        if not self.get_player_inv(uid):
            skill = {"attack": 0, "strength": 0, "defence": 0, "hitpoints": 0, "ranged": 0, "magic": 0, "prayer": 0,
                     "slayer": 0,
                     "woodcutting": 0, "fishing": 0, "firemaking": 0, "cooking": 0, "mining": 0, "smithing": 0,
                     "thieving": 0, "farming": 0, "fletching": 0, "crafting": 0, "runecrafting": 0, "herblore": 0,
                     "alternative_magic": 0}
            inventory = {}
            equipment = {"helmet": None, "platebody": None, "boots": None, "gloves": None, "cape": None, "quiver": None,
                         "ring": None, "amulet": None, "shield": None, "weapon": None}
            action = {"action": None, "start_time": None}
            skill = json.dumps(skill)
            inventory = json.dumps(inventory)
            equipment = json.dumps(equipment)
            action = json.dumps(action)
            with self.connect() as conn:
                conn.execute("INSERT INTO skill (uid,skill) VALUES (?,?)", (uid, skill,), )
            with self.connect() as conn:
                conn.execute("INSERT INTO inventory (uid,inventory,equipment,action) VALUES (?,?,?,?)",
                             (uid, inventory, equipment, action,), )
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
