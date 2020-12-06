import os
import pickle
import re

import requests as rq
from bs4 import BeautifulSoup as bs

base = os.path.dirname(os.path.abspath(__file__))
fist_part_url = r"https://sitcom-friends-eng.seesaa.net/article/388471106.html"
rel_res_pickle_path = r"./res.pickle"
res_pickle_path = os.path.normpath(os.path.join(base, rel_res_pickle_path))

user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/78.0.3904.97 Safari/537.36"
)
headers_dict = {"User-Agent": user_agent}
if os.path.exists(res_pickle_path):
    with open(res_pickle_path, "rb") as f:
        res = pickle.load(f)
else:
    res = rq.get(fist_part_url, headers=headers_dict)
    if res.status_code == 200:
        with open(res_pickle_path, "wb") as f:
            pickle.dump(res, f)


soup: bs = bs(res.content, "lxml")
title = soup.title.text
regex_pattern = r".+フレンズ(\d)-(\d+)[あ-ん]+(\d+).*"
match_group_list = re.match(regex_pattern, title)
season = match_group_list.group(1)
episode = match_group_list.group(2)
part = match_group_list.group(3)
print("season: ", match_group_list.group(1))
print("episode: ", match_group_list.group(2))
print("part: ", match_group_list.group(3))

part_link_list = [fist_part_url]
while True:
    part = str(int(part) + 1)
    print("part:", part)
    next_part_info = soup.find(
        "a", text=re.compile(".+フレンズ{}-{}[あ-ん]+{}.*".format(season, episode, part))
    )
    if next_part_info:
        # time.sleep(2)
        next_part_url = next_part_info.attrs["href"]
        part_link_list.append(next_part_url)
        res = rq.get(next_part_url, headers=headers_dict)
        print(res.status_code)
        soup: bs = bs(res.content, "lxml")
    else:
        break

print(part_link_list)
