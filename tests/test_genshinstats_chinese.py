import os
import genshinstats as gs

gs.set_cookie(ltuid=os.environ['CN_LTUID'], ltoken=os.environ['CN_LTOKEN'])

uid = 101322963
mihoyo_uid = 75276539

def test_recognize_server():
    assert gs.recognize_server(uid) == 'cn_gf01'

def test_user_stats():
    stats = gs.get_user_stats(uid)

def test_characters():
    characters = gs.get_characters(uid)

def test_spiral_abyss():
    abyss = [
        gs.get_spiral_abyss(uid),
        gs.get_spiral_abyss(uid, previous=True)
    ]

def test_is_game_uid():
    assert gs.is_game_uid(710785423)
    assert not gs.is_game_uid(8366222)

def test_is_chinese():
    assert gs.is_chinese('cn_gf01')
    assert gs.is_chinese('cn_qd01')
    assert not gs.is_chinese('os_usa')
    assert not gs.is_chinese('os_asia')

    assert gs.is_chinese('123456789')
    assert gs.is_chinese(567890123)
    assert not gs.is_chinese('678901234')
    assert not gs.is_chinese(890123456)

def test_search():
    users = gs.search('西风', chinese=True)
    assert len(users) >= 2
    assert any(int(user['uid']) == 75276539 for user in users)

def test_record_card():
    card = gs.get_record_card(5861124, chinese=True)
    assert card is not None

def test_uid_from_community():
    assert gs.get_uid_from_hoyolab_uid(5861124, chinese=True) == 100122103

def test_recommended():
    recommended = gs.get_recommended_users()
    assert len(recommended) > 100

def test_hot_posts():
    hot_posts = gs.get_hot_posts(size=120)
    assert len(hot_posts) > 100
