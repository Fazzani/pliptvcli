import re
from functools import lru_cache

from pliptv.config_loader import PlaylistConfig
from pliptv.models.streams import StreamMeta
from pliptv.pl_filters.filter_abc import LoggingFilterAbcMixin, FilterABC
from pliptv.utils.log.decorators import func_logger


class DisplayNameFilter(FilterABC, metaclass=LoggingFilterAbcMixin):
    def __init__(self, config: PlaylistConfig):
        super().__init__(config=config)

    @lru_cache(maxsize=32)
    @func_logger(enabled=True)
    def apply(self, value: StreamMeta) -> StreamMeta:
        """Apply display name filter

        Arguments:
            value {str} -- stream name

        Returns:
            Tuple[Optional[str], str] -- culture, clean stream name
        """

        value.tvg[f"__{__name__}__dn_b"] = value.display_name
        value.tvg[f"__{__name__}__cu_b"] = value.culture

        for match in map(
            lambda x: re.search(x, value.display_name, re.IGNORECASE),
            self.filter_config.regex_clean_names,
        ):
            if match and len(match.groups()) > 2:
                value.culture = match.group(2)
                value.display_name = match.group(3).strip()
                value.tvg[f"__{__name__}__matched"] = "True"
                value.tvg[f"__{__name__}__dn_a"] = value.display_name
                value.tvg[f"__{__name__}__cu_a"] = value.culture
                return value
        value.culture = ""
        value.display_name = value.display_name.translate(
            {ord(c): " " for c in "@#$%^&*{};,./?\\`~-=_"}
        )
        value.tvg[f"__{__name__}__dn_a"] = value.display_name
        value.tvg[f"__{__name__}__cu_a"] = value.culture
        return value
