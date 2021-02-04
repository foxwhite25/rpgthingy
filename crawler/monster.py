import requests
from lxml import etree
from urllib import request
import os
import sqlite3
from googletrans import Translator
import ujson as json
import re
import cairosvg

os.chdir(r'C:\Users\vctxi\PycharmProjects\rpgthingy')
url = 'https://wiki.melvoridle.com/index.php?title=Monsters'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 '
                  'Safari/537.36'}
conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS monsterlist
       (ID INT PRIMARY KEY     NOT NULL,
        name        TEXT    NOT NULL,
        loot        json    NOT NULL,
        stat        json    NOT NULL,
        bone        TEXT    NOT NULL );''')
conn.commit()
translator = Translator(service_urls=[
    'translate.google.cn', ])
opener = request.build_opener()
opener.addheaders = [('User-agent',
                      'Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U;                                           en-GB) Presto/2.8.149 Version/11.10')]
request.install_opener(opener)


def p2f(x):
    return float(x.strip('%')) / 100


def get_item_id(x):
    r = conn.execute(
        "SELECT ID FROM itemlist WHERE name=?", (x,)
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
    for urls in html.xpath(
            r'//*[@id="mw-content-text"]/div/table[2]/tbody//tr/td[2]/a/@href'):
        detail_urls.append(urls)
    return detail_urls


def get_data(url):
    stl = 0
    detail_url = 'https://wiki.melvoridle.com/' + str(url)
    print(detail_url)
    resp = requests.get(detail_url, headers=headers)
    text = resp.text
    html = etree.HTML(text)
    name = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[1]/th/text()')[0]
    name = name.rstrip('\n')
    id = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[3]/td/text()')[0]
    id = [int(s) for s in id.split() if s.isdigit()][0]
    a = html.xpath('//*[@id="mw-content-text"]/div/table[3]//text()')
    # 战斗数据处理
    a = [x for x in a if not x.startswith('\n')]
    a = list(map(lambda s: s.strip(), a))
    a.pop(0)
    n = 0
    for each in a:
        a[n] = each.replace(",", "")
        a[n] = a[n].replace(" s", "")
        try:
            a[n] = int(a[n])
        except:
            pass
        n += 1
    evasion = {"melee": a[11], "range": a[12], "magic": a[13]}
    skill = {"atk": a[15], "str": a[16], "def": a[17], "rag": a[18], "mag": a[19]}
    b = {"combat_level": a[1], "hp": a[3], "attack_speed": a[5], "max_hit": a[7], "accuracy": a[9], "evasion": evasion,
         "skill": skill}
    combat_stats = json.dumps(b)
    loot_table = {}
    bone = html.xpath('//*[@id="mw-content-text"]/div/table[4]/tbody/tr[2]/td[1]/span/a[2]/text()')
    if bone:
        bone = bone[0]
    else:
        bone = "-1"
    try:
        n1 = html.xpath('//*[@id="mw-content-text"]/div/table[5]//text()')
        n1 = list(map(lambda s: s.strip(), n1))
        n1 = list(filter(None, n1))
        n1 = n1[4:-3]
        n = 0
        temp = {}
        quantity = {}
        loot_table = {}
        for each in n1:
            if n == 1:
                try:
                    each = int(each)
                    quantity["from"] = each
                    quantity["to"] = each
                except:
                    each = list(map(str, re.findall(r'\d+', each)))
                    quantity["from"] = each[0]
                    quantity["to"] = each[1]
            if n == 0:
                temp["name"] = each
                id2 = get_item_id(each)[0]
                temp["id"] = id2
            if n == 4:
                temp["chance"] = p2f(each)
            temp["quantity"] = quantity
            n += 1
            if n == 5:
                loot_table[id2] = temp
                temp = {}
                n = 0
        try:
            coin = html.xpath('//*[@id="mw-content-text"]/div/p[5]/span/text()')[0]
        except:
            coin = html.xpath('//*[@id="mw-content-text"]/div/p[6]/span/text()')[0]
        quantity = {}
        try:
            coin = int(coin)
            quantity["from"] = coin
            quantity["to"] = coin
        except:
            coin = list(map(str, re.findall(r'\d+', coin)))
            quantity["from"] = int(coin[0])
            quantity["to"] = int(coin[1])
        loot_table['coin'] = quantity
    except:
        pass
    loot_table = json.dumps(loot_table)
    c = conn.cursor()
    c.execute('''insert or replace into monsterlist (
        ID,
        name,
        loot,
        stat,
        bone)
    values (
        ?,
        ?,
        ?,
        ?,
        ?)''', (id, name, loot_table, combat_stats, bone,))
    conn.commit()
    jpg = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[2]/td/span/a/img/@src')[0]
    url1 = r'https://wiki.melvoridle.com' + jpg
    name1 = fr"C:\Users\vctxi\PycharmProjects\rpgthingy\svg\monster\{id}.svg"
    img = request.urlretrieve(url1, name1)
    try:
        cairosvg.svg2png(url=img[0], write_to=fr"C:\Users\vctxi\PycharmProjects\rpgthingy\icons\monster\{id}.png")
    except:
        name1 = fr"C:\Users\vctxi\PycharmProjects\rpgthingy\icons\monster\{id}.png"
        img = request.urlretrieve(url1, name1)
    print(id, name, )
    print(loot_table, combat_stats, )
    print("==================================================")


def main():
    detail_urls = get_urls(url)
    for each in detail_urls:
        get_data(each)


if __name__ == '__main__':
    main()
