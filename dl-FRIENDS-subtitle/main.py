import os
import pickle
import re
from typing import Optional, List, Dict

import requests as rq
from bs4 import BeautifulSoup as bs
from typing_extensions import Literal


def delete_tag(s):
    regex_pattern = r"<.*?>"
    s = re.sub(regex_pattern, "", s)
    """ recursive processing """
    if re.search(regex_pattern, s):
        delete_tag(s)
    else:
        return s


def ParseText(text_list: List[str]):
    block_type: Optional[str] = "quotes"  # part2(その2)以降の記事はセリフのブロックから始まるのでquotesに設定
    is_skip_line_cnt: int = 0
    eng_title: Optional[str] = None
    jpn_title: Optional[str] = None
    ori_title_in_jpn: Optional[str] = None
    eng_subtitle_list: List[Dict[str, str]] = []
    jpn_transcript_list: List[Dict[str, str]] = []
    jpn_commentary: List[str] = []
    name: Optional[str] = None
    eng_quote: Optional[str] = None
    jpn_quote: Optional[str] = None

    for line, next_line in zip(text_list[:-2], text_list[1:]):
        if line == "区切り" and next_line == "区切り":  # ここからは作者の通知なので不要
            break
        if is_skip_line_cnt > 0:
            is_skip_line_cnt -= 1
            continue

        # もしシーズン番号などがあればそのブロックはtitle
        if re.match(r"シーズン\s*[０-９0-9]+\s*第\s*[０-９0-9]+\s*話", line):
            block_type = "title"
            continue
        if block_type == "title":
            if eng_title is None or jpn_title is None:
                temp_title_list = line.replace("）", "").split("（")
                eng_title, jpn_title = [title.strip() for title in temp_title_list]
                continue
            if ori_title_in_jpn is None:
                ori_title_in_jpn = line.split("「")[1].replace("」", "")
                continue
            if line == "区切り":
                block_type = "quotes"
                continue

        # セリフのブロックquotes
        if block_type == "quotes":
            if line.find("[Scene: ") == 0:  # 場面の説明なので飛ばす
                is_skip_line_cnt = 1  # 次の1行も場面の解説(日本語)なので飛ばす
                continue
            # 話者の抽出
            if re.match(r"^([ァ-ヴー・]+):$", line) is not None:
                # eng_quoteとjpn_quoteがNoneでない場合(直前にセリフがある場合)はリストに格納
                if eng_quote is not None and jpn_quote is not None:
                    eng_subtitle_list.append({"name": name, "quote": eng_quote})
                    jpn_transcript_list.append({"name": name, "quote": jpn_quote})
                # 話者の名前を入れて、セリフを初期化
                name = line.replace(":", "")
                eng_quote = None
                jpn_quote = None
                continue
            # セリフ(英語)の抽出
            if "<strong>" in line:
                temp_quote = re.sub(r"</?strong>", "", line)
                if eng_quote is None:
                    eng_quote = temp_quote
                else:
                    eng_quote += "\n{}".format(temp_quote)
                continue
            # brackets(括弧)で囲まれている場合は、日本語のセリフの場合と、英語の場面説明の場合があるので判別
            if re.match(r"^[\(（].+[\)）]$", line) is not None:
                temp_quote = re.sub(r"^[ -~\n]+$", "", line).strip()
                if re.match(
                    r"^[a-zA-Z0-9!\-\/:-@¥[-`{-~\s]*$", temp_quote
                ):  # 英数字記号のみの場合は英語の場面説明
                    continue
                else:
                    if jpn_quote is None:
                        jpn_quote = temp_quote
                    else:
                        jpn_quote += "\n{}".format(temp_quote)
                    continue
            if line == "区切り":
                # eng_quoteとjpn_quoteがNoneでない場合(直前にセリフがある場合)はリストに格納
                if eng_quote is not None and jpn_quote is not None:
                    eng_subtitle_list.append({"name": name, "quote": eng_quote})
                    jpn_transcript_list.append({"name": name, "quote": jpn_quote})
                block_type = "commentary"
                continue

        # ブログの作者の解説
        if block_type == "commentary":
            if line == "区切り":
                temp_commentary = "\n{}".format(next_line)
                is_skip_line_cnt = 1  # すでに変数に入れてしまったので、次の行はスキップ
                jpn_commentary.append(temp_commentary)
                continue
            else:
                temp_commentary = delete_tag(line)
                jpn_commentary.append(temp_commentary)
                continue
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
        r"https://sitcom-friends-eng.seesaa.net/article/388471107.html"
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

        # 記事の中身を抽出して前処理
        # text_list: List[str] = soup.find("div", class_="text").text
        text_list: List[str] = list(map(str, soup.find("div", class_="text").contents))
        temp_text_list = [
            "区切り"
            if text1 == "<br/>" and text2 == "<br/>"
            else text1.replace("\u3000", " ").strip()
            for text1, text2 in zip(text_list[:-2], text_list[1:])
        ]
        organized_text_list = [text for text in temp_text_list if text != "<br/>"]

        # 記事を解析する
        (
            eng_title,
            jpn_title,
            ori_title_in_jpn,
            eng_subtitle_list,
            jpn_transcript_list,
            jpn_commentary,
        ) = ParseText(organized_text_list)
