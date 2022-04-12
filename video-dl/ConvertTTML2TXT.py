import platform
import re
import sys
from pathlib import Path


def ConvertTTML2TXT(file_path) -> str:
    file_path_str = str(file_path) if isinstance(file_path, Path) else file_path
    save_file_path = str(file_path_str).replace(".ttml", ".txt")
    with open(file_path_str, mode="r") as f:
        txt_list = f.readlines()

    one_sentence = ""
    sentence_list: list[str] = []
    for row in txt_list:
        if row[:9] == "<p begin=":
            part_of_sentence = re.sub("<.+?>", "", row).strip()
            if re.match(r"^[A-Z]+ ?[A-Z .]*: ", part_of_sentence):
                part_of_sentence = "\n" + part_of_sentence
            if part_of_sentence[-1:] in [".", "]", "?", "!"]:
                one_sentence += part_of_sentence
                sentence_list.append(one_sentence)
                one_sentence = ""
            elif part_of_sentence == "":
                sentence_list.append("")
            else:
                one_sentence += part_of_sentence + " "
    with open(save_file_path, mode="w") as f:
        f.write("\n".join(sentence_list))
    return save_file_path


if __name__ == "__main__":
    # iOSで動いているかの判定
    is_iOS = False
    if "iPhone" in platform.platform() or "iPad" in platform.platform():
        is_iOS = True
        from FilePickerPyto import FilePickerPyto

        file_path = Path(
            FilePickerPyto(file_types=["public.all"], allows_multiple_selection=False)[
                0
            ]
        )
    else:
        try:
            from FilePicker import GetFilePathByGUI

            file_path = Path(
                GetFilePathByGUI(
                    file_type=(["TTMLファイル", "*.ttml"],),
                )[0]
            )
        except ModuleNotFoundError:
            path_str = input("\n変換する字幕のパスを入力してください:")
            file_path = Path(path_str)

    sub_base_name, sub_ext = file_path.stem, file_path.suffix
    new_file_path = ""
    if sub_ext == ".ttml":
        new_file_path = ConvertTTML2TXT(file_path)
    else:
        input("以下の字幕フォーマットのみ対応しています。\n" "・TTML(ABC newsなど)\n" "エンターを押すと終了します。")
        sys.exit()

    print("\nttmlをテキストに変換しました")
