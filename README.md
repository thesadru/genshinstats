# genshinstats
This project is meant to be a wrapper for the Genshin Impact's [hoyolab.com](https://www.hoyolab.com/genshin/) api.
The api endpoints used in this project are not publicly known but are free to use for 3rd part tools, so I have decided to get these a bit more publicity by making a wrapper for them.

You can pip install with [PyPI](https://pypi.org/project/genshinstats/)

# how to use
Import the `genshinstats` module and set the cookie to login.
To set the cookie use `set_cookie(account_id=..., cookie_token=...)`.
Pass your own cookie values in this fields. ([How to get your cookie](#how-to-get-your-cookie))
The cookie is required and will raise an error if missing.

All functions are documented and type hinted.
# examples
Simple examples of usage:
```py
import genshinstats as gs # import module
gs.set_cookie(account_id=119480035, cookie_token="hEIIh08ghAIlHY1QQZBnsngVWXzaEMQtrSV0Bowu") # login

uid = 710785423
user_info = gs.get_user_info(uid) # get user info with a uid
total_characters = len(user_info['characters']) # get the amount of characters
print('user "sadru" has a total of',total_characters,'characters')
```
> Cookies should be your own. These are just some example cookies of an account that can be deleted at any time.
```py
stats = gs.get_user_info(uid)['stats']
for field,value in stats.items():
    print(f"{field.replace('_',' ')}: {value}")
```
```py
characters = gs.get_all_characters(uid)
for char in characters:
    print(f"{char['rarity']}* {char['name']:10} | lvl {char['level']:2} C{char['constellation']}")
```
```py
spiral_abyss = gs.get_spiral_abyss(uid,previous=True)
stats = spiral_abyss['stats']
for field,value in stats.items():
    print(f"{field.replace('_',' ')}: {value}")
```
```py
with open('users.txt','w',encoding='utf-8',errors='ignore') as file:
    for player in gs.get_public_players():
        print(player['uid'])
        file.write(f"{player['uid']},{player['community_uid']}\n")
```
## submodules
### gachalog
Gets your gacha pull logs.
For this you must first open the history/details page in genshin impact,
the script will then get all required data by itself.
```py
types = gs.get_gacha_types() # get all possible types
name = types[2]['name'] # name == "Character Event Wish"
log = gs.get_gacha_log(name) # get the gacha log
for i in log:
    print(f"{i['time']} - {i['name']} ({i['rarity']}* {i['type']})")
```
```py
ids = gs.get_all_gacha_ids() # get all possible gacha ids (only counts opened details pages)
for i in ids:
    details = gs.get_gacha_details(i) # 
    print(f"{details['gacha_type']} - {details['banner']}")
    print('5 stars:', ', '.join(i['name'] for i in details['r5_up_items']))
    print('4 stars:', ', '.join(i['name'] for i in details['r4_up_items']))
    print()
```
View other's history by setting an authkey yourself:
```py
# directly with the token:
gs.set_authkey("D3ZYe49SUzpDgzrt/l00n2673Zg8N/Yd9OSc7NulRHhp8EhzlEnz2ISBtKBR0fZ/DGs8...")
# read from a custom file:
gs.set_authkey(logfile='other_output_log.txt')
```
> Since the authkey lasts only a day this is more like for exporting than for actual use.

## change language
Some api endpoints support changing languages, you can see them listed here:
```py
genshinstats.get_all_characters(...,lang='fr-fr')

gachalog.get_gacha_log(...,lang='fr')
gachalog.get_gacha_types(lang='fr')
gachalog.get_gacha_details(...,lang='fr-fr')
gachalog.recognize_gacha_type(lang='fr')
```

# how to get your cookie
1. go to [hoyolab.com](https://www.hoyolab.com/genshin/)
2. login to your account
3. open inspect mode (Developer Tools)
4. go to `Application`, `Cookies`, `https://www.hoyolab.com`.
5. copy `account_id` and `cookie_token`
6. use `set_cookie(account_id=..., cookie_token=...)` in your code

# errors
genshinstats uses its own errors defined in `genshinstats.errors`. 

The most common one you'll probably see is `DataNotPublic`.
To solve this error You must go to [hoyolab.com](https://www.hoyolab.com/genshin/accountCenter/gameRecord) and make your account public.
([how to make your account public](https://cdn.discordapp.com/attachments/529573765743509504/817509874417008759/make_account_public.png))

# about this project
## contribution
All contributions are welcome as long as it's in a form of a clean PR.
Currently looking for people to help me get the ds salt of the new api version.
## crediting
This project can be freely downloaded and distributed.
Crediting is appreciated.
