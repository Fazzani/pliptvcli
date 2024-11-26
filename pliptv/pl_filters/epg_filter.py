from difflib import SequenceMatcher
from functools import lru_cache, reduce
from typing import Any, List, Optional

from pliptv.config_loader import PlaylistConfig
from pliptv.epg_service import get_epg_index
from pliptv.m3u_utils import translate_channel_name
from pliptv.models.epg import Channel, Epg
from pliptv.models.streams import Stream
from pliptv.pl_filters.filter_abc import FilterABC, LoggingFilterAbcMixin
from pliptv.utils.log.decorators import func_logger


def _get_config(config, group: str) -> List[Any]:
    return list(filter(lambda e: group in e["names"], config.epg.matching_groups))


class EpgFilter(FilterABC, metaclass=LoggingFilterAbcMixin):
    def __init__(self, config: PlaylistConfig):
        super().__init__(config=config)

    @lru_cache(maxsize=32)
    @func_logger(enabled=True)
    def apply(self, value: Stream) -> Stream:
        """Apply display epg filter

        Arguments:
            value {str} -- stream name

        Returns:
            Stream meta data
        """
        epg: Epg = get_epg_index(self.filter_config.index_url)
        if not epg:
            raise AssertionError

        ratio: float = 0.0
        channel_epg: Optional[Channel] = None

        epg_sources = list(
            filter(
                lambda e: value.meta.tvg.group_title in e["names"],
                self.filter_config.matching_groups,
            )
        )

        if epg_sources:
            epg_urls: List[str] = reduce(
                lambda x, y: x + y, [e["sources"] for e in epg_sources]
            )
            for c in filter(lambda e: e.url in epg_urls, epg.tv.channel):
                r = SequenceMatcher(
                    None,
                    translate_channel_name(f"{value.meta.display_name}"),
                    translate_channel_name(f"{c.display_name.name}"),
                ).ratio()
                if r > ratio:
                    ratio = r
                    channel_epg = c

        if channel_epg and ratio > self.filter_config.matching_ratio:
            value.meta.tvg.tvg_id = channel_epg.id
            value.meta.tvg.tvg_name = channel_epg.id
            value.meta.tvg.tvg_logo = (
                channel_epg.icon.src
                if channel_epg.icon and value.meta.tvg.tvg_logo
                else value.meta.tvg.tvg_logo
            )
            # Filter report
            value.meta.tvg[f"__{__name__}__dn_b"] = value.meta.display_name
            value.meta.tvg[f"__{__name__}__dn_a"] = channel_epg.id
            value.meta.tvg[f"__{__name__}__matched"] = "True"
            value.meta.tvg[f"__{__name__}__matched_source"] = channel_epg.url

        return value
