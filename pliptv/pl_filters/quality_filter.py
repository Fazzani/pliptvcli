import re
from functools import lru_cache

from pliptv.config_loader import PlaylistConfig
from pliptv.models.streams import StreamMeta
from pliptv.pl_filters.filter_abc import LoggingFilterAbcMixin, FilterABC
from pliptv.utils.log.decorators import func_logger


class QualityFilter(FilterABC, metaclass=LoggingFilterAbcMixin):
    def __init__(self, config: PlaylistConfig):
        super().__init__(config=config)

    @lru_cache(maxsize=32)
    @func_logger(enabled=True)
    def apply(self, value: StreamMeta) -> StreamMeta:
        """Apply quality filter

        Arguments:
            value {str} -- Stream name

        Returns:
            Tuple[str, str] -- quality, clean stream name
        """
        for k, v in self.filter_config.regex.__dict__.items():
            match = re.search(v, value.display_name, re.IGNORECASE | re.DOTALL)
            if match and len(match.groups()) > 1:
                value.quality = k
                ch_name, q, others = match.groups()
                value.display_name = f"{ch_name.strip()} {others.strip()}".strip()
                return value

        value.quality = self.filter_config.default
        return value
