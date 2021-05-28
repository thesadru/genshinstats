"""Wrapper for the hoyolab.com gameRecord api.

Can fetch data for a user's stats like stats, characters, spiral abyss runs...
"""
import hashlib
import logging
import random
import string
import time
from http.cookies import SimpleCookie
from typing import Any, Dict, List, overload
from urllib.parse import urljoin

from requests import Session

from .errors import raise_for_error
from .pretty import *
from .utils import USER_AGENT, is_chinese, recognize_server

__all__ = [
    'session', 'set_cookies', 'set_cookie_header', 'get_browser_cookies', 'set_cookies_auto',
    'get_ds_token', 'fetch_endpoint', 'get_user_stats', 'get_characters', 'get_spiral_abyss'
]

logger = logging.getLogger('genshinstats')
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
DS_SALT = "6cqshh5dhw73bzxn20oexa9k516chk7s"
OS_BBS_URL = "https://bbs-api-os.hoyolab.com/"  # overseas
CN_TAKUMI_URL = "https://api-takumi.mihoyo.com/"  # chinese

# typing overloads for set_cookie (check PEP 484 for more info)
@overload
def set_cookies(*, ltuid: int, ltoken: str): ...
@overload
def set_cookies(*, account_id: int, cookie_token: str): ...
@overload
def set_cookies(**kwargs: Any): ...

def set_cookies(**kwargs) -> None:
    """Logs-in using a cookie, this function must be run at least once
    
    The provided cookies can either be ltuid and ltoken or account_id and cookie_token.
    Combination of both is also allowed.
    """
    kwargs = {k: str(v) for k, v in kwargs.items()}
    session.cookies.update(kwargs)

def set_cookie_header(header: str) -> None:
    """Like set_cookie, but you can set the cookie with a header instead."""
    session.cookies.update(SimpleCookie(header))

# possible alternatives for get_browser_cookies
def get_browser_cookies_alt(browser: str = None) -> Dict[str, str]:
    import browser_cookie3
    load = getattr(browser_cookie3, browser.lower()) if browser else browser_cookie3.load
    
    cookies = {}
    for domain in ('mihoyo', 'hoyolab'):
        for c in load(domain_name=domain):
            if c.name in ('ltuid', 'ltoken', 'account_id', 'cookie_token'):
                cookies[c.name] = str(c.value)
    return cookies

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
    cookies = {}
    for domain in ('mihoyo', 'hoyolab'):
        c = {c.name: str(c.value) for c in load(domain_name=domain) if c.name in allowed_cookies}
        cookies.update(c)
    return cookies

def set_cookies_auto(browser: str = None) -> None:
    """Like set_cookie, but gets the cookies by itself from your browser.
    
    Requires the module browser-cookie3
    Be aware that this process can take up to 10 seconds.
    To speed it up you may select a browser.
    
    If a specifc browser is set, gets data from that browser only.
    Avalible browsers: chrome, chromium, opera, edge, firefox
    """
    logger.debug(f'Loading cookies automatically.')
    session.cookies.update(get_browser_cookies(browser))

def get_ds_token(salt: str) -> str:
    """Creates a new ds token for authentication."""
    t = int(time.time())  # current seconds
    r = ''.join(random.choices(string.ascii_letters, k=6))  # 6 random chars
    h = hashlib.md5(f"salt={salt}&t={t}&r={r}".encode()).hexdigest()  # hash and get hex
    return f'{t},{r},{h}'

def fetch_endpoint(endpoint: str, chinese: bool = False, **kwargs) -> Dict[str, Any]:
    """Fetch an enpoint from the API.

    Takes in an endpoint url which is joined with the base url.
    A request is then sent and returns a parsed response.
    Includes error handling and ds token renewal.
    
    Can specifically use the chinese base url and request data for chinese users, 
    but that requires being logged in as that user.
    """
    session.headers['ds'] = get_ds_token(DS_SALT)
    method = kwargs.pop('method', 'get')
    url = urljoin(CN_TAKUMI_URL if chinese else OS_BBS_URL, endpoint)
    
    logger.debug(f'Fetching endpoint "{url}"')
    r = session.request(method, url, **kwargs)
    r.raise_for_status()
    
    data = r.json()
    if data['retcode'] == 0:
        return data['data']
    
    raise_for_error(data)

def get_user_stats(uid: int) -> dict:
    """Gets stats of a user.
    
    Stats contain the main information regarding a user, 
    that includes stats, characters and explorations.
    """
    server = recognize_server(uid)
    data = fetch_endpoint(
        "game_record/genshin/api/index",
        chinese=is_chinese(uid),
        params=dict(server=server, role_id=uid)
    )
    return prettify_stats(data)

def get_characters(uid: int, character_ids: List[int] = None, lang: str = 'en-us') -> list:
    """Gets characters of a user.
    
    Characters contain info about their level, constellation, weapon, and artifacts.
    Talents are not included.
    
    If character_ids are provided gets only characters with those ids.
    
    Change the language with lang, 
    possible langs can be found with get_langs() under the value field.
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
    """Gets how far the user has gotten in spiral abyss and their season progress.
    
    Spiral abyss info contains their progress, stats and individual completes.
    
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
