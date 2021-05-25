import genshinstats as gs

banners = gs.get_banner_types()
for banner_type, banner_name in banners.items():
    print(banner_name)
    
    since = 0
    for pull_index, pull in gs.get_wish_history(banner_type):
        since += 1
        if pull['rarity'] == 5:
            print(f"{since} pulls since 5*, {90-since} until pity")
            break
    else:
        print(f"Never pulled a 5*, {90-since} until pity.")
