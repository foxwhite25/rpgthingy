import re
from urllib import request

import requests
from bs4 import BeautifulSoup

site = 'https://wiki.melvoridle.com/index.php?title=Mining'

response = requests.get(site)

soup = BeautifulSoup(response.text, 'html.parser')
img_tags = soup.find_all('img')
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 '
                  'Safari/537.36'}
urls = [img['src'] for img in img_tags]
opener = request.build_opener()
opener.addheaders = [('User-agent',
                      'Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10')]
request.install_opener(opener)

for url in urls:
    url1 = r'https://wiki.melvoridle.com' + url
    print(url1)
    try:
        img = request.urlretrieve(url1, r'C:\Users\vctxi\Desktop\XCW\hoshino\hoshino\modules\rpgthingy\svg\mini' + url[
                                                                                                                   12:].replace(
            "_", ' ').replace('%28', '').replace('%29', ''))
    except:
        pass
