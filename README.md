# genshin stats api
This project is meant to be a wrapper for the [hoyolab.com](https://www.hoyolab.com/genshin/) gameRecord api.
I have attempted to reverse engineer their API to find out the important tokens and cookies and then to what urls they are sent.
You can pip install with [PyPI](https://pypi.org/project/genshinstats/)

# how to use
Import the `genshin_stats` module and do `set_cookie(...)` to login.
You can either use `set_cookie(account_id=..., cookie_token=...)`.
The cookie is required and will raise an error if missing.
All functions are documented and type hinted.
## example
Simple example of usage:
```py
import genshinstats as gs # import module
gs.set_cookie(account_id=8366222, cookie_token="zHbPk8BO3FG4hEOFD2aO6ZlGR1vF75ipuTmFyi2w") # login
result = gs.search('sadru') # search a community user
uid = gs.get_uid_from_community(result['users'][1]['uid']) # get the uid fro the results
user_info = gs.get_user_info(uid) # get user info with the uid
total_characters = len(user_info['avatars']) # get the list of characters, called avatars in the basic API
print('user "sadru" has a total of',total_characters,'characters')
```
> the cookie token in this example is not valid, you must use your own.
## prettifiers
There are prettifier functions that turn data into a pretty version.
This is to rename some fields that don't make sense, like fetters.
These are highly recommended.
```py
characters = gs.prettify_characters(gs.get_all_characters(uid))
for char in characters:
    print(f"{char['rarity']}* {char['name']:10} Level: {char['level']} C{char['constellation']}")
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
## crediting
This project can be freely downloaded and distributed.
Crediting is appreciated.
