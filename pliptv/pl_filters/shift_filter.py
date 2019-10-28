import re
from functools import lru_cache

from pliptv.config_loader import PlaylistConfig
from pliptv.models.streams import StreamMeta
from pliptv.pl_filters.filter_abc import LoggingFilterAbcMixin, FilterABC
from pliptv.utils.log.decorators import func_logger


class ShiftFilter(FilterABC, metaclass=LoggingFilterAbcMixin):
    def __init__(self, config: PlaylistConfig):
        super().__init__(config=config)

    @lru_cache(maxsize=32)
    @func_logger(enabled=True)
    def apply(self, value: StreamMeta) -> StreamMeta:
        """Apply Shift filter

        Arguments:
            value {str} -- Stream name

        Returns:
            Tuple[str, str] -- quality, clean stream name
        """
        self.__logger.debug(  # type: ignore
            f"applying filter <{self.__class__.__name__}> on {str(value)} "
        )

        match = re.search(
            self.filter_config.regex, value.display_name, re.IGNORECASE | re.DOTALL
        )
        if match and len(match.groups()) > 1:
            value.tvg.tvg_shift = match.group(2).strip()
            value.display_name = match.group(1).strip()
            return value

        return value
