# genshin stats api
This project is meant to be a wrapper for the [hoyolab.com](https://www.hoyolab.com/genshin/) gameRecord api.
I have attempted to reverse engineer their API to find out the important tokens and cookies and then to what urls they are sent.
You can pip install with [PyPI](https://pypi.org/project/genshinstats/)

# how to use
Import the `genshin_stats` module and do `set_cookie(...)` to login.
You can either use `set_cookie(account_id=..., cookie_token=...)`.
The cookie is required and will raise an error if missing.
All functions are documented and type hinted.
## examples
Simple examples of usage:
```py
import genshinstats as gs # import module
gs.set_cookie(account_id=8366222, cookie_token="zHbPk8BO3FG4hEOFD2aO6ZlGR1vF75ipuTmFyi2w") # login
user_info = gs.get_user_info(710785423) # get user info with a uid
total_characters = len(user_info['characters']) # get the amount of characters
print('user "sadru" has a total of',total_characters,'characters')
```
> the cookie token in this example is not valid, you must use your own.
```py
stats = gs.get_user_info(uid)['stats']
for field,value in stats.items():
    print(f'{field.replace("_"," ")}: {value}')
```
```py
characters = gs.get_all_characters(uid)
for char in characters:
    print(f"{char['rarity']}* {char['name']:10} Level: {char['level']:2} C{char['constellation']}")
```
```py
spiral_abyss = gs.get_spiral_abyss(uid,previous=True)
stats = spiral_abyss['stats']
for field,value in stats.items():
    print(f'{field.replace("_"," ")}: {value}')
```
## gacha log
You can also get your gacha pull logs.
For this you must first open the history page in genshin impact.
The script will then get all required data by itself.
```py
types = gs.get_gacha_types() # get the types
name = types[3]['name'] # name == "Character Event Wish"
log = gs.get_gacha_log() # get the gacha log
for i in log:
    print(f"{i['type']} {i['name']} {i['rarity']}* ({i['time']})")
```
# how to get your cookie
1. go to [hoyolab.com](https://www.hoyolab.com/genshin/)
2. login to your account
3. open inspect mode (Developer Tools)
4. go to `Application`, `Cookies`, `https://www.hoyolab.com`.
5. copy `account_id` and `cookie_token`
6. use `set_cookie(account_id=..., cookie_token=...)` in your code

# about this project
## contribution
All contributions are welcome as long as it's in a form of a clean PR.
Currently looking for people to reverse engineer the new api version.
## crediting
This project can be freely downloaded and distributed.
Crediting is appreciated.
