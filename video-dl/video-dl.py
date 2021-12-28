import os
import platform
import sys

import yt_dlp

if "iPhone" in platform.platform() or "iPad" in platform.platform():
    import background as bg


def DownloadVideo(save_path, url, subtitle_lang_list):
    ydl_opts = {
        "outtmpl": f"{save_path}%(title)s.%(ext)s",
        "format": "mp4",
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": subtitle_lang_list,
        "subtitlesformat": "srt/best",
        "continuedl": True,
    }

    os.makedirs(save_path, exist_ok=True)

    print("video downloading...")

    if "iPhone" in platform.platform() or "iPad" in platform.platform():
        with bg.BackgroundTask():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
    else:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    print("finish")


if __name__ == "__main__":
    if "iPhone" in platform.platform() or "iPad" in platform.platform():
        work_dir = (
            "/private/var/mobile/Library/Mobile Documents/com~apple~CloudDocs/Downloads"
        )
        save_dir = "/Video"
        save_path = os.path.join(work_dir, save_dir)
        url = sys.argv[1]
    else:
        save_path = "video-dl\\test_data\\"
        url = "https://www.youtube.com/watch?v=YojicM91ev8"
    subtitle_lang_list = ["en", "-live_chat"]
    DownloadVideo(save_path, url, subtitle_lang_list)
