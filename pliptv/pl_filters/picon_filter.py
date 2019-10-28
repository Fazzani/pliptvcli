import logging
from functools import lru_cache

from pliptv.config_loader import playlist_config, PlaylistConfig
from pliptv.models.streams import StreamMeta
from pliptv.picons_service import PICONS
from pliptv.pl_filters.filter_abc import LoggingFilterAbcMixin, FilterABC
from pliptv.utils.log.decorators import func_logger

LOG = logging.getLogger(__name__)


class PiconFilter(FilterABC, metaclass=LoggingFilterAbcMixin):
    def __init__(self, config: PlaylistConfig):
        super().__init__(config=config)

    @lru_cache(maxsize=32)
    @func_logger(enabled=True)
    def apply(self, value: StreamMeta) -> StreamMeta:
        """Apply display picon filter

        Arguments:
            value {str} -- stream name

        Returns:
            Tuple[Optional[str], str] -- culture, clean stream name
        """
        key = f"{value.display_name.lower()}".replace(" ", "")
        if key in PICONS.__dict__:
            value.tvg.tvg_logo = PICONS.__dict__[key]
            LOG.info(f"Picons: matched {value.display_name}: {value.tvg.tvg_logo}")

        return value


if __name__ == "__main__":
    filter = PiconFilter(playlist_config)
    filter.apply(None)
