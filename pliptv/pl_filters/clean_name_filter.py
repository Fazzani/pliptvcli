import re
from functools import lru_cache

from pliptv.config_loader import PlaylistConfig
from pliptv.models.streams import Stream
from pliptv.pl_filters.filter_abc import FilterABC, LoggingFilterAbcMixin
from pliptv.utils.log.decorators import func_logger


class CleanNameFilter(FilterABC, metaclass=LoggingFilterAbcMixin):
    def __init__(self, config: PlaylistConfig):
        super().__init__(config=config)

    @lru_cache(maxsize=32)
    @func_logger(enabled=True)
    def apply(self, value: Stream) -> Stream:
        for reg in self.filter_config.regex:
            regex = re.compile(reg, re.I | re.DOTALL)
            value.meta.display_name = regex.sub("", value.meta.display_name).strip()
        for replacement in self.filter_config.replacements:
            value.meta.display_name.replace(replacement, "")
        return value
