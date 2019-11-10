import logging
import os

import click

from pliptv.cli_questions import ask_information, log
from pliptv.config_loader import PlaylistConfig
from pliptv.m3u_utils import (
    download_file,
    load_filters,
    save_pl,
    apply_filters,
    save_pl_to_path,
)
from pliptv.models.streams import M3u
from pliptv.utils.log import setup_logging

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
def main(auto) -> None:
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

    pl_info = (
        ask_information(auto)
        if not auto
        else {
            "playlist_url": os.getenv("PL"),
            "playlist_config_path": os.getenv("CONFIG_FILE_PATH"),
        }
    )

    try:
        playlist_config = PlaylistConfig(pl_info.get("playlist_config_path"))
        pl_url = pl_info.get("playlist_url")
        log(f"Downloading playlist from {pl_url}", "white")
        lines = download_file(pl_url)
        log(f"{len(lines)} retrieved for the playlist {pl_url}", "white")

        m3u = M3u.from_list("playlist", lines)

        log(f"Loading filters", "white")
        filters = load_filters()
        log(f"{len(filters)} loaded..", "white")

        log(f"Applying filters on {m3u.name}", "white")
        pl_filtred = list(
            map(lambda _: apply_filters(_.meta, filters, playlist_config), m3u)
        )
        assert pl_filtred

        log(f"Saving {m3u.name}", "white")
        file_result = save_pl_to_path(m3u, os.getenv("OUTPUT_PATH"))
        log(f"Generated playlist for {m3u.name}: {file_result}", "white")

        # url = save_pl(m3u)
        # log(f"Generated playlist url for {m3u.name}: {url}", "white")

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
