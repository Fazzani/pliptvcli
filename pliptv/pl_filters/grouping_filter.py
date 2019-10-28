import logging
import re
from functools import lru_cache

from pliptv.config_loader import PlaylistConfig
from pliptv.models.streams import StreamMeta
from pliptv.pl_filters.filter_abc import LoggingFilterAbcMixin, FilterABC
from pliptv.utils.log.decorators import func_logger

LOG = logging.getLogger(__name__)


class GroupingFilter(FilterABC, metaclass=LoggingFilterAbcMixin):
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
        for group, regex in self.filter_config.map.__dict__.items():
            match = re.search(regex, value.tvg.group_title, re.IGNORECASE)
            if match:
                LOG.info(
                    f"Moving {value.display_name} from {value.tvg.group_title} to group {group}"
                )
                value.tvg.group_title = group
                break
        return value
