"""Wrapper for the hoyolab.com gameRecord api.

Can fetch data for a user's stats like stats, characters, spiral abyss runs...
"""
import hashlib
import random
import string
import time
from http.cookies import SimpleCookie
from typing import Any, Dict, List, Mapping, MutableMapping, Union
from urllib.parse import urljoin

import requests
from requests.sessions import RequestsCookieJar, Session

from .errors import NotLoggedIn, TooManyRequests, raise_for_error
from .pretty import prettify_abyss, prettify_characters, prettify_stats, prettify_activities
from .utils import USER_AGENT, is_chinese, recognize_server, retry

__all__ = [
    "set_cookie",
    "set_cookies",
    "get_browser_cookies",
    "set_cookies_auto",
    "set_cookie_auto",
    "fetch_endpoint",
    "get_user_stats",
    "get_characters",
    "get_spiral_abyss",
    "get_activities",
    "get_all_user_data",
]

session = Session()
session.headers.update({
    # required headers
    "x-rpc-app_version": "", 
    "x-rpc-client_type": "",
    "x-rpc-language": "en-us",
    # authentications headers
    "ds": "",
    # recommended headers
    "user-agent": USER_AGENT
})

cookies: List[RequestsCookieJar] = [] # a list of all avalible cookies

OS_DS_SALT = "6cqshh5dhw73bzxn20oexa9k516chk7s"
CN_DS_SALT = "14bmu1mz0yuljprsfgpvjh3ju2ni468r"
OS_BBS_URL = "https://bbs-api-os.hoyolab.com/"  # overseas
CN_TAKUMI_URL = "https://api-takumi.mihoyo.com/"  # chinese

def set_cookie(cookie: Union[Mapping[str, Any], str] = None, **kwargs: Any) -> None:
    """Logs-in using a cookie.

    Usage:
    >>> set_cookie(ltuid=..., ltoken=...)
    >>> set_cookie(account_id=..., cookie_token=...)
    >>> set_cookie({'ltuid': ..., 'ltoken': ...})
    >>> set_cookie("ltuid=...; ltoken=...")
    """
    if bool(cookie) == bool(kwargs):
        raise ValueError("Cannot use both positional and keyword arguments at once")

    set_cookies(cookie or kwargs)

def set_cookies(*args: Union[Mapping[str, Any], str], clear: bool = True) -> None:
    """Sets multiple cookies at once to cycle between. Takes same arguments as set_cookie.

    Unlike set_cookie, this function allows for multiple cookies to be used at once.
    This is so far the only way to circumvent the rate limit.

    If clear is set to False the previously set cookies won't be cleared.
    """
    if clear:
        cookies.clear()

    for cookie in args:
        if isinstance(cookie, Mapping):
            cookie = {k: str(v) for k, v in cookie.items()} # SimpleCookie needs a string
        cookie = SimpleCookie(cookie)

        jar = RequestsCookieJar()
        jar.update(cookie)
        cookies.append(jar)

