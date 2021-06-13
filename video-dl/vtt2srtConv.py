import os
import sys

from vtt_to_srt.vtt_to_srt import vtt_to_srt

work_dir = "/private/var/mobile/Library/Mobile Documents/com~apple~CloudDocs/Downloads"
save_dir = "Video"

file_name = sys.argv[1]

file_path = os.path.join(work_dir, save_dir, file_name)
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
    data_list = f.writelines(new_data_list)