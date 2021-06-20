import pysrt
from pysrt import SubRipTime, SubRipItem


limit_time_seconds = 30

subs = pysrt.open("./video-dl/friends_e03s17.srt")
new_subs = pysrt.SubRipFile()

limit = SubRipTime(seconds=30)

start = None
end = None
cnt = 0
text = []
for sub in subs:
    if cnt == 43:
        print(sub.end)
        print(subs[-1].end)
        print(sub.text)
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
