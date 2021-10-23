"""Calculates your pity for each banner"""
import genshinstats as gs

banners = gs.get_banner_types()
for banner_type, banner_name in banners.items():
    print("\n" + banner_name)
    since = 0
    for pull in gs.get_wish_history(banner_type):
        since += 1
        if pull["rarity"] == 5:
            print(f"{since} pulls since 5*, {90-since} until pity")
            break
    else:
        print(f"Pulled a 5* a long time ago or never, less than {90-since} until pity")
