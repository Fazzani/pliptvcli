import logging
import re
from functools import lru_cache

from pliptv.config_loader import PlaylistConfig
from pliptv.models.streams import Stream
from pliptv.pl_filters.filter_abc import FilterABC, LoggingFilterAbcMixin
from pliptv.utils.log.decorators import func_logger

LOG = logging.getLogger(__name__)


class VodFilter(FilterABC, metaclass=LoggingFilterAbcMixin):
    def __init__(self, config: PlaylistConfig):
        super().__init__(config=config)

    @lru_cache(maxsize=32)
    @func_logger(enabled=True)
    def apply(self, value: Stream) -> Stream:
        """Filter by VOD

        Arguments:
            value {str} -- stream name

        Returns:
            Tuple[Optional[str], str] -- culture, clean stream name
        """
        for r in self.filter_config.regex:
            match = re.search(r, value.url, re.IGNORECASE)
            if match:
                value.meta.is_vod = True
                if not value.meta.hidden:
                    for reg in self.filter_config.hidden_groups:
                        match_group = re.search(reg, value.meta.tvg.group_title, re.IGNORECASE)
                        if match_group:
                            value.meta.hidden = True
                            break
                break

        return value
