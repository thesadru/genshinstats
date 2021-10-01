# genshinstats
[![Downloads](https://pepy.tech/badge/genshinstats)](https://pepy.tech/project/genshinstats)
[![Downloads/month](https://pepy.tech/badge/genshinstats/month)](https://pepy.tech/project/genshinstats)
[![PyPI package](https://img.shields.io/pypi/v/genshinstats)](https://pypi.org/project/genshinstats/)
[![Last Commit](https://img.shields.io/github/last-commit/thesadru/genshinstats)](https://github.com/thesadru/genshinstats/commits/master)
[![Repo Size](https://img.shields.io/github/repo-size/thesadru/genshinstats)](https://github.com/thesadru/genshinstats/graphs/code-frequency)
[![License](https://img.shields.io/github/license/thesadru/genshinstats)](https://github.com/thesadru/genshinstats/blob/master/LICENSE)
[![Discord](https://img.shields.io/badge/chat-discord-0d86d7)](https://discord.gg/sMkSKRPuCR)

Genshinstats is an unofficial wrapper for the Genshin Impact api. It supports getting user stats, wish history and automatic claiming of daily check-in rewards.

## how to install
using [pip](https://pypi.org/project/genshinstats/)
```
pip install genshinstats
```
### Alternatives:
using pip from git
```
pip install git+https://github.com/thesadru/genshinstats
```
clone and install manually
```
git clone https://github.com/thesadru/genshinstats.git
cd genshinstats
python setup.py install
```

# how to use
You simply need to import the module and use the `set_cookie` function to login. 
Since all mihoyo's apis are private there's no kind of api token or authentication header, instead you are required to use your own account cookies. ([how can I get my cookies?](#how-can-I-get-my-cookies))

The best way to learn is with examples so I have provided a usage example for every function.

You may also use the [documentation](https://thesadru.github.io/pdoc/genshinstats/)

# examples
Simple examples of usage:
```py
import genshinstats as gs
gs.set_cookie(ltuid=119480035, ltoken="cnF7TiZqHAAvYqgCBoSPx5EjwezOh1ZHoqSHf7dT")

uid = 710785423
data = gs.get_user_stats(uid)
total_characters = len(data['characters'])
print('user "sadru" has a total of', total_characters, 'characters')
```
> Cookies should be your own. These are just some example cookies of an account that can be deleted at any time.

> Note that `set_cookie` and `set_cookies` are different functions! The latter should only be used when getting data for other users (for example social media bots)
```py
stats = gs.get_user_stats(uid)['stats']
for field, value in stats.items():
    print(f"{field}: {value}")
# achievements: 210
# active_days: 121
# characters: 19
# ...
```
```py
characters = gs.get_characters(uid)
for char in characters:
    print(f"{char['rarity']}* {char['name']:10} | lvl {char['level']:2} C{char['constellation']}")
# 5* Xiao       | lvl 90 C0
# 4* Beidou     | lvl 80 C1
# 4* Fischl     | lvl 80 C1
# ...
```

```py
spiral_abyss = gs.get_spiral_abyss(uid, previous=True)
stats = spiral_abyss['stats']
for field, value in stats.items():
    print(f"{field}: {value}")
# total_battles: 14
# total_wins: 9
# max_floor: 11-3
# total_stars: 19
```

It's possible to set the cookies with a header
```py
gs.set_cookie("ltoken=cnF7TiZqHAAvYqgCBoSPx5EjwezOh1ZHoqSHf7dT; ltuid=119480035")
```
Or set them automatically by getting them from a browser
```py
gs.set_cookie_auto() # search all browsers
gs.set_cookie_auto('chrome') # search specific browser
```
> requires `cookie-browser3`, can take up to 10s
## submodules
### wishes
Gets your wish history.
For this you must first open the history/details page in genshin impact,
you can find the page in the wish menu on the bottom left.
The script is then able to get your authkey by itself and fetch the data with it.
```py
for i in gs.get_wish_history():
    print(f"{i['time']} - {i['name']} ({i['rarity']}* {i['type']})")
# 2021-03-22 09:50:12 - Razor (4* Character)
# 2021-03-22 09:50:12 - Harbinger of Dawn (3* Weapon)
# 2021-03-22 09:50:12 - Cool Steel (3* Weapon)
# 2021-03-22 09:50:12 - Emerald Orb (3* Weapon)
# ...
```
```py
types = gs.get_banner_types() # get all possible types
print(types)
# {100: 'Novice Wishes',
#  200: 'Permanent Wish',
#  301: 'Character Event Wish',
#  302: 'Weapon Event Wish'}

# get pulls only from a specific banner
for i in gs.get_wish_history(301):
    print(f"{i['time']} - {i['name']} ({i['rarity']}* {i['type']})")
```
```py
banner_ids = gs.get_banner_ids()
for i in banner_ids:
    details = gs.get_banner_details(i) 
    print(f"{details['banner_type_name']} - {details['banner']}")
    print('5 stars:', ', '.join(i['name'] for i in details['r5_up_items']))
    print('4 stars:', ', '.join(i['name'] for i in details['r4_up_items']))
    print()
# Weapon Event Wish - Event Wish "Epitome Invocation"
# 5 stars: Elegy for the End, Skyward Blade
# 4 stars: The Alley Flash, Wine and Song, Favonius Greatsword, Favonius Warbow, Dragon's Bane
```
> `get_banner_ids()` gets a list of all banners whose details page has been opened in the game.
>
> Basically uses the same approach as `get_authkey`

View other's history by passing in an authkey:
```py
authkey = "t5QMiyrenV50CFbqnB4Z+aG4ltprY1JxM5YoaChr9QH0Lp6rK5855xxa1P55..."
gs.get_wish_history(size=20, authkey=authkey)
```
Or by directly setting the authkey:
```py
# directly with the token:
gs.set_authkey("D3ZYe49SUzpDgzrt/l00n2673Zg8N/Yd9OSc7NulRHhp8EhzlEnz2ISBtKBR0fZ/DGs8...")
# get from a url:
gs.set_authkey("https://webstatic-sea.mihoyo.com/ys/event/im-service/index.html?...")
# read from a custom file:
gs.set_authkey('other_output_log.txt')
```
> Since the authkey lasts only a day this is more like for exporting than for actual use.
> 
> When importing from platforms like android you must use the authkey manually. ([how can I get my authkey?](#how-can-I-get-my-authkey))
### daily rewards
Automatically get daily sign in rewards for the currently logged-in user.
```py
reward = gs.claim_daily_reward()
if reward is not None:
    print(f"Claimed daily reward - {reward['cnt']}x {reward['name']}")
else:
    print("Could not claim daily reward")
```
You can also get a list of all rewards you have claimed so far
```py
for i in gs.get_claimed_rewards():
    print(i['cnt'], i['name'])
# 20 Primogem
# 5000 Mora
# 3 Fine Enhancement Ore
# 3 Adventurer's Experience
# 8000 Mora
```
### transaction logs
Logs for artifact, weapon, resin, genesis crystol and primogem "transactions".
You may view a history of everything you have gained in the last 3 months however you may not get the exact amount of any of these so it's generally meant for statistics of gain/loss.
> These functions require the same authkey as wish history.

All of these functions work the same:
```
get_primogem_log
get_resin_log
get_crystal_log
get_artifact_log
get_weapon_log
```

```py
for i in gs.get_primogem_log(size=40):
    print(f"{i['time']} - {i['reason']}: {i['amount']} primogems")
# 2021-08-14 19:43:12 - Achievement reward: 5 primogems
# 2021-08-13 18:32:58 - Daily Commission reward: 20 primogems
# 2021-08-13 18:22:00 - Daily Commission reward: 10 primogems
# 2021-08-13 18:19:05 - Daily Commission reward: 10 primogems
# 2021-08-13 17:48:09 - Shop purchase: -1600 primogems
```
```py
total = 0
for i in gs.get_primogem_log():
    total += i['amount']
    print(f"Since {i['time']} you have gained {total} primogems   ", end='\r')
# Since 2021-01-02 20:35:16 you have gained 5197 primogems
```

Since you the api itself doesn't provide the current amount of resin genshinstats provides a way to calculate it yourself. 
First it requires a reference to how much primogems you had at a specific time and then it calculates how much you should have currently.
```py
from datetime import datetime

# calculating the current amount of resin based on the fact you had 60 resin on the September 28th 2021 12:00 UTC
print(gs.current_resin(datetime(2021, 9, 28, 12, 00), 60))
```
> Since mihoyo can take up to an hour to update their public database of logs this will only work as long as you haven't used any resin in the last hour

> If you do not know how much resin you had at any point you can very roughly approximate it with `gs.approximate_current_resin()`

### hoyolab
Miscalenious stuff for mihoyo's hoyolab. Has searching, auto check-in and code redemption.
```py
# search all users and get their nickname and uid
for user in gs.search('sadru'):
    print(f"{user['nickname']} ({user['uid']}) - \"{user['introduce']}\"")

# check in to hoyolab
gs.hoyolab_check_in()

# get a record card; has user nickname and game uid
card = gs.get_record_card(8366222)
print(f"{card['nickname']} ({card['game_role_id']}) - AR {card['level']}")

# get an in-game uid from a hoyolab uid directly
uid = 8366222
# if it's an actual hoyolab uid
if not gs.is_game_uid(uid): 
    uid = gs.get_uid_from_hoyolab_uid(uid)
```
You can also redeem gift codes mihoyo gives out during events such as livestreams
```py
gs.redeem_code('GENSHINGIFT')
```
> `redeem_code()` requires a special form of authentication: an `account_id` and `cookie_token` cookies.
> You can get these by grabbing cookies from [the official genshin site](https://genshin.mihoyo.com/en/gift) instead of hoyolabs.

### caching
Caching is currently not native to genshinstats however there's a builtin way to install a cache into every function.

This will cache everything install a cache into every* function in genshinstats.
```py
cache = {}
gs.install_cache(cache)
```

The same cache reference is used accross all functions allowing you to see the entire cache and possibly even clear it.
```py
cache = {}
gs.install_cache(cache)

gs.get_characters(710785423)
print(cache.keys())
# dict_keys([('get_user_stats', 710785423), ('get_characters', 710785423, None, 'en-us')])
```

You're highly encouraged to use preexisting cache objects from libraries such as `cachetools` to allow for more functionality
```py
from cachetools import Cache
cache = Cache(100) # only store maximum of 100 objects in the cache
gs.install_cache(cache)
```

However the majority of these approaches have a fatal flaw: if they are not periodically cleared then old data might get stuck in them. It's therefore recommended to keep a ttl cache or automatically clear the cache yourself.
```py
from cachetools import TTLCache
cache = TTLCache(1024, 3600) # max 1024 objects with max livespan of 1 hour
gs.install_cache(cache)
```

> \*Not every function *can* be cached, some are dependent on cookies and some do not cleanly integrate with preexisting caches.

> The `install_cache` function requires a `MutableMapping[Tuple[Any, ...], Any]` and only uses `__geitem__`, `__setitem__` and `__contains__`. You may and are encouraged to create your own cache objects.
> In case you're considering storing your data in json files or similar it's encouraged to hash your keys before storing them as tuples as keys are generally not supported in other formats.

## change language
Some api endpoints support changing languages, you can see them listed here:
```py
get_characters
get_banner_types
get_wish_history
get_gacha_items
get_banner_details
claim_daily_reward
```
You can get a all language codes and their names with `get_langs()`
```py
{'de-de': 'Deutsch',
 'en-us': 'English',
 'es-es': 'Español',
 'fr-fr': 'Français',
 'id-id': 'Indonesia',
 'ja-jp': '日本語',
 'ko-kr': '한국어',
 'pt-pt': 'Português',
 'ru-ru': 'Pусский',
 'th-th': 'ภาษาไทย',
 'vi-vn': 'Tiếng Việt',
 'zh-cn': '简体中文',
 'zh-tw': '繁體中文'}
```
Any of these codes can then be passed as the `lang` parameter
```py
characters = gs.get_characters(710785423, lang='zh-cn')
print(characters)
# {'name': '莫娜',
#  'rarity': 5,
#  'element': 'Hydro',
#  ...
#  'weapon': {'name': '万国诸海图谱',
#             'rarity': 4,
#             'type': '法器',
#             'description': '详尽记载了大陆周边海流气候的海图，是从异国经由商路流落到璃月的奇异典籍。',
#             ...},
#  ...
```

## using genshinstats asynchronously (for example with a discord bot)
You have probably noticed that while you're fetching data with genshinstats or any other sync library for that matter that other async functions never run. 
To solve this issue you must turn the synchronous function into an asynchronous one.

To use any function asynchronously you can use the `asyncio.to_thread(func, *args, **kwargs)` function.
If you're using python 3.8 or less you can use `loop.run_in_executor(None, func, *args)`. Check out the [`asyncio`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor) docs for more info.
```py
import asyncio
import genshinstats as gs

gs.set_cookie_auto()

async def main():
    characters = await asyncio.to_thread(gs.get_characters, 710785423)
    print(characters)

asyncio.run(main())
```

# faq
## How can I get my cookies?
1. go to [hoyolab.com](https://www.hoyolab.com/genshin/)
2. login to your account
3. press `F12` to open inspect mode (aka Developer Tools)
4. go to `Application`, `Cookies`, `https://www.hoyolab.com`.
5. copy `ltuid` and `ltoken`
6. use `set_cookie(ltuid=..., ltoken=...)` in your code
> It is possible that ltuid or ltoken are for some reason not avalible in your cookies (blame it on mihoyo).
> In this case there are probably the old `account_id` and `cookie_token` cookies, so use those with `set_cookie(account_id=..., cookie_token=...)`.
>
> If not even those are avalible go to https://account.mihoyo.com/#/login and use the `login_ticket` cookie in `https://webapi-os.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket?login_ticket=<...>`

### automatic alternative
You can call `get_browser_cookies` to get a dictionary of cookies that are needed for authentication.
```py
import genshinstats as gs
cookies = gs.get_browser_cookies()
print(cookies)
# {'ltuid': '93827185', 'ltoken': 'aH0cEGX458eJjGoC2z0iiDHL7UGMz09ad0a9udwh'}
```
You can then use these cookies in your actual code or save them as enviroment variables
```py
gs.set_cookie(ltuid=93827185, ltoken='aH0cEGX458eJjGoC2z0iiDHL7UGMz09ad0a9udwh')
```
You can also just set the cookies using `set_cookie_auto` which calls `get_browser_cookies` every time you run the script
```py
gs.set_cookie_auto()
```
### setting multiple cookies at once
Mihoyo allows users to get data for only up to 30 other users per day, to circumvent this limitation you can set multiple cookies at once with `set_cookies()`
```py
gs.set_cookies({'ltuid': 1, 'ltoken': 'token...'}, {'ltuid': 2, 'ltoken': 'other token...'})
```
> Creating alt accounts by hand is a lengthy and painful process so you can use one of the countless automated account creators like [genshin account creator](https://github.com/thesadru/genshin-account-creator)

## How can I get my authkey?
To get your authkey manually from other platforms you can use any of these approaches:

- PC
    1. Open Paimon menu [ESC]
    2. Click Feedback
    3. Wait for it to load and a browser page should open
    4. Copy the link
- Android
    1. Open Paimon menu
    2. Click Feedback
    3. Wait for it to load and a feedback page should open
    4. Turn off your Wi-Fi and data connection
    5. Press refresh on top right corner
    6. The page should display an error and show you some text with black font
    7. Hold the text and press select all, then copy that text (don't copy only some  portion of the text)
- IOS
    1. Open Paimon menu
    2. Click Feedback
    3. Wait for it to load and a feedback page should open
    4. Press In-game issue
    5. Press Co-Op Mode
    6. There is a link on the bottom of the reply; press that
    7. A browser should open up
    8. Copy the link
- PS
    1. Open Genshin Impact on your PlayStation
    2. Open the event mail that contains the QR Code
    3. Scan the QR Code with your phone
    4. Copy the link
    > You can only use this if you have an in-game mail with QR Code to open the web event

> this is largerly copied from [paimon.moe](https://paimon.moe/wish)

## Why do I keep getting `DataNotPublic` errors even though I'm trying to view my own account stats and didn't set anything to private?
The `DataNotPublic` is raised when a user has not made their data public, because the account visibility is set to private by default.
To solve this error You must go to [hoyolab.com](https://www.hoyolab.com/genshin/accountCenter/gameRecord) and make your account public by clicking [the toogle next to "public"](https://cdn.discordapp.com/attachments/529573765743509504/817509874417008759/make_account_public.png).

## How do the cookie and authkey work?
Every endpoint in mihoyo's api requires authentication, this is in the form of a cookie and an authkey.
User stats use a cookie and wish history uses an authkey.

The cookie is bound to the user and as far as I know can only be reset by changing your password, so remember to never give your cookie to anyone. For extra safety you may want to create an alt account, so your real account is never in any danger. This token will allow you to view public stats of all users and private stats of yourself.

The authkey is a temporary token to access your wish history. It's unique for every user and is reset after 24 hours. It cannot be used to view the history of anyone else. It is fine to share this key with anyone you want, the only "private" data they will have access to is the wish history.

Tip for developers: the first 682 characters (85 bytes) of the authkey are always the same for each user. You can use this to easily indentify if an authkey belongs to the same user as another authkey.

## How can I claim daily rewards for other users.
When making projects that claim daily rewards for other users you can pass in a `cookie` parameter - `claim_daily_rewards(cookie={'ltuid': ..., 'ltoken': ...})`.
This will avoid having to set global cookies so you can use it with threading.

This cookie parameter is avalible for the majority of other accounts.

## Is it possible that my account can be stolen when I login with the cookie?
I would like to be completely clear in this aspect, I do no have any way to access the cookies you use to login. If you give your cookie to someone it is indeed possible to get into your account but that doesn't yet mean they can do anything with it. The most probable thing a hacker would do is just do a password request, but since version `1.3` they will need to confirm this request with an email. That means they would need to know what your email is and have a way to get into it, which I doubt they can. Since version `1.5` there is also 2FA which will make it completely impossible to steal your account.

They can of course access your data like email, phone number and real name, however those are censored so unless they already have an idea what those could be that data is useless to them. (For example the email may be `thesadru@gmail.com` but it'll only show up as `th****ru@gmail.com`)

TL;DR unless you have also given your password away your account cannnot be stolen.

## How do I get the wish history of other players?
To get the wish history of other players you must get their authkey and pass it as a keyword into `get_wish_history`. That will make the function return their wish history instead of yours, it will also avoid the error when you try to run your project on a machine that doesn't have genshin installed.

To get the autkey you ask the player to press `ESC` while in the game and click the feedback button on the bottom left, then get them to send the url they get redirected to. You can then extract the authkey with `extract_authkey(url)` which you can then pass into the functions.

## Why doesn't `get_wish_history()` return a normal list?
When you do `print(gs.get_wish_history())` you get  an output that looks something like `<generator object get_wish_history at 0x000001DA6A128580>`

This is because the wish history is split into pages which must be requested one at a time, that means trying to return all the pulls at once would take way too long. The wokaround around this is to use a "generator" - a special list that generates values on the fly.

If you absolutely need a list you can just explicitely cast the generator to a list with `list(get_wish_history())` however that might take a few seconds fetch.

## How does `set_cookie_auto()` work? Can my data be stolen with it?
`set_cookie_auto()` searches your browsers for possible cookies used to login into your genshin accounts and then uses those, so there's no need to use `set_cookies()`.
When getting said cookies, they are filtered so only ones for mihoyo are ever pulled out. They will only ever be used as authentication and will never be sent anywhere else.

## What's the ratelimit?
You may only fetch data for 30 users per day per cookie.
That means that when making projects that fetches data for other users it's recommended to use multiple cookies.
You can set a bunch of cookies at once with `set_cookies(cookie1, cookie2, ...)`.

## How can I get an in-game uid from a hoyolab uid?
`get_uid_from_hoyolab(hoyolab_uid)` can do that for you. It will return None if the user's data is private. To check whether a given uid is a game or a hoyolab one use `is_game_uid(uid)`.

## How can I get a user's username?
Getting the user's username and adventure rank is possible only with their hoyolab uid. You can get them with `get_record_card(hoyolab_uid)` along with a bunch of other data.

## How do I get one type of uid from another?
- uids of currently logged in user: `gs.get_game_accounts()`
- from hoyolab uid to game uid: `gs.get_uid_from_hoyolab(hoyolab_uid)`
- from authkey to uid: `gs.get_uid_from_authkey(authkey)`
- from uid to hoyolab uid: `currently impossible`

# project layout
```
caching.py          caching utilities
daily.py            automatic daily reward claiming
errors.py           errors used by genshinstats
genshinstats.py     user stats and characters
hoyolab.py          user hoyolab community info
map.py              genshin webstatic map
pretty.py           formatting of api responses
transactions.py     transaction logs
utils.py            various utility functions
wishes.py           wish history
```

# CHANGELOG
## 1.4.10
- Added an `equipment` kwarg to `get_user_stats`
- Added support for activities
## 1.4.9.4
- Made Ei and Sara have correct names in the abyss
## 1.4.9.3
- Teapot now prettifies data properly
- Aloy no longer has 105 stars
## 1.4.9.2
- Made sure that None returns do not get cached
## 1.4.9.1
- Minor mypy fixes
## 1.4.9
- Added support for the genshin map
- Made `daily_reward_info` return a namedtuple
## 1.4.8
- Fixed support for chinese accounts
## 1.4.7
- Added `install_cache` for installing a cache into the entire library
## 1.4.6.1
- Added an error for when you don't have a hoyolab account created
## 1.4.6
- Added several new log related endpoints
    - get_primogem_log, get_resin_log, get_crystal_log
    - get_artifact_log, get_weapon_log
- Made tests cleaner (now requires pytest)
- Added an explanation how to get your authkey on other platforms
## 1.4.5.1
- Made yanfei have the correct name in spiral abyss
## 1.4.5
- Added support for the serenita teapot
    - This is not yet an official endpoint, therefore there's a large number of bugs. For example the comfort level is shared across all styles.
- Made `get_game_accounts` be prettified
    - This will most likely break a lot of scripts, I'm sorry in advance.
- Added a `retry` decorator
## 1.4.4.4
- Added support for electroculi and outfits
- Annotated all unsubscripted lists in the library as `List[Dict[str, Any]]`
## 1.4.4.3
- Added electro traveler's element to the character prettifier
- Annotated all unsubscripted dicts in the library as `Dict[str, Any]`
- Fixed bug where getting banner types with different authkeys would not get the cached result
## 1.4.4.2
- Added a custom error message for set_cookie_auto
## 1.4.4.1
- Added `validate_authkey`
- Made `claim_daily_reward` no longer require a uid.
- Renamed `GachaLogException` to `AuthkeyError`
- Removed `genshinstats.asyncify()` in favor of `asyncio.to_thread()`
## 1.4.4
- Added a cookie parameter to all functions that use cookies
- Added `set_visibility`
- Made `claim_daily_reward` send an email in the correct language
- Improved `setup.py`
- Updated to the new wish history domain
## 1.4.3
- Added a cookie parameter to `claim_daily_reward`
## 1.4.2
- Made several improvements to the claiming of daily rewards
## 1.4.1
- Added `get_recommended_users`
- Added `get_hot_posts`
## 1.4
- Renamed majority of functions
    - `get_user_data` -> `get_user_stats`
    - `get_gacha_history` -> `get_wish_history`
        - the before ambigious `gacha` was renamed to `wish` or `bannner`
    - `sign_in` -> `claim_daily_reward`
    - ...
- Removed `get_all_*` style functions - functions are overloaded to get all by default
- Made it possible to use multiple cookies to overcome ratelimits
    - `set_cookie` keeps its behaviour but is now overloaded to work with headers
    - `set_cookies` sets multiple cookies which will be silently rotated as needed
- Removed the need for short lang codes, they are now parsed internally
- `get_langs` and `get_banner_types` now return a dict instead of a list of dicts
- Gift codes can now be redeemed for all game accounts instead of just a single one.
- Added `__all__` to not spam the namespace with unexpected variables
- Reduced the amount of errors