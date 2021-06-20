import os

import pysrt
from pysrt import SubRipItem, SubRipTime

limit_time_seconds = 30
file_path = "./video-dl/temp_data/friends_e03s17.srt"
file_name, ext = os.path.splitext(file_path)
new_file_path = file_name + "_merged" + ext
subs = pysrt.open(file_path)
new_subs = pysrt.SubRipFile()

limit = SubRipTime(seconds=30)

start = None
end = None
cnt = 0
text = []
for sub in subs:
    if start is None and end is None:
        start = sub.start
        end = sub.end
        text.append(sub.text)
        continue

    if sub.end - start > limit:
        cnt += 1
        new_sub = SubRipItem(cnt, start=start, end=end, text="\n".join(text))
        new_subs.append(new_sub)
        start = sub.start
        end = sub.end
        text = [sub.text]
        if sub.end == subs[-1].end:
            cnt += 1
            new_sub = SubRipItem(cnt, start=start, end=end, text="\n".join(text))
            new_subs.append(new_sub)
            break
        continue

    end = sub.end
    text.append(sub.text)

new_subs.save(new_file_path)
