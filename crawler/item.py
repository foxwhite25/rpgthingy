import requests
from lxml import etree
from urllib import request
import os
import sqlite3
from googletrans import Translator
import re
import cairosvg
from PIL import Image
from io import BytesIO


os.chdir(r'C:\Users\vctxi\PycharmProjects\rpgthingy')
url = 'https://wiki.melvoridle.com/index.php?title=Table_of_Items'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 '
                  'Safari/537.36'}
conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS itemlist
       (ID INT PRIMARY KEY     NOT NULL,
        name           TEXT    NOT NULL,
        price          INT    NOT NULL,
        cat          TEXT    NOT NULL,
        type          TEXT    NOT NULL,
        url          TEXT    NOT NULL);''')
conn.commit()
translator = Translator(service_urls=[
    'translate.google.cn', ])
opener = request.build_opener()
opener.addheaders = [('User-agent', 'Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10')]
request.install_opener(opener)

def get_urls(url):
    resp = requests.get(url, headers=headers)
    text = resp.text
    html = etree.HTML(text)
    detail_urls = []
    for urls in html.xpath(
            r'//*[@style="text-align: left;"]//@href'):
        detail_urls.append(urls)
    if detail_urls == []:
        for urls in html.xpath(
                r'//*[@id="mw-content-text"]/div/table[3]/tbody//@href'):
            detail_urls.append(urls)
    res = []
    [res.append(x) for x in detail_urls if x not in res]
    try:
        res.remove('/index.php?title=Combat_Triangle')
        res.remove('/index.php?title=Melee')
        res.remove('/index.php?title=Ranged')
    except ValueError:
        pass
    return res


def get_data(url):
    stl = 0
    detail_url = 'https://wiki.melvoridle.com/' + str(url)
    print(detail_url)
    resp = requests.get(detail_url, headers=headers)
    text = resp.text
    html = etree.HTML(text)
    name = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[1]/th/text()')[0]
    name = name.rstrip('\n')
    id = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[4]/td/text()')[0]
    id = [int(s) for s in id.split() if s.isdigit()][0]
    jpg = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[2]/td/span/a/img/@src')[0]
    cat = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[5]/td/a/text()')[0]
    coin = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[7]/td/text()')[1]
    type = html.xpath('// *[ @ id = "mw-content-text"] / div / table[2] / tbody / tr[6] / td/text()')[0]
    type = type.replace("Type: ","")
    coin = list(map(str, re.findall(r'\d+', coin)))
    coin2 = ""
    print(jpg)
    for n in coin:
        coin2 += n
    coin = int(coin2)
    os.chdir(r'C:\Users\vctxi\PycharmProjects\rpgthingy\icons')
    url1 = r'https://wiki.melvoridle.com' + jpg
    name1 = fr"C:\Users\vctxi\PycharmProjects\rpgthingy\svg\item\{id}.svg"
    img = request.urlretrieve(url1, name1)
    try:
        cairosvg.svg2png(url=img[0], write_to=fr"C:\Users\vctxi\PycharmProjects\rpgthingy\icons\item\{id}.png")
    except:
        name1 = fr"C:\Users\vctxi\PycharmProjects\rpgthingy\icons\item\{id}.png"
        img = request.urlretrieve(url1, name1)
    os.chdir(r'C:\Users\vctxi\PycharmProjects\rpgthingy')
    c = conn.cursor()
    c.execute('''insert or replace into itemlist (
        ID,
        cat,
        name,
        price,
        type,
        url)
    values (
        ?,
        ?,
        ?,
        ?,
        ?,
        ?)''', (id, cat, name, coin,type,url))
    conn.commit()
    print(f"Id:{id},名字:{name},分类:{cat},价格:{coin}")


def main():
    detail_urls = get_urls(url)
    for each in detail_urls:
        get_data(each)


if __name__ == '__main__':
    main()
