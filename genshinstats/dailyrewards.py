"""Automatic sign-in for hoyolab's daily rewards.

Automatically claims the next reward in the daily check-in rewards.
"""
from .errors import SignInException
from .genshinstats import fetch_endpoint
from .hoyolab import get_game_accounts

OS_URL = "https://hk4e-api-os.mihoyo.com/event/sol/" # overseas
OS_ACT_ID = "e202102251931481"
CN_URL = "https://api-takumi.mihoyo.com/event/bbs_sign_reward/" # chinese
CN_ACT_ID = "e202009291139501"

def get_daily_reward_info(chinese: bool=False) -> dict:
    """Fetches daily award info for the currently logged-in user."""
    url,act_id = (CN_URL,CN_ACT_ID) if chinese else (OS_URL,OS_ACT_ID)
    return fetch_endpoint(
        url+"info",
        params=dict(act_id=act_id)
    )

def get_daily_rewards(chinese: bool=False) -> list:
    """Gets claimed awards for the currently logged-in user"""
    url,act_id = (CN_URL,CN_ACT_ID) if chinese else (OS_URL,OS_ACT_ID)
    return fetch_endpoint(
        url+"award",
        params=dict(act_id=act_id) # chinese might need more params? idk yet
    )['list']

def claim_daily_reward(chinese: bool=False, force: bool=False) -> bool:
    """Signs into hoyolab and claims the daily rewards.
    
    Chinese and overseas servers work a bit differently,
    so you must specify you want to claim rewards for chinese accounts.
    
    If the reward cannot be claimed, no claim will be attempted unless forced.
    Returns whether sign-in was successful
    """
    if not force:
        info = get_daily_reward_info(chinese)
        if info['first_bind']:
            raise SignInException('First sign-in must be done manually. Please go to the website and claim your rewards.')
        if info['is_sign']:
            return False # already signed in
    
    account = get_game_accounts(chinese)[0] # we need just one uid
    url,act_id = (CN_URL,CN_ACT_ID) if chinese else (OS_URL,OS_ACT_ID)
    fetch_endpoint(
        url+"sign",
        method='POST',
        params=dict(act_id=act_id,uid=account['game_uid'],region=account['region'])
    )
    return True
