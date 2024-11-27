"""
Download picons files
"""

from __future__ import print_function

import json
import os
from functools import lru_cache

import requests
import validators


class Picon(object):
    def __init__(self, data):
        self.__dict__ = data


@lru_cache(maxsize=10000)
def get_picons_index(gist_url: str) -> Picon:
    if not validators.url(gist_url):
        gist_url = str(os.getenv("GIST_PICONS_URL"))
        if not validators.url(gist_url):
            raise ValueError(f"{gist_url} not a valid url")

    response = requests.get(gist_url)
    if response.ok:
        data = Picon(json.loads(response.text))
        return data
    return Picon(None)
