import os

import genshinstats as gs
import pytest

uid = 101322963
mihoyo_uid = 75276539


@pytest.fixture(scope="module", autouse=True)
def set_cookie():
    gs.set_cookie(ltuid=os.environ["CN_LTUID"], ltoken=os.environ["CN_LTOKEN"])


def test_recognize_server():
    assert gs.recognize_server(uid) == "cn_gf01"


def test_user_stats():
    stats = gs.get_user_stats(uid)


def test_characters():
    characters = gs.get_characters(uid)


def test_spiral_abyss():
    abyss = [gs.get_spiral_abyss(uid), gs.get_spiral_abyss(uid, previous=True)]


def test_search():
    users = gs.search("西风", chinese=True)
    assert len(users) >= 2
    assert any(int(user["uid"]) == 75276539 for user in users)


def test_record_card():
    card = gs.get_record_card(5861124, chinese=True)
    assert card is not None


def test_uid_from_community():
    assert gs.get_uid_from_hoyolab_uid(5861124, chinese=True) == 100122103
