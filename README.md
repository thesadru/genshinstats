# genshin stats api
This project is meant to be a wrapper for the [hoyolab.com](https://www.hoyolab.com/genshin/) gameRecord api.
I have attempted to reverse engineer their API to find out the important tokens and cookies and then to what urls they are sent.
You can pip install with [PyPI](https://pypi.org/project/genshinstats-api/)

# how to use
Import the `genshin_stats` module and do `config(...)` to login.
You can either use `set_cookie(account_id=..., cookie_token=...)` or `set_cookie(cookie=...)`.
The cookie is required and will raise an error if missing.
All functions are documented and type hinted.

# how to get your cookie
1. go to [hoyolab.com](https://www.hoyolab.com/genshin/)
2. login to your account
3. open inspect mode (Developer Tools)
4. go to `Application`, `Cookies`, `https://www.hoyolab.com`.
5. copy `account_id` and `cookie_token`
6. use `set_cookie(account_id=..., cookie_token=...)` in your code

# contribution
All contributions are welcome as long as it's in a form of a clean PR.
Currently I'm trying to find a way to allow easier cookie fetching rather than manually. 
