import logging

from pliptv.config_loader import playlist_config
from pliptv.m3u_utils import (
    download_file,
    load_filters,
    save_pl,
    apply_filters,
)
from pliptv.models.streams import M3u
from pliptv.utils.log import setup_logging

setup_logging()

LOG = logging.getLogger(__name__)


def main() -> None:
    try:
        LOG.info(f"Downloading playlist from {playlist_config.url}")
        lines = download_file(playlist_config.url)
        LOG.debug(f"{len(lines)} retrieved for the playlist {playlist_config.url}")

        m3u = M3u.from_list("playlist", lines)

        LOG.debug(f"Loading filters")
        filters = load_filters()
        LOG.debug(f"{len(filters)} loaded..")

        LOG.info(f"Applying filters on {m3u.name}")
        pl_filtred = list(
            map(lambda _: apply_filters(_.meta, filters, playlist_config), m3u)
        )
        assert pl_filtred

        LOG.info(f"Saving {m3u.name} into ")
        url = save_pl(m3u)
        LOG.info(f"Generated playlist url for {m3u.name}: {url}")

        # Display report
        # get_report(m3u)

    except Exception as err:
        LOG.error("Unexpected error:", err)
        raise
    finally:
        LOG.info("The end.")


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


