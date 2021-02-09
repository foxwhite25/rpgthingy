import requests
from lxml import etree
from urllib import request
import os
import sqlite3
from monster import get_item_id
from combat import get_monster_id
from googletrans import Translator
import ujson as json
import re
import cairosvg

os.chdir(r'C:\Users\vctxi\PycharmProjects\rpgthingy')
url = 'https://wiki.melvoridle.com/index.php?title=Equipment'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 '
                  'Safari/537.36'}
conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS equipment
       (ID INT PRIMARY KEY     NOT NULL,
        stat        json    NOT NULL)''')
conn.commit()
translator = Translator(service_urls=[
    'translate.google.cn', ])
opener = request.build_opener()
opener.addheaders = [('User-agent',
                      'Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U;                                           en-GB) Presto/2.8.149 Version/11.10')]
request.install_opener(opener)


def p2f(x):
    return float(x.strip('%')) / 100


def get_url_item(x):
    r = conn.execute(
        "SELECT url FROM itemlist WHERE name=?", (x,)
    ).fetchall()
    conn.commit()
    if not r:
        print("Cannot get id from " + x)
    return r[0]


def get_urls(url):
    resp = requests.get(url, headers=headers)
    text = resp.text
    html = etree.HTML(text)
    detail_urls = []
    a = []
    for urls in html.xpath(
            r'//*[@id="mw-content-text"]/div/table/tbody/tr/td[2]/a/@href'):
        detail_urls.append(urls)
    return detail_urls


def get_data(url):
    stl = 0
    detail_url = 'https://wiki.melvoridle.com/' + str(url)
    resp = requests.get(detail_url, headers=headers)
    text = resp.text
    html = etree.HTML(text)
    name = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[1]/th/text()')[0].replace('\n', "")
    slot = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[8]/td/text()')[0].split()[2]
    stats = html.xpath('//*[@id="mw-content-text"]/div/table[3]//text()')
    stat = [x.replace('\n', '') for x in stats]
    stat = list(filter(None, stat))
    stats = []
    for each in stat:
        try:
            stats.append(int(each))
        except:
            try:
                stats.append(p2f(each))
            except:
                pass
    if slot != "Weapon":
        stat = {"str_bonus": {"melee": stats[0], "ranged": stats[9]},
                "atk_bonus": {"melee": {"stab": stats[2], "slash": stats[4], "block": stats[6]}, "ranged": stats[8],
                              "magic": stats[11]},
                "magic_bonus": stats[13],
                "def_bonus": {"melee": stats[1], "ranged": stats[5], "magic": stats[7]},
                "damage_reduction": stats[3],
                "slayer_xp": stats[10],
                "level": {"def": stats[12], "rag": stats[14], "mag": stats[15]},
                "slot": slot}
    else:
        weapon_type = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[4]/td[1]/span/text()')[0]
        is_two_hand = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[12]/td[2]/text()')[0].replace("\n",
                                                                                                                 "")
        if is_two_hand == "true":
            is_two_hand = True
        else:
            is_two_hand = False
        stat = {"attack_speed": stats[0],
                "type": weapon_type,
                "str_bonus": {"melee": stats[3], "ranged": stats[12]},
                "atk_bonus": {"melee": {"stab": stats[5], "slash": stats[7], "block": stats[8]}, "ranged": stats[10],
                              "magic": stats[14]},
                "magic_bonus": stats[16],
                "def_bonus": {"melee": stats[1], "ranged": stats[4], "magic": stats[6]},
                "damage_reduction": stats[2],
                "slayer_xp": stats[9],
                "level": {"def": stats[11], "rag": stats[13], "mag": stats[15]},
                "two_hand": is_two_hand,
                "slot": slot}
    stats = json.dumps(stat)
    stat = json.dumps(stat, indent=4, sort_keys=True)
    print(name)
    id = get_item_id(name)[0]
    print(id, stat)
    c = conn.cursor()
    c.execute('''insert or replace into equipment (
        ID,
        stat)
    values (
        ?,
        ?)''', (id, stats,))
    conn.commit()


def main():
    detail_urls = get_urls(url)
    print(detail_urls)
    for each in detail_urls:
        get_data(each)


if __name__ == '__main__':
    main()
