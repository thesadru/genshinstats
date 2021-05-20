"""Genshin Impact gacha pulls log.

Gets pull data from the current banners in basic json.
Requires an auth key that can be gotten from an output_log.txt file.
"""
import heapq
import logging
import os
import re
from functools import lru_cache
from itertools import islice
from tempfile import gettempdir
from typing import Any, Iterator, Optional
from urllib.parse import unquote, urljoin

from requests import Session

from .errors import MissingAuthKey, raise_for_error
from .pretty import *
from .utils import USER_AGENT, get_output_log

logger = logging.getLogger('genshinstats')
GENSHIN_LOG = get_output_log()
GACHA_LOG_URL = "https://hk4e-api.mihoyo.com/event/gacha_info/api/"
AUTHKEY_FILE = os.path.join(gettempdir(),'genshinstats_authkey.txt')

session = Session()
session.headers.update({
    # recommended header
    "user-agent":USER_AGENT
})
session.params = {
    # required params
    "authkey_ver":1,
    "lang":"en",
    # authentications params
    "authkey":"",
}
gacha_session = Session() # extra session for static resources

def _read_logfile(logfile: str=None) -> str:
    if GENSHIN_LOG is None:
        raise FileNotFoundError('No Genshin Installation was found, could not get gacha data.')
    with open(logfile or GENSHIN_LOG) as file:
        return file.read()

def extract_authkey(string: str) -> Optional[str]:
    """Extracts an authkey from the provided string. Returns None if not found."""
    match = re.search(r'https://.+?authkey=([^&]+)',string,re.MULTILINE)
    if match is not None:
        return unquote(match.group(1))
    return None

def get_authkey(logfile: str=None) -> str:
    """Gets the query for log requests.
    
    This will either be done from the logs or from a tempfile.
    """
    logger.debug('Getting an authkey from log files.')
    # first try the log
    authkey = extract_authkey(_read_logfile(logfile))
    if authkey is not None:
        with open(AUTHKEY_FILE,'w') as file:
            file.write(authkey)
        return authkey
    # otherwise try the tempfile (may be expired!)
    if os.path.isfile(AUTHKEY_FILE):
        with open(AUTHKEY_FILE) as file:
            return file.read()
    
    raise MissingAuthKey('No authkey could be found in the logs or in a tempfile. '
                         'Open the history in-game first before attempting to request it.')

def get_all_gacha_ids(logfile: str=None) -> list:
    """Gets all gacha ids from a log file.
    
    You need to open the details of all banners for this to work.
    """
    log = _read_logfile(logfile)
    ids = re.findall(r'OnGetWebViewPageFinish:https://.+?gacha_id=([^&]+)',log)
    return list(set(ids))

def set_authkey(authkey: str=None, url: str=None, logfile: str=None) -> None:
    """Sets an authkey for log requests.
    
    passing in authkey will simply save it, 
    passing in a url will take the authkey out of it,
    passing in a logfile will search it,
    otherwise searches the logs and a tempfile.
    """
    if authkey is not None:
        pass
    elif url is not None:
        authkey = extract_authkey(url)
        if authkey is None:
            raise ValueError("url does not have an authkey parameter")
    else:
        authkey = get_authkey(logfile)
    session.params['authkey'] = authkey

def fetch_gacha_endpoint(endpoint: str, authkey: str=None, **kwargs) -> dict:
    """Fetch an enpoint from mihoyo's gacha info.
    
    Takes in an endpoint url which is joined with the base url.
    If an autheky is provided, it uses that authkey specifically.
    A request is then sent and returns a parsed response.
    Includes error handling and getting the authkey.
    """
    if authkey is None:
        session.params['authkey'] = session.params['authkey'] or get_authkey() # update authkey
    else:
        kwargs['params']['authkey'] = authkey
    method = kwargs.pop('method','get')
    url = urljoin(GACHA_LOG_URL, endpoint)
    
    logger.debug(f'Fetching gacha endpoint "{url}"')
    r = session.request(method,url,**kwargs)
    r.raise_for_status()
    
    data = r.json()
    if data['retcode'] == 0:
        return data['data']
    
    raise_for_error(data)

