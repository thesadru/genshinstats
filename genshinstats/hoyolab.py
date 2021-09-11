"""Wrapper for the hoyolab.com community api.

Can search users, get record cards, redeem codes...
"""
import time
from typing import Any, Dict, List, Mapping, Optional

from .caching import permanent_cache
from .genshinstats import fetch_endpoint
from .pretty import prettify_game_accounts
from .utils import deprecated, recognize_server

__all__ = [
    "get_langs",
    "search",
    "set_visibility",
    "hoyolab_check_in",
    "get_game_accounts",
    "get_record_card",
    "get_uid_from_hoyolab_uid",
    "redeem_code",
    "get_recommended_users",
    "get_hot_posts",
]


@permanent_cache()
def get_langs() -> Dict[str, str]:
    """Gets codes of all languages and their names"""
    data = fetch_endpoint(
        "community/misc/wapi/langs",
        cookie={},
        params=dict(gids=2)
    )['langs']
    return {i['value']: i['name'] for i in data}

def search(keyword: str, size: int = 20, chinese: bool = False) -> List[Dict[str, Any]]:
    """Searches all users.

    Can return up to 20 results, based on size.
    """
    url = "https://bbs-api.mihoyo.com/" if chinese else "https://api-os-takumi.mihoyo.com/community/"
    return fetch_endpoint(
        url + "apihub/wapi/search",
        cookie={}, # this endpoint does not require cookies
        params=dict(keyword=keyword, size=size, gids=2)
    )['users']

def set_visibility(public: bool, cookie: Mapping[str, Any] = None) -> None:
    """Sets your data to public or private."""
    fetch_endpoint(
        "game_record/card/wapi/publishGameRecord",
        cookie=cookie,
        method='POST',
        # what's game_id about???
        json=dict(is_public=public, game_id=2)
    )

@deprecated()
def hoyolab_check_in(chinese: bool = False, cookie: Mapping[str, Any] = None) -> None:
    """Checks in the currently logged-in user to hoyolab.

    This function will not claim daily rewards!!!
    """
    url = "https://bbs-api.mihoyo.com/" if chinese else "https://api-os-takumi.mihoyo.com/community/"
    fetch_endpoint(
        url + "apihub/api/signIn",
        chinese=chinese,
        cookie=cookie,
        method='POST',
        json=dict(gids=2)
    )

def get_game_accounts(chinese: bool = False, cookie: Mapping[str, Any] = None) -> List[Dict[str, Any]]:
    """Gets all game accounts of the currently signed in player.

    Can get accounts both for overseas and china.
    """
    url = "https://api-takumi.mihoyo.com/" if chinese else "https://api-os-takumi.mihoyo.com/"
    data = fetch_endpoint(url+"binding/api/getUserGameRolesByCookie", cookie=cookie)['list']
    return prettify_game_accounts(data)

def get_record_card(hoyolab_uid: int, chinese: bool = False, cookie: Mapping[str, Any] = None) -> Optional[Dict[str, Any]]:
    """Gets a game record card of a user based on their hoyolab uid.

    A record card contains data regarding the stats of a user for their displayed server.
    Their uid for a given server is also included.
    In case the user hasn't set their data to public or you are ratelimited the function returns None.

    You can get a hoyolab id with `search`.
    """
    cards = fetch_endpoint(
        "game_record/card/wapi/getGameRecordCard",
        chinese=chinese,
        cookie=cookie,
        params=dict(uid=hoyolab_uid, gids=2)
    )['list']
    return cards[0] if cards else None

def get_uid_from_hoyolab_uid(hoyolab_uid: int, chinese: bool = False, cookie: Mapping[str, Any] = None) -> Optional[int]:
    """Gets a uid with a community uid.

    This is so it's possible to search a user and then directly get the uid.
    In case the uid is private, returns None.
    """
    card = get_record_card(hoyolab_uid, chinese, cookie)
    return int(card['game_role_id']) if card else None

def redeem_code(code: str, uid: int = None, cookie: Mapping[str, Any] = None) -> None:
    """Redeems a gift code for the currently signed in user.

    Api endpoint for https://genshin.mihoyo.com/en/gift.
    !!! This function requires account_id and cookie_token cookies !!!

    The code will be redeemed for every avalible account,
    specifying the uid will claim it only for that account.
    Returns the amount of users it managed to claim codes for.

    You can claim codes only every 5s so you must sleep between claims.
    The function sleeps for you when claiming for every account
    but you must sleep yourself when passing in a uid or when an error is encountered.

    Currently codes can only be claimed for overseas accounts, not chinese.
    """
    if uid is not None:
        fetch_endpoint(
            "https://hk4e-api-os.mihoyo.com/common/apicdkey/api/webExchangeCdkey",
            cookie=cookie,
            params=dict(uid=uid, region=recognize_server(uid),
                        cdkey=code, game_biz='hk4e_global', lang='en')
        )
    else:
        # cannot claim codes for accounts with ar lower than 10
        accounts = [account for account in get_game_accounts(cookie=cookie)
                    if account['level'] >= 10]
        for i, account in enumerate(accounts):
            if i: time.sleep(5) # there's a ratelimit of 1 request every 5 seconds
            redeem_code(code, account['uid'], cookie)

def get_recommended_users(page_size: int = None) -> List[Dict[str, Any]]:
    """Gets a list of recommended active users"""
    return fetch_endpoint(
        "community/user/wapi/recommendActive",
        cookie={},
        params=dict(page_size=page_size or 0x10000, offset=0, gids=2)
    )['list']

def get_hot_posts(forum_id: int = 1, size: int = 100, lang: str = 'en-us') -> List[Dict[str, Any]]:
    """Fetches hot posts from the front page of hoyolabs

    Posts are split into different forums set by ids 1-5.
    There may be less posts returned than size.
    """
    # the api is physically unable to return more than 2 ^ 24 bytes
    # that's around 2 ^ 15 posts so we limit the amount to 2 ^ 14
    # the user shouldn't be getting that many posts in the first place
    return fetch_endpoint(
        "community/post/api/forumHotPostFullList",
        cookie={},
        params=dict(forum_id=forum_id, page_size=min(size, 0x4000), lang=lang)
    )['posts']
