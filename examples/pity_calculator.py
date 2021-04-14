import genshinstats as gs

for t in gs.get_gacha_types():
    print(t['name'])
    
    since = 0
    for pull in gs.get_gacha_log(t['key']):
        since += 1
        if pull['rarity'] == 5:
            print(f"{since} pulls since 5*, {90-since} until pity")
            break
    else:
        print(f"Never pulled a 5*, {90-since} until pity.")
