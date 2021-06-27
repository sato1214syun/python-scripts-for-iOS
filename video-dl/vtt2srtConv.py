import sys

from vtt_to_srt.vtt_to_srt import vtt_to_srt
from mergeSRT import MergeSRT


def ConvVTT2SRT(file_path):
    vtt_to_srt(file_path)
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


def files_picked() -> None:
        files = sharing.picked_files()
        sharing.share_items(files)


if __name__ == "__main__":
    filePicker = sharing.FilePicker()
    filePicker.file_types = ["public.data"]
    filePicker.allows_multiple_selection = True

    filePicker.completion = files_picked
    sharing.pick_documents(filePicker)
    file_path = sys.argv[1]
    new_file_path = ConvVTT2SRT(file_path)
    MergeSRT(new_file_path)
