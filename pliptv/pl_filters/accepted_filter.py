import logging
from functools import lru_cache

from pliptv.config_loader import PlaylistConfig
from pliptv.models.streams import Stream
from pliptv.pl_filters.filter_abc import FilterABC, LoggingFilterAbcMixin
from pliptv.utils.log.decorators import func_logger

LOG = logging.getLogger(__name__)


class AcceptedFilter(FilterABC, metaclass=LoggingFilterAbcMixin):
    def __init__(self, config: PlaylistConfig):
        super().__init__(config=config)

    @lru_cache(maxsize=32)
    @func_logger(enabled=True)
    def apply(self, value: Stream) -> Stream:
        """Filter by language and quality

        Arguments:
            value {str} -- stream name

        Returns:
            Tuple[Optional[str], str] -- culture, clean stream name
        """
        if not value.meta.hidden:
            value.meta.hidden = (
                str.lower(value.meta.culture) not in self.filter_config.language or str.lower(value.meta.quality) not in self.filter_config.quality
            )
        return value
