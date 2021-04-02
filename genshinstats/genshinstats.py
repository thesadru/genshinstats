"""Wrapper for the hoyolab.com gameRecord api.

Can fetch data for a user's stats like stats, characters, spiral abyss runs...
"""
import hashlib
import logging
import random
import string
import time
from http.cookies import SimpleCookie
from typing import List
from urllib.parse import urljoin

from requests import Session

from .pretty import *
from .utils import USER_AGENT, is_chinese, raise_for_error, recognize_server

logger = logging.getLogger('genshinstats')
session = Session()
session.headers.update({
    # required headers
    "x-rpc-app_version":"1.5.0", # global api uses 1.x.x, chinese api uses 2.x.x
    "x-rpc-client_type":"4",
    "x-rpc-language":"en-us",
    # authentications headers
    "ds":"",
    # recommended headers
    "user-agent":USER_AGENT
})
DS_SALT = "6cqshh5dhw73bzxn20oexa9k516chk7s"
OS_BBS_URL = "https://bbs-api-os.hoyolab.com/"
CN_TAKUMI_URL = "https://api-takumi.mihoyo.com/"

def set_cookie(account_id: int, cookie_token: str) -> None:
    """Basic configuration function, required for anything beyond search.
    
    Account id and cookie token must be copied from your browser's cookies.
    """
    session.cookies.set('account_id',str(account_id))
    session.cookies.set('cookie_token',cookie_token)

def set_cookie_header(header: str) -> None:
    """Like set_cookie, but you can set the header directly."""
    c = SimpleCookie()
    c.load(header)
    session.cookies.update(c)

def set_cookie_auto(browser: str=None):
    """Like set_cookie, but gets the cookies by itself.
    
    Requires the module browser-cookie3
    Be aware that this process can take up to 10 seconds, 
    so it should be ran only once.
    To speed it up select a browser.
    
    If a specifc browser is set, gets data from that browser only.
    Avalible browsers: chrome, chromium, opera, edge, firefox
    """
    import browser_cookie3
    logger.debug(f'Loading cookies automatically.')
    if browser is None:
        jar = browser_cookie3.load()
    else:
        jar = getattr(browser_cookie3,browser)()
    
    for c in jar:
        if 'hoyolab' in c.domain or 'mihoyo' in c.domain:
            session.cookies.set(c.name,c.value)

def get_ds_token(salt: str) -> str:
    """Creates a new ds token.
    
    Uses an MD5 hash with a unique salt.
    """
    t = int(time.time()) # current seconds
    r = ''.join(random.sample(string.ascii_lowercase+string.digits, k=6)) # 6 random chars
    h = hashlib.md5(f"salt={salt}&t={t}&r={r}".encode()).hexdigest() # hash and get hex
    return f'{t},{r},{h}'

def fetch_endpoint(endpoint: str, *, chinese: bool=False, **kwargs) -> dict:
    """Fetch an enpoint from the hoyolabs API.
    
    Takes in an endpoint url which is joined with the base url.
    A request is then sent and returns a parsed response.
    Includes error handling and ds token renewal.
    
    Can specifically use the chinese base url  and request data for chinese users, 
    but that requires being logged in as that user.
    """
    session.headers['ds'] = get_ds_token(DS_SALT)
    method = kwargs.pop('method','get')
    url = urljoin(CN_TAKUMI_URL if chinese else OS_BBS_URL, endpoint)
    
    logger.debug(f'Fetching endpoint "{url}"')
    r = session.request(method,url,**kwargs)
    r.raise_for_status()
    
    data = r.json()
    if data['retcode'] == 0:
        return data['data']
    
    raise_for_error(data)

def get_user_info(uid: int, raw: bool=False) -> dict:
    """Gets game user info of a user based on their uid.
    
    Game user info contain the main nformation regarding a user.
    Contains owned characters, stats, city and world explorations and role.
    """
    server = recognize_server(uid)
    data = fetch_endpoint(
        "game_record/genshin/api/index",
        chinese=is_chinese(uid),
        params=dict(server=server,role_id=uid)
    )
    return data if raw else prettify_user_info(data)

def get_characters(uid: int, character_ids: List[int], lang: str='en-us', raw: bool=False) -> list:
    """Gets characters of a user set by their ids.
    
    Characters contain info about their level, constelation, weapon, and artifacts.
    Talents are not included.
    
    Change the language with lang, 
    possible langs can be found with get_langs() under the value field.
    """
    server = recognize_server(uid)
    data = fetch_endpoint(
        "game_record/genshin/api/character",
        chinese=is_chinese(uid),
        method='POST',
        json={'character_ids':character_ids,'role_id':uid,'server':server},
        headers={'x-rpc-language':lang},
    )["avatars"]
    return data if raw else prettify_characters(data)

def get_all_characters(uid: int, lang: str='en-us', raw: bool=False) -> list:
    """Gets all characters of a user.
    
    Characters contain info about their level, constelation, weapon, and artifacts.
    Talents are not included.
    
    Change the language with lang, 
    possible langs can be found with get_langs() under the value field.
    """
    characters = get_user_info(uid)['characters']
    return get_characters(uid,[i['id'] for i in characters], lang, raw)

def get_spiral_abyss(uid: int, previous: bool=False, raw: bool=False) -> dict:
    """Gets how far the user has gotten in spiral abyss and their season progress.
    
    Spiral abyss info contains their porgress, stats and individual completes.
    
    Every season these stats refresh and you can get the previous stats with `previous`.
    """
    server = recognize_server(uid)
    schedule_type = 2 if previous else 1
    data = fetch_endpoint(
        "game_record/genshin/api/spiralAbyss",
        chinese=is_chinese(uid),
        params=dict(server=server,role_id=uid,schedule_type=schedule_type)
    )
    return data if raw else prettify_spiral_abyss(data)

