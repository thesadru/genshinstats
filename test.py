import json
import logging
import os
import time
import unittest
import warnings
import contextlib

import genshinstats as gs

logging.basicConfig()
# gs.logger.setLevel(logging.DEBUG)

data = {}
uid = 710785423
hoyolab_uid = 8366222

class GenshinStatsTest(unittest.TestCase):
    @staticmethod
    def setUpClass():
        gs.set_cookie(ltuid=os.environ['GS_LTUID'],ltoken=os.environ['GS_LTOKEN'])
    def test_recognize_server(self):
        self.assertEqual(gs.recognize_server(uid),'os_euro')
    def test_user_stats(self):
        data['stats'] = gs.get_user_stats(uid)
    def test_characters(self):
        data['characters'] = gs.get_characters(uid)
    def test_spiral_abyss(self):
        data['spiral_abyss'] = [
            gs.get_spiral_abyss(uid,previous=False),
            gs.get_spiral_abyss(uid,previous=True)
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
        data['record_card'] = gs.get_record_card(hoyolab_uid)
    def test_uid_from_community(self):
        self.assertEqual(gs.get_uid_from_hoyolab_uid(hoyolab_uid), uid)
    
    def test_banner_types(self):
        data['banner_types'] = gs.get_banner_types()
    def test_wish_history(self):
        data['wish_history'] = list(gs.get_wish_history(size=60))
    def test_wish_items(self):
        data['wish_items'] = gs.get_wish_items()
    def test_all_banner_ids(self):
        data['banner_ids'] = gs.get_banner_ids()
    def test_banner_details(self):
        data['banner_details'] = gs.get_banner_details("b8fd0d8a6c940c7a16a486367de5f6d2232f53")
        data['banner_details_all'] = [gs.get_banner_details(i) for i in gs.get_banner_ids()]
    def test_authkey_param(self):
        authkey = gs.extract_authkey(gs.wishes._read_logfile())
        list(gs.get_wish_history(200, size=20, authkey=authkey))
    def test_empty_gacha(self):
        s = time.time()
        x = list(gs.get_wish_history(200, size=0))
        t = time.time() - s
        self.assertEqual(x, [])
        self.assertLess(t, .01)
    def test_uid_from_authkey(self):
        self.assertEqual(gs.get_uid_from_authkey(gs.get_authkey()),uid)
        
    def test_langs(self):
        lang = 'fr-fr'
        short_lang = 'fr'
        data['langs'] = {
            'characters':gs.get_characters(uid, lang=lang),
            'gacha_types':gs.get_banner_types(lang=short_lang),
            'wish_history':list(gs.get_wish_history(200, 20, lang=short_lang)),
            'gacha_items':gs.get_wish_items(lang=lang),
            'gacha_details':gs.get_banner_details("b8fd0d8a6c940c7a16a486367de5f6d2232f53", lang=lang),
        }
        # data['langs'] = {}
        # for l in gs.get_langs():
        #     lang = l['value']
        #     short_lang = l['value'].split('-')[0]
        #     if short_lang == 'zh': short_lang = lang # ???
        #     data['langs'][lang] = {
        #         'lang':lang,'short_lang':short_lang,
        #         'characters':gs.get_all_characters(uid,lang=lang),
        #         'gacha_types':gs.get_gacha_types(lang=short_lang),
        #         'wish_history':list(gs.get_wish_history(301,10,lang=short_lang)),
        #         'gacha_items':gs.get_gacha_items(lang=lang),
        #         'gacha_details':gs.get_gacha_details(gacha_id,lang=lang),
        #     }
    
    @staticmethod
    def tearDownClass():
        with open('test.json','w', encoding='utf-8') as file:
            json.dump(data,file,indent=4,ensure_ascii=False)

class AccountSpecificTests(unittest.TestCase):
    @staticmethod
    def setUpClass():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            gs.set_cookie_auto()
    def test_game_uids(self):
        gs.get_game_accounts()
    def test_check_in(self):
        with contextlib.suppress(gs.SignInException):
            gs.hoyolab_check_in()
    @unittest.skip('Redeem code takes too long')
    def test_redeem_code(self):
        # takes like 30s to run
        with self.assertRaises(gs.CodeRedeemException):
            gs.redeem_code('genshingift',uid)
        with self.assertRaises(gs.CodeRedeemException):
            gs.redeem_code('invalid',uid)
    def test_daily_reward(self):
        gs.claim_daily_reward()
    def test_daily_reward_info(self):
        gs.get_daily_reward_info()
    def test_monthly_rewards(self):
        gs.get_monthly_rewards()
    def test_claimed_rewards(self):
        next(gs.get_claimed_rewards())

if __name__ == '__main__':
    unittest.main()
