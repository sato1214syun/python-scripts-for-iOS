import sys
import youtube_dl
import os
import background as bg

workDir = "/private/var/mobile/Library/Mobile Documents/com~apple~CloudDocs/Downloads"
saveDir = "/Video"
savePath = "{}{}/".format(workDir, saveDir)

url = sys.argv[1]
sub_lang = "en"

ydl_opts = {
    "outtmpl": "{}%(title)s.%(ext)s".format(savePath),
    "format": "mp4",
    "subtitlesformat": "srt/best",
    "writesubtitles": True,
    "writeautomaticsub": False,
    "allsubtitles": True,
    # "subtitleslangs": [sub_lang],
    "continuedl": True,
}

os.makedirs(savePath, exist_ok=True)

print("video downloading...")

with bg.BackgroundTask() as b:
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

print("finish")
