import logging
import re
from functools import lru_cache

from pliptv.config_loader import PlaylistConfig
from pliptv.models.streams import Stream
from pliptv.pl_filters.filter_abc import FilterABC, LoggingFilterAbcMixin
from pliptv.utils.log.decorators import func_logger

LOG = logging.getLogger(__name__)


class RemoveHeadersFilter(FilterABC, metaclass=LoggingFilterAbcMixin):
    def __init__(self, config: PlaylistConfig):
        super().__init__(config=config)

    @lru_cache(maxsize=32)
    @func_logger(enabled=True)
    def apply(self, value: Stream) -> Stream:
        """Apply Remove headers filter

        Arguments:
            value {str} -- stream name

        Returns:
            Tuple[Optional[str], str] -- culture, clean stream name
        """
        if not value.meta.hidden:
            for r in self.filter_config.regex:
                match = re.search(r, value.meta.display_name, re.IGNORECASE)
                if match:
                    value.meta.hidden = True
                    value.meta.is_header = True
                    break
                else:
                    match = re.search(r, value.meta.tvg.tvg_name, re.IGNORECASE)
                    if match:
                        value.meta.hidden = True
                        value.meta.is_header = True
                        break
        return value
