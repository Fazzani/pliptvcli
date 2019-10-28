import logging
import re
from functools import lru_cache

from pliptv.config_loader import PlaylistConfig
from pliptv.models.streams import StreamMeta
from pliptv.pl_filters.filter_abc import LoggingFilterAbcMixin, FilterABC
from pliptv.utils.log.decorators import func_logger

LOG = logging.getLogger(__name__)


class HideGroupFilter(FilterABC, metaclass=LoggingFilterAbcMixin):
    def __init__(self, config: PlaylistConfig):
        super().__init__(config=config)

    @lru_cache(maxsize=32)
    @func_logger(enabled=True)
    def apply(self, value: StreamMeta) -> StreamMeta:
        """Apply grouping streams  filter

        Arguments:
            value {str} -- stream name

        Returns:
            Tuple[Optional[str], str] -- culture, clean stream name
        """
        matched = any(
            [
                re.search(regex, value.tvg.group_title, re.IGNORECASE) is not None
                for regex in self.filter_config.groups
            ]
        )

        if self.filter_config.strategy == "pessimist":
            if not matched:
                value.hidden = "True"
                LOG.info(f"Hide {value.tvg.group_title}")
        else:
            if matched:
                value.hidden = "True"
                LOG.info(f"Hide {value.tvg.group_title}")
        return value
