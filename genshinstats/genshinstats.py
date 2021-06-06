"""Wrapper for the hoyolab.com gameRecord api.

Can fetch data for a user's stats like stats, characters, spiral abyss runs...
"""
import hashlib
import random
import string
import time
from http.cookies import SimpleCookie
from typing import Any, Dict, List, Mapping, Optional, Union
from urllib.parse import urljoin

from requests import Session

from .errors import NotLoggedIn, TooManyRequests, raise_for_error
from .pretty import *
from .utils import USER_AGENT, is_chinese, recognize_server

__all__ = [
    'set_cookie', 'set_cookies', 'get_browser_cookies', 'set_cookies_auto', 'set_cookie_auto', 'get_ds_token', 
    'fetch_endpoint', 'get_user_stats', 'get_characters', 'get_spiral_abyss', 'get_all_user_data'
]

session = Session()
session.headers.update({
    # required headers
    "x-rpc-app_version": "1.5.0",  # overseas api uses 1.x.x, chinese api uses 2.x.x
    "x-rpc-client_type": "4",
    "x-rpc-language": "en-us",
    # authentications headers
    "ds": "",
    # recommended headers
    "user-agent": USER_AGENT
})
cookies: List[SimpleCookie] = []

DS_SALT = "6cqshh5dhw73bzxn20oexa9k516chk7s"
OS_BBS_URL = "https://bbs-api-os.hoyolab.com/"  # overseas
CN_TAKUMI_URL = "https://api-takumi.mihoyo.com/"  # chinese

CookieLike = Union[SimpleCookie, Mapping[str, Any], str] # type-hint only
def _add_cookie(cookie: CookieLike, clear: bool = False) -> Optional[SimpleCookie]:
    """Adds a cookie, makes sure there are no copies"""
    if isinstance(cookie, Mapping) and not isinstance(cookie, SimpleCookie):
        cookie = {k: str(v) for k, v in cookie.items()}
    cookie = SimpleCookie(cookie)
    
    if 'ltuid' in cookie:
        key = 'ltuid'
    elif 'account_id' in cookie:
        key = 'account_id'
    else:
        raise ValueError(f'Invalid cookie: {cookie!r} - has no ltuid or account_id')
    
    if clear:
        cookies.clear()
    elif cookie[key] in (i[key] for i in cookies):
        return None
    
    cookies.append(cookie)
    return cookie

def set_cookie(cookie: CookieLike = None, **kwargs: Any) -> None:
    """Logs-in using a cookie.
    
    Usage:
    >>> set_cookie(ltuid=..., ltoken=...)
    >>> set_cookie(account_id=..., cookie_token=...)
    >>> set_cookie({'ltuid': ..., 'ltoken': ...})
    >>> set_cookie("ltuid=..., ltoken=...")
    """
    if bool(cookie) == bool(kwargs):
        raise ValueError("Cannot use both positional and keyword arguments at once")
    
    _add_cookie(cookie or kwargs, clear=True)

def set_cookies(*cookies: CookieLike) -> None:
    """Sets multiple cookies at once to cycle between. Takes same arguments as set_cookie.
    
    Unlike set_cookie, this function allows for multiple cookies to be used at once.
    This is so far the only way to circumvent the rate limit.
    """
    for cookie in cookies:
        _add_cookie(cookie)

def get_browser_cookies(browser: str = None) -> Dict[str, str]:
    """Gets cookies from your browser for later storing.
    
    If a specifc browser is set, gets data from that browser only.
    Avalible browsers: chrome, chromium, opera, edge, firefox
    """
    import browser_cookie3
    load = getattr(browser_cookie3, browser.lower()) if browser else browser_cookie3.load
    # For backwards compatibility we also get account_id and cookie_token
    # however we can't just get every cookie because there's sensitive information
    allowed_cookies = {'ltuid', 'ltoken', 'account_id', 'cookie_token'}
    return {
        c.name: c.value 
        for domain in ('mihoyo', 'hoyolab') 
        for c in load(domain_name=domain) 
        if c.name in allowed_cookies and c.value is not None
    }

def set_cookie_auto(browser: str = None) -> None:
    """Like set_cookie, but gets the cookies by itself from your browser.
    
    Requires the module browser-cookie3
    Be aware that this process can take up to 10 seconds.
    To speed it up you may select a browser.
    
    If a specifc browser is set, gets data from that browser only.
    Avalible browsers: chrome, chromium, opera, edge, firefox
    """
    _add_cookie(get_browser_cookies(browser), clear=True)
