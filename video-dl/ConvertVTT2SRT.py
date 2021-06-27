import os
import sys

from vtt_to_srt.vtt_to_srt import vtt_to_srt

from MergeSRT import MergeSRT


def ConvertVTT2SRT(file_path) -> str:
    if os.path.splitext(file_path)[1] != ".vtt":
        input("vttファイルを選択して下さい。エンターを押すと終了します")
        sys.exit()
    vtt_to_srt(file_path)
    return file_path.replace(".vtt", ".srt")


if __name__ == "__main__":
    try:
        from FilePickerPyto import FilePickerPyto

        file_path = FilePickerPyto(
            file_types=["public.text"], allows_multiple_selection=False
        )[0]
    except ImportError:
        file_path = input("ファイルパスを入力してください\n>>")

    new_file_path = ConvertVTT2SRT(file_path)
    print("vttファイルをsrtに変換しました")
    MergeSRT(new_file_path)
    print("srtファイルの時間調整が完了しました")
