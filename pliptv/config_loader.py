"""
Load playlist config from yaml file
"""
import logging

import yaml

LOG = logging.getLogger(__name__)


class DictToObject(object):
    def __init__(self, dictionary):
        def _traverse(key, element):
            if isinstance(element, dict):
                return key, DictToObject(element)
            else:
                return key, element

        objd = dict(_traverse(k, v) for k, v in dictionary.items())
        self.__dict__.update(objd)

    @classmethod
    def default(cls):
        return cls({})


class PlaylistConfig:
    def __init__(self, config_path: str):
        with open(config_path, "r") as stream:
            try:
                LOG.info(f"Loading playlist config from file path: {config_path}")
                self.__dict__.update(DictToObject(yaml.safe_load(stream)).__dict__)
                LOG.debug(f"Loaded playlist config: {self.__dict__}")
            except yaml.YAMLError as exc:
                LOG.error(exc)


# path = os.getenv("CONFIG_FILE_PATH")
# config_path_from_env = (
#     os.path.expandvars(path)
#     if path
#     else "./itests/pliptv/pl_filters/data/config_playlist.yaml"
# )
# playlist_config = PlaylistConfig(config_path_from_env)
