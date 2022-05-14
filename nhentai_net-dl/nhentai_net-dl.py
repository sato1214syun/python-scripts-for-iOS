import os
import os.path
import pickle
from platform import platform
import re
import shutil
import sys
import urllib.parse

import requests as rq
from NHentai import NHentai
from NHentai.entities.doujin import Doujin
from tqdm import tqdm


# HTMLページの取得・タグの抜き出しの処理後、画像収集を行う
def CollectImage(url):

    print("画像ダウンロードを開始します...")  # ダウンロード処理開始のメッセージ
    # extract mediaData
    doujin_info = GetMediaData(url)
    img_info_dict = GetImageInfo(doujin_info)  # get img data
    downloadByPython(img_info_dict)
    return


def GetMediaData(url) -> Doujin:
    # extract gURL
    regex_pat = re.compile(r"https?://nhentai.net/g/([0-9]+)/*[0-9]*")
    if (match := regex_pat.match(url)) is not None:
        id: str = match.group(1)
    else:
        sys.exit("Error! : Not a nhentai.net url")

    # mediaDataを取得
    print("情報を読み込み中です。。。")
    nhentai = NHentai()
    doujin_info = nhentai.get_doujin(id=id)
    return doujin_info


def GetImageInfo(doujin_info: Doujin):
    print("画像urlを取得中...")
    img_info_dict = {}
    if jp_title := doujin_info.title.japanese:
        img_info_dict["title"] = jp_title.replace("/", "_")
    else:
        img_info_dict["title"] = doujin_info.title.english.replace("/", "_")

    img_info_dict["num_of_pages"] = doujin_info.total_pages
    img_info_list = doujin_info.images
    file_ext_list = [img_info.mime for img_info in img_info_list]

    img_info_dict["url_ext_list"] = {
        img_info.src: ext for img_info, ext in zip(img_info_list, file_ext_list)
    }

    return img_info_dict


def downloadByPython(img_info_dict):
    num_of_pages = img_info_dict["num_of_pages"]
    title = img_info_dict["title"]
    headers = {"User-Agent": "Magic Browser", "Accept-encoding": "gzip"}
    work_dir = (
        "/private/var/mobile/Library/Mobile Documents/com~apple~CloudDocs/Downloads"
    )
    if os.path.exists(work_dir) is False:
        work_dir = os.path.dirname(__file__)
    zip_save_dir = os.path.join(work_dir, "nsfw_book")
    save_dir = os.path.join(zip_save_dir, title)

    print("画像をダウンロード中...")
    os.makedirs(save_dir, exist_ok=True)

    if "background" in sys.modules:
        with bg.BackgroundTask() as b:
            Download(
                img_info_dict, save_dir, zip_save_dir, title, num_of_pages, headers
            )
            b.stop()
    else:
        Download(img_info_dict, save_dir, zip_save_dir, title, num_of_pages, headers)


