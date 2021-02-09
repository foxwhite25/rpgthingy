import hoshino
from hoshino import Service, util
from hoshino.typing import MessageSegment, NoticeSession, CQEvent
from lib import *
from math import *
from PIL import Image, ImageFont, ImageDraw

DB_PATH = os.path.expanduser("~/.hoshino/poke_man_blhx.db")
__BASE = os.path.split(os.path.realpath(__file__))
IMAGE_DIR_PATH = os.path.join(__BASE[0], 'icons')
ITEM_DIR_PATH = os.path.join(IMAGE_DIR_PATH, 'item')
MONSTER_DIR_PATH = os.path.join(IMAGE_DIR_PATH, 'monster')
sv = Service('random_idle', bundle='pcr娱乐')
db = RecordDAO(DB_PATH)

class MessageDef:
    @staticmethod
    def character(uid):
        image = Image.new('RGB', (900, 1600))


@reg_cmd('测试输出')
async def cmd_test(bot: HoshinoBot, ev: CQEvent, args):
    for i in args:
        await bot.send(ev, str(i))

