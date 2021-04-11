import json

import genshinstats as gs

# getting all data takes a long time
if input('Load Data? [y/n] ') in 'yY':
    with open('gacha_log.json') as file:
        data = json.load(file)
else:
    # print while getting data
    data = {}
    for t in gs.get_gacha_types():
        data[t['name']] = []
        for i in gs.get_gacha_log(t['key']):
            print(f"{i['time']} - {i['name']} ({i['rarity']}* {i['type']})")
            data[t['name']].append(i)

total_pulls = sum(len(i) for i in data.values())
print(f"\ntotal pulls: {total_pulls}")
# iterate from most pulled on to least pulled on banner
for banner,pulls in sorted(data.items(),key=lambda x:len(x[1]),reverse=True):
    banner_pulls = len(pulls)
    pull_percentage = round(banner_pulls / total_pulls * 100, 2)
    
    # iterate over pulls until a 5* is found
    since_5star = None
    for i,pull in enumerate(pulls):
        if pull['rarity'] == 5:
            since_5star = i
            break
    
    print(banner)
    print(f"{banner_pulls} pulls ({pull_percentage}% of all pulls)")
    if since_5star:
        print(f"{since_5star} pulls since 5*, {90-since_5star} until pity")
    else:
        print(f"Never pulled a 5*, {90-banner_pulls} until pity.")
    print()

if input('Save data? [y/n] ') in 'yY':
    with open('gacha_log.json','w') as file:
        json.dump(data,file)
