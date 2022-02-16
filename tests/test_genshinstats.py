import os

import genshinstats as gs
import pytest
import urllib3

# unless anyone knows how to inject certificates into a github workflow this is required
try:
    gs.get_langs()
    gs.search("a")
except urllib3.exceptions.SSLError:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    gs.genshinstats.session.verify = False

uid = 710785423
hoyolab_uid = 8366222


@pytest.fixture(scope="module", autouse=True)
def set_cookie():
    gs.set_cookie(ltuid=os.environ["GS_LTUID"], ltoken=os.environ["GS_LTOKEN"])


def test_recognize_server():
    assert gs.recognize_server(uid) == "os_euro"


def test_user_stats():
    stats = gs.get_user_stats(uid)


def test_characters():
    characters = gs.get_characters(uid)


def test_spiral_abyss():
    abyss = [gs.get_spiral_abyss(uid), gs.get_spiral_abyss(uid, previous=True)]


def test_activities():
    activities = gs.get_activities(uid)


def test_is_game_uid():
    assert gs.is_game_uid(710785423)
    assert not gs.is_game_uid(8366222)


def test_is_chinese():
    for i in ("cn_gf01", "cn_qd01", "123456789", 567890123):
        assert gs.is_chinese(i)
    for i in ("os_usa", "os_asia", "678901234", 890123456):
        assert not gs.is_chinese(i)


def test_record_card():
    card = gs.get_record_card(hoyolab_uid)
    assert card is not None


def test_uid_from_community():
    assert gs.get_uid_from_hoyolab_uid(hoyolab_uid) == uid


def test_recommended():
    recommended = gs.get_recommended_users()
    assert len(recommended) > 100


def test_hot_posts():
    hot_posts = gs.get_hot_posts(size=120)
    assert len(hot_posts) > 100