@lru_cache()
def get_gacha_types(authkey: str=None, lang: str='en') -> list:
    """Gets possible gacha types.
    
    Returns a list of dicts.
    """
    return fetch_gacha_endpoint(
        "getConfigList",
        authkey=authkey,
        params=dict(lang=lang)
    )['gacha_type_list']

def recognize_gacha_type(gacha: Any, authkey: str=None, lang: str='en') -> Optional[dict]:
    """Recognizes a given gacha type by id, key or name."""
    gacha = str(gacha) # everything is a string anyways, just cast here
    for t in get_gacha_types(authkey,lang):
        if gacha in t.values():
            return t
    return None

def get_gacha_log(gacha_type: int, size: int=None, authkey: str=None, end_id: int=0, lang: str='en', raw: bool=False) -> Iterator[dict]:
    """Gets the gacha pull history log.
    
    Needs a gacha type, this must be the key (for example 301).
    Possible gacha types can be found in the return of get_gacha_types().
    
    Yields instead of returning, since it's paginated.
    May return less than size when size is too big.
    If size is not set it will yield until it runs out of items.
    
    To be able to get history starting from somewhere other than the earliest pull,
    you must pass in the id of the first pull before (chronologically after) the one you want to start from as end_id.
    """
    if size is not None and size <= 0:
        return
    
    # we create gacha_name outside prettify so we don't make extra requests
    gacha_name = recognize_gacha_type(gacha_type,authkey=authkey,lang=lang)['name']
    page_size = 20 # max size per page is 20
    while True:
        data = fetch_gacha_endpoint(
            "getGachaLog",
            authkey=authkey,
            params=dict(gacha_type=gacha_type,size=page_size,end_id=end_id,lang=lang)
        )['list']
        
        yield from data if raw else prettify_gacha_log(data,gacha_name)
        
        if len(data) < page_size:
            return # return if reached the end
        if size is not None:
            size -= page_size
            page_size = min(size,20)
            if size <= 0:
                return

        end_id = data[-1]['id']

def get_entire_gacha_log(size: int=None, authkey: str=None, end_id: int=0, lang: str='en', raw: bool=False) -> Iterator[dict]:
    """Gets the entire gacha pull history log.
    
    Basically same as running get_gacha_log() with every possible key.
    Will yield pulls from most recent to oldest.
    """
    gens = [get_gacha_log(t['key'],authkey=authkey,end_id=end_id,lang=lang,raw=raw) 
            for t in get_gacha_types(authkey)]
    return islice(heapq.merge(*gens,key=lambda x:x['time'],reverse=True),size)

def get_gacha_items(lang: str='en-us', raw: bool=False) -> list:
    """Gets the list of items that can be gotten from the gacha.
    
    Returns a list of avalible characters and weapons.
    To get more info about a specific item use its id.
    """
    r = gacha_session.get(
        f"https://webstatic-sea.mihoyo.com/hk4e/gacha_info/os_asia/items/{lang}.json"
    )
    r.raise_for_status()
    return r.json() if raw else prettify_gacha_items(r.json())

def get_gacha_details(gacha_id: str, lang: str='en-us', raw: bool=False) -> dict:
    """Gets details of a specific gacha banner.
    
    This requires a specific gacha banner id.
    These keep rotating so you need to find them yourself or run get_all_gacha_ids().
    example standard wish: "a37a19624270b092e7250edfabce541a3435c2"
    
    Change the language of the output with lang, 
    possible langs can be found with get_langs() under the value field.
    
    The newbie gacha has no json resource tied to it, so you can't get info about it.
    """
    r = gacha_session.get(
        f"https://webstatic-sea.mihoyo.com/hk4e/gacha_info/os_asia/{gacha_id}/{lang}.json"
    )
    r.raise_for_status()
    return r.json() if raw else prettify_gacha_details(r.json())

def get_uid_from_authkey(authkey: str=None) -> int:
    """Gets a uid from an authkey. 
    
    If an authkey is not passed in uses the currently set authkey.
    """
    uid = fetch_gacha_endpoint(
        "getGachaLog",
        authkey=authkey,
        params=dict(gacha_type=200,size=1)
    )['list'][0]['uid']
    return int(uid)
