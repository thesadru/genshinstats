"""Automatic sign-in for hoyolab's daily rewards.

Automatically claims the next reward in the daily check-in rewards.
"""
from typing import Iterator, Optional, Tuple, List
from .genshinstats import fetch_endpoint
from .hoyolab import get_game_accounts

__all__ = [
    'get_daily_reward_info', 'get_claimed_rewards', 'get_monthly_rewards', 'claim_daily_reward'
]

OS_URL = "https://hk4e-api-os.mihoyo.com/event/sol/" # overseas
OS_ACT_ID = "e202102251931481"
CN_URL = "https://api-takumi.mihoyo.com/event/bbs_sign_reward/" # chinese
CN_ACT_ID = "e202009291139501"

def get_daily_reward_info(chinese: bool=False) -> Tuple[bool, int]:
    """Fetches daily award info for the currently logged-in user.
    
    Returns a tuple (if the user is logged in, how many total rewards the user claimed so far)
    """
    url,act_id = (CN_URL,CN_ACT_ID) if chinese else (OS_URL,OS_ACT_ID)
    data = fetch_endpoint(
        url+"info",
        params=dict(act_id=act_id)
    )
    return data['is_sign'], data['total_sign_day']

def get_claimed_rewards(chinese: bool=False) -> Iterator[dict]:
    """Gets claimed awards for the currently logged-in user"""
    url,act_id = (CN_URL,CN_ACT_ID) if chinese else (OS_URL,OS_ACT_ID)
    current_page = 1
    while True:
        data = fetch_endpoint(
            url+"award",
            params=dict(act_id=act_id, current_page=current_page, page_size=31)
        )['list']
        yield from data
        if len(data) < 10:
            break
        current_page += 1

def get_monthly_rewards(chinese: bool = False, lang: str = 'en-us') -> List[dict]:
    url,act_id = (CN_URL,CN_ACT_ID) if chinese else (OS_URL,OS_ACT_ID)
    return fetch_endpoint(
        url+"home",
        params=dict(act_id=act_id, lang=lang)
    )['awards'] # there's also a month attribute, but we ignore that

def claim_daily_reward(chinese: bool=False, lang: str = 'en-us') -> Optional[dict]:
    """Signs into hoyolab and claims the daily rewards.
    
    Chinese and overseas servers work a bit differently,
    so you must specify you want to claim rewards for chinese accounts.
    
    If the reward cannot be claimed, no claim will be attempted.
    Returns the claimed reward or None if the reward cannot be claimed.
    """
    signed_in, claimed_rewards = get_daily_reward_info(chinese)
    if signed_in:
        return None # already signed in
    
    account = get_game_accounts(chinese)[0] # we need just one uid
    url,act_id = (CN_URL,CN_ACT_ID) if chinese else (OS_URL,OS_ACT_ID)
    fetch_endpoint(
        url+"sign",
        method='POST',
        params=dict(act_id=act_id,uid=account['game_uid'],region=account['region'])
    )
    rewards = get_monthly_rewards(chinese, lang=lang)
    return rewards[claimed_rewards + 1]
