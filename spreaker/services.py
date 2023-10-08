from os.path import exists

import feedparser
import requests
from bs4 import BeautifulSoup
from django.conf import settings

from core.shared import CommonResponse


def get_rssurl(input_url: str) -> CommonResponse:
    out = CommonResponse()
    if not input_url.startswith("https://www.spreaker.com/show/"):
        out.status = "error"
        out.message = "Not a spreaker url"
    else:
        req = requests.get(input_url)
        soup = BeautifulSoup(req.text, features="html.parser")
        feedvalue = soup.find("a", {"id": "show_episodes_feed"})
        if feedvalue:
            out.value = feedvalue["href"]
            out.status = "success"
        else:
            out.message = "Error getting feed url"
            out.status = "error"
    return out


def get_rss_data(input_url: str, limit: int = 10) -> CommonResponse:
    out = CommonResponse()
    counter = 0
    if not input_url.startswith("https://www.spreaker.com/show/"):
        out.status = "error"
        out.message = "Not a spreaker url"
    else:
        req = feedparser.parse(url_file_stream_or_string=input_url)
        out.value = []
        for iter in req["entries"]:
            if counter == limit:
                break
            out.value.append(iter)
            counter += 1
    return out


def get_audio(input_url: str, fname: str) -> CommonResponse:
    out = CommonResponse()
    if not input_url.startswith("https://dts.podtrac.com") and not input_url.startswith("https://api.spreaker.com"):
        out.status = "error"
        out.message = "Not a spreaker url"
    else:
        local_path = f"{settings.PERSIST_AUDIO_ROOTDIR}/{fname}.mp3"
        if not exists(local_path):
            req = requests.get(input_url, allow_redirects=True)
            try:
                localfile = open(local_path, "wb")
                localfile.write(req.content)
                localfile.close()
                out.status = "success"
                out.message = "Downloaded."
            except PermissionError:
                out.status = "error"
                out.message = "Permission denied to open file"
        else:
            out.status = "success"
            out.message = "Already downloaded."
    return out
