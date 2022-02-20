from __future__ import annotations

import os
import platform
import re
import sys
from urllib.parse import urlparse

import yt_dlp

GET_AUTO_SUB_LIST = ["abcnews.go.com"]
POSITIVE_ANSWERS = [
    "y",
    "Y",
    "yes",
    "Yes",
    "yEs",
    "yeS",
    "YEs",
    "yES",
    "YeS",
    "YES",
]

NEGATIVE_ANSWERS = [
    "n",
    "N",
    "no",
    "No",
    "nO",
    "NO",
]


def DownloadVideo(
    ydl_opts: dict[str, str | bool | list[str]],
    is_iOS: bool = False,
) -> None:
    if is_iOS:
        with bg.BackgroundTask():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
    else:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])


def URLConversionForGMA(url):
    url = re.sub(
        r"www.goodmorningamerica.com/[a-zA-Z]+", "abcnews.go.com/GMA/News", url
    )
    return url


if __name__ == "__main__":
    # iOSで動いているかの判定
    is_iOS = False
    if "iPhone" in platform.platform() or "iPad" in platform.platform():
        is_iOS = True
        import background as bg
        import pasteboard
    else:
        import pyperclip

    if is_iOS:
        WORK_DIR = (
            "/private/var/mobile/Library/Mobile Documents/com~apple~CloudDocs/Downloads"
        )
        DIR_NAME = "/Video"
        SAVE_DIR_PATH = f"{WORK_DIR}{DIR_NAME}/"
        input_argv = sys.argv
        if len(input_argv) > 1:
            url = input_argv[1]
        else:
            url = pasteboard.url()
    else:
        SAVE_DIR_PATH = "video-dl\\test_data\\"
        url = pyperclip.paste()

    parsed_url = urlparse(url)
    if parsed_url.netloc == "www.goodmorningamerica.com":
        url = URLConversionForGMA(url)
        parsed_url = urlparse(url)

    # クリップボードにurlを格納
    ... if is_iOS else pyperclip.copy(url)
    os.makedirs(SAVE_DIR_PATH, exist_ok=True)

    ydl_opts: dict[str, str | bool | list[str]]
    # ダウンロードできる字幕を確認
    print("Investigating available subtitles...")
    ydl_opts = {"listsubtitles": True}
    DownloadVideo(ydl_opts)
    # ダウンロードをするか確認
    while True:
        answer = input("\nContinue downloading?(y/n):")
        if answer in NEGATIVE_ANSWERS:
            sys.exit()
        elif answer in POSITIVE_ANSWERS:
            break
        else:
            print("Answer with proper word. e.g.) 'y, Y, yes, n, N, no'")
    # オプションのパラメータを決定
    print("Downloading video...")
    write_auto_sub = True if parsed_url.netloc in GET_AUTO_SUB_LIST else False
    ydl_opts = {
        "outtmpl": f"{SAVE_DIR_PATH}%(title)s.%(ext)s",
        "format": "mp4",
        "writesubtitles": True,
        "writeautomaticsub": write_auto_sub,
        "subtitleslangs": ["en", "-live_chat"],
        "subtitlesformat": "srt/best",
        "continuedl": True,
        "ignoreerrors": True,
    }
    DownloadVideo(ydl_opts, is_iOS=is_iOS)
    print("finish")
