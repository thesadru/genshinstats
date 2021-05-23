"""Wrapper for the hoyolab.com community api.

Can search users, get record cards, active players...
"""
from genshinstats.pretty import prettify_langs
import logging
import time
from functools import lru_cache
from typing import Dict, List, Optional

from .errors import CodeRedeemException
from .genshinstats import fetch_endpoint
from .utils import recognize_server

__all__ = [
    'search', 'hoyolab_check_in', 'get_langs', 'get_game_accounts',
    'get_record_card', 'get_uid_from_hoyolab_uid', 'redeem_code'
]

logger = logging.getLogger('genshinstats')

def search(keyword: str, size: int = 20) -> dict:
    """Searches all users.

    Can return up to 20 results, based on size.
    """
    return fetch_endpoint(
        "community/apihub/wapi/search",
        params=dict(keyword=keyword, size=size, gids=2)
    )['users']

def hoyolab_check_in() -> None:
    """Checks in the currently logged-in user to hoyolab.

    This function will not claim daily rewards!!!
    """
    fetch_endpoint(
        "community/apihub/api/signIn",
        method='POST',
        json=dict(gids=2)
    )

@lru_cache()
def get_langs() -> List[Dict[str, str]]:
    """Gets a list of languages."""
    data = fetch_endpoint(
        "community/misc/wapi/langs",
        params=dict(gids=2)
    )['langs']
    return prettify_langs(data)

def get_game_accounts(chinese: bool = False) -> List[dict]:
    """Gets all game accounts of the currently signed in player.

    Can get accounts both for overseas and china.
    """
    url = "https://api-takumi.mihoyo.com/" if chinese else "https://api-os-takumi.mihoyo.com/"
    return fetch_endpoint(url+"binding/api/getUserGameRolesByCookie")['list']

def get_record_card(hoyolab_uid: int) -> Optional[dict]:
    """Gets a game record card of a user based on their hoyolab uid.

    A record card contains data regarding the stats of a user for their displayed server.
    Their uid for a given server is also included.
    In case the user hasn't set their data to public the function returns None.

    You can get a hoyolab id with `search`.
    """
    cards = fetch_endpoint(
        "game_record/card/wapi/getGameRecordCard",
        params=dict(uid=hoyolab_uid, gids=2)
    )['list']
    return cards[0] if cards else None

def get_uid_from_hoyolab_uid(hoyolab_uid: int) -> Optional[int]:
    """Gets a uid with a community uid.

    This is so it's possible to search a user and then directly get the uid.
    In case the uid is private, returns None.
    """
    card = get_record_card(hoyolab_uid)
    return int(card['game_role_id']) if card else None

def redeem_code(code: str, uid: Optional[int] = None) -> None:
    """Redeems a gift code for the currently signed in user.

    Api endpoint for https://genshin.mihoyo.com/en/gift.
    !!! This function requires account_id and cookie_token cookies !!!

    The code will be redeemed for every avalible account, 
    specifying the uid will claim it only for that account.
    Returns the amount of users it managed to claim codes for.

    Claiming code for every account will take 5s per account because of cooldowns.

    Currently codes can only be claimed for overseas accounts, not chinese.
    """
    if uid is not None:
        fetch_endpoint(
            "https://hk4e-api-os.mihoyo.com/common/apicdkey/api/webExchangeCdkey",
            params=dict(uid=uid, region=recognize_server(uid),
                        cdkey=code, game_biz='hk4e_global', lang='en')
        )
    else:
        for account in get_game_accounts():
            try:
                redeem_code(code, account['game_uid'])
            except CodeRedeemException as e:
                print(f"Redeem for {account['nickname']} ({account['game_uid']}) failed: {e}.")
            else:
                print(f"Redeemed code for {account['nickname']} ({account['game_uid']}).")
            time.sleep(5)
