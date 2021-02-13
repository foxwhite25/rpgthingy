import hoshino
from hoshino import Service, util, priv
from hoshino.typing import MessageSegment, NoticeSession, CQEvent
import random
from .ma import *
from .lib import *
from PIL import Image, ImageFont, ImageDraw #2740156726

RPG_DB_PATH = os.path.expanduser("~/.hoshino/rpg.db")
__BASE = os.path.split(os.path.realpath(__file__))
IMAGE_DIR_PATH = os.path.join(__BASE[0], 'icons')
ITEM_DIR_PATH = os.path.join(IMAGE_DIR_PATH, 'item')
MONSTER_DIR_PATH = os.path.join(IMAGE_DIR_PATH, 'monster')
GAME_NAME = "我也不知道应该叫啥"
db = RecordDAO(RPG_DB_PATH)
DATA_PATH = os.path.expanduser("~/.hoshino/data.db")
dat = dat(DATA_PATH)


@reg_cmd(['购买背包', 'bbp'])
async def cmd_buy_bp(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    if not db.is_player_exist(uid):
        await bot.send(ev, '你还未创建角色！请输入?创建角色 角色名')
        return
    try:
        if args[0] == "max":
            times = 1000000
        elif isinstance(args[0], int):
            times = args[0]
    except IndexError:
        times = default_arg(1, args, 0)
    i_slot = db.get_player_stat(uid)[1]
    coin = db.get_player_stat(uid)[2]
    cost = int(get_bp_cost(i_slot))
    tcost, t = cost, 0
    for temp in range(1, times):
        if coin >= cost:
            i_slot += 1
            coin -= cost
            cost = int(get_bp_cost(i_slot))
            tcost += cost
            t += 1
        else:
            if t == 0:
                await bot.send(ev, f"你的金币不够{millify(cost)}枚，无法购买背包")
                break
            else:
                db.update_player_stat(uid, "i_slot", i_slot)
                db.update_player_stat(uid, "coin", coin)
                await bot.send(ev, f"成功使用{millify(tcost)}枚金币购买了{t}格背包")
                break


@reg_cmd(['查看属性', 'stat'])
async def cmd_test(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    if not db.is_player_exist(uid):
        await bot.send(ev, '你还未创建角色！请输入?创建角色 角色名')
        return
    img = profile(uid)
    await bot.send(ev, img)


@reg_cmd('创建角色')
async def cmd_create(bot: HoshinoBot, ev: CQEvent, args):
    try:
        name = str(args[0])
    except IndexError:
        name = ''
    uid = ev['user_id']
    if name == '':
        await bot.send(ev, '请输入?创建角色 角色名')
        return
    if db.is_player_exist(uid):
        await bot.send(ev, '您已创建角色！')
        return
    db.ini_player(uid, name)
    await bot.send(ev, f'角色{name}已创建，欢迎来到{GAME_NAME}！')


@reg_cmd(['查看物品栏', '打开背包', '打开物品栏', '查看背包', '查询物品栏', '查询背包', '康康背包', 'bp'])
async def cmd_inventory(bot: HoshinoBot, ev: CQEvent, args):
    page = default_arg(1, args, 0)
    per_page = default_arg(20, args, 1)
    reverse = default_arg(False, args, 2)
    try:
        if args[2] == "False":
            reverse = False
        elif args[2] == "True":
            reverse = True
    except:
        pass
    if not isinstance(page, int) or not isinstance(per_page, int):
        await bot.send(ev, '参数必须为数字，格式为：?查看物品栏 (页数;默认:1) (每页显示数量;默认:20) (反转;默认:False)')
        return
    uid = ev['user_id']
    if not db.is_player_exist(uid):
        await bot.send(ev, '你还未创建角色！请输入?创建角色 角色名')
        return
    msg = f"第{page}页物品栏:\n"
    msg += str(inventory(uid, page, reverse, per_page)) + "\n"
    msg += "输入：?查看物品栏 (页数;默认:1) (每页显示数量;默认:20) (反转;默认:False) 可查看其它页面"
    await bot.send(ev, msg)


@reg_cmd('采矿')
async def cmd_mine(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    if not db.is_player_exist(uid):
        await bot.send(ev, '你还未创建角色！请输入?创建角色 角色名')
        return
    msg = mining(uid)
    await bot.send(ev, msg)


@reg_cmd('采集矿石')
async def cmd_mine(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    if not db.is_player_exist(uid):
        await bot.send(ev, '你还未创建角色！请输入?创建角色 角色名')
        return
    uid = ev['user_id']
    skill = get_gather_skill_mastery(uid, "mining")
    yes = []
    for ores in ore:
        if ores["level"] <= skill["slv"]:
            yes.append(ores["id"])
    if 45 <= args[0] <= 54 or args[0] == 388:
        if is_player_in_action(uid):
            a = is_player_in_action(uid)
            await bot.send(ev, f"当前已经在进行{a[0]}{dat.get_item_from_col('id', a[1])[1]}了")
            return
        else:
            if is_str_in_list(yes, args[0]):
                db.update_player_action(['挖掘', args[0]], uid)
                img = get_item_image(args[0])
                await bot.send(ev,
                               f"{MessageSegment.image(util.pic2b64(img))}\n成功开始了采集{dat.get_item_from_col('id', args[0])[1]}行动\n当你想要取消的时候输入?结算行动")
                return
            else:
                await bot.send(ev, f"你的等级不足，无法挖掘{dat.get_item_from_col('id', args[0])[1]}")
    else:
        await bot.send(ev, f'{args[0]}并不是可挖掘的矿物')


@reg_cmd('结算行动')  # 1613026494.634164
async def cmd_complete(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    if not db.is_player_exist(uid):
        await bot.send(ev, '你还未创建角色！请输入?创建角色 角色名')
        return
    if is_player_in_action(uid):
        action = db.get_player_action(uid)
        if action['action'][0] == '挖掘':
            msg = cal_mining(action, uid)
            await bot.send(ev, msg)
            db.update_player_action(None, uid)
            return
    else:
        await bot.send(ev, '你并没有在任何行动中')
    return


@reg_cmd('改名')
async def cmd_give(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    if not db.is_player_exist(uid):
        await bot.send(ev, '你还未创建角色！请输入?创建角色 角色名')
        return
    if not db.is_player_exist(uid):
        await bot.send(ev, '你还未创建角色！请输入?创建角色 角色名')
        return
    try:
        a = args[0]
        b = db.update_player_name(uid, str(a))
        await bot.send(ev, f"你已从{b[0]}改名为{a}。")
    except IndexError:
        await bot.send(ev, "未知格式，格式为:?改名 [新名字]")


@reg_cmd('添加物品')
async def cmd_give(bot: HoshinoBot, ev: CQEvent, args):
    if priv.check_priv(ev, priv.SUPERUSER):
        try:
            a = (args[0], args[1])
            uid = ev['user_id']
            name = change_item_num(uid, args[0], args[1])
            img = get_item_image(args[0])
            await bot.send(ev,
                           f"{MessageSegment.image(util.pic2b64(img))}\n已添加{args[1]}个{name}到{MessageSegment.at(uid)}的物品栏")
        except:
            await bot.send(ev, '格式错误')
    else:
        await bot.send(ev, "权限不足")


@reg_cmd('添加随机物品')
async def give(bot: HoshinoBot, ev: CQEvent, args):
    if priv.check_priv(ev, priv.SUPERUSER):
        uid = ev['user_id']
        a = {}
        for temp in range(1, 500):
            a[random.randint(0, 500)] = random.randint(0, 500)
            add_loot_to_inv(a,uid)
        await bot.send(ev, f"已添加500个随机物品到{MessageSegment.at(uid)}的物品栏")
    else:
        await bot.send(ev, "权限不足")
