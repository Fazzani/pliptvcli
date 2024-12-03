import logging
import re
from functools import lru_cache

from pliptv.config_loader import PlaylistConfig
from pliptv.models.streams import Stream
from pliptv.pl_filters.filter_abc import FilterABC, LoggingFilterAbcMixin
from pliptv.utils.log.decorators import func_logger

LOG = logging.getLogger(__name__)


class GroupingFilter(FilterABC, metaclass=LoggingFilterAbcMixin):
    def __init__(self, config: PlaylistConfig):
        super().__init__(config=config)

    @lru_cache(maxsize=32)
    @func_logger(enabled=True)
    def apply(self, value: Stream) -> Stream:
        """Apply grouping streams filter

        Arguments:
            value {str} -- stream name

        Returns:
            Tuple[Optional[str], str] -- culture, group moving filter
        """
        if not value.meta.is_vod and not value.meta.is_header:
            value.meta.hidden = True
            for group, regex in self.filter_config.map.__dict__.items():
                match = re.search(regex, value.meta.tvg.group_title, re.IGNORECASE)
                if match:
                    LOG.debug(f"Moving {value.meta.display_name} from {value.meta.tvg.group_title} to group {group}")
                    value.meta.tvg.group_title = group
                    value.meta.hidden = False
                    break
        return value
