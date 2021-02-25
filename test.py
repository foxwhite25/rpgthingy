from collections import Counter

import ujson as json
import math
import os
import sqlite3
import textwrap
from PIL import Image, ImageFont, ImageDraw

os.chdir(r'C:\Users\vctxi\.hoshino')
conn = sqlite3.connect('data.db')
r = conn.execute(
    "SELECT id FROM recipes WHERE skill='符文铭刻' ",
).fetchall()
print(r)
a = {}
for each in r:
    a[each[0]] = 0
print(a)