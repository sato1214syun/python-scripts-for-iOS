import os
import pickle
import re

# import requests as rq
# from bs4 import BeautifulSoup as bs
from requests.models import Response
from requests_html import HTMLSession

base = os.path.dirname(os.path.abspath(__file__))
url = r"https://sitcom-friends-eng.seesaa.net/article/388471106.html"
rel_res_pickle_path = r"./res.pickle"
res_pickle_path = os.path.normpath(os.path.join(base, rel_res_pickle_path))

session: HTMLSession = HTMLSession()
res: Response = session.get(url)
res.html.render()
res.html.encoding("Shift-JIS")


list = res.html.find("a")
pass

"""
base = os.path.dirname(os.path.abspath(__file__))
url = r"https://sitcom-friends-eng.seesaa.net/article/388471106.html"


rel_res_pickle_path = r"./res.pickle"
res_pickle_path = os.path.normpath(os.path.join(base, rel_res_pickle_path))
if os.path.exists(res_pickle_path):
    with open(res_pickle_path, "rb") as f:
        res = pickle.load(f)
else:
    res = rq.get(url)
    with open(res_pickle_path, "wb") as f:
        pickle.dump(res, f)

soup = bs(res.content, "lxml")
list = soup.find_all("a", text=re.compile(".*"))
print(list)
"""
