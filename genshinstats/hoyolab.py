"""Wrapper for the hoyolab.com community api.

Can search users, get record cards, active players...
"""
import time
from functools import lru_cache
from typing import Iterable, Optional

from .errors import CodeAlreadyUsed, TooLowAdventureRank
from .genshinstats import fetch_endpoint
from .utils import recognize_server


def search(keyword: str, size: int=20) -> dict:
    """Searches posts, topics and users.
    
    Can return up to 20 results, based on size.
    """
    return fetch_endpoint(
        "community/apihub/wapi/search",
        params=dict(keyword=keyword,size=size,gids=2)
    )

def check_in():
    """Checks in the user who's cookies are currently being used.
    
    This will give you points on hoyolab's site.
    """
    fetch_endpoint(
        "community/apihub/api/signIn",
        method='POST',
        params=dict(gids=2)
    )

@lru_cache()
def get_langs() -> list:
    """Gets a list of translations for hoyolabs."""
    return fetch_endpoint(
        "community/misc/wapi/langs",
        params=dict(gids=2)
    )['langs']

def get_game_accounts(chinese: bool=False) -> list:
    """Gets all game accounts of the currently signed in player.
    
    Can get accounts both for global and china.
    """
    url = "https://api-takumi.mihoyo.com/" if chinese else "https://api-os-takumi.mihoyo.com/"
    return fetch_endpoint(url+"binding/api/getUserGameRolesByCookie")['list']

def get_community_user_info(community_uid: int) -> dict:
    """Gets community info of a user based on their community uid.
    
    Community info contains general data regarding the uid, nickname, introduction gender and so.
    It also contains stats for general community actions.
    
    You can get community id with `search`.
    """
    return fetch_endpoint(
        "community/user/wapi/getUserFullInfo",
        params=dict(uid=community_uid)
    )

def get_record_card(community_uid: int) -> Optional[dict]:
    """Gets a game record card of a user based on their community uid.
    
    A record card contains data regarding the stats of a user for their displayed server.
    Their UID for a given server is also included.
    In case the user has set their profile to be private, returns None.
    
    You can get community id with `search`.
    """
    cards = fetch_endpoint(
        "game_record/card/wapi/getGameRecordCard",
        params=dict(uid=community_uid,gids=2)
    )['list']
    return cards[0] if cards else None

def get_uid_from_community(community_uid: int) -> Optional[int]:
    """Gets a uid with a community uid.
    
    This is so it's possible to search a user and then directly get the uid.
    In case the uid is private, returns None.
    """
    card = get_record_card(community_uid)
    return int(card['game_role_id']) if card else None

_last_redeem = .0
def _redeem_code(code: str, uid: int, region: str=None, game_biz: str='hk4e_global'):
    """Redeems a single code. Use redeem_code instead."""
    global _last_redeem
    t = time.time() - _last_redeem
    if t < 5: time.sleep(5-t)
    
    region = region or recognize_server(uid)
    try:
        return fetch_endpoint(
            "https://hk4e-api-os.mihoyo.com/common/apicdkey/api/webExchangeCdkey",
            params=dict(uid=uid,region=region,cdkey=code,game_biz=game_biz,lang='en')
        )
    finally:
        _last_redeem = time.time()

def redeem_code(code: str, uid: int=None) -> int:
    """Redeems a gift code for the currently signed in user.
    
    Api endpoint for https://genshin.mihoyo.com/en/gift.
    
    The code will be redeemed for every avalible account, 
    specifying the uid will claim it only for that account.
    Returns the amount of users it managed to claim codes for.
    
    Claiming code for every account will take 5s per account because of cooldowns.
    
    Currently codes can only be claimed for global accounts, not chinese.
    """
    if uid is not None:
        _redeem_code(code,uid)
        return 1
    
    success = 0
    for account in get_game_accounts():
        try: 
            _redeem_code(code,account['game_uid'],account['region'],account['game_biz'])
        except (CodeAlreadyUsed,TooLowAdventureRank): 
            pass
        else: 
            success += 1
    
    return success

def get_active_players(page_size: int=None, offset: int=0) -> list:
    """Gets a list of recommended active players
    
    When page size is None, gets all avalible active players.
    """
    return fetch_endpoint(
        "community/user/wapi/recommendActive",
        params=dict(page_size=page_size or 0xffff,offset=offset,gids=2)
    )['list']

def get_public_players() -> Iterable[dict]:
    """Gets a list of players with public accounts.
    
    Returns a dict of their community uid, game uid and their game card.
    """
    players = get_active_players()
    for player in players:
        community_uid = player['user']['uid']
        card = get_record_card(community_uid)
        if card is None:
            continue
        
        yield {
            'community_uid':community_uid,
            'uid':card['game_role_id'],
            'card':card
        }
