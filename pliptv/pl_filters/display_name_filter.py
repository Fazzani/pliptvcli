import logging
import re
from functools import lru_cache

from pliptv.config_loader import PlaylistConfig
from pliptv.models.streams import Stream
from pliptv.pl_filters.filter_abc import FilterABC, LoggingFilterAbcMixin
from pliptv.utils.log.decorators import func_logger

LOG = logging.getLogger(__name__)


class DisplayNameFilter(FilterABC, metaclass=LoggingFilterAbcMixin):
    def __init__(self, config: PlaylistConfig):
        super().__init__(config=config)

    @lru_cache(maxsize=32)
    @func_logger(enabled=True)
    def apply(self, value: Stream) -> Stream:
        """Apply display name filter

        Arguments:
            value {str} -- stream name

        Returns:
            Tuple[Optional[str], str] -- culture, clean stream name
        """
        quality_filter = re.compile(r"^((?:4k|8k)\s*[\-:|]*)", re.I)
        for regex_compiled in map(
            lambda x: re.compile(x, re.I | re.U),
            self.filter_config.regex,
        ):
            match = quality_filter.match(value.meta.display_name)
            if match:
                value.meta.display_name = value.meta.display_name.replace(match.group(1), "") + f" {match.group(1)}"

            match = regex_compiled.match(value.meta.display_name.replace("◉", "ar"))
            if match and len(match.groups()) > 1:
                value.meta.culture = match.group(1).strip().lower()
                value.meta.display_name = match.group(2).strip().capitalize()
                value.meta.tvg[f"__{__name__}__matched"] = True
                value.meta.tvg[f"__{__name__}__dn_a"] = value.meta.display_name
                value.meta.tvg[f"__{__name__}__cu_a"] = value.meta.culture

            match = regex_compiled.match(value.meta.tvg.tvg_name.replace("◉", "ar"))
            if match and len(match.groups()) > 1:
                value.meta.country = match.group(1).strip().lower()

        if not value.meta.tvg[f"__{__name__}__matched"]:
            value.meta.culture = ""
            value.meta.display_name = value.meta.display_name.translate({ord(c): " " for c in "@#$%^&*{};,./?\\`~-=_"})
            value.meta.tvg[f"__{__name__}__dn_a"] = value.meta.display_name
            value.meta.tvg[f"__{__name__}__cu_a"] = value.meta.culture

        return value
