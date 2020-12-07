import os
import pickle
import re

import requests as rq
from bs4 import BeautifulSoup as bs
from typing_extensions import Literal

first_part_url: Literal = (
    r"https://sitcom-friends-eng.seesaa.net/article/388471106.html"
)
regex_pattern1: Literal = r"(^https?://.+/)\d+\.html"
base_url: str = re.match(regex_pattern1, first_part_url).group(1)
first_article_no: int = int(first_part_url.replace(base_url, "").split(".")[0])
user_agent: str = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/78.0.3904.97 Safari/537.36"
)
headers_dict: dict = {"User-Agent": user_agent}

# pickleの保存先
base: str = os.path.dirname(os.path.abspath(__file__))
pickle_save_dir_path = os.path.normpath(os.path.join(base, "temp_data"))
os.makedirs(pickle_save_dir_path, exist_ok=True)


target_season = None
target_episode = None
article_no = first_article_no - 1

while True:
    # 次のarticle_noをセット
    article_no += 1
    pickle_file_name: str = "{}.pickle".format(article_no)
    res_pickle_path: str = os.path.normpath(
        os.path.join(pickle_save_dir_path, pickle_file_name)
    )
    # その記事番号のpickleがある場合
    if os.path.exists(res_pickle_path):
        with open(res_pickle_path, "rb") as f:
            res = pickle.load(f)
    else:
        # urlを生成してhtmlを読み込む
        article_url = base_url + str(article_no) + ".html"
        res = rq.get(article_url, headers=headers_dict)

    # htmlが正常に読み込めなかったらスキップ
    if res.status_code != 200:
        continue

    # beautifulsoupでタイトルを解析
    soup: bs = bs(res.content, "lxml")
    title: str = soup.title.text
    regex_pattern2: Literal = r".+フレンズ(\d)-(\d+)[あ-ん]+(\d+).*"
    match_group_list = re.match(regex_pattern2, title)

    # ---以下使える記事かどうかの判定---
    # 正規表現のマッチがない場合(エピソードと関係ない記事の場合)はスキップ
    if match_group_list is None:
        continue
    # 正規表現とマッチした場合(何かしらのエピソードの記事の場合)は
    # シーズン、エピソード、パートを取得
    season = match_group_list.group(1)
    episode = match_group_list.group(2)
    part = match_group_list.group(3)
    print("S{}E{}-{}の記事を読み込んでいます。。。".format(season, episode, part))
    # 最初の記事の場合はターゲットとして設定
    if target_season is None and target_episode is None:
        target_season = season
        target_episode = episode
    # ターゲット(初期値)と異なるシーズン＆エピソードの場合は終了
    elif target_season != season or target_episode != episode:
        print("他のエピソードの記事まで到達したので終了します")
        break
    # ---ここまで---

    # 使用する記事の場合はpickleを保存
    with open(res_pickle_path, "wb") as f:
        pickle.dump(res, f)
    # 記事の中身を解析する
