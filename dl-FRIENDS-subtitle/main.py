import os
import pickle
import re
from typing import Dict, List, Optional

import requests as rq
from bs4 import BeautifulSoup as bs
from requests.models import Response

from HtmlEditor import EditArticleHtml, EditIndexHtml, SidebarLinkConverter
from HtmlParser import ParseText


def ReadWebPage(
    article_url: str,
    pickle_file_path: str,
) -> Optional[Response]:
    # その記事番号のpickleがある場合
    if os.path.exists(pickle_file_path):
        with open(pickle_file_path, "rb") as f:
            res = pickle.load(f)
    else:
        # urlを生成してhtmlを読み込む

        res = rq.get(article_url, headers=headers_dict)
        # htmlが正常に読み込めなかったらエラー
        if res.status_code != 200:
            res = None
    return res


if __name__ == "__main__":
    # first_part_url: str = sys.argv[0]
    first_part_url = input("変換したい記事のURLを入力:")

    regex_for_url: str = r"(^https?://.+/)\d+\.html"
    match_group = re.match(regex_for_url, first_part_url)
    if match_group is None:
        raise ValueError("参照しているページのurlが正しくありません")

    # requests用のパラメータの準備
    web_page_base_url = match_group.group(1)
    article_no: str = first_part_url.replace(web_page_base_url, "").split(".")[0]
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/78.0.3904.97 Safari/537.36"
    )
    headers_dict: Dict[str, str] = {"User-Agent": user_agent}

    # pickleの保存先
    current_dir: str = os.path.dirname(os.path.abspath(__file__))
    pickle_save_dir_path = os.path.normpath(os.path.join(current_dir, "temp_data"))
    os.makedirs(pickle_save_dir_path, exist_ok=True)

    # webページをurlかPickleから読み込み
    article_url = web_page_base_url + str(article_no) + ".html"
    pickle_file_path = os.path.join(
        pickle_save_dir_path, "{}.pickle".format(article_no)
    )
    res = ReadWebPage(article_url, pickle_file_path)

    soup: bs = None
    if res is None:
        ValueError("urlが正しくありません")
    else:
        # beautifulsoupでタイトルを解析
        soup = bs(res.content, "lxml")
    page_title: str = soup.title.text
    regex_for_page_title: str = r".+フレンズ(\d)-(\d+)[改あ-ん]+(\d+).*"
    matched_group_list = re.match(regex_for_page_title, page_title)
    if matched_group_list is None:
        raise ValueError("正しくないwebページが使用されていませんか？")

    # 正規表現とマッチした場合(何かしらのエピソードの記事の場合)は
    # シーズン、エピソード、パートを取得
    target_season: str = matched_group_list.group(1)
    target_episode: str = matched_group_list.group(2)
    first_part: str = matched_group_list.group(3)
    # episodeのpart1(その1)か確認
    if first_part not in ["1", "01", "001"]:
        raise ValueError("エピソードのその1の記事を使用して下さい")

    # 使用可能な記事の場合はpickleを保存
    if os.path.exists(pickle_file_path) is False:
        with open(pickle_file_path, "wb") as f:
            pickle.dump(res, f)

    # ---以下各記事の読み込みと解析---
    ep_title: Dict[str, str] = {}
    ep_subtitle: List[List[Dict[str, str]]] = []
    ep_commentary: List[List[str]] = []
    article_no = str(int(article_no) - 1)
    while True:
        article_no = str(int(article_no) + 1)
        # webページを読み込み
        article_url = web_page_base_url + str(article_no) + ".html"
        pickle_file_path = os.path.join(pickle_save_dir_path, article_no)
        res = ReadWebPage(article_url, pickle_file_path)

        # htmlが正常に読み込めなかったらスキップ
        if res is None:
            continue

        # beautifulsoupで読み込み
        soup = bs(res.content, "lxml")

        # ---以下使える記事かどうかの判定---
        matched_group_list = re.match(regex_for_page_title, soup.title.text)
        if matched_group_list is None:
            continue

        # 正規表現とマッチした場合(何かしらのエピソードの記事の場合)は
        # シーズン、エピソード、パートを取得
        season: str = matched_group_list.group(1)
        episode: str = matched_group_list.group(2)
        part: str = matched_group_list.group(3)
        # ターゲット(初期値)と異なるシーズン＆エピソードの場合は終了
        if int(season) == int(target_season) + 1 or (
            int(episode) == int(target_episode) + 1
        ):
            print("他のエピソードの記事まで到達したので終了します")
            break
        if season != target_season or episode != target_episode:
            continue
        # ---ここまで---

        # 使用する記事の場合はpickleを保存
        if os.path.exists(pickle_file_path) is False:
            with open(pickle_file_path, "wb") as f:
                pickle.dump(res, f)

        # 記事の中身を抽出して前処理
        text_list: List[str] = list(map(str, soup.find("div", class_="text").contents))
        temp_text_list = [
            "区切り"
            if text1 == "<br/>" and text2 == "<br/>"
            else text1.replace("\u3000", " ").strip()
            for text1, text2 in zip(text_list[:-2], text_list[1:])
        ]
        temp_text_list = [text for text in temp_text_list if text != "<br/>"]

        # 作者からコメント以降を削除
        organized_text_list = []
        for line in temp_text_list:
            if "Rach からのお願い" in line or "Rach からのお詫び" in line:
                break
            organized_text_list.append(line)

        # 記事を解析する
        print("\nシーズン{}エピソード{}その{}の記事を解析しています。。。".format(season, episode, part))
        temp_ep_title, part_subtitle, part_commentary = ParseText(organized_text_list)

        if temp_ep_title is not None:
            ep_title = temp_ep_title
        ep_subtitle.append(part_subtitle)
        ep_commentary.append(part_commentary)

    print("\nシーズン{}エピソード{}の記事を作成しています。。。".format(target_season, target_episode))
    EditArticleHtml(
        season=int(target_season),
        episode=int(target_episode),
        title=ep_title["en"],
        subtitle=ep_subtitle,
        commentary_list=ep_commentary,
    )
    print("\nindex.htmlを修正しています。。。")
    sidebar_tag_in_index = EditIndexHtml(
        season=int(target_season),
        episode=int(target_episode),
        title=ep_title["en"],
    )
    print("\n既存の記事のサイドバーのリンクを修正しています")
    SidebarLinkConverter(sidebar_tag_in_index)

    print("完了しました")
