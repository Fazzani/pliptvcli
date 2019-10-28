from abc import ABC, abstractmethod, ABCMeta
from functools import lru_cache

from pliptv.config_loader import PlaylistConfig
from pliptv.models.streams import StreamMeta
from pliptv.utils.log.logging_meta import MetaLoggingBase


class FilterABC(ABC):
    _filter_config_name: str = ""

    @abstractmethod
    def __init__(self, config: PlaylistConfig, *args, **kargs) -> None:
        self.config = config

    @abstractmethod
    @lru_cache(maxsize=32)
    def apply(self, value: StreamMeta) -> StreamMeta:
        return value

    @property
    def filter_config_name(self):
        if not self._filter_config_name or self._filter_config_name == "":
            self._filter_config_name = self.__class__.__name__.lower()
        return self._filter_config_name

    @filter_config_name.setter
    def filter_config_name(self, value: str):
        self._filter_config_name = value

    @property
    def filter_config(self):
        return self.config.__dict__.get(self.filter_config_name)

    @property
    def priority(self):
        return self.filter_config.priority

    @property
    def enabled(self):
        return self.filter_config.__dict__.get("enabled", True)


class LoggingFilterAbcMixin(MetaLoggingBase, ABCMeta):
    pass
