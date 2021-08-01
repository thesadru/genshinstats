import calendar
import contextlib
import json
import os
import random
import time
import unittest
import warnings
from datetime import datetime

import genshinstats as gs

data = {}
uid = 710785423
hoyolab_uid = 8366222
test_cookie = dict(ltuid=os.environ['GS_LTUID'], ltoken=os.environ['GS_LTOKEN'])

class GenshinStatsTest(unittest.TestCase):
    @staticmethod
    def setUpClass():
        gs.set_cookie(test_cookie)

    def test_recognize_server(self):
        self.assertEqual(gs.recognize_server(uid), 'os_euro')

    def test_cookie(self):
        gs.set_cookies()  # equivalent to gs.cookies.clear()
        self.assertEqual(gs.genshinstats.cookies, [])
        gs.set_cookies('header1', 'header2')
        self.assertEqual(len(gs.genshinstats.cookies), 2)
        gs.set_cookie(test_cookie)
        expected = gs.genshinstats.RequestsCookieJar()
        expected.update(test_cookie)
        self.assertEqual(gs.genshinstats.cookies[0], test_cookie)

    def test_cookie_param(self):
        gs.set_cookies()
        # from README.md
        cookie = dict(ltuid=119480035, ltoken="cnF7TiZqHAAvYqgCBoSPx5EjwezOh1ZHoqSHf7dT")
        accounts = gs.get_game_accounts(cookie=cookie)
        self.assertEqual(accounts, [])
        with contextlib.suppress(gs.SignInException):
            gs.hoyolab_check_in(cookie)
        gs.set_cookie(test_cookie)

    def test_user_stats(self):
        data['stats'] = gs.get_user_stats(uid)

    def test_characters(self):
        data['characters'] = gs.get_characters(uid)

    def test_spiral_abyss(self):
        data['spiral_abyss'] = [
            gs.get_spiral_abyss(uid, previous=False),
            gs.get_spiral_abyss(uid, previous=True)
        ]

    def test_is_game_uid(self):
        self.assertTrue(gs.is_game_uid(710785423))
        self.assertFalse(gs.is_game_uid(8366222))

    def test_is_chinese(self):
        self.assertTrue(gs.is_chinese('cn_gf01'))
        self.assertTrue(gs.is_chinese('cn_qd01'))
        self.assertFalse(gs.is_chinese('os_usa'))
        self.assertFalse(gs.is_chinese('os_asia'))
        self.assertTrue(gs.is_chinese('123456789'))
        self.assertTrue(gs.is_chinese(567890123))
        self.assertFalse(gs.is_chinese('678901234'))
        self.assertFalse(gs.is_chinese(890123456))

    def test_search(self):
        data['search'] = gs.search('sadru')

    def test_record_card(self):
        card = gs.get_record_card(hoyolab_uid)
        self.assertIsNotNone(card)
        data['record_card'] = card

    def test_uid_from_community(self):
        self.assertEqual(gs.get_uid_from_hoyolab_uid(hoyolab_uid), uid)

    def test_recommended(self):
        recommended = gs.get_recommended_users()
        self.assertGreater(len(recommended), 100)

    def test_hot_posts(self):
        hot_posts = gs.get_hot_posts(size=120)
        self.assertGreater(len(hot_posts), 100)

    # wish history: 
    def test_banner_types(self):
        data['banner_types'] = gs.get_banner_types()

    def test_wish_history(self):
        data['wish_history'] = list(gs.get_wish_history(size=60))

    def test_gacha_items(self):
        data['gacha_items'] = gs.get_gacha_items()

    def test_all_banner_ids(self):
        data['banner_ids'] = gs.get_banner_ids()

    def test_banner_details(self):
        gs.get_banner_details("b8fd0d8a6c940c7a16a486367de5f6d2232f53")
        data['banner_details'] = [
            gs.get_banner_details(i) for i in gs.get_banner_ids()]

    def test_authkey_param(self):
        authkey = gs.extract_authkey(gs.wishes._read_logfile())
        list(gs.get_wish_history(200, size=20, authkey=authkey))

    def test_uid_from_authkey(self):
        self.assertEqual(gs.get_uid_from_authkey(gs.get_authkey()), uid)

    def test_langs(self):
        lang = random.choice(list(gs.get_langs()))
        data['langs'] = {
            'characters': gs.get_characters(uid, lang=lang),
            'banner_types': gs.get_banner_types(lang=lang),
            'wish_history': list(gs.get_wish_history(200, 20, lang=lang)),
            'gacha_items': gs.get_gacha_items(lang=lang),
            'banner_details': gs.get_banner_details("b8fd0d8a6c940c7a16a486367de5f6d2232f53", lang=lang),
        }
        # data['langs'] = {}
        # for lang, name in gs.get_langs().items():
        #     data['langs'][lang] = {
        #         'lang':lang,
        #         'lang_name': name,
        #         'characters':gs.get_characters(uid, lang=lang),
        #         'banner_types': gs.get_banner_types(lang=lang),
        #         'wish_history':list(gs.get_wish_history(301, 10, lang=lang)),
        #         'gacha_items':gs.get_gacha_items(lang=lang),
        #         'banner_details':gs.get_banner_details("b8fd0d8a6c940c7a16a486367de5f6d2232f53", lang=lang),
        #     }

    @staticmethod
    def tearDownClass():
        with open('test.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)


class AccountSpecificTests(unittest.TestCase):
    @staticmethod
    def setUpClass():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            gs.set_cookie_auto()
        gs.set_visibility(True)

    def test_game_uids(self):
        gs.get_game_accounts()

    def test_check_in(self):
        with contextlib.suppress(gs.SignInException):
            gs.hoyolab_check_in()

    @unittest.skip('Unreliable. Redeem code takes too long.')
    def test_redeem_code(self):
        # takes like 30s to run
        with self.assertRaises(gs.CodeRedeemException):
            gs.redeem_code('genshingift')  # already claimed
        time.sleep(5)  # ratelimit
        with self.assertRaises(gs.CodeRedeemException):
            gs.redeem_code('invalid')  # invalid code

    def test_daily_reward(self):
        gs.claim_daily_reward()

    def test_daily_reward_info(self):
        gs.get_daily_reward_info()

    def test_monthly_rewards(self):
        rewards = gs.get_monthly_rewards()
        now = datetime.now()
        self.assertEqual(len(rewards), calendar.monthrange(
            now.year,  now.month)[1])

    def test_claimed_rewards(self):
        next(gs.get_claimed_rewards())

    def test_set_visibility(self):
        gs.set_visibility(False)
        gs.set_cookies()
        cookie = gs.get_browser_cookies()
        with self.assertRaises(gs.DataNotPublic):
            gs.get_user_stats(uid, cookie=test_cookie)
        gs.set_cookie(cookie)
        gs.set_visibility(True)
    


if __name__ == '__main__':
    unittest.main()
