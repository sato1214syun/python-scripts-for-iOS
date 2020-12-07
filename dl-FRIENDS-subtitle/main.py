import os
import pickle
import re
from typing import Optional, List, Dict

import requests as rq
from bs4 import BeautifulSoup as bs
from typing_extensions import Literal


def ParseText(text_list: List[str]):
    is_first_part: bool = False
    is_skip_line_cnt: int = 0
    is_in_quote: bool = False
    is_in_jpn_quote: bool = False
    eng_title: Optional[str] = None
    jpn_title: Optional[str] = None
    ori_title_in_jpn: Optional[str] = None
    eng_subtitle_list: List[Dict[str, str]] = []
    jpn_transcript_list: List[Dict[str, str]] = []
    jpn_commentary: List[str] = []
    name: Optional[str] = None
    eng_quote: Optional[str] = None
    jpn_quote: Optional[str] = None

    for line in text_list:
        if "（Rach" in line:
            break
        if is_skip_line_cnt > 0:
            is_skip_line_cnt -= 1
            continue
        if re.match(r"シーズン\s*[０-９0-9]+\s*第\s*[０-９0-9]+\s*話", line):
            is_first_part = True
            continue
        if is_first_part is True and (eng_title is None or jpn_title is None):
            temp_title_list = line.replace("）", "").split("（")
            eng_title, jpn_title = [title.strip() for title in temp_title_list]
            continue
        if is_first_part is True and ori_title_in_jpn is None:
            ori_title_in_jpn = line.split("「")[1].replace("」", "")
            continue
        if line.find("[Scene: ") == 0:  # 場面の説明なので飛ばす
            is_skip_line_cnt = 1  # 次の1行も場面の解説(日本語)なので飛ばす
            continue
        if line.find("(") == 0:  # 場面説明なのでスキップ
            continue

        # 1セリフ終了の場合は変数に格納し、フラグを初期化
        if is_in_quote is True and is_in_jpn_quote is True and "（" not in line:
            eng_subtitle_list.append({"name": name, "quote": eng_quote})
            jpn_transcript_list.append({"name": name, "quote": jpn_quote})
            is_in_quote = False
            is_in_jpn_quote = False

        # 話者とセリフの抽出
        # 話者
        matched_group = re.match(r"^([ァ-ヴー・]+):\s?$", line)
        if matched_group is not None:
            is_in_quote = True
            name = matched_group.group(1)
            eng_quote = None
            jpn_quote = None
            continue
        # セリフ(英語)
        if is_in_quote is True and "<strong>" in line:
            temp_quote = re.sub(r"</?strong>", "", line)
            if eng_quote is None:
                eng_quote = temp_quote
            else:
                eng_quote += "\n{}".format(temp_quote)
            continue
        # セリフ(日本語)
        if is_in_quote is True and line.find("（") == 0:
            is_in_jpn_quote = True
            temp_quote = re.sub(r"[（）]", "", line).strip()
            if jpn_quote is None:
                jpn_quote = temp_quote
            else:
                jpn_quote += "\n{}".format(temp_quote)
            continue

        # ブログの作者の解説
        jpn_commentary.append(line)
    return (
        eng_title,
        jpn_title,
        ori_title_in_jpn,
        eng_subtitle_list,
        jpn_transcript_list,
        jpn_commentary,
    )


if __name__ == "__main__":
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
    headers_dict: Dict[str, str] = {"User-Agent": user_agent}

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
        if os.path.exists(res_pickle_path) is False:
            with open(res_pickle_path, "wb") as f:
                pickle.dump(res, f)

        # 記事の中身を解析する
        text_list: List[str] = list(map(str, soup.find("div", class_="text").contents))
        text_list = [
            text.replace("\u3000", " ").strip()
            for text in text_list
            if re.match(r"^<(?!strong).+>.*$|<div.+|\n", text) is None
        ]
        (
            eng_title,
            jpn_title,
            ori_title_in_jpn,
            eng_subtitle_list,
            jpn_transcript_list,
            jpn_commentary,
        ) = ParseText(text_list)
        print(eng_title)
