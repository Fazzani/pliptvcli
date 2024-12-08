# coding: utf-8
import logging
import multiprocessing
import os
import re
from datetime import datetime
from typing import Any, Optional, cast

import click
import jsonpickle
from tqdm import tqdm

from pliptv.cli_questions import ask_information, log
from pliptv.config_loader import PlaylistConfig
from pliptv.m3u_utils import (
    ENCODING_UTF8,
    apply_filters,
    download_file,
    export_playlist,
    get_filter_pool,
    get_lines,
    load_filters,
    save_pl_to_path,
)
from pliptv.models.streams import M3u, Stream
from pliptv.pl_filters.accepted_filter import AcceptedFilter
from pliptv.utils.log import setup_logging
from pliptv.utils.tools import uri_validator

setup_logging()

LOG: logging.Logger = logging.getLogger(__name__)
STRM_EXT = ".strm"
TV_SERIES_REGEX = re.compile(r"(.+[\s])*(s\d{1,4})[^\w](e\d{1,4})", flags=re.IGNORECASE)
IS_ARABIC_REGEX = re.compile(r"[\u0600-\u06FF]")

# TODO: combine using click with env variables and remove 'ask_information'
# TODO: notification when processing finished
# TODO: Python 12 migration


@click.command()
@click.option(
    "--auto",
    default=False,
    type=bool,
    is_flag=True,
    help="Read all arguments from environment variables (without prompt)",
)
@click.option(
    "--export",
    default=False,
    type=bool,
    is_flag=True,
    help="Export playlist into a file",
)
@click.option(
    "--vod",
    "is_generation_vod_enabled",
    default=False,
    type=bool,
    is_flag=True,
    help="Generate VOD 'strm' file",
)
@click.option(
    "--cache",
    "is_cache_enabled",
    default=False,
    type=bool,
    is_flag=True,
    help="Persist generated playlist",
)
def main(auto: bool, export: bool, is_generation_vod_enabled: bool, is_cache_enabled: bool) -> None:
    """
    Extensible CLI m3u playlist manager
    many default filters was provided for:
    - auto matching EPG
    - auto matching logos
    - cleaning stream names
    - grouping streams
    - hide groups
    - and many more filters

    """

    log("XPL CLI", color="blue", figlet=True)
    log(main.__doc__, "green")

    pl_info: dict[str, Any] = (  # type: ignore
        ask_information(auto)
        if not auto
        else {
            "playlist_url": os.getenv("PL"),
            "strm_output_path": os.getenv("STRM_OUTPUT_PATH"),
            "playlist_config_path": (
                os.getenv("CONFIG_FILE_PATH")
                if os.getenv("CONFIG_FILE_PATH") is not None
                else os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    "data/config_playlist.yaml",
                )
            ),
            "playlist_output_path": (
                os.getenv("OUTPUT_PATH")
                if os.getenv("OUTPUT_PATH") is not None
                else os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
            ),
        }
    )

    try:
        if pl_info is None:
            raise Exception("pl_info is required")

        log(f"✓✓✓ pl_info: {str(pl_info)}", "green")

        playlist_config = PlaylistConfig(str(pl_info.get("playlist_config_path")))
        pl_url: str = str(pl_info.get("playlist_url"))
        if uri_validator(pl_url):
            log(f"Downloading playlist from {pl_url}", "white")
            lines = download_file(pl_url)
        else:
            with open(pl_url, "r", encoding=ENCODING_UTF8) as f:
                lines = get_lines(f.readlines())

        log(f"✓✓✓ {len(lines)} streams retrieved", "green")

        m3u: M3u = M3u.from_list("playlist", lines)

        log("Loading filters", "white")
        filters = load_filters()
        log(f"✓✓✓ {len(filters)} filters loaded", "green")

        log(f"Applying filters on {m3u.name.capitalize()}", "white")
        filter_pool = get_filter_pool(filters, playlist_config)

        with multiprocessing.Pool(4) as pool:
            multiple_results = [pool.apply_async(apply_filters, args=(stream, filter_pool)) for stream in m3u]
            m3u = M3u(
                m3u.name,
                [res.get() for res in tqdm(multiple_results, desc="Live Tv processing")],
            )

        channels_list = M3u(m3u.name, list(filter(lambda x: not x.meta.is_vod and not x.meta.hidden, m3u)))
        log(f"Saving {m3u.name.capitalize()} with {len(channels_list.streams)} channels", "yellow")
        file_result = save_pl_to_path(channels_list, str(pl_info.get("playlist_output_path")))

        log(f"Generated playlist for {m3u.name.capitalize()}: {file_result}", "white")

        if is_cache_enabled:
            cache_playlist_generation(m3u)

        if export:
            url: str = export_playlist(channels_list)
            log(f"✓✓✓ Playlist exported to: {url}", "green")

        vod_created_streams = vod_processing(is_generation_vod_enabled, pl_info, playlist_config, m3u)
        if vod_created_streams:
            log(f"Processed {m3u.name.capitalize()} with {len(vod_created_streams)} vod", "yellow")

        if is_cache_enabled:
            cache_playlist_generation(m3u, "_final")

        if vod_created_streams:
            cleanup(vod_created_streams, str(pl_info.get("strm_output_path")))

        # Display report
        # get_report(m3u)

    except Exception as err:
        log(f"Unexpected error: {err}", "red")
        raise
    finally:
        log("✓✓✓ The end.", "green")


