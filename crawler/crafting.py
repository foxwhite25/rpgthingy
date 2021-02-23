import requests
from lxml import etree
from urllib import request
import os
import sqlite3
from googletrans import Translator
import re
import ujson as json

os.chdir(r'C:\Users\vctxi\.hoshino')
url = 'https://wiki.melvoridle.com/index.php/Crafting'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 '
                  'Safari/537.36'}
conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS recipes
       (id INT PRIMARY KEY NOT NULL ,
       "to" json      NOT NULL,
        "from"           json    NOT NULL,
        time           INT    NOT NULL,
        exp          INT    NOT NULL,
        level            INT NOT NULL,
        skill TEXT NOT NULL );''')
conn.commit()
translator = Translator(service_urls=[
    'translate.google.cn', ])
opener = request.build_opener()
opener.addheaders = [('User-agent',
                      'Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10')]
request.install_opener(opener)


def list_to_int(num):
    for n in num:
        try:
            num[num.index(n)] = int(n)
        except:
            pass
    return num


def get_item_id(name):
    r = conn.execute(
        "SELECT id FROM itemlist WHERE name=? ", (name,)
    ).fetchall()[0]
    return r


def get_urls(url):
    resp = requests.get(url, headers=headers)
    text = resp.text
    html = etree.HTML(text)
    detail_urls = []
    for urls in html.xpath(
            '//*[@id="mw-content-text"]/div//table/tbody/tr/td[2]/a/@href'):
        detail_urls.append(urls)
    black_list = ['/index.php?title=Crafting_Skillcape', '/index.php?title=Caaarrrlll',
                  '/index.php?title=Crafting_Potion_I', '/index.php?title=Crafting_Potion_II',
                  '/index.php?title=Crafting_Potion_III', '/index.php?title=Crafting_Potion_IV']
    detail_urls = [item for item in detail_urls if item not in black_list]
    return detail_urls


def get_data(url):
    detail_url = 'https://wiki.melvoridle.com/' + str(url)
    print(detail_url)
    resp = requests.get(detail_url, headers=headers)
    text = resp.text
    html = etree.HTML(text)
    num = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[3]/td//text()')[:-1]
    name = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[1]/th/text()')[0].rstrip('\n')
    if len(num) == 1:
        num = html.xpath('//*[@id="mw-content-text"]/div/table[4]/tbody/tr[3]/td//text()')[:-1]
        quantity = html.xpath('//*[@id="mw-content-text"]/div/table[4]/tbody/tr[4]/td/text()')[0]
        xp = html.xpath('//*[@id="mw-content-text"]/div/table[4]/tbody/tr[5]/td/text()')[0].rstrip(' XP\n')
        time = html.xpath('//*[@id="mw-content-text"]/div/table[4]/tbody/tr[6]/td/text()')[0].rstrip('s\n')
        level = html.xpath('//*[@id="mw-content-text"]/div/table[4]/tbody/tr[2]/td/span/text()')[0].rstrip('\n').strip(
            'Level ')
    else:
        quantity = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[4]/td/text()')[0]
        xp = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[5]/td/text()')[0].rstrip(' XP\n')
        time = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[6]/td/text()')[0].rstrip('s\n')
        level = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[2]/td/span/text()')[0].rstrip('\n').strip(
            'Level ')
    for n in num:
        try:
            num.remove(' ')
        except:
            pass
    num = list_to_int(num)
    quantity = int(quantity)
    level = int(level)
    time = int(time)
    xp = int(xp)
    fr = {}
    to = {}
    a = 0
    for n in num:
        if a == 0:
            temp = n
            a = 1
            continue
        if a == 1:
            fr[get_item_id(n)[0]] = temp
            a = 0
    i = get_item_id(name)[0]
    to[get_item_id(name)[0]] = quantity
    fr = json.dumps(fr, indent=4)
    to = json.dumps(to, indent=4)
    c.execute('''insert or replace into recipes (id,'to','from','time','exp','level','skill')
    values (?,?,?,?,?,?,?)''', (i ,to, fr, time, xp, level, 'crafting'))
    conn.commit()


def main():
    detail_urls = get_urls(url)
    print(detail_urls)
    for each in detail_urls:
        get_data(each)


if __name__ == '__main__':
    main()
