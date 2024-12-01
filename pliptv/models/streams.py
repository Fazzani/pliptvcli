from __future__ import annotations

import logging
import re
from typing import Any, List, Tuple

"""
#EXTM3U
#EXTINF:0 channel-id="34" epg-id="124" tvg-name="5 канал"
 pay="1" channel-id="stream-name-here"
 tvg-logo="http://<url to image file with logo>"
 groups="<common group name>|<group name>"
 url-epg="<url to epg file in .xml format (if any) for this stream>" tvg-shift="+1",test
"""
LOG: logging.Logger = logging.getLogger(__name__)

CAR_RETURN = "\n"


class Tvg:
    """Tvg media"""

    def __init__(
        self,
        tvg_id: str = "",
        tvg_name: str = "",
        tvg_logo: str = "",
        tvg_shift: str = "",
        group_title: str = "",
        **meta,
    ):
        self.tvg_id = tvg_id
        self.tvg_name = tvg_name
        self.tvg_logo = tvg_logo
        self.tvg_shift = tvg_shift
        self.group_title = group_title
        self.meta = meta if meta else {}

    def __str__(self):
        return f'tvg-id="{self.tvg_id}" tvg-name="{self.tvg_name}" tvg-logo="{self.tvg_logo}" tvg-shift="{self.tvg_shift}" group-title="{self.group_title}" '

    def __repr__(self):
        return f'tvg-id="{self.tvg_id}" tvg-name="{self.tvg_name}" tvg-logo="{self.tvg_logo}" tvg-shift="{self.tvg_shift}" group-title="{self.group_title}" '

    def __getitem__(self, key):
        return self.meta[key] if key in self.meta.keys() else ""

    def __setitem__(self, key: str, value: Any):
        self.meta[key] = value


class StreamMeta:
    QUALITY_KEY: str = "quality"
    CULTURE_KEY: str = "culture"
    HIDDEN_KEY: str = "hidden"

    def __init__(self, display_name: str, tvg: Tvg | None = None):
        self.tvg = tvg if tvg else Tvg()
        self.display_name = display_name
        self.isVod = False
        self.isHeader = False
        self.hidden = False

    def __str__(self):
        return f"#EXTINF:-1 {str(self.tvg)}, {self.display_name}"

    def __repr__(self):
        return f"{self.display_name}"

    def __getitem__(self, item: Any):
        return self.tvg[item]

    def __setitem__(self, key: str, data: Any):
        self.tvg[key] = data

    @property
    def culture(self):
        return self.tvg[StreamMeta.CULTURE_KEY]

    @culture.setter
    def culture(self, value):
        self.tvg[StreamMeta.CULTURE_KEY] = value

    @property
    def hidden(self):
        return self.tvg[StreamMeta.HIDDEN_KEY]

    @hidden.setter
    def hidden(self, value):
        self.tvg[StreamMeta.HIDDEN_KEY] = value

    @property
    def quality(self):
        return self.tvg[StreamMeta.QUALITY_KEY]

    @quality.setter
    def quality(self, value):
        self.tvg[StreamMeta.QUALITY_KEY] = value


class Stream:
    def __init__(self, url: str, meta: StreamMeta):
        self.url = url
        self.meta = meta

    def __str__(self):
        return f"{str(self.meta)}{CAR_RETURN}{self.url}"

    def __repr__(self):
        return f"{str(self.meta)}{CAR_RETURN}{self.url}"


class M3u:
    FILE_HEAD = "#EXTM3U"
    LINE_HEADER_VALUE_REGEX = r'(?:{}=")(.*?)(?=")'
    HEADER_ATTRS = ["tvg-id", "tvg-name", "tvg-logo", "tvg-shift", "group-title"]

    def __init__(self, name: str, streams: List[Stream]):
        self.name = name
        self.streams = streams
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.streams):
            self.index += 1
            return self.streams[self.index - 1]
        else:
            self.index = 0
            raise StopIteration()

    def __str__(self):
        return M3u.FILE_HEAD + CAR_RETURN + CAR_RETURN.join([str(stream) for stream in filter(lambda x: not x.meta.hidden, self.streams)])

    @staticmethod
    def _meta_from_header_line(m3u_header_line: str) -> StreamMeta:
        if not m3u_header_line:
            raise AssertionError
        meta_raw_array = m3u_header_line.rsplit(",", 1)
        meta = StreamMeta(meta_raw_array[1], Tvg())

        meta.tvg.tvg_id = M3u._get_header_value(meta_raw_array[0], "tvg-id")
        meta.tvg.tvg_name = M3u._get_header_value(meta_raw_array[0], "tvg-name")
        meta.tvg.tvg_logo = M3u._get_header_value(meta_raw_array[0], "tvg-logo")
        meta.tvg.tvg_shift = M3u._get_header_value(meta_raw_array[0], "tvg-shift")
        meta.tvg.group_title = M3u._get_header_value(meta_raw_array[0], "group-title")

        return meta

    @staticmethod
    def _get_header_value(line: str, attr: str) -> str:
        match = re.search(M3u.LINE_HEADER_VALUE_REGEX.format(attr), line, re.I)
        if match:
            return match.group(1)
        return ""

    @classmethod
    def from_list(cls, name: str, pl: List[Tuple[str, str]]) -> M3u:
        """Build M3u instance from list

        Arguments:
            name {str} -- playlist name
            pl {List[Tuple[str, str]]} -- list(url, header)

        Returns:
            M3u -- M3u object
        """
        if not pl:
            raise AssertionError

        return cls(name, list(map(lambda x: Stream(x[1], M3u._meta_from_header_line(x[0])), pl)))
