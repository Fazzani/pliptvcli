from abc import ABC, ABCMeta, abstractmethod
from enum import Enum
from functools import lru_cache
from typing import Any

from pliptv.config_loader import PlaylistConfig
from pliptv.models.streams import Stream
from pliptv.utils.log.logging_meta import MetaLoggingBase


class ActionEnum(Enum):
    NONE = 0
    PRESERVE = 1
    REMOVE = 2

    @classmethod
    def _missing_(cls, value):
        return cls.NONE


class FilterABC(ABC):
    _filter_config_name: str = ""

    @abstractmethod
    def __init__(self, config: PlaylistConfig, *args, **kargs) -> None:
        self.config = config

    @abstractmethod
    @lru_cache(maxsize=32)
    def apply(self, value: Stream) -> Stream:
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
    def filter_config(self) -> Any:
        return self.config.__dict__.get(self.filter_config_name)

    @property
    def priority(self) -> int:
        return self.filter_config.priority

    @property
    def enabled(self):
        return self.filter_config.__dict__.get("enabled", True)

    @property
    def action(self) -> ActionEnum:
        return ActionEnum(self.filter_config.__dict__.get("action", 0))


class LoggingFilterAbcMixin(MetaLoggingBase, ABCMeta):
    pass
