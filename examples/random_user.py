"""Shows you stats for random users"""
import random
import genshinstats as gs
gs.set_cookie_auto()

users = gs.get_recommended_users()
uids = [i['user']['uid'] for i in users]

while True:
    card = gs.get_record_card(random.choice(uids))
    if card is None:
        continue
    
    print(f"{card['nickname']} - {card['region_name']} ({card['game_role_id']})")
    print('\n'.join(f"{i['name']}: {i['value']}" for i in card['data']))
    
    input('\nPress enter to get next user ')