def cache_playlist_generation(m3u, suffix: str = ""):
    log("✓✓✓ Cache generation...", "green")

    generation_data: str = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    with open(f"cache_{generation_data}{suffix}.json", "w", encoding="utf-8") as f:
        f.write(cast(str, jsonpickle.encode(m3u, indent=4)))


def vod_processing(vod: bool, pl_info: dict[str, Any], playlist_config: PlaylistConfig, m3u: M3u) -> Optional[list[str]]:
    """STRM VOD files generator.

    Args:
        vod (bool): is activated
        pl_info (dict[str, Any]): application arguments
        playlist_config (PlaylistConfig): playlist configuration
        m3u (M3u): M3u playlist
        cleanup_folder (bool): Cleanup destination folder. Defaults to False.
    """
    strm_output_path = str(pl_info.get("strm_output_path"))
    if vod and strm_output_path is not None:
        log(
            f"✓✓✓ Generating VOD strm files into {strm_output_path}",
            "green",
        )
        # TODO: filter multiprocessing

        videos_output_path: str = os.path.join(strm_output_path, "movies")
        tv_series_output_path: str = os.path.join(strm_output_path, "series")

        accepted_cultures = AcceptedFilter(playlist_config).filter_config.language
        vod_list: list[Stream] = list(
            filter(lambda x: x.meta.is_vod and not x.meta.hidden and str.lower(x.meta.culture) in accepted_cultures, m3u.streams)
        )

        created_streams: list[str] = []
        for stream in tqdm(
            vod_list,
            desc="VOD strm processing",
        ):
            match_tv_series = TV_SERIES_REGEX.search(stream.meta.display_name)
            output_path: str = os.path.join(tv_series_output_path, match_tv_series.group(1).strip()) if match_tv_series else videos_output_path
            strm_output_fullpath: str = os.path.join(output_path, stream.meta.display_name.strip() + STRM_EXT)
            try:
                created_streams.append(strm_output_fullpath)
                if not os.path.exists(strm_output_fullpath):
                    os.makedirs(output_path, exist_ok=True)
                    with open(strm_output_fullpath, "w", encoding=ENCODING_UTF8) as f:
                        f.write(stream.url)
            except Exception as e:
                log(f"Error while generating VOD stream: {e} {stream.url}", "red")
                continue

        log(
            f"✓✓✓ Generated VOD strm files for playlist: {m3u.name.capitalize()} into {strm_output_path}",
            "green",
        )
        return created_streams


def cleanup(created_streams: list[str], strm_output_path: str):
    """Removes all streams that weren't yet existed in the playlist from output path.

    Args:
        created_streams (list[str]): all streams that were created
        strm_output_path (str): streams output path (root directory)
    """
    import glob

    LOG.debug(f"Cleanup: {strm_output_path}")
    for file_path in tqdm(glob.iglob(f"{strm_output_path}/**/*{STRM_EXT}", recursive=True), desc="Cleaning up VOD folder"):
        if file_path not in created_streams:
            os.remove(file_path)
            dir_name: str = os.path.dirname(file_path)
            if len(os.listdir(dir_name)) == 0:
                os.rmdir(dir_name)


def get_report(m3u):
    reported_streams = filter(
        lambda x: x.meta.tvg and any([k.endswith("__matched") for k in x.meta.tvg.meta.keys()]),
        m3u.streams,
    )
    count = 0
    for s in reported_streams:
        count += 1
        report = ""
        for m, v in s.meta.tvg.meta.items():
            if m.startswith("__"):
                report += f"{m}: {v}; "
        LOG.info(f"{report}")

    LOG.info(f"{count} matched streams")


if __name__ == "__main__":
    main()
