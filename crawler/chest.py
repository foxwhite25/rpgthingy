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
url = 'https://wiki.melvoridle.com/index.php?title=Chest_Loot_Tables'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 '
                  'Safari/537.36'}
conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS chest
       (ID INT PRIMARY KEY     NOT NULL,
        loot_table        json    NOT NULL)''')
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
            r'//span/a[2]/text()'):
        detail_urls.append(urls)
    blacklist = []
    for urls in html.xpath(
            r'//*[@id="mw-content-text"]/div//table//tbody/tr/td/span/a/text()'):
        blacklist.append(urls)
    detail_urls = list(set(detail_urls)-set(blacklist))
    for each in detail_urls:
        a.append(get_url_item(each)[0])
    return a


def get_data(url):
    stl = 0
    detail_url = 'https://wiki.melvoridle.com/' + str(url)
    resp = requests.get(detail_url, headers=headers)
    text = resp.text
    html = etree.HTML(text)
    num = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr/td[4]/text()')
    items = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr/td[1]/span/a[2]/text()')
    quantity = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr/td[2]/text()')
    id = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[4]/td/text()')[0]
    id = [int(s) for s in id.split() if s.isdigit()][0]
    chance = []
    for each in num:
        chance.append(p2f(each))
    res = {}
    for key in items:
        nums = items.index(key)
        try:
            q = int(quantity[nums])
            up = q
            down = q
        except:
            q = list(map(str, re.findall(r'\d+', quantity[nums])))
            up = int(q[0])
            down = int(q[1])
        key = get_item_id(key)[0]
        res[key] = float(chance[nums]) * (float(up) + float(down))/2
    res = json.dumps(res)
    c = conn.cursor()
    c.execute('''insert or replace into chest (
        ID,
        loot_table)
    values (
        ?,
        ?)''', (id, res,))
    conn.commit()


def main():
    detail_urls = get_urls(url)
    print(detail_urls)
    for each in detail_urls:
        get_data(each)


if __name__ == '__main__':
    main()
