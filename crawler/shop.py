import requests
from lxml import etree
from urllib import request
import os
import sqlite3
from googletrans import Translator
import re
import ujson as json

os.chdir(r'C:\Users\vctxi\.hoshino')
url = 'https://wiki.melvoridle.com/index.php/Shop'
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
    black_list = ['/index.php?title=Bank_Slot']
    detail_urls = [item for item in detail_urls if item not in black_list]
    return detail_urls


def get_data(url):
    detail_url = 'https://wiki.melvoridle.com/' + str(url)
    print(detail_url)
    resp = requests.get(detail_url, headers=headers)
    text = resp.text
    html = etree.HTML(text)
    name = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[1]/th/text()')[0]
    num = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[5]/td/p//text()')
    u = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[5]/td/p//@href')
    black_list = ['\n', '\xa0']
    num = [item for item in num if item not in black_list]
    if not num:
        num = html.xpath('//*[@id="mw-content-text"]/div/table[4]/tbody/tr[2]/td/span/text()')
        u = ['coin']
    print(num)
    for item in num:
        a = item.replace(',', '')
        a = a.replace('\xa0', '')
        try:
            num[num.index(item)] = int(a)
        except:
            num[num.index(item)] = a
    for n, i in enumerate(u):
        if i == '/index.php?title=Currency' or i == '/index.php?title=File:Coins.svg':
            u[n] = 'coin'
    print(name, num, u)


def main():
    detail_urls = get_urls(url)
    print(detail_urls)
    # for each in detail_urls:
    # get_data(each)
    print(json.dumps({"159": 2,'388':10}))


if __name__ == '__main__':
    main()
