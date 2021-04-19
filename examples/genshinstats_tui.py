import genshinstats as gs

gs.set_cookie(account_id=...,cookie_token=...)

uid = input('Please enter a uid: ')
action = input('What would you like to view? [1. stats, 2. characters, 3. spiral abyss] ')

if action == '1':
    print(f'Getting stats for {uid}...\n')
    data = gs.get_user_info(uid)
    
    print(f"\nstats: ")
    for field,value in data['stats'].items():
        print(f"{field.replace('_',' ')}: {value}")
    print(f"\nexplorations: ")
    for area in data['explorations']:
        print(f"{area['name']}: explored {area['explored']}% | {area['type']} level {area['level']}")
    
elif action == '2':
    print(f'Getting characters for {uid}...\n')
    data = gs.get_all_characters(uid)
    
    data.sort(key=lambda x:(x['rarity'],x['level']),reverse=True)
    for char in data:
        print(f"{char['name']} ({char['rarity']}* {char['element']}): lvl {char['level']} C{char['constellation']}")
    
elif action == '3':
    previous = input('Get previous season instead of current? [y/n] ') in 'yY'
    print(f'Getting spiral abyss info for {uid}...\n')
    data = gs.get_spiral_abyss(uid,previous=previous)
    print(f"season {data['season']} ({data['season_start_time']} - {data['season_end_time']})")
    
    for field,value in data['stats'].items():
        print(f"{field.replace('_',' ')}: {value}")
    print('\ncharacter ranks:')
    for field,value in data['character_ranks'].items():
        print(f"{field.replace('_',' ')}: "+', '.join(f"{i['name']} ({i['value']})" for i in value[:5]))
