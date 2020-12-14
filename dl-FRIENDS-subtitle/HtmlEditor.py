import os
from copy import deepcopy
from shutil import copy2, copytree, rmtree
from typing import Dict, List
import re

from bs4 import BeautifulSoup as bs

current_dir, _ = os.path.split(__file__)
root_path: str = os.path.join(current_dir, r"templates/")
index_path = os.path.join(root_path, r"index.html")
article_dir_path = os.path.join(root_path, r"article/")
ep_template_path = os.path.join(root_path, r"original/episode_template.html")
backup_dir_path = os.path.join(current_dir, r"templates/backup/")


def EditIndexHtml(season: int, episode: int, title: str):
    # index.htmlをバックアップ
    back_up_index_path = os.path.join(backup_dir_path, "index.html")
    os.makedirs(backup_dir_path, exist_ok=True)
    copy2(index_path, back_up_index_path)
    # index.htmlを開いてBeautifulSoupで読み込み
    with open(index_path, "r", encoding="utf-8") as f:
        index_html = f.read()
    soup: bs = bs(index_html, "lxml")

    # Main Section
    article_link = "article/season{0}/{0}_{1}.html".format(season, episode)
    # articleタグ内のliタグを検索し、要素番号から編集するタグを決定
    article_list = soup.find_all("article")
    preparing_article_list = article_list[season - 1].find_all("a")
    target1 = preparing_article_list[episode - 1]
    # ターゲットのタグを編集
    target1.attrs["href"] = article_link
    target1.string = "{}-{}. {}".format(str(season), str(episode), title)

    # Sidebar Menuの編集
    text_regex_pattern = re.compile(r"^\s*Season {}\s*$".format(season))
    opener_tag = soup.find("span", class_="opener", text=text_regex_pattern)
    ul_tag = opener_tag.find_next("ul", class_="alt")
    sidebar_a_tag_list = ul_tag.find_all("a")
    target2 = sidebar_a_tag_list[episode - 1]
    # ターゲットのタグを編集
    target2.attrs["href"] = article_link
    target2.string = "{}-{}. {}".format(str(season), str(episode), title)

    # index.htmlを保存
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(soup.prettify(formatter="html5"))

    sidebar_tag = soup.find("div", id="sidebar")
    return sidebar_tag


def EditArticleHtml(
    season: int,
    episode: int,
    title: str,
    subtitle: List[List[Dict[str, str]]],
    commentary_list: List[List[str]],
):
    # episodeディレクトリをバックアップ
    backup_article_dir_path = os.path.join(backup_dir_path, "article")
    if os.path.exists(backup_article_dir_path):
        rmtree(backup_article_dir_path)  # ディレクトリがすでに存在していたら削除
    copytree(article_dir_path, backup_article_dir_path)
    # episode_template.htmlを開いてBeautifulSoupで読み込み
    with open(ep_template_path, "r", encoding="utf-8") as f:
        episode_template_html = f.read()
    soup: bs = bs(episode_template_html, "lxml")

    # Main Section
    # ページタイトルを変更
    soup.title.string = "{}-{} {} - Let's learn English with F･R･I･E･N･D･S".format(
        season, episode, title
    )
    # 見出しタイトルを追加
    insert_pos_s_ep_numbering = soup.find("header", class_="main")
    new_tag = soup.new_tag("h3")
    new_tag.string = 'Season {} Episode {} "{}"'.format(season, episode, title)
    insert_pos_s_ep_numbering.append(new_tag)
    # 見出し画像のパスを指定
    img_tag = soup.find("img")
    img_tag.attrs["src"] = "../../assets/images/season{}.jpg".format(season)
    # タグを追加していく
    for part_no, subtitle_list in enumerate(subtitle, 1):
        insert_pos_for_part = soup.find("section")
        # 一番外側のdivをsection内に追記
        new_tag = soup.new_tag("div", attrs={"class": "part"})
        insert_pos_for_part.append(new_tag)
        # part_noを追記
        insert_pos_for_part_no = soup.find_all("div", class_="part")[part_no - 1]
        new_tag = soup.new_tag("h4")
        new_tag.string = "Part {}".format(part_no)
        insert_pos_for_part_no.append(new_tag)
        # セリフのブロックの大枠div, box-container-outer-を追記
        new_tag = soup.new_tag("div", attrs={"class": "box-container-outer"})
        insert_pos_for_part_no.append(new_tag)
        # 話者ごとにセリフのタグを追記していく
        for quote_no, subtitle_dict in enumerate(subtitle_list):
            speaker = subtitle_dict["speaker"]
            en_quote = subtitle_dict["en"]
            jp_quote = subtitle_dict["jp"]
            # 話者ごとの区分け用のdiv,box-container-middleを追記
            insert_pos_for_subtitle = soup.find_all(
                "div", class_="box-container-outer"
            )[part_no - 1]
            new_tag = soup.new_tag("div", attrs={"class": "box-container-middle"})
            insert_pos_for_subtitle.append(new_tag)
            # セリフのタグを1セリフ分追記
            insert_pos_for_subtitle = insert_pos_for_subtitle.find_all(
                "div", class_="box-container-middle"
            )[quote_no]
            # 話者名を追加
            new_tag = soup.new_tag("div", attrs={"class": "speaker"})
            new_tag.string = speaker
            insert_pos_for_subtitle.append(new_tag)
            # セリフの枠div, box-container-innerを追記
            new_tag = soup.new_tag("div", attrs={"class": "box-container-inner"})
            insert_pos_for_subtitle.append(new_tag)
            # セリフ(English, Japanese)を追記
            insert_pos_for_each_lng_quotes = insert_pos_for_subtitle.find(
                "div", class_="box-container-inner"
            )
            new_tag = soup.new_tag("div", attrs={"class": "en_quote"})
            new_tag.string = en_quote
            insert_pos_for_each_lng_quotes.append(new_tag)
            new_tag = soup.new_tag("div", attrs={"class": "jp_quote"})
            new_tag.string = jp_quote
            insert_pos_for_each_lng_quotes.append(new_tag)
        # commentaryを追記
        new_tag = soup.new_tag("h5")
        new_tag.string = "Commentary"
        insert_pos_for_part_no.append(new_tag)
        # commentary用のblockquoteを追記
        new_tag = soup.new_tag("blockquote")
        insert_pos_for_part_no.append(new_tag)
        insert_pos_for_comm_paragraph = soup.find_all("blockquote")[part_no - 1]
        for paragraph in commentary_list[part_no - 1]:
            new_tag = soup.new_tag("p")
            new_tag.string = paragraph
            insert_pos_for_comm_paragraph.append(new_tag)

    # この記事のパスを作成
    ep_html_name = "{}_{}.html".format(season, episode)
    season_dir_path = os.path.join(article_dir_path, "season{}".format(season))
    episode_html_path = os.path.join(season_dir_path, ep_html_name)
    # episode用のhtmlを保存
    os.makedirs(article_dir_path, exist_ok=True)
    os.makedirs(season_dir_path, exist_ok=True)
    with open(os.path.join(episode_html_path), "w", encoding="utf-8") as f:
        f.write(soup.prettify(formatter="html5"))


