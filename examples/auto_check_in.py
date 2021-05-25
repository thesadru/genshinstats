import genshinstats as gs
import time

gs.set_cookies_auto()

while True:
    reward = gs.claim_daily_reward()
    if reward is not None:
        print(f"Claimed daily reward - {reward['cnt']} {reward['name']}")
    else:
        print("Could not claim daily reward")
    time.sleep(24*60*60 - 2)
