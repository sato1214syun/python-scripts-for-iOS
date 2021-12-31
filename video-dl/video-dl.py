import os
import platform
import sys

import yt_dlp


def DownloadVideo(save_path, url, subtitle_lang_list):
    ydl_opts = {
        "outtmpl": f"{save_path}%(title)s.%(ext)s",
        "format": "mp4",
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": subtitle_lang_list,
        "subtitlesformat": "srt/best",
        "continuedl": True,
        "ignoreerrors": True,
    }

    print("video downloading...")

    if is_iOS:
        with bg.BackgroundTask():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
    else:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    print("finish")


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
        work_dir = (
            "/private/var/mobile/Library/Mobile Documents/com~apple~CloudDocs/Downloads"
        )
        save_dir = "/Video"
        save_path = f"{work_dir}/{save_dir}/"
        input_argv = sys.argv
        if len(input_argv) > 1:
            url = input_argv[1]
        else:
            url = pasteboard.url()
    else:
        save_path = "video-dl\\test_data\\"
        # url = "https://abcnews.go.com/US/video/ghislaine-maxwell-found-guilty-charges-81994466"
        url = pyperclip.paste()
    os.makedirs(save_path, exist_ok=True)
    subtitle_lang_list = ["en", "-live_chat"]
    DownloadVideo(save_path, url, subtitle_lang_list)
