import calendar
import contextlib
import time
from datetime import datetime

import genshinstats as gs
import pytest

gs.set_cookie_auto()

uid = 710785423

def test_game_accounts():
    accounts = gs.get_game_accounts()
    assert uid in [account['uid'] for account in accounts]

def test_check_in():
    # SignInException is the only ones allowed
    with contextlib.suppress(gs.SignInException), pytest.deprecated_call():
        gs.hoyolab_check_in()

def test_redeem_code():
    pytest.skip("Redeem takes too long")
    
    with pytest.raises(gs.CodeRedeemException):
        gs.redeem_code('genshingift')
    time.sleep(5)  # ratelimit
    with pytest.raises(gs.CodeRedeemException):
        gs.redeem_code('invalid')

def test_daily_reward():
    signed_in, claimed_rewards = gs.get_daily_reward_info()
    reward = gs.claim_daily_reward()
    
    if signed_in:
        assert reward is None
    else:
        assert reward is not None
        
        rewards = gs.get_monthly_rewards()
        assert rewards[claimed_rewards]['name'] == reward['name']

def test_daily_reward_info():
    s, c = gs.get_daily_reward_info()
    assert isinstance(s, bool)
    assert isinstance(c, int)

def test_monthly_rewards():
    rewards = gs.get_monthly_rewards()
    now = datetime.now()
    assert len(rewards) == calendar.monthrange(now.year,  now.month)[1]

def test_claimed_rewards():
    reward = next(gs.get_claimed_rewards())
