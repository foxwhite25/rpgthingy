from typing import List, Callable
from hoshino import Service
from hoshino.typing import *
import sqlite3
import os

sv = Service(name='RPG Thingy')
cmds: Dict[str, Callable] = {}
DB_PATH = os.path.expanduser("~/.hoshino/rpg.db")


@sv.on_prefix('//')  # 指令执行
async def exec_cmd(bot: HoshinoBot, ev: CQEvent):
    # if ev['message_type'] != 'group':
    #     await bot.send(ev, '请在QQ群中使用本插件')
    #     return
    plain_cmd = ev.message.extract_plain_text()
    cmd, *args = plain_cmd.split(' ')  # 分割指令与参数
    if cmd in cmds:
        func = cmds[cmd]
        await func(bot, ev, args)
    elif cmd != '':
        sv.logger.info('指令列表' + str(cmds))
        await bot.send(ev, '未知指令\n输入//说明或//help查看说明')


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
                "CREATE TABLE IF NOT EXISTS start"
                "(uid INT NOT NULL, str INT NOT NULL,dex INT NOT NULL,con INT NOT NULL, int INT NOT NULL, wis INT NOT NULL,cha INT NOT NULL,race INT NOT NULL,class INT NOT NULL PRIMARY KEY(uid))"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS stat"
                "(uid INT NOT NULL, head INT NOT NULL,chest INT NOT NULL,pant INT NOT NULL, boot INT NOT NULL, coin INT NOT NULL,level INT NOT NULL, exp INT NOT NULL,PRIMARY KEY(uid))"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS equipment"
                "(id INT NOT NULL,type TEXT NOT NULL,PRIMARY KEY(id))"
            )