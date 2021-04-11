import genshinstats as gs
import time

gs.set_cookie(...)

while True:
    success = gs.sign_in()
    if success:
        print('Claimed daily reward.')
    else:
        print('Could not claim daily rewards')
    time.sleep(24*60*60 - 2)
