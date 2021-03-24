"""Wrapper for the hoyolab.com gameRecord api.

Can fetch data for a user's stats like stats, characters, spiral abyss runs...
"""
import hashlib
import random
import re
import string
import time
from http.cookies import SimpleCookie
from typing import List
from urllib.parse import urljoin

from requests import Session
from requests.cookies import cookiejar_from_dict

from .errors import *
from .pretty import *

session = Session()
session.headers.update({
    # required headers
    "x-rpc-app_version":"1.5.0", # chinese api uses 2.x.x, global api uses 1.x.x
    "x-rpc-client_type":"4",
    "x-rpc-language":"en-us",
    # authentications headers
    "ds":"",
    # recommended headers
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
})
DS_SALT = "6cqshh5dhw73bzxn20oexa9k516chk7s"
HOYOLABS_URL = "https://bbs-api-os.hoyolab.com/" # global
TAKUMI_URL = "https://api-takumi.mihoyo.com" # chinese

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
    session.cookies = cookiejar_from_dict({k:v.value for k,v in c.items()},session.cookies)

def get_ds_token(salt: str) -> str:
    """Creates a new ds token.
    
    Uses an MD5 hash with a unique salt.
    """
    t = int(time.time()) # current seconds
    c = ''.join(random.sample(string.ascii_lowercase+string.digits, k=6)) # 6 random chars
    h = hashlib.md5(f"salt={salt}&t={t}&r={c}".encode()).hexdigest() # hash and get hex
    return f'{t},{c},{h}'

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
    url = urljoin(TAKUMI_URL if chinese else HOYOLABS_URL, endpoint)
    
    r = session.request(method,url,**kwargs)
    r.raise_for_status()
    
    data = r.json()
    if data['data'] is not None: # success
        return data['data']
    
    # Custom HTTP Errors
    retcode,msg = data['retcode'],data['message']
    # UID
    if   retcode == 1009  and msg == "角色信息错误":
        raise InvalidUID('UID could not be found.')
    elif retcode == 10102 and msg == 'Data is not public for the user':
        raise DataNotPublic('User has set their data to be private. To enable go to https://www.hoyolab.com/genshin/accountCenter/gameRecord')
    # token
    elif retcode == -401  and msg == '请求异常':
        raise InvalidDS('Invalid DS token, might be expired.')
    elif retcode == -100 or retcode == 10001 and msg == 'Please login':
        raise NotLoggedIn('Login cookies have not been provided or are incorrect.')
    # other
    elif retcode == 1     and msg == 'Invalid schedule type':
        raise InvalidScheduleType('Invalid Spiral Abyss schedule type, can only be 1 or 2.')
    elif retcode == 2001  and msg == 'Duplicate operation or update failed':
        raise CannotCheckIn('Check-in is currently timed out, wait at least a day before checking-in again.')
    elif retcode == -2003 and msg == 'Invalid redemption code':
        raise InvalidCode('Invalid redemption code')
    elif retcode == -2017 and msg == 'This Redemption Code is already in use':
        raise CodeAlreadyUsed('Redemption code has been claimed already.')
    elif retcode == -2021 and msg == 'You do not meet the Adventure Rank requirements. This redemption code is only valid if your Adventure Rank is equal to or above 10':
        raise TooLowAdventureRank('Cannot claim codes for account with advunture rank lower than 10.')
    elif retcode == -5003 and msg == "Traveler, you've already checked in today~":
        raise AlreadySignedIn('Already claimed daily reward, try again tommorow.')
    elif retcode ==-10002 and msg == 'No character created yet':
        raise NoGameAccount('Cannot get rewards info. Account has no game account binded to it.')
    elif retcode == -1    and msg.endswith(' is not exists'):
        t,n = msg.split(':')
        raise InvalidItemID(f'{t} "{n.split()[0]}" does not exist.')
    else:
        raise GenshinStatsException(f"{retcode} Error ({data['message']}) for url: \"{r.url}\"")

def recognize_server(uid: int) -> str:
    """Recognizes which server a UID is from."""
    server = {
        1:'cn_gf01',
        5:'cn_qd01',
        6:'os_usa',
        7:'os_euro',
        8:'os_asia',
        9:'os_cht',
    }.get(int(str(uid)[0]))
    if server:
        return server
    else:
        raise InvalidUID("UID isn't associated with any server")

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

def is_game_uid(uid: int) -> bool:
    """Recognizes whether the uid is a game uid.
    
    Return True if it's a game uid, False if it's a community uid
    """
    return bool(re.fullmatch(r'[6789]\d{8}',str(uid)))

def is_chinese(x: str) -> bool:
    """Recognizes whether the server/uid is chinese."""
    return str(x).startswith(('cn','1','5'))
