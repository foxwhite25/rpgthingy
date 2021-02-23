import hoshino
from hoshino import Service, util, priv
from hoshino.typing import MessageSegment, NoticeSession, CQEvent
import random
from .ma import *
from .lib import *
from PIL import Image, ImageFont, ImageDraw  # 2740156726

RPG_DB_PATH = os.path.expanduser("~/.hoshino/rpg.db")
__BASE = os.path.split(os.path.realpath(__file__))
IMAGE_DIR_PATH = os.path.join(__BASE[0], 'icons')
ITEM_DIR_PATH = os.path.join(IMAGE_DIR_PATH, 'item')
MONSTER_DIR_PATH = os.path.join(IMAGE_DIR_PATH, 'monster')
GAME_NAME = "我也不知道应该叫啥"
db = RecordDAO(RPG_DB_PATH)
DATA_PATH = os.path.expanduser("~/.hoshino/data.db")
dat = dat(DATA_PATH)


@reg_cmd('测试输出')
async def cmd_test(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    await bot.send(ev, '少女祈祷中...')
    msg = crafting(uid)
    await bot.send(ev, msg)
    return


@reg_cmd('充能列表')
async def cmd_eqp(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    upgrade = db.get_player_inv(uid)[5]
    upgrade = json.loads(upgrade)
    msg = '充能列表:\n'
    for item, charge in upgrade.items():
        if charge != 'None':
            msg += f'{dat.get_item_from_col("id", item)[1]}:{charge}\n'
    await bot.send(ev, msg)
    return


@reg_cmd(['装备'])
async def cmd_eqp(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    if is_bp_full(uid):
        await bot.send(ev, '背包已满，请使用?售卖 [物品ID] [数量]来清理背包，或者?购买背包 (数量或者max)来增加背包容量')
        return
    try:
        iid = args[0]
        equipment = json.loads(db.get_player_inv(uid)[2])
        new_eqp_slot = dat.get_equ_stat(iid)['slot'].lower()
        inv = json.loads(db.get_player_inv(uid)[1])
        try:
            old_id = None
            if equipment[new_eqp_slot]:
                old_id = equipment[new_eqp_slot]
                inv = dict(Counter(inv) + Counter({old_id: 1}))
            iid = str(iid)
            if old_id == iid:
                await bot.send(ev, f"你已经在装备{dat.get_item_from_col('id', iid)[1]}了")
                return
            a = inv[iid]
            inv = dict(Counter(inv) - Counter({iid: 1}))
            equipment[new_eqp_slot] = iid
            equipment = json.dumps(equipment, indent=4)
            inv = json.dumps(inv, indent=4)
            db.update_player_inv(uid, inv)
            db.update_player_equipment(uid, equipment)
            if old_id:
                await bot.send(ev,
                               f"成功使用{dat.get_item_from_col('id', iid)[1]}替换{dat.get_item_from_col('id', old_id)[1]}")
                return
            else:
                await bot.send(ev, f"成功装备{dat.get_item_from_col('id', iid)[1]}")
                return
        except IndexError:
            await bot.send(ev, f"你的{dat.get_item_from_col('id', iid)[1]}不足")
            return
    except IndexError:
        msg = armour(uid)
        await bot.send(ev, msg)


@reg_cmd('取消装备')
async def cmd_uneqp(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    if is_bp_full(uid):
        await bot.send(ev, '背包已满，请使用?售卖 [物品ID] [数量]来清理背包，或者?购买背包 (数量或者max)来增加背包容量')
        return
    try:
        iid = args[0]
        equipment = json.loads(db.get_player_inv(uid)[2])
        new_eqp_slot = dat.get_equ_stat(iid)['slot'].lower()
        inv = json.loads(db.get_player_inv(uid)[1])
        iid = str(iid)
        if equipment[new_eqp_slot] == iid:
            old_id = equipment[new_eqp_slot]
            inv = dict(Counter(inv) + Counter({old_id: 1}))
            equipment[new_eqp_slot] = None
            equipment = json.dumps(equipment, indent=4)
            inv = json.dumps(inv, indent=4)
            db.update_player_inv(uid, inv)
            db.update_player_equipment(uid, equipment)
            await bot.send(ev, f"成功取消装备{dat.get_item_from_col('id', iid)[1]}")
            return
        else:
            await bot.send(ev, f"你并没有装备{dat.get_item_from_col('id', iid)[1]}")
            return
    except IndexError:
        msg = "未知格式，格式为?取消装备 [物品ID]"
        await bot.send(ev, msg)


@reg_cmd(['商店'])
async def cmd_shop(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    if not db.is_player_exist(uid):
        await bot.send(ev, '你还未创建角色！请输入?创建角色 角色名')
        return
    await bot.send(ev, shop(uid))


@reg_cmd(['购买'])
async def cmd_buy(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    current_coin = db.get_player_stat(uid)[2]
    if is_bp_full(uid):
        await bot.send(ev, '背包已满，请使用?售卖 [物品ID] [数量]来清理背包，或者?购买背包 (数量或者max)来增加背包容量')
        return
    if not db.is_player_exist(uid):
        await bot.send(ev, '你还未创建角色！请输入?创建角色 角色名')
        return
    try:
        iid = args[0]
    except:
        await bot.send(ev, '未知格式，格式为?购买 [物品ID](镐子，斧头，钓鱼竿，营火例外) [数量,默认:1]')
        return
    if iid == '镐子':
        picks = dat.get_shop()['pickaxe']
        pick = db.get_upgrade(uid)['pickaxe']
        picks = picks[pick + 1]
        if picks[5] > current_coin:
            await bot.send(ev, f'你的GP不足{picks[5]}无法购买{picks[1]}')
            return
        db.update_player_stat(uid, 'coin', current_coin - picks[5])
        current_upgrade = db.get_upgrade(uid)
        current_upgrade['pickaxe'] += 1
        current_upgrade = json.dumps(current_upgrade)
        db.update_player_upgrade(uid, current_upgrade)
        await bot.send(ev, f'成功使用{picks[5]}GP购买{picks[1]}')
        return
    amount = default_arg(1, args, 1)
    if not isinstance(amount, int) and amount != 'max':
        await bot.send(ev, '未知格式，格式为?购买 [物品ID](镐子，斧头，钓鱼竿，营火例外) [数量,默认:1,"max"只适用于手套]')
        return
    gloves = dat.get_shop()['gloves']
    inv = db.get_player_inv(uid)[1]
    current_charge = db.get_player_inv(uid)[5]
    current_charge = json.loads(current_charge)
    inv = json.loads(inv)
    cp = None
    for i, c, p in gloves:
        if i == iid:
            cp = (c, p)
    if cp:
        if amount == 'max':
            amount = math.floor(current_coin / cp[1])
        if (cp[1] * amount) > current_coin:
            await bot.send(ev, f"你的GP不足{cp[1] * amount}无法购买{dat.get_item_from_col('id', iid)[1]}")
            return
        db.update_player_stat(uid, 'coin', current_coin - (cp[1] * amount))
        try:
            a = inv[str(iid)]
        except:
            a = 0
        if current_charge[str(iid)] == "None":
            inv = add_two_inv(inv, {str(iid): 1})
            inv = json.dumps(inv)
            db.update_player_inv(uid, inv)
            current_charge[str(iid)] = cp[0] * amount
        else:
            current_charge[str(iid)] += cp[0] * amount
        db.update_player_charge(uid, json.dumps(current_charge, indent=4))
        await bot.send(ev, f"使用了{cp[1] * amount}GP购买了{dat.get_item_from_col('id', iid)[1]}的{cp[0] * amount}充能")
        return
    a = get_shop_item_cost(iid, uid)
    if not a:
        await bot.send(ev, f'{iid}不是可以购买的东西')
        return
    coin = 0
    d = a
    for item, value in d.items():
        if item == 'coin':
            coin = value * amount
            continue
        try:
            b = inv[item]
            if b >= value * amount:
                pass
            else:
                await bot.send(ev, f"你的{dat.get_item_from_col('id', item)[1]}不足")
                return
        except:
            await bot.send(ev, f"你的{dat.get_item_from_col('id', item)[1]}不足")
            return
    if coin > current_coin:
        await bot.send(ev, f"你的GP不足{coin}无法购买{dat.get_item_from_col('id', iid)[1]}")
        return
    try:
        del a['coin']
    except:
        pass
    c = {str(iid): amount}
    d = Counter({})
    for n in range(0, amount):
        d += Counter(a)
    new = Counter(inv) - d + Counter(c)
    new = json.dumps(dict(new))
    db.update_player_inv(uid, new)
    db.update_player_stat(uid, 'coin', current_coin - coin)
    await bot.send(ev, f"使用了{coin}GP购买了{dat.get_item_from_col('id', iid)[1]}")
    return


@reg_cmd(['购买背包', 'bbp'])
async def cmd_buy_bp(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    times = default_arg(1, args, 0)
    if not db.is_player_exist(uid):
        await bot.send(ev, '你还未创建角色！请输入?创建角色 角色名')
        return
    try:
        if args[0] == "max":
            times = 1000000
        else:
            times = args[0]
    except IndexError:
        pass
    i_slot = db.get_player_stat(uid)[1]
    coin = db.get_player_stat(uid)[2]
    cost = int(get_bp_cost(i_slot))
    tcost, t = cost, 0
    for temp in range(0, times):
        if coin >= cost:
            i_slot += 1
            coin -= cost
            cost = int(get_bp_cost(i_slot))
            tcost += cost
            t += 1
        else:
            if t == 0:
                await bot.send(ev, f"你的金币不够{millify(cost)}枚，无法购买背包")
                return
            else:
                break
    db.update_player_stat(uid, "i_slot", i_slot)
    db.update_player_stat(uid, "coin", coin)
    await bot.send(ev, f"成功使用{millify(tcost)}枚金币购买了{t}格背包")


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


@reg_cmd(['采集矿石', '采矿'])
async def cmd_mine(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    if not db.is_player_exist(uid):
        await bot.send(ev, '你还未创建角色！请输入?创建角色 角色名')
        return
    if is_bp_full(uid):
        await bot.send(ev, '背包已满，请使用?售卖 [物品ID] [数量]来清理背包，或者?购买背包 (数量或者max)来增加背包容量')
        return
    try:
        a = args[0]
    except IndexError:
        await bot.send(ev, '少女祈祷中...')
        msg = mining(uid)
        await bot.send(ev, str(msg) + '\n发送?采矿 [物品ID]开始采矿')
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


@reg_cmd(['烧制物品', '炼制', '锻造', '熔炼'])
async def cmd_smithing(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    if is_bp_full(uid):
        await bot.send(ev, '背包已满，请使用?售卖 [物品ID] [数量]来清理背包，或者?购买背包 (数量或者max)来增加背包容量')
        return
    try:
        a = args[0]
    except IndexError:
        await bot.send(ev, '少女祈祷中...')
        msg = smithing(uid)
        await bot.send(ev, str(msg) + '\n发送?锻造 [物品ID]开始锻造')
        return
    skill = get_gather_skill_mastery(uid, "smithing")
    inv = db.get_player_inv(uid)[1]
    inv = json.loads(inv)
    recipes = dat.get_recipes(args[0])
    if recipes[5] > skill["slv"]:
        await bot.send(ev, f"你的等级不足，无法锻造{dat.get_item_from_col('id', args[0])[1]}")
        return
    print(dat.get_all_recipes('锻造'), str(args[0]))
    if str(args[0]) in dat.get_all_recipes('锻造'):
        if is_player_in_action(uid):
            a = is_player_in_action(uid)
            await bot.send(ev, f"当前已经在进行{a[0]}{dat.get_item_from_col('id', a[1])[1]}了")
            return
        else:
            fr = json.loads(recipes[2])
            for item, value in fr.items():
                try:
                    a = inv[item]
                    if a >= value:
                        pass
                    else:
                        await bot.send(ev, f"你的{dat.get_item_from_col('id', item)[1]}不足")
                        return
                except:
                    await bot.send(ev, f"你的{dat.get_item_from_col('id', item)[1]}不足")
                    return
            db.update_player_action(['锻造', args[0]], uid)
            img = get_item_image(args[0])
            await bot.send(ev,
                           f"{MessageSegment.image(util.pic2b64(img))}\n成功开始了锻造{dat.get_item_from_col('id', args[0])[1]}行动\n当你想要取消的时候输入?结算行动")
            return
    else:
        await bot.send(ev, f'{dat.get_item_from_col("id", args[0])[1]}并不是可锻造的物品')


@reg_cmd('查看物品')
async def cmd_item(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    try:
        item = args[0]
    except IndexError:
        await bot.send(ev, '未知格式，格式为:?查看物品 [物品ID]')
        return
    msg = get_item(uid, item)
    if msg == -1:
        await bot.send(ev, f'查无{item}')
        return
    await bot.send(ev, msg)


@reg_cmd('查看合成')
async def cmd_item(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    try:
        item = args[0]
    except IndexError:
        await bot.send(ev, '未知格式，格式为:?查看合成 [目标物品ID]')
        return
    recipes = dat.get_recipes(item)
    if not recipes:
        await bot.send(ev, f'暂无{item}的合成表')
        return
    fr = json.loads(recipes[2])
    to = json.loads(recipes[1])
    msg = f"{dat.get_name_from_id(item)[0]}的合成表:\n"
    msg += f'所需时间:{recipes[3]}s\n'
    msg += f'所需技能:{recipes[6]}\n'
    msg += f'技能等级需求:{recipes[5]}\n'
    msg += f'技能获得经验:{recipes[4]}\n'
    msg += f'材料:\n'
    for item, num in fr.items():
        msg += f'{num}x' + str(get_item(uid, item)) + "\n"
    msg += "合成为:\n"
    for item, num in to.items():
        msg += f'{num}x' + str(get_item(uid, item)) + "\n"
    await bot.send(ev, msg)


@reg_cmd('结算行动')  # 1613026494.634164
async def cmd_complete(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    if not db.is_player_exist(uid):
        await bot.send(ev, '你还未创建角色！请输入?创建角色 角色名')
        return
    if is_player_in_action(uid):
        action = db.get_player_action(uid)
        db.update_player_action(None, uid)
        if action['action'][0] == '挖掘':
            msg = cal_mining(action, uid)
            await bot.send(ev, msg)
            return
        if action['action'][0] == '锻造':
            msg = cal_smithing(action, uid)
            await bot.send(ev, msg)
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
            add_loot_to_inv(a, uid)
        await bot.send(ev, f"已添加500个随机物品到{MessageSegment.at(uid)}的物品栏")
    else:
        await bot.send(ev, "权限不足")


@reg_cmd(['售卖', '出售'])
async def cmd_sell(bot: HoshinoBot, ev: CQEvent, args):
    uid = ev['user_id']
    a = 0
    black_list = [335, 336, 337, 338, 339]
    sell_list = {}
    for each in args:
        if a == 0:
            temp = each
            a = 1
        else:
            sell_list[temp] = each
            a = 0
    if not args:
        await bot.send(ev, f'未知格式，格式为:?出售 [物品ID1] [数量1(max代表全部)] [物品ID2] [数量2(max代表全部)] ...')
        return
    if not (len(args) % 2) == 0:
        await bot.send(ev, f'未知格式，格式为:?出售 [物品ID1] [数量1(max代表全部)] [物品ID2] [数量2(max代表全部)] ...')
        return
    for item, amount in sell_list.items():
        if isinstance(amount, int) or amount == 'max':
            inv = db.get_player_inv(uid)[1]
            inv = json.loads(inv)
            if item in black_list:
                await bot.send(ev, f'{dat.get_item_from_col("id", item)[1]}无法出售')
                return
            try:
                item = dat.get_item_from_col("id", item)
            except:
                await bot.send(ev, f'查无{item[1]}')
                continue
            try:
                a = inv[str(item[0])]
                if amount == 'max':
                    amount = inv[str(item[0])]
            except KeyError:
                await bot.send(ev, f'你的{item[1]}不足{amount}')
                continue
            if inv[str(item[0])] < amount:
                await bot.send(ev, f'你的{item[1]}不足{amount}')
                continue
            coin = db.get_player_stat(uid)[2]
            db.update_player_stat(uid, 'coin', coin + amount * item[3])
            inv[str(item[0])] = inv[str(item[0])] - amount
            db.update_player_inv(uid, json.dumps(inv, indent=4))
            await bot.send(ev, f'已经使用{amount}个{item[1]}兑换为{amount * item[3]}GP')
            continue
        else:
            await bot.send(ev, f'未知格式，格式为:?出售 [物品ID1] [数量1(max代表全部)] [物品ID2] [数量2(max代表全部)] ...')
            continue


@reg_cmd(['help', '帮助', '说明'])
async def cmd_help(bot: HoshinoBot, ev: CQEvent, args):
    await bot.send(ev, '用你脑子想一想，我会不会写文档')
