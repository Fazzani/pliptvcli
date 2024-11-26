import re
from functools import lru_cache

from pliptv.config_loader import PlaylistConfig
from pliptv.models.streams import Stream
from pliptv.pl_filters.filter_abc import FilterABC, LoggingFilterAbcMixin
from pliptv.utils.log.decorators import func_logger


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

        value.meta.tvg[f"__{__name__}__dn_b"] = value.meta.display_name
        value.meta.tvg[f"__{__name__}__cu_b"] = value.meta.culture

        for match in map(
            lambda x: re.search(x, value.meta.display_name, re.IGNORECASE),
            self.filter_config.regex_clean_names,
        ):
            if match and len(match.groups()) > 2:
                value.meta.culture = match.group(2)
                value.meta.display_name = match.group(3).strip()
                value.meta.tvg[f"__{__name__}__matched"] = "True"
                value.meta.tvg[f"__{__name__}__dn_a"] = value.meta.display_name
                value.meta.tvg[f"__{__name__}__cu_a"] = value.meta.culture
                return value
        value.meta.culture = ""
        value.meta.display_name = value.meta.display_name.translate(
            {ord(c): " " for c in "@#$%^&*{};,./?\\`~-=_"}
        )
        value.meta.tvg[f"__{__name__}__dn_a"] = value.meta.display_name
        value.meta.tvg[f"__{__name__}__cu_a"] = value.meta.culture
        return value
