"""
3PG Download xmltv file
"""
from __future__ import print_function

import os

import requests


class Picon(object):
    def __init__(self, data):
        self.__dict__ = data


def get_picons_index(gist_url: str) -> Picon:
    response = requests.get(gist_url)
    if response.ok:
        data = Picon(response.json())
        return data
    return Picon(None)


if __name__ == "__main__":
    url = os.getenv("GIST_PICONS_URL")
    assert url
    index = get_picons_index(url)

PICONS = get_picons_index(str(os.getenv("GIST_PICONS_URL")))
