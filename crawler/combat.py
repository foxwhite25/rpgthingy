import os
import sqlite3
from urllib import request
from monster import get_urls
from googletrans import Translator

os.chdir(r'C:\Users\vctxi\PycharmProjects\rpgthingy')
url = 'https://wiki.melvoridle.com/index.php?title=Combat_areas'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 '
                  'Safari/537.36'}
conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS combatarea
       (ID INT PRIMARY KEY     NOT NULL,
        monster        json    NOT NULL)''')
conn.commit()
translator = Translator(service_urls=[
    'translate.google.cn', ])
opener = request.build_opener()
opener.addheaders = [('User-agent',
                      'Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U;                                           en-GB) Presto/2.8.149 Version/11.10')]
request.install_opener(opener)


def p2f(x):
    return float(x.strip('%')) / 100


def get_monster_id(x):
    r = conn.execute(
        "SELECT ID FROM monsterlist WHERE name=?", (x,)
    ).fetchall()
    conn.commit()
    if not r:
        print("Cannot get id from " + x)
    return r[0]


def get_data(url):
    stl = 0
    detail_url = 'https://wiki.melvoridle.com/' + str(url)


def main():
    detail_urls = get_urls(url)
    print(detail_urls)


if __name__ == '__main__':
    main()