def get_browser_cookies(browser: str = None) -> Dict[str, str]:
    """Gets cookies from your browser for later storing.

    If a specific browser is set, gets data from that browser only.
    Avalible browsers: chrome, chromium, opera, edge, firefox
    """
    try:
        import browser_cookie3  # optional library
    except ImportError:
        raise ImportError("functions 'set_cookie_auto' and 'get_browser_cookie` require \"browser-cookie3\". "
                          "To use these function please install the dependency with \"pip install browser-cookie3\".")
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

    If a specific browser is set, gets data from that browser only.
    Avalible browsers: chrome, chromium, opera, edge, firefox
    """
    set_cookies(get_browser_cookies(browser), clear=True)
set_cookies_auto = set_cookie_auto # alias


def generate_ds_token(salt: str) -> str:
    """Creates a new ds token for authentication."""
    t = int(time.time())  # current seconds
    r = ''.join(random.choices(string.ascii_letters, k=6))  # 6 random chars
    h = hashlib.md5(f"salt={salt}&t={t}&r={r}".encode()).hexdigest()  # hash and get hex
    return f'{t},{r},{h}'

# sometimes a random connection error can just occur, mihoyo being mihoyo
@retry(3, requests.ConnectionError)
def _request(*args: Any, **kwargs: Any) -> Any:
    """Fancy requests.request"""
    r = session.request(*args, **kwargs)
    
    r.raise_for_status()
    kwargs['cookies'].update(session.cookies)
    session.cookies.clear()
    data = r.json()
    if data['retcode'] == 0:
        return data['data']
    raise_for_error(data)

def fetch_endpoint(endpoint: str, chinese: bool = False, cookie: Mapping[str, Any] = None, **kwargs) -> Dict[str, Any]:
    """Fetch an enpoint from the API.

    Takes in an endpoint url which is joined with the base url.
    A request is then sent and returns a parsed response.
    Includes error handling and ds token renewal.

    Can specifically use the chinese base url and request data for chinese users,
    but that requires being logged in as that user.

    Supports handling ratelimits if multiple cookies are set with `set_cookies`
    """
    # parse the arguments for requests.request
    kwargs.setdefault('headers', {})
    method = kwargs.pop('method', 'get')
    if chinese:
        kwargs['headers'].update({
            "ds": generate_ds_token(CN_DS_SALT),
            "x-rpc-app_version": "2.7.0",
            "x-rpc-client_type": "5",
        })
        url = urljoin(CN_TAKUMI_URL, endpoint)
    else:
        kwargs['headers'].update({
            "ds": generate_ds_token(OS_DS_SALT),
            "x-rpc-app_version": "1.5.0", 
            "x-rpc-client_type": "4",
        })
        url = urljoin(OS_BBS_URL, endpoint)

    if cookie is not None:
        if not isinstance(cookie, MutableMapping) or not all(isinstance(v, str) for v in cookie.values()):
            cookie = {k: str(v) for k, v in cookie.items()}
        return _request(method, url, cookies=cookie, **kwargs)
    elif len(cookies) == 0:
        raise NotLoggedIn('Login cookies have not been provided')

    for cookie in cookies.copy():
        try:
            return _request(method, url, cookies=cookie, **kwargs)
        except TooManyRequests:
            # move the ratelimited cookie to the end to let the ratelimit wear off
            cookies.append(cookies.pop(0))

    # if we're here it means we used up all our cookies so we must handle that
    if len(cookies) == 1:
        raise TooManyRequests("Cannnot get data for more than 30 accounts per day.")
    else:
        raise TooManyRequests("All cookies have hit their request limit of 30 accounts per day.")

def get_user_stats(uid: int, equipment: bool = False, lang: str = 'en-us', cookie: Mapping[str, Any] = None) -> Dict[str, Any]:
    """Gets basic user information and stats.
    
    If equipment is True an additional request will be made to get the character equipment
    """
    server = recognize_server(uid)
    data = fetch_endpoint(
        "game_record/genshin/api/index",
        chinese=is_chinese(uid),
        cookie=cookie,
        params=dict(server=server, role_id=uid),
        headers={'x-rpc-language': lang},
    )
    data = prettify_stats(data)
    if equipment:
        data['characters'] = get_characters(uid, [i['id'] for i in data['characters']], lang, cookie)
    return data

def get_characters(uid: int, character_ids: List[int] = None, lang: str = 'en-us', cookie: Mapping[str, Any] = None) -> List[Dict[str, Any]]:
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
        cookie=cookie,
        method='POST',
        json=dict(character_ids=character_ids, role_id=uid, server=server),  # POST uses the body instead
        headers={'x-rpc-language': lang},
    )["avatars"]
    return prettify_characters(data)

def get_spiral_abyss(uid: int, previous: bool = False, cookie: Mapping[str, Any] = None) -> Dict[str, Any]:
    """Gets spiral abyss runs of a user and details about them.

    Every season these stats refresh and you can get the previous stats with `previous`.
    """
    server = recognize_server(uid)
    schedule_type = 2 if previous else 1
    data = fetch_endpoint(
        "game_record/genshin/api/spiralAbyss",
        chinese=is_chinese(uid),
        cookie=cookie,
        params=dict(server=server, role_id=uid, schedule_type=schedule_type)
    )
    return prettify_abyss(data)

def get_activities(uid: int, lang: str = 'en-us', cookie: Mapping[str, Any] = None) -> Dict[str, Any]:
    """Gets the activities of the user
    
    As of this time only Hyakunin Ikki is availible.
    """
    server = recognize_server(uid)
    data = fetch_endpoint(
        "game_record/genshin/api/activities",
        chinese=is_chinese(uid),
        cookie=cookie,
        params=dict(server=server, role_id=uid),
        headers={'x-rpc-language': lang},
    )
    return prettify_activities(data)

def get_all_user_data(uid: int, lang: str = 'en-us', cookie: Mapping[str, Any] = None) -> Dict[str, Any]:
    """Fetches all data a user can has. Very slow.

    A helper function that gets all avalible data for a user and returns it as one dict.
    However that makes it fairly slow so it's not recommended to use it outside caching.
    """
    data = get_user_stats(uid, equipment=True, lang=lang, cookie=cookie)
    data['spiral_abyss'] = [get_spiral_abyss(uid, previous, cookie) for previous in [False, True]]
    return data
