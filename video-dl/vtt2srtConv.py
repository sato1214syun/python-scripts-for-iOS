import sys
import os

from vtt_to_srt.vtt_to_srt import vtt_to_srt
from mergeSRT import MergeSRT

try:
    from FilePickerPyto import FilePickerPyto

    is_pyto = True
except Exception:
    is_pyto = False
    pass


def ConvVTT2SRT(file_path) -> str:
    vtt_to_srt(file_path)
    if os.path.splitext(file_path)[1] != ".vtt":
        input("vttファイルを選択して下さい。エンターを押すと終了します")
        sys.exit()
    new_file_path = file_path.replace(".vtt", ".srt")

    with open(new_file_path, encoding="utf-8") as f:
        data_list = f.readlines()

    cnt = 2
    new_data_list = ["1\n"]
    for data in data_list[1:]:
        new_data_list.append(data)
        if data == "\n":
            new_data_list.append("{}\n".format(cnt))
            cnt += 1

    with open(new_file_path, mode="w", encoding="utf-8") as f:
        f.writelines(new_data_list)

    return new_file_path


if __name__ == "__main__":
    if is_pyto:
        file_path = FilePickerPyto()[0]
    else:
        file_path = input("ファイルパスを入力してください\n>>")
    new_file_path = ConvVTT2SRT(file_path)
    print("vttファイルをsrtに変換しました")
    MergeSRT(new_file_path)
    print("srtファイルの時間調整が完了しました")
