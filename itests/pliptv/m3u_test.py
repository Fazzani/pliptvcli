import unittest

import xmlrunner

from pliptv.models.streams import M3u


class M3uTests(unittest.TestCase):
    def test_import_from_dict(self):
        display_name = "tf1"
        tf1_id = "tf1_id"
        group_bein = "bein qa"
        pl = [
            (
                f'#EXTINF:-1 tvg-Id="{tf1_id}" tvg-logo="http://logo-tf1.png" tvg-name="*** SERVER DMTN-IPTV ***" tvg-logo="" group-title="france",{display_name}',
                "http://vipmax-tv.net:8080/user/pass/11499",
            ),
            (
                f'#EXTINF:-1 tvg-ID="tvgid" tvg-name="tvgname" tvg-logo="logo" group-title="{group_bein}", bein sports 1 hd',
                "http://vipmax-tv.net:8080/user/pass/1",
            ),
        ]
        m3u = M3u.from_list("test", pl)
        self.assertEqual(len(m3u.streams), 2)
        self.assertEqual(m3u.streams[0].meta.display_name, display_name)
        self.assertEqual(m3u.streams[0].meta.tvg.tvg_id, tf1_id)
        self.assertEqual(m3u.streams[1].meta.tvg.tvg_logo, "logo")
        self.assertEqual(m3u.streams[1].meta.tvg.group_title, group_bein)
        m3u_raw = str(m3u)
        self.assertIsNotNone(m3u_raw)
        # f = open("tmp.txt", "w+")
        # f.write(m3u_raw)
        # f.close()

    def test_translate_channel_name(self):
        from pliptv.m3u_utils import translate_channel_name

        res = translate_channel_name("bein_sports")
        self.assertEqual("Beinsports", res)


if __name__ == "__main__":
    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output="test-reports"),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False,
        buffer=False,
        catchbreak=False,
    )
