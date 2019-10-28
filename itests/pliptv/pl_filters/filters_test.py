import os
import unittest
import xmlrunner

from pliptv.config_loader import playlist_config
from pliptv.models.streams import StreamMeta
from pliptv.pl_filters.display_name_filter import DisplayNameFilter
from pliptv.pl_filters.filter_abc import FilterABC
from pliptv.pl_filters.filters_loader import (
    load_class_from_name,
    class_list_from_modules,
    load_modules_from_path,
)
from pliptv.pl_filters.quality_filter import QualityFilter
from pliptv.pl_filters.shift_filter import ShiftFilter


class FiltersTests(unittest.TestCase):
    def test_shift_filter_ok(self):
        pl_filter = ShiftFilter(playlist_config.config)

        test_suite = [
            (StreamMeta("fr: name1 +1"), "1", "fr: name1"),
            (StreamMeta("|usa| name2"), "", "|usa| name2"),
            (StreamMeta("ar| test 12 +4 1080"), "4", "ar| test 12"),
            (StreamMeta("test 123 HD +8"), "8", "test 123 HD"),
        ]

        for val in test_suite:
            with self.subTest(val=val):
                res = pl_filter.apply(val[0])
                self.assertTrue(res.display_name == val[2])
                self.assertTrue(res.tvg.tvg_shift == val[1])

    def test_clean_name_filter_ok(self):
        pl_filter = DisplayNameFilter(playlist_config.config)

        test_suite = [
            (StreamMeta("fr: name1"), "fr", "name1"),
            (StreamMeta("|usa| name2"), "usa", "name2"),
            (StreamMeta("ar| test 12"), "ar", "test 12"),
            (StreamMeta("test 123 HD"), "", "test 123 HD"),
        ]

        for val in test_suite:
            with self.subTest(val=val):
                res = pl_filter.apply(val[0])
                self.assertTrue(res.display_name == val[2])
                self.assertTrue(res[StreamMeta.CULTURE_KEY] == val[1])

    def test_quality_filter_ok(self):
        pl_filter = QualityFilter(playlist_config.config)

        test_suite = [
            (StreamMeta("name1 1080p"), "fhd", "name1"),
            (StreamMeta("fr: name1 4k"), "4k", "fr: name1"),
            (StreamMeta("ar| test 12 hd1"), "hd", "ar| test 12 1"),
            (StreamMeta("test 123"), "sd", "test 123"),
        ]

        for val in test_suite:
            with self.subTest(val=val):
                res = pl_filter.apply(val[0])
                self.assertTrue(
                    val[0].display_name == val[2], f"{res.display_name} isn't {val[2]}"
                )
                self.assertTrue(
                    val[0][StreamMeta.QUALITY_KEY] == val[1],
                    f"{res[StreamMeta.QUALITY_KEY]} isn't {val[1]}",
                )

    def test_filter_loader(self):
        modules = load_modules_from_path(
            os.path.join(
                os.path.dirname(__file__), "../../../dags/common/playlists/pl_filters"
            ),
            pattern=r".+_filter.py$",
        )
        self.assertIsNotNone(modules)

        class_list = class_list_from_modules(modules[0][0])
        self.assertIsNotNone(class_list)

        cls = load_class_from_name(f"{modules[0][0]}.{class_list[0]}")
        self.assertIsNotNone(cls)
        self.assertTrue(issubclass(cls, FilterABC))


if __name__ == "__main__":
    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output="test-reports"),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False,
        buffer=False,
        catchbreak=False,
    )
