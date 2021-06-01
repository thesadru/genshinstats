"""Automatic sign-in for hoyolab's daily rewards.

Automatically claims the next reward in the daily check-in rewards.
"""
from typing import Any, Dict, Iterator, Optional, Tuple
from urllib.parse import urljoin

from .genshinstats import fetch_endpoint
from .hoyolab import get_game_accounts

__all__ = [
    'fetch_daily_endpoint', 'get_daily_reward_info', 'get_claimed_rewards', 
    'get_monthly_rewards', 'claim_daily_reward'
]

OS_URL = "https://hk4e-api-os.mihoyo.com/event/sol/" # overseas
OS_ACT_ID = "e202102251931481"
CN_URL = "https://api-takumi.mihoyo.com/event/bbs_sign_reward/" # chinese
CN_ACT_ID = "e202009291139501"

def fetch_daily_endpoint(endpoint: str, chinese: bool = False, **kwargs) -> Dict[str, Any]:
    """Fetch an enpoint for daily rewards"""
    url,act_id = (CN_URL,CN_ACT_ID) if chinese else (OS_URL,OS_ACT_ID)
    kwargs.setdefault('params',{})['act_id'] = act_id
    url = urljoin(url, endpoint)
    
    return fetch_endpoint(url, **kwargs)


def get_daily_reward_info(chinese: bool = False) -> Tuple[bool, int]:
    """Fetches daily award info for the currently logged-in user.
    
    Returns a tuple - whether the user is logged in, how many total rewards the user has claimed so far
    """
    data = fetch_daily_endpoint("info", chinese)
    return data['is_sign'], data['total_sign_day']

def get_monthly_rewards(chinese: bool = False, lang: str = 'en-us') -> list:
    """Gets a list of avalible rewards for the current month"""
    return fetch_daily_endpoint(
        "home", chinese, 
        params=dict(lang=lang)
    )['awards']

def get_claimed_rewards(chinese: bool = False) -> Iterator[dict]:
    """Gets all claimed awards for the currently logged-in user"""
    current_page = 1
    while True:
        data = fetch_daily_endpoint(
            "award", chinese, 
            params=dict(current_page=current_page)
        )['list']
        yield from data
        if len(data) < 10:
            break
        current_page += 1

def claim_daily_reward(chinese: bool=False, lang: str = 'en-us') -> Optional[dict]:
    """Signs into hoyolab and claims the daily rewards.
    
    Chinese and overseas servers work a bit differently,
    so you must specify whether you want to claim rewards for chinese accounts.
    
    Returns the claimed reward or None if the reward cannot be claimed yet.
    """
    signed_in, claimed_rewards = get_daily_reward_info(chinese)
    if signed_in:
        return None # already signed in
    
    account = get_game_accounts(chinese)[0] # we need just one uid
    fetch_daily_endpoint(
        "sign", chinese, 
        method="POST",
        params=dict(uid=account['game_uid'], region=account['region'])
    )
    rewards = get_monthly_rewards(chinese, lang=lang)
    return rewards[claimed_rewards + 1]
