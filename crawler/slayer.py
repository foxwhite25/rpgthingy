import requests
from lxml import etree
from urllib import request
import os
import sqlite3
from monster import get_urls
from combat import get_monster_id
from googletrans import Translator
import ujson as json
import re
import cairosvg

os.chdir(r'C:\Users\vctxi\PycharmProjects\rpgthingy')
url = 'https://wiki.melvoridle.com/index.php?title=Slayer_areas'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 '
                  'Safari/537.36'}
conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS slayer
       (ID INT PRIMARY KEY     NOT NULL,
        name        TEXT    NOT NULL,
        level        INT    NOT NULL,
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
    name = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[1]/th/text()')[0]
    id = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[3]/td/text()')[0].split()[3]
    level = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[4]/td/p/span/text()')[0].split()[1]
    monsters = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody//tr//td//span//a//text()')
    mid = []
    for each in monsters:
        mid.append(get_monster_id(each)[0])
    mid = json.dumps(mid)
    c = conn.cursor()
    c.execute('''insert or replace into slayer (
        ID,
        name,
        monster,
        level)
    values (
        ?,
        ?,
        ?,
        ?)''', (id, name, mid,level,))
    conn.commit()


def main():
    detail_urls = get_urls(url)
    for each in detail_urls:
        get_data(each)


if __name__ == '__main__':
    main()