set_cookies_auto = set_cookie_auto # alias

def get_ds_token(salt: str = DS_SALT) -> str:
    """Creates a new ds token for authentication."""
    t = int(time.time())  # current seconds
    r = ''.join(random.choices(string.ascii_letters, k=6))  # 6 random chars
    h = hashlib.md5(f"salt={salt}&t={t}&r={r}".encode()).hexdigest()  # hash and get hex
    return f'{t},{r},{h}'

def _fetch_endpoint(method: str, url: str, **kwargs) -> dict:
    """Fetches an endpoint without any extra stuff"""
    r = session.request(method, url, **kwargs)
    r.raise_for_status()
    
    data = r.json()
    if data['retcode'] == 0:
        return data['data']
    
    raise_for_error(data)

def fetch_endpoint(endpoint: str, chinese: bool = False, **kwargs) -> Dict[str, Any]:
    """Fetch an enpoint from the API.

    Takes in an endpoint url which is joined with the base url.
    A request is then sent and returns a parsed response.
    Includes error handling and ds token renewal.
    
    Can specifically use the chinese base url and request data for chinese users, 
    but that requires being logged in as that user.
    """
    session.headers['ds'] = get_ds_token()
    method = kwargs.pop('method', 'get')
    url = urljoin(CN_TAKUMI_URL if chinese else OS_BBS_URL, endpoint)
    
    # go through every single avalible cookie to avoid ratelimits
    for cookie in cookies.copy():
        
        cookie = {k: v.value for k,v in cookie.items()}
        try:
            return _fetch_endpoint(method, url, cookies=cookie, **kwargs)
        except TooManyRequests:
            cookies.append(cookies.pop(0)) # move the ratelimited cookie to the end
    else:
        # more readable errors
        if len(cookies) == 0:
            raise NotLoggedIn('Login cookies have not been provided')
        if len(cookies) == 1:
            raise TooManyRequests("Cannnot get data for more than 30 accounts per day.")
        else:
            raise TooManyRequests("All cookies have hit their request limit of 30 accounts per day.")

def get_user_stats(uid: int) -> dict:
    """Gets basic user information and stats."""
    server = recognize_server(uid)
    data = fetch_endpoint(
        "game_record/genshin/api/index",
        chinese=is_chinese(uid),
        params=dict(server=server, role_id=uid)
    )
    return prettify_user_stats(data)

def get_characters(uid: int, character_ids: List[int] = None, lang: str = 'en-us') -> list:
    """Gets characters of a user.
    
    Characters contain info about their level, constellation, weapon, and artifacts.
    Talents are not included.
    
    If character_ids are provided then only characters with those ids are returned.
    """
    if character_ids is None:
        character_ids = [i['id'] for i in get_user_stats(uid)['characters']]
    
    server = recognize_server(uid)
    data = fetch_endpoint(
        "game_record/genshin/api/character",
        chinese=is_chinese(uid),
        method='POST',
        json=dict(character_ids=character_ids, role_id=uid, server=server),  # POST uses the body instead
        headers={'x-rpc-language': lang},
    )["avatars"]
    return prettify_characters(data)

def get_spiral_abyss(uid: int, previous: bool = False) -> dict:
    """Gets spiral abyss runs of a user and details about them.
    
    Every season these stats refresh and you can get the previous stats with `previous`.
    """
    server = recognize_server(uid)
    schedule_type = 2 if previous else 1
    data = fetch_endpoint(
        "game_record/genshin/api/spiralAbyss",
        chinese=is_chinese(uid),
        params=dict(server=server, role_id=uid, schedule_type=schedule_type)
    )
    return prettify_spiral_abyss(data)

def get_all_user_data(uid: int, lang: str = 'en-us') -> dict:
    """Fetches all data a user can has. Very slow.
    
    A helper function that gets all avalible data for a user and returns it as one dict.
    However that makes it fairly slow so it's not recommended to use it outside caching.
    """
    data = get_user_stats(uid)
    data['characters'] = get_characters(uid, [i['id'] for i in data['characters']], lang=lang)
    data['spiral_abyss'] = [get_spiral_abyss(uid), get_spiral_abyss(uid, previous=True)]
    return data
