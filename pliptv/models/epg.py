# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = welcome_from_dict(json.loads(json_string))

from dataclasses import dataclass
from typing import Any, Optional, List, TypeVar, Type, cast, Callable

T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except Exception:
            pass
    assert False


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


@dataclass
class DisplayName:
    lang: str
    t: str
    _custom_name: str = ""

    @property
    def name(self):
        if not self._custom_name:
            self._custom_name = self.t.title()
        return self._custom_name

    @name.setter
    def name(self, value):
        self._custom_name = value

    @staticmethod
    def from_dict(obj: Any) -> "DisplayName":
        assert isinstance(obj, dict)
        lang = from_str(obj.get("lang"))
        t = from_str(obj.get("$t"))
        return DisplayName(lang, t)

    def to_dict(self) -> dict:
        result: dict = {"lang": from_str(self.lang), "$t": from_str(self.t)}
        return result


@dataclass
class Icon:
    src: str

    @staticmethod
    def from_dict(obj: Any) -> "Icon":
        assert isinstance(obj, dict)
        src = from_str(obj.get("src"))
        return Icon(src)

    def to_dict(self) -> dict:
        result: dict = {"src": from_str(self.src)}
        return result


@dataclass
class Channel:
    id: str
    country: str
    display_name: DisplayName
    url: str
    active: str
    icon: Optional[Icon] = None

    @staticmethod
    def from_dict(obj: Any) -> "Channel":
        assert isinstance(obj, dict)
        id = from_str(obj.get("id"))
        country = from_str(obj.get("country"))
        display_name = DisplayName.from_dict(obj.get("display-name"))
        url = from_str(obj.get("url"))
        active = from_str(obj.get("active"))
        icon = from_union([Icon.from_dict, from_none], obj.get("icon"))
        return Channel(id, country, display_name, url, active, icon)

    def to_dict(self) -> dict:
        result: dict = {
            "id": from_str(self.id),
            "country": from_str(self.country),
            "display-name": to_class(DisplayName, self.display_name),
            "url": from_str(self.url),
            "active": from_str(self.active),
            "icon": from_union([lambda x: to_class(Icon, x), from_none], self.icon),
        }
        return result


@dataclass
class Tv:
    generator_info_name: str
    generator_info_url: str
    channel: List[Channel]

    @staticmethod
    def from_dict(obj: Any) -> "Tv":
        assert isinstance(obj, dict)
        generator_info_name = from_str(obj.get("generator-info-name"))
        generator_info_url = from_str(obj.get("generator-info-url"))
        channel = from_list(Channel.from_dict, obj.get("channel"))
        return Tv(generator_info_name, generator_info_url, channel)

    def to_dict(self) -> dict:
        result: dict = {
            "generator-info-name": from_str(self.generator_info_name),
            "generator-info-url": from_str(self.generator_info_url),
            "channel": from_list(lambda x: to_class(Channel, x), self.channel),
        }
        return result


@dataclass
class Epg:
    tv: Tv

    @staticmethod
    def from_dict(obj: Any) -> "Epg":
        assert isinstance(obj, dict)
        tv = Tv.from_dict(obj.get("tv"))
        return Epg(tv)

    def to_dict(self) -> dict:
        result: dict = {"tv": to_class(Tv, self.tv)}
        return result


def epg_from_dict(s: Any) -> Epg:
    return Epg.from_dict(s)


def epg_to_dict(x: Epg) -> Any:
    return to_class(Epg, x)
