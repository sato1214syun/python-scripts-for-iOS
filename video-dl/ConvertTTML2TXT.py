import os
import sys
import re


def ConvertTTML2TXT(file_path) -> str:
    save_file_path = file_path.replace(".ttml", ".srt")
    with open(file_path, mode="r") as f:
        txt_list = f.readlines()

    one_sentence = ""
    sentence_list: list[str] = []
    for row in txt_list:
        if row[:9] == "<p begin=":
            part_of_sentence = re.sub("<.+?>", "", row).strip()
            if re.match(r"[A-Z]+ ?[A-Z]*: ", part_of_sentence):
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
    from FilePickerPyto import FilePickerPyto

    file_path = FilePickerPyto(
        file_types=["public.text"], allows_multiple_selection=False
    )[0]
    sub_base_name, sub_ext = os.path.splitext(file_path)
    new_file_path = ""
    if sub_ext == ".ttml":
        new_file_path = ConvertTTML2TXT(file_path)
    else:
        input(
            "以下の字幕フォーマットのみ対応しています。\n"
            "・TTML(ABC newsなど)\n"
            "エンターを押すと終了します。"
        )
        sys.exit()
