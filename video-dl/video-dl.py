from __future__ import annotations

from pathlib import Path
from platform import platform
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
    ydl_opts: dict[str, str | bool | list[str] | list[dict]],
    is_pyto: bool = False,
) -> None:
    if is_pyto:
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

    if is_iOS:
        WORK_DIR = Path(
            "/private/var/mobile/Library/Mobile Documents/com~apple~CloudDocs/Downloads"
        )
        DIR_NAME = "Video"
        SAVE_DIR_PATH = WORK_DIR / DIR_NAME
    else:
        SAVE_DIR_PATH = Path("./video-dl/download")

    url = ""
    if is_pyto:
        input_argv = sys.argv
        if len(input_argv) > 1:
            url = input_argv[1]
        else:
            url = pasteboard.url()

    parsed_url = urlparse(url)
    if len(parsed_url.scheme) < 1:
        try:
            url = pyperclip.paste()
        except PyperclipException:
            url = input("urlを入力してください:")

    parsed_url = urlparse(url)
    if len(parsed_url.scheme) < 1:
        print("urlが正しくないため終了します")
        sys.exit()

    if parsed_url.netloc == "www.goodmorningamerica.com":
        url = URLConversionForGMA(url)
        parsed_url = urlparse(url)
    print(f"\nTrying to download from {url}\n")

    # 保存ディレクトリを作成
    SAVE_DIR_PATH.mkdir(parents=True, exist_ok=True)

    ydl_opts: dict[str, str | bool | list[str] | list[dict]]
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
        "outtmpl": f"{str(SAVE_DIR_PATH)}/%(title)s.%(ext)s",
        "format": "mp4",
        "postprocessors": [
            {
                "key": "FFmpegSubtitlesConvertor",
                "format": "srt",
                "when": "before_dl",
            },
        ],
        "writesubtitles": True,
        "writeautomaticsub": write_auto_sub,
        "subtitleslangs": ["en.*", "-live_chat"],
        "subtitlesformat": "srt/best",
        "continuedl": True,
        "ignoreerrors": True,
        "keepvideo": True,
    }
    DownloadVideo(ydl_opts, is_pyto=is_pyto)
    print("finish")
