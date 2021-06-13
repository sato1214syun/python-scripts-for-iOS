from vtt_to_srt.vtt_to_srt import vtt_to_srt
import sys
import os

work_dir = "/private/var/mobile/Library/Mobile Documents/com~apple~CloudDocs/Downloads"
save_dir = "Video"

file_name = sys.argv[1]

file_path = os.path.join(work_dir, save_dir, file_name)
vtt_to_srt(file_path)