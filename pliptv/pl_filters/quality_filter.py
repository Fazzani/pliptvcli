import re
from functools import lru_cache

from pliptv.config_loader import PlaylistConfig
from pliptv.models.streams import Stream
from pliptv.pl_filters.filter_abc import ActionEnum, FilterABC, LoggingFilterAbcMixin
from pliptv.utils.log.decorators import func_logger


class QualityFilter(FilterABC, metaclass=LoggingFilterAbcMixin):
    def __init__(self, config: PlaylistConfig):
        super().__init__(config=config)

    @lru_cache(maxsize=32)
    @func_logger(enabled=True)
    def apply(self, value: Stream) -> Stream:
        """Apply quality filter

        Arguments:
            value {str} -- Stream name

        Returns:
            Tuple[str, str] -- quality, clean stream name
        """
        for k, v in self.filter_config.regex.__dict__.items():
            match = re.search(v, value.meta.display_name, re.IGNORECASE | re.DOTALL)
            if match and len(match.groups()) > 1:
                if self.action == ActionEnum.REMOVE:
                    value.meta.hidden = True
                    break

                value.meta.quality = k
                ch_name, q, others = match.groups()
                value.meta.display_name = f"{ch_name.strip()} {others.strip()}".strip()
                return value

        value.meta.quality = self.filter_config.default
        return value
