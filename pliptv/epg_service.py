"""
3PG Download xmltv file
"""
from __future__ import print_function

import os
from pprint import pprint

import requests

from pliptv.models.epg import Epg, epg_from_dict


def get_epg_index(epg_url: str) -> Epg:
    assert epg_url, "url : must be not empty"
    r = requests.get(epg_url)
    epg_string = r.json()
    assert epg_string, "No json data"
    return epg_from_dict(epg_string)


def generate_channel_names(epg: Epg) -> None:
    for c in epg.tv.channel:
        c.display_name.name = c.display_name.name.replace("hd", "")


if __name__ == "__main__":
    url = os.getenv("EPG_INDEX_URL")
    assert url
    index = get_epg_index(url)
    pprint(index.tv.channel)

EPG = get_epg_index(str(os.getenv("EPG_INDEX_URL")))
generate_channel_names(EPG)