def SidebarLinkConverter(sidebar_tag_in_index):
    # template/article/内の全てのepisode/htmlのパスを取得
    ep_html_path_list: List[str] = []
    for cur_dir, _, file_name_list in os.walk(current_dir):
        for file_name in file_name_list:
            ep_html_path_list.append(os.path.join(cur_dir, file_name))

    for ep_html_path in ep_html_path_list:
        sidebar_tag_in_ep_html = deepcopy(sidebar_tag_in_index)
        a_tag_list = sidebar_tag_in_ep_html.find_all("a")
        index_dir_path = os.path.dirname(index_path)
        for a_tag in a_tag_list:
            rel_link_in_index = a_tag.attrs["href"].string
            abs_link_in_index = os.path.normpath(
                os.path.join(index_dir_path, rel_link_in_index)
            )
            rel_link_for_ep_html = os.path.relpath(abs_link_in_index, ep_html_path)
            a_tag.attrs["href"] = rel_link_for_ep_html
        # episode.htmlを読み込み
        with open(ep_html_path, "r", encoding="utf-8") as f:
            ep_html = f.read()
        soup: bs = bs(ep_html, "lxml")
        ori_sidebar_tag = soup.find("div", id="sidebar")
        ori_sidebar_tag.replace_with(sidebar_tag_in_ep_html)

        # 保存
        with open(os.path.join(ep_html_path), "w", encoding="utf-8") as f:
            f.write(soup.prettify(formatter="html5"))


if __name__ == "__main__":
    subtitle: List[List[Dict[str, str]]] = [
        [
            {
                "speaker": "speaker1",
                "en_quote": "English quote1",
                "jp_quote": "Japanese Quote1",
            },
            {
                "speaker": "speaker2",
                "en_quote": "English quote2",
                "jp_quote": "Japanese Quote2",
            },
        ],
        [
            {
                "speaker": "speaker3",
                "en_quote": "English quote3",
                "jp_quote": "Japanese Quote3",
            },
            {
                "speaker": "speaker4",
                "en_quote": "English quote4",
                "jp_quote": "Japanese Quote4",
            },
        ],
    ]

    commentary_list: List[List[str]] = [
        ["part1_commentary1.part1_commentary2", "part1_commentary3.part1_commentary4"],
        ["part2_commentary1.part2_commentary2", "part2_commentary3.part2_commentary4"],
    ]
    EditArticleHtml(
        season=3,
        episode=11,
        title="test",
        subtitle=subtitle,
        commentary_list=commentary_list,
    )
    sidebar_tag_in_index = EditIndexHtml(season=3, episode=11, title="test")
    SidebarLinkConverter(sidebar_tag_in_index)
