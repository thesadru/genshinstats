import csv
import genshinstats as gs

with open('export.csv', 'w', newline='', encoding='utf-8') as file:
    fieldnames = ['time', 'name', 'type', 'rarity', 'banner']
    writer = csv.DictWriter(file, fieldnames, extrasaction='ignore')
    writer.writeheader()
    print('preparing data...', end='\r')
    for i, pull in enumerate(gs.get_wish_history()):
        print(f'fetched {i} pulls', end='\r')
        writer.writerow(pull)
