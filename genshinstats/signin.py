"""Automatic sign-in for hoyolab's daily rewards.

Automatically claims the next reward in the daily check-in rewards.
"""
from .errors import FirstSignIn, NoGameAccount
from .genshinstats import fetch_endpoint
from .hoyolab import get_game_uids

ACT_ID = "e202102251931481"
SOL_URL = "https://hk4e-api-os.mihoyo.com/event/sol/" # global
SIGN_URL = "https://api-takumi.mihoyo.com/event/bbs_sign_reward/" # chinese

def get_daily_reward_info(chinese: bool=False) -> dict:
    """Fetches daily award info for the currently logged-in user."""
    url = SIGN_URL if chinese else SOL_URL
    return fetch_endpoint(
        url+"info",
        params=dict(act_id=ACT_ID)
    )

def get_daily_rewards(chinese: bool=False) -> list:
    """Gets claimed awards for the currently logged-in user"""
    url = SIGN_URL if chinese else SOL_URL
    return fetch_endpoint(
        url+"award",
        params=dict(act_id=ACT_ID) # chinese might need more params? idk yet
    )['list']

def sign_in(chinese: bool=False, force: bool=False) -> bool:
    """Signs into hoyolab and claims the daily rewards.
    
    Chinese and global servers work a bit differentelly,
    so you must specify you want to claim rewards for chinese accounts here.
    
    If the reward cannot be claimed, no claim will be attempted.
    To force the request use force.
    
    Returns whether sign-in was successful
    """
    info = get_daily_reward_info(chinese)
    if not force:
        if info['first_bind']:
            raise FirstSignIn('First sign-in must be done manually. Please go to the website and claim your rewards.')
        if info['is_sign']:
            return False # already signed in
    
    u = get_game_uids(chinese)[0] # we need just one uid (idk about the chinese version)
    fetch_endpoint(
        SOL_URL+"sign",
        method='POST',
        params=dict(act_id=ACT_ID,uid=u['game_uid'],region=u['region'])
    )
    return True
