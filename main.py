import logging
import multiprocessing
import os
from typing import Any

import click
from tqdm import tqdm

from pliptv.cli_questions import ask_information, log
from pliptv.config_loader import PlaylistConfig
from pliptv.m3u_utils import (
    apply_filters,
    download_file,
    get_filter_pool,
    get_lines,
    load_filters,
    save_pl,
    save_pl_to_path,
)
from pliptv.models.streams import M3u
from pliptv.utils.log import setup_logging
from pliptv.utils.tools import uri_validator

setup_logging()

LOG = logging.getLogger(__name__)


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
    default=False,
    type=bool,
    is_flag=True,
    help="Generate VOD 'strm' file",
)
def main(auto: bool, export: bool, vod: bool) -> None:
    """
    Extensible CLI m3u playlist manager
    many default filters was provided for:
    - auto matching EPG
    - auto matching logos
    - cleaning stream names
    - grouping streams
    - hide groups
    - and many others

    """

    log("XPL CLI", color="blue", figlet=True)
    log(main.__doc__, "green")

    pl_info: dict[str, Any] = (  # type: ignore
        ask_information(auto)
        if not auto
        else {
            "playlist_url": os.getenv("PL"),
            "strm_output_path": os.getenv("STRM_OUTPUT_PATH"),
            "playlist_config_path": os.getenv("CONFIG_FILE_PATH")
            if os.getenv("CONFIG_FILE_PATH") is not None
            else os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "data/config_playlist.yaml"
            ),
            "playlist_output_path": os.getenv("OUTPUT_PATH")
            if os.getenv("OUTPUT_PATH") is not None
            else os.path.join(os.path.dirname(os.path.realpath(__file__)), "data"),
        }
    )

    try:
        if pl_info is None:
            raise Exception("pl_info is required")
        log(f"pl_info: {str(pl_info)}", "green")

        playlist_config = PlaylistConfig(str(pl_info.get("playlist_config_path")))
        pl_url: str = str(pl_info.get("playlist_url"))
        if uri_validator(pl_url):
            log(f"Downloading playlist from {pl_url}", "white")
            lines = download_file(pl_url)
        else:
            with open(pl_url, "r", encoding="utf8") as f:
                lines = get_lines(f.readlines())
        log(f"{len(lines)} retrieved for the playlist {pl_url}", "white")

        m3u = M3u.from_list("playlist", lines)

        log("Loading filters", "white")
        filters = load_filters()
        log(f"{len(filters)} loaded..", "white")

        log(f"Applying filters on {m3u.name.capitalize()}", "white")
        filter_pool = get_filter_pool(filters, playlist_config)

        with multiprocessing.Pool(4) as pool:
            multiple_results = [
                pool.apply_async(apply_filters, args=(stream, filter_pool))
                for stream in m3u
            ]
            m3u = M3u(m3u.name, [res.get() for res in tqdm(multiple_results)])

        log(f"Saving {m3u.name.capitalize()}", "white")
        file_result = save_pl_to_path(m3u, str(pl_info.get("playlist_output_path")))
        log(f"Generated playlist for {m3u.name.capitalize()}: {file_result}", "white")

        if export:
            url = save_pl(m3u)
            log(f"Generated playlist url for {m3u.name.capitalize()}: {url}", "white")

        strm_output_path = str(pl_info.get("strm_output_path"))
        if vod and strm_output_path is not None:
            log(
                f"Generating VOD strm files url for {m3u.name.capitalize()} into {strm_output_path}",
                "green",
            )
            for stream in tqdm(filter(lambda x: x.meta.isVod, m3u.streams)):
                strm_output_fullpath: str = os.path.join(
                    strm_output_path, stream.meta.display_name + ".strm"
                )
                with open(strm_output_fullpath, "w") as f:
                    f.write(stream.url)

            log(
                f"Generated VOD strm files for playlist: {m3u.name.capitalize()} into {strm_output_path}",
                "green",
            )

        # Display report
        # get_report(m3u)

    except Exception as err:
        log(f"Unexpected error: {err}", "red")
        raise
    finally:
        log("The end.", "green")


def get_report(m3u):
    reported_streams = filter(
        lambda x: x.meta.tvg
        and any([k.endswith("__matched") for k in x.meta.tvg.meta.keys()]),
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
