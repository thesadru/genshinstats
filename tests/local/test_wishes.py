import genshinstats as gs

def test_banner_types():
    banner_types = gs.get_banner_types()
    assert len(banner_types) == 4

def test_wish_history():
    wish_history = list(gs.get_wish_history(size=20))
    assert len(wish_history) == 20

def test_gacha_items():
    gacha_items = gs.get_gacha_items()
    assert len(gacha_items) >= 74

def test_banner_details():
    banner_ids = gs.get_banner_ids() or ["b8fd0d8a6c940c7a16a486367de5f6d2232f53"]
    banner_details = gs.get_banner_details(banner_ids[0])

def test_authkey_param():
    authkey = gs.extract_authkey(gs.wishes._read_logfile())
    wish_history = list(gs.get_wish_history(200, size=20, authkey=authkey))

def test_uid_from_authkey():
    uid = gs.get_uid_from_authkey(gs.get_authkey())
    assert gs.is_game_uid(uid)

def test_langs(uid: int = 710785423):
    langs = gs.get_langs()
    lang = 'de-de'

    characters = gs.get_characters(uid, lang=lang)
    for char in characters:
        if 'Player' in char['icon']:
            assert char["name"] == "Reisende"
    
    banner_types = gs.get_banner_types(lang=lang)
    assert banner_types[200] == "Standardgebet"
    
    history = list(gs.get_wish_history(200, size=20, lang=lang))
    assert history[0]['banner'] == "Standardgebet"
    
    items = gs.get_gacha_items(lang=lang)
    assert items[0]['type'] == "Figur"
    
    details = gs.get_banner_details("b8fd0d8a6c940c7a16a486367de5f6d2232f53", lang=lang)
    assert details['banner'] == "Aktionsgebet „Balladen in Bechern“"
