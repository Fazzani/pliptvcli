import logging
from functools import lru_cache

from pliptv.config_loader import PlaylistConfig
from pliptv.models.streams import StreamMeta
from pliptv.picons_service import get_picons_index
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
        picons = get_picons_index(self.filter_config.source_url)
        if key in picons.__dict__:
            value.tvg.tvg_logo = picons.__dict__[key]
            LOG.info(f"Picons: matched {value.display_name}: {value.tvg.tvg_logo}")

        return value
