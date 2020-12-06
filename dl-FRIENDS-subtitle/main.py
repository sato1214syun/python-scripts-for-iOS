import os
import pickle
import re

import requests as rq
from bs4 import BeautifulSoup as bs

base = os.path.dirname(os.path.abspath(__file__))
url = r"https://sitcom-friends-eng.seesaa.net/article/388471106.html"
rel_res_pickle_path = r"./res.pickle"
res_pickle_path = os.path.normpath(os.path.join(base, rel_res_pickle_path))

base = os.path.dirname(os.path.abspath(__file__))
url = r"https://sitcom-friends-eng.seesaa.net/article/388471106.html"


rel_res_pickle_path = r"./res.pickle"
res_pickle_path = os.path.normpath(os.path.join(base, rel_res_pickle_path))
if os.path.exists(res_pickle_path):
    with open(res_pickle_path, "rb") as f:
        res = pickle.load(f)
else:
    headers_dict = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"
    }
    res = rq.get(url, headers=headers_dict)
    print(res.status_code)
    if res.status_code == 200:
        with open(res_pickle_path, "wb") as f:
            pickle.dump(res, f)


soup: bs = bs(res.content, "lxml")
title = soup.title.text
regex_pattern = r".+フレンズ(\d)-(\d+)[あ-ん]+(\d+).+"
match_group_list = re.match(regex_pattern, title)
season = match_group_list.group(1)
chapter = match_group_list.group(2)
part = match_group_list.group(3)
print("season: ", match_group_list.group(1))
print("chapter: ", match_group_list.group(2))
print("part: ", match_group_list.group(3))
list = soup.find_all(
    "a",
    text=re.compile(
        ".+フレンズ{}-{}[あ-ん]+{}.+".format(str(season), str(chapter), str(int(part) + 1))
    ),
)
print(list)
