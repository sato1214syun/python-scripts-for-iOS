from pathlib import Path
from platform import platform
import re
import sys
from urllib.parse import urlparse
from importlib.util import find_spec

import yt_dlp

# iOS appのpytoで使用するモジュールをimport
if find_spec("pasteboard"):
    import pasteboard
    import background as bg
else:
    import pyperclip


class Y_N_Query:
    def __init__(self) -> None:
        self.__POSITIVE_ANSWERS = [
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

        self.__NEGATIVE_ANSWERS = [
            "n",
            "N",
            "no",
            "No",
            "nO",
            "NO",
        ]

    def getAnswer(self, do_loop: bool):
        response = None
        while response is None:
            ans = input("(y/n):")
            if ans in self.__POSITIVE_ANSWERS:
                return True
            elif ans in self.__NEGATIVE_ANSWERS:
                return False

            print("入力が正しくありません")
            if not do_loop:
                break


class VideoDownloader:
    def __init__(self) -> None:
        self.ydl_opts = {
            "outtmpl": r"./%(title)s.%(ext)s",
            "format": "mp4",
            "postprocessors": [
                {
                    "key": "FFmpegSubtitlesConvertor",
                    "format": "srt",
                    "when": "before_dl",
                },
            ],
            "writeautomaticsub": False,
            "writesubtitles": True,
            "subtitleslangs": ["en.*", "-live_chat"],
            "subtitlesformat": "srt/best",
            "continuedl": True,
            "ignoreerrors": True,
            "keepvideo": True,
        }

    def setOutputPath(self, save_dir: Path, file_name: str = r"%(title)s.%(ext)s"):
        self.ydl_opts["outtmpl"] = str(save_dir) + "/" + file_name
        return

    def setUrl(self, url: str):
        self.url = url
        return

    def writeAutomaticSub(self):
        # ダウンロードできる字幕を確認
        print("Investigating available subtitles...")
        ydl_opts = {"listsubtitles": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

        print("\nDownload auto generated sub?")
        isEnabled = Y_N_Query().getAnswer(do_loop=True)
        self.ydl_opts["writeautomaticsub"] = isEnabled
        return

    def download(self):
        print(f"\nTrying to download from {self.url}\n")
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self.url])
        return


class PlatformInfo:
    def __init__(self):
        self.machine = self.checkPlatform()
        self.app = self.checkApp()
        self.work_dir = self.getWorkingDirectory()

    def checkPlatform(self):
        if "iPhone" in platform() or "iPad" in platform():
            return "iOS"
        else:
            return "PC"

    def checkApp(self):
        if self.machine == "iOS":
            if find_spec("pasteboard"):
                return "pyto"
            else:
                return "general_app"
        return

    def getWorkingDirectory(self):
        if self.machine == "iOS":
            WORK_DIR = Path(
                "/private/var/mobile/Library/Mobile Documents"
                "/com~apple~CloudDocs/Downloads"
            )
            DIR_NAME = "Video"
            self.save_dir_path = WORK_DIR / DIR_NAME
        else:
            self.save_dir_path = Path("./video-dl/download")


class urlHandler:
    def __init__(self, app: None | str):
        self.url = self.getUrl(app)

    def checkUrl(self, url: str) -> None | str:
        parsed_url = urlparse(url)
        if len(parsed_url.scheme) < 1:
            return
        return url

    def getUrlForPyto(self) -> None | str:
        if sys.argv:
            if url := self.checkUrl(sys.argv[1]):
                return url
        if url := self.checkUrl(pasteboard.url()):
            return url

    def inputUrlByTerminal(self):
        url = input("\nurlを入力してください:")
        if url == "exit":
            sys.exit()

        url = self.checkUrl(url)
        if not url:
            print("urlが正しくありません")
        return url

    def getUrl(self, app: None | str):
        url = None
        if app == "pyto":
            url = self.getUrlForPyto()
        else:
            try:
                url = pyperclip.paste()
                url = self.checkUrl(url)
            except pyperclip.PyperclipException:
                pass

        while not url:
            url = self.inputUrlByTerminal()

        return self.URLConversionForGMA(url)

    def URLConversionForGMA(self, url):
        return re.sub(
            r"www.goodmorningamerica.com/[a-zA-Z]+", "abcnews.go.com/GMA/News", url
        )


def main():
    platform_info = PlatformInfo()
    url = urlHandler(platform_info.app).url
    video_downloader = VideoDownloader()
    platform_info.save_dir_path.mkdir(parents=True, exist_ok=True)
    video_downloader.setUrl(url)
    video_downloader.setOutputPath(platform_info.save_dir_path)
    video_downloader.writeAutomaticSub()

    print("Downloading video...")
    video_downloader.download()
    print("finish")


if __name__ == "__main__":
    main()
