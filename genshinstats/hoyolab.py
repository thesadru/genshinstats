"""Wrapper for the hoyolab.com community api.

Can search users, get record cards, active players...
"""
from functools import lru_cache
from typing import Optional, Iterable

from .genshinstats import fetch_endpoint


def search(keyword: str, size: int=20) -> dict:
    """Searches posts, topics and users.
    
    Takes in a keyword, replaces spaces with + and quotes other characters.
    Can return up to 20 results, based on size.
    """
    return fetch_endpoint("community/apihub/wapi/search",keyword=keyword,size=size,gids=2)

def check_in():
    """Checks in the user who's cookies are currently being used.
    
    This will give you points on hoyolab's site and also rewards in genshin.
    This also makes it possible to create an auto checkin.
    """
    fetch_endpoint("community/apihub/api/signIn",'POST',gids=2)

@lru_cache()
def get_langs() -> list:
    """Gets a list of translations for hoyolabs."""
    return fetch_endpoint("community/misc/wapi/langs",gids=2)['langs']

def get_community_user_info(community_uid: int) -> dict:
    """Gets community info of a user based on their community uid.
    
    Community info contains general data regarding the uid, nickname, introduction gender and so.
    It also contains stats for general community actions.
    
    You can get community id with `search`.
    """
    return fetch_endpoint("community/user/wapi/getUserFullInfo",uid=community_uid)

def get_record_card(community_uid: int) -> Optional[dict]:
    """Gets a game record card of a user based on their community uid.
    
    A record card contains data regarding the stats of a user for their displayed server.
    Their UID for a given server is also included.
    In case the user has set their profile to be private, returns None.
    
    You can get community id with `search`.
    """
    cards = fetch_endpoint("game_record/card/wapi/getGameRecordCard",uid=community_uid,gids=2)['list']
    return cards[0] if cards else None

def get_uid_from_community(community_uid: int) -> Optional[int]:
    """Gets a uid with a community uid.
    
    This is so it's possible to search a user and then directly get the uid.
    In case the uid is private, returns None.
    """
    card = get_record_card(community_uid)
    return int(card['game_role_id']) if card else None

def get_active_players(page_size: int=20, offset: int=0) -> list:
    """Gets a list of recommended active players
    
    Max page size is 195, you cannot offset beyond that.
    """
    return fetch_endpoint("community/user/wapi/recommendActive",gids=2,page_size=page_size,offset=offset)['list']

def get_public_players() -> Iterable[dict]:
    """Gets a list of players with public players.
    
    Returns a dict of their community uid, game uid and their game card.
    """
    players = get_active_players(page_size=0xffffffff)
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