def Download(img_info_dict, save_dir, zip_save_dir, title, num_of_pages, headers):
    # ページ数の桁数を決定する
    std_page_digit = 3
    page_digit = len(str(num_of_pages))
    if page_digit > std_page_digit:
        std_page_digit = page_digit + 1

    # 画像をダウンロードする
    for page_cnt, (dl_url, ext) in enumerate(
        img_info_dict["url_ext_list"].items(), start=1
    ):
        page_no = str(page_cnt).zfill(std_page_digit)  # 桁数そろえ
        file_name = "{}.{}".format(page_no, ext)
        try:
            while True:
                save_path = os.path.join(save_dir, file_name)  # 保存パスを決定
                if os.path.isfile(save_path):  # 同名ファイルが存在する場合はダウンロードをスキップ
                    print("\n{}枚目の画像は保存済みなのでスキップします".format(page_cnt))
                    raise Exception()
                # 画像をダウンロード
                try:
                    res = rq.get(dl_url, headers=headers, stream=True, timeout=5)
                    break
                except rq.Timeout:
                    print("\nタイムアウトのため{}枚目の画像をスキップします".format(page_cnt))

            # 有効なurlから画像をダウンロード
            if res.status_code != 200:  # if invalid url
                continue
            file_size = int(res.headers["content-length"])
            chunk = 1
            chunk_size = 1024
            num_bars = int(file_size / chunk_size)
            progress = "{}/{}枚".format(page_cnt, num_of_pages)
            with open(save_path, "wb") as f:
                for chunk in tqdm(
                    res.iter_content(chunk_size=chunk_size),
                    total=num_bars,
                    unit="KB",
                    desc=progress,
                    leave=True,
                ):
                    f.write(chunk)
        except Exception:
            # print("\nダウンロード中にエラーが発生しています原因を調査してください")
            """
            except Exception as e:
                if e:
                    print('=== エラー内容 ===')
                    print('type:' + str(type(e)))
                    print('args:' + str(e.args))
                    print('message:' + e.message)
                    print('e自身:' + str(e))
            """
            continue
    # zipに圧縮
    print("\n画像フォルダを圧縮中...")
    shutil.make_archive(save_dir, "zip", zip_save_dir, title)
    shutil.rmtree(save_dir)  # フォルダを削除


def CheckUrl(url):
    parse_result = urllib.parse.urlparse(url)
    if len(parse_result.scheme) <= 0:
        url = False
    return url


def GetUrl(is_pyto: bool):
    url = ""
    if is_pyto:
        input_argv = sys.argv
        if len(input_argv) > 1:
            url = input_argv[1]
        else:
            url = pasteboard.url()

    if not CheckUrl(url):
        try:
            url = pyperclip.paste()
        except PyperclipException:
            url = input("urlを入力してください:")
    if not CheckUrl(url):
        url = input("urlを入力してください:")
    return CheckUrl(url)


# main関数
if __name__ == "__main__":
    # iOSで動いているかの判定
    is_iOS = False
    is_pyto = False
    if "iPhone" in platform() or "iPad" in platform():
        is_iOS = True
        try:
            import background as bg
            import pasteboard
            is_pyto = True
        except ImportError:
            import pyperclip
            from pyperclip import PyperclipException
    else:
        import pyperclip
        from pyperclip import PyperclipException

    temp_file_name = "nhentai.pickle"
    # 画像ファイルの命名モード
    # "number"   => ダウンロード番号を画像ファイル名とする
    # "filename" => ダウンロード時URLの画像ファイル名をそのまま使用
    # "date"     => ダウンロード時の時刻を画像ファイル名とする
    name_mode = "number"

    # 前回、ダウンロードが途中で終了している場合
    if os.path.exists(temp_file_name):
        print("前回、ダウンロードが途中で終了しました。")  # メッセージの出力
        print("途中からダウンロードを再開しますか？(y/n)", end=" ")
        choiceFlag = False  # ユーザ入力が有効かどうかのフラグ
        # 正しい入力が得られるまでループする
        while choiceFlag is False:
            choice = input()  # ユーザの入力を受け付ける
            Y_choices = ["y", "Y", "yes", "YES", "Yes", "YEs", "yeS", "yES", "YeS"]
            N_choices = ["n", "N", "no", "NO", "No", "nO"]

            if choice in Y_choices:  # 再開する場合
                choiceFlag = True  # フラグの切り替え
            elif choice in N_choices:  # 再開しない場合
                # 一時ファイルを削除する
                if os.path.exists(temp_file_name):
                    os.remove(temp_file_name)
                choiceFlag = True  # フラグの切り替え
            else:
                print("入力が正しくありません。")
    if not os.path.exists(temp_file_name):
        # 新規のダウンロード開始
        url = GetUrl(is_pyto)
        CollectImage(url)
    else:
        # ダウンロード再開
        with open(temp_file_name, "rb") as f:
            img_info_dict = pickle.load(f)
        downloadByPython(img_info_dict)

    print("Success! : 画像の取得が完了しました")
    # 処理が終了したら一時ファイルを削除する
