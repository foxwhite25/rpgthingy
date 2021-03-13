import os
import sqlite3
import json

RPG_DB_PATH = os.path.expanduser("~/.hoshino/rpg.db")
js = json.dumps({'0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0}, indent=4)


class RecordDAO:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def connect(self):
        return sqlite3.connect(self.db_path)

    def update(self):
        with self.connect() as conn:
            r = conn.execute(
                "UPDATE mastery SET woodcutting=?", (js,)
            )


db = RecordDAO(RPG_DB_PATH)
db.update()
