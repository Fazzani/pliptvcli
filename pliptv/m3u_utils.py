"""
steps:
- download m3u files
- filters to clean name, add epg, add picons, add others meta data
- push pl to public url
"""

import inspect
import logging
import os
import string
from io import StringIO
from json import JSONEncoder
from typing import List, Tuple
from urllib.parse import urlparse

import requests
from memoization import cached
from pyshorteners import Shortener

from pliptv.azure_service import upload_bytes_to_azure
from pliptv.config_loader import PlaylistConfig
from pliptv.models.streams import M3u, Stream
from pliptv.pl_filters.filter_abc import FilterABC
from pliptv.pl_filters.filters_loader import (
    class_list_from_modules,
    load_class_from_name,
    load_modules_from_path,
)

DEFAULT_FILTERS_PATH = os.path.join(os.path.dirname(__file__), "./pl_filters")
DEFAULT_FILTERS_PATTERN = r".+_filter.py$"
LOG = logging.getLogger(__name__)
ENCODING_UTF8 = "UTF-8"


def download_file(pl_url: str) -> List[Tuple[str, str]]:
    """
    download a m3u file and transform it to dict
    Arguments:
        pl_url {str} -- playlist url
    Returns:
        dict --  m3u transformed to dict
    """
    if not pl_url:
        raise AssertionError
    res_parse_url = urlparse(pl_url)
    if not res_parse_url.scheme:
        raise AssertionError
    if not res_parse_url.netloc:
        raise AssertionError
    r = requests.get(pl_url)
    lines = StringIO(r.content.decode(ENCODING_UTF8)).readlines()
    if not lines:
        raise AssertionError
    return get_lines(lines)


def get_lines(lines: list[str]) -> List[Tuple[str, str]]:
    """
    Get a media lines
    Arguments:
        lines {list[str]} -- playlist lines
    Returns:
        dict --  m3u transformed to dict
    """

    if not lines:
        raise AssertionError

    keys = [lines[i].rstrip() for i in range(1, len(lines), 2)]
    values = [lines[i].rstrip() for i in range(2, len(lines), 2)]
    return list(zip(keys, values))


def apply_filters(stream: Stream, filter_pool: List[FilterABC]) -> Stream:
    """Apply enabled filters ordered by priority"""
    for filter_instance in filter(lambda x: x.enabled, sorted(filter_pool, key=lambda x: x.priority)):
        filter_instance.apply(stream)
        LOG.debug(
            f"after applying {filter_instance.__class__.__name__} hidden: {stream.meta.hidden} culture: {str(stream.meta.culture)} {str(stream)}"
        )
    return stream


@cached
def get_filter_pool(filters: List[Tuple[str, str]], config: PlaylistConfig) -> List[FilterABC]:
    """Build pool filters"""
    filter_pool: List[FilterABC] = []
    for c in filters:
        class_list = class_list_from_modules(
            c[0],
            lambda x: inspect.isclass(x) and not inspect.isabstract(x) and x.__name__.endswith("Filter"),
        )
        if not class_list:
            raise AssertionError
        cls = load_class_from_name(f"{c[0]}.{class_list[0]}")

        filter_pool.append(cls(config))
    LOG.debug(f"Filters pool contains {len(filter_pool)} filter(s)")
    return filter_pool


def load_filters(
    filters_path: str = DEFAULT_FILTERS_PATH,
    filters_pattern: str = DEFAULT_FILTERS_PATTERN,
) -> List[Tuple[str, str]]:
    """Dynamic filter loader from folder path

    Keyword Arguments:
        filters_path {str} -- filter folder path (default: {DEFAULT_FILTERS_PATH})
        filters_pattern {str} -- filter files pattern (default: {DEFAULT_FILTERS_PATTERN})

    Returns:
        Tuple[str, List[str]] -- filter module, filter module class
    """
    return load_modules_from_path(filters_path, pattern=filters_pattern)


def shorten_url(url: str, access_token: str) -> str:
    if not url:
        raise AssertionError
    if not access_token:
        raise AssertionError
    return Shortener(api_key=access_token).bitly.short(url)


def export_playlist(pl: M3u) -> str:
    """Save playlist file on azure and return shorten url from bit"""
    url = upload_bytes_to_azure(f"{pl.name}.m3u", str(pl))
    at = os.getenv("BITLY_ACCESS_TOKEN")
    if not at:
        raise AssertionError
    return shorten_url(url, at)


def save_pl_to_path(pl: M3u, output_path: str) -> str:
    """Save playlist file to output path"""
    file_result = os.path.join(output_path, f"{pl.name}.m3u")
    with open(file_result, "w+", encoding=ENCODING_UTF8) as file:
        file.write(str(pl))
    return file_result


def translate_channel_name(name: str) -> str:
    return name.translate(str.maketrans(dict.fromkeys(string.punctuation))).title()


class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
