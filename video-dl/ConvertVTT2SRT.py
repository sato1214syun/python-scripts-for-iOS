import os
import platform
import sys

from vtt_to_srt.vtt_to_srt import vtt_to_srt

from MergeSRT import MergeSRT


def ConvertVTT2SRT(file_path: str) -> str:
    vtt_to_srt(file_path)
    print("vttファイルをsrtに変換しました")
    return file_path.replace(".vtt", ".srt")


if __name__ == "__main__":
    # iOSで動いているかの判定
    is_iOS = False
    if "iPhone" in platform.platform() or "iPad" in platform.platform():
        is_iOS = True
        from FilePickerPyto import FilePickerPyto
        file_path = FilePickerPyto(
            file_types=["public.text"], allows_multiple_selection=False
        )[0]
    else:
        from FilePicker import GetFilePathByGUI
        file_path = GetFilePathByGUI(
            file_type=(["VTTファイル", "*.vtt"],),
        )[0]

    sub_base_name, sub_ext = os.path.splitext(file_path)
    new_file_path = ""
    if sub_ext == ".vtt":
        new_file_path = ConvertVTT2SRT(file_path)
    else:
        input(
            "以下の字幕フォーマットのみ対応しています。\n"
            "・VTT(YouTubeなど)\n"
            "エンターを押すと終了します。"
        )
        sys.exit()

    MergeSRT(new_file_path)
    print("srtファイルの時間調整が完了しました")
