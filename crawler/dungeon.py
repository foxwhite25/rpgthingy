import requests
from lxml import etree
from urllib import request
import os
import sqlite3
from monster import get_urls, get_item_id
from combat import get_monster_id
from googletrans import Translator
import ujson as json
import re
import cairosvg

os.chdir(r'C:\Users\vctxi\PycharmProjects\rpgthingy')
url = 'https://wiki.melvoridle.com/index.php?title=Dungeons'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 '
                  'Safari/537.36'}
conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS dungeon
       (ID INT PRIMARY KEY     NOT NULL,
        name        TEXT    NOT NULL,
        loot_table        json    NOT NULL,
        monster        json    NOT NULL)''')
conn.commit()
translator = Translator(service_urls=[
    'translate.google.cn', ])
opener = request.build_opener()
opener.addheaders = [('User-agent',
                      'Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U;                                           en-GB) Presto/2.8.149 Version/11.10')]
request.install_opener(opener)


def get_data(url):
    stl = 0
    detail_url = 'https://wiki.melvoridle.com/' + str(url)
    resp = requests.get(detail_url, headers=headers)
    text = resp.text
    html = etree.HTML(text)
    name = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[1]/th/text()')[0].split()[0]
    id = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[3]/td/text()')[0].split()[2]
    monsters = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody//tr//td//span//a//text()')
    num = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody//tr//td[6]/text()')
    num2 = []
    for each in num:
        num2.append(each.split()[0])
    mid = []
    for each in monsters:
        mid.append(get_monster_id(each)[0])
    if id != "15":
        loot = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[4]/td/ul/li[2]/span/a[2]/text()')[0]
        coin = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[4]/td/ul/li[1]/span/text()')[0]
        coin = coin.replace(",", '')
    else:
        loot = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[4]/td/span/a[2]/text()')[0]
        coin = 0
        num2.pop(0)
    quantity = {}
    try:
        coin = int(coin)
        quantity["from"] = coin
        quantity["to"] = coin
    except:
        coin = list(map(str, re.findall(r'\d+', coin)))
        quantity["from"] = int(coin[0])
        quantity["to"] = int(coin[1])
    try:
        cape = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[4]/td/ul/li[3]/span/a[2]/text()')[0]
        cape = get_item_id(cape)[0]
    except:
        cape = None
        pass
    loot_table = {"chest": get_item_id(loot)[0], "coin": quantity, "cape": cape}
    loot_table = json.dumps(loot_table)
    res = {}
    for key in mid:
        for value in num2:
            res[key] = value
            num2.remove(value)
            break
    print(res)
    monster = json.dumps(res)
    print(monster)
    c = conn.cursor()
    c.execute('''insert or replace into dungeon (
        ID,
        name,
        monster,
        loot_table)
    values (
        ?,
        ?,
        ?,
        ?)''', (id, str(name), monster, loot_table,))
    conn.commit()


def main():
    detail_urls = get_urls(url)
    print(detail_urls)
    for each in detail_urls:
        get_data(each)


if __name__ == '__main__':
    main()
