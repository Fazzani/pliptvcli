import re
from functools import lru_cache

from pliptv.config_loader import PlaylistConfig
from pliptv.models.streams import Stream
from pliptv.pl_filters.filter_abc import ActionEnum, FilterABC, LoggingFilterAbcMixin
from pliptv.utils.log.decorators import func_logger


class ShiftFilter(FilterABC, metaclass=LoggingFilterAbcMixin):
    def __init__(self, config: PlaylistConfig):
        super().__init__(config=config)

    @lru_cache(maxsize=32)
    @func_logger(enabled=True)
    def apply(self, value: Stream) -> Stream:
        """Apply Shift filter

        Arguments:
            value {str} -- Stream name

        Returns:
            Tuple[str, str] -- quality, clean stream name
        """
        self.__logger.debug(f"applying filter <{self.__class__.__name__}> on {str(value)} ")  # type: ignore

        match = re.search(self.filter_config.regex, value.meta.display_name, re.IGNORECASE | re.DOTALL)
        if match and len(match.groups()) > 1:
            if self.action == ActionEnum.REMOVE:
                value.meta.hidden = True
            value.meta.tvg.tvg_shift = match.group(2).strip()
            value.meta.display_name = match.group(1).strip()
            return value

        return value
