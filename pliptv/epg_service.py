"""
3PG Download xmltv file
"""
from __future__ import print_function

import os
from functools import lru_cache

import requests
import validators

from pliptv.models.epg import Epg, epg_from_dict


@lru_cache(maxsize=10000)
def get_epg_index(epg_url: str) -> Epg:
    assert epg_url, "url : must be not empty"
    if not validators.url(epg_url):
        epg_url = str(os.getenv("EPG_INDEX_URL"))
        if not validators.url(epg_url):
            raise ValueError(f"{epg_url} not a valid url")

    r = requests.get(epg_url)
    epg_string = r.json()
    assert epg_string, "No json data"
    return epg_from_dict(epg_string)


def generate_channel_names(epg: Epg) -> None:
    for c in epg.tv.channel:
        c.display_name.name = c.display_name.name.replace("hd", "")
