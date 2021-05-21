"""Wrapper for the hoyolab.com community api.

Can search users, get record cards, active players...
"""
import logging
import time
from functools import lru_cache
from typing import List, Optional

from .errors import CodeRedeemException, RedeemCooldown
from .genshinstats import fetch_endpoint
from .utils import recognize_server

logger = logging.getLogger('genshinstats')

def search(keyword: str, size: int = 20) -> dict:
    """Searches all users.

    Can return up to 20 results, based on size.
    """
    return fetch_endpoint(
        "community/apihub/wapi/search",
        params=dict(keyword=keyword, size=size, gids=2)
    )['users']

def hoylab_check_in() -> None:
    """Checks in the user who's cookies are currently being used.

    This will give you points on hoyolab's site.
    """
    fetch_endpoint(
        "community/apihub/api/signIn",
        method='POST',
        json=dict(gids=2)
    )

@lru_cache()
def get_langs() -> List[dict]:
    """Gets a list of languages."""
    return fetch_endpoint(
        "community/misc/wapi/langs",
        params=dict(gids=2)
    )['langs']

def get_game_accounts(chinese: bool = False) -> List[dict]:
    """Gets all game accounts of the currently signed in player.

    Can get accounts both for overseas and china.
    """
    url = "https://api-takumi.mihoyo.com/" if chinese else "https://api-os-takumi.mihoyo.com/"
    return fetch_endpoint(url+"binding/api/getUserGameRolesByCookie")['list']

def get_record_card(hoyolab_uid: int) -> Optional[dict]:
    """Gets a game record card of a user based on their community uid.

    A record card contains data regarding the stats of a user for their displayed server.
    Their uid for a given server is also included.
    In case the user hasn't set their data to public the function returns None.

    You can get community id with `search`.
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

def _redeem_code(code: str, uid: int, region: str = None, game_biz: str = 'hk4e_global', sleep: bool = True) -> None:
    """Redeems a single code. Use redeem_code instead."""
    region = region or recognize_server(uid)
    try:
        fetch_endpoint(
            "https://hk4e-api-os.mihoyo.com/common/apicdkey/api/webExchangeCdkey",
            params=dict(uid=uid, region=region, cdkey=code, game_biz=game_biz, lang='en')
        )
    except RedeemCooldown as e:
        if not sleep:
            raise
        logger.debug(f'Sleeping {e.cooldown}s for code redemption.')
        time.sleep(e.cooldown + 0.5) # sleep a bit more just to be sure
        _redeem_code(code, uid, region, game_biz, sleep=False)


def redeem_code(code: str, uid: int = None, sleep: bool = True) -> int:
    """Redeems a gift code for the currently signed in user.

    Api endpoint for https://genshin.mihoyo.com/en/gift.

    The code will be redeemed for every avalible account, 
    specifying the uid will claim it only for that account.
    Returns the amount of users it managed to claim codes for.

    Claiming code for every account will take 5s per account because of cooldowns.
    This can be disable completely by setting sleep to False.

    Currently codes can only be claimed for overseas accounts, not chinese.
    """
    if uid is not None:
        _redeem_code(code, uid, sleep=sleep)
        return 1

    success = 0
    for account in get_game_accounts():
        logger.info(f"Redeeming code for {account['nickname']} ({account['game_uid']}).")
        try:
            _redeem_code(code, account['game_uid'], account['region'], account['game_biz'], sleep=sleep)
        except CodeRedeemException as e:
            logger.info(f"Redeem for {account['nickname']} ({account['game_uid']}) failed ({e}).")
        else:
            success += 1

    return success
