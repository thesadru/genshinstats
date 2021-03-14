"""Automatic sign-in for hoyolab's daily rewards.

Automatically claims the next reward in the daily check-in rewards.
"""
from .errors import FirstSignIn
from .genshinstats import fetch_endpoint
from .hoyolab import get_game_uids

ACT_ID = "e202102251931481"
SOL_URL = "https://hk4e-api-os.mihoyo.com/event/sol/"

def get_daiy_reward_info() -> dict:
    """Fetches daily award info for the currently logged-in user."""
    return fetch_endpoint(SOL_URL+"info",act_id=ACT_ID)

def get_daily_rewards() -> list:
    """Gets claimed awards for the currently logged-in user"""
    return fetch_endpoint(SOL_URL+"award",act_id=ACT_ID)['list']

def sign_in(force: bool=False) -> bool:
    """Signs into hoyolab and claims the daily rewards.
    
    If the reward cannot be claimed, no claim will be attempted.
    To force the request use force.
    
    Returns whether sign-in was successful
    """
    info = get_daiy_reward_info()
    if not force:
        if info['first_bind']:
            raise FirstSignIn('First sign-in must be done manually. Please go to the website and claim your rewards.')
        if info['is_sign']:
            return False # already signed in
    
    u = get_game_uids()[0] # we need just one uid
    fetch_endpoint(SOL_URL+"sign",'POST',act_id=ACT_ID,uid=u['game_uid'],region=u['region'])
    return True
