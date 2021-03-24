"""Genshin Impact gacha pulls log.

Gets pull data from the current banners in basic json.
Requires an auth key that can be gotten from an output_log.txt file.
"""
import os
import re
import time
from functools import lru_cache
from tempfile import gettempdir
from urllib.parse import unquote, urljoin

from requests import Session

from .errors import *
from .pretty import prettify_gacha_details, prettify_gacha_items, prettify_gacha_log

GENSHIN_DIR = os.path.expanduser('~/AppData/LocalLow/miHoYo/Genshin Impact')
GENSHIN_LOG = os.path.join(GENSHIN_DIR,'output_log.txt')
GACHA_LOG_URL = "https://hk4e-api.mihoyo.com/event/gacha_info/api/"
AUTHKEY_FILE = os.path.join(gettempdir(),'genshinstats_authkey.txt')
AUTHKEY_DURATION = 60*60*24 # 1 day

session = Session()
session.headers.update({
    # recommended header
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
})
session.params = {
    # required params
    "authkey_ver":1,
    "lang":"en",
    # authentications params
    "authkey":"",
}
gacha_session = Session() # extra session for static resources

_authkey_re = r'https://.+authkey=([^&]+).*#/(?:log)?'
def get_authkey(logfile: str=None) -> str:
    """Gets the query for log requests.
    
    This will either be done from the logs or from a tempfile.
    """
    # first try the log
    with open(logfile or GENSHIN_LOG) as file:
        log = file.read()
    match = re.search(_authkey_re,log,re.MULTILINE)
    if match is not None:
        authkey = unquote(match.group(1))
        with open(AUTHKEY_FILE,'w') as file:
            file.write(authkey)
        return authkey
    
    # otherwise try the tempfile
    if (os.path.isfile(AUTHKEY_FILE) and 
        time.time()-os.path.getmtime(AUTHKEY_FILE) <= AUTHKEY_DURATION):
        with open(AUTHKEY_FILE,) as file:
            return file.read()
    
    raise MissingAuthKey('No authkey could be found in the params, logs or in a tempfile. '
                         'Open the history in-game first before attempting to request it.')

def get_all_gacha_ids(logfile: str=None) -> list:
    """Gets all gacha ids from a log file.
    
    You need to open the details of all banners for this to work.
    """
    with open(logfile or GENSHIN_LOG) as file:
        log = file.read()
    ids = re.findall(r'OnGetWebViewPageFinish:https://.+gacha_id=([^&]+).*#/',log)
    return list(set(ids))

def set_authkey(authkey: str=None, url: str=None, logfile: str=None):
    """Sets an authkey for log requests.
    
    passing in authkey will simply save it, 
    passing in a url will take the authkey out of it,
    passing in a logfile will search it,
    otherwise uses get_authkey
    """
    if authkey is not None:
        pass
    elif url is not None:
        match = re.match(_authkey_re,url)
        if match is None:
            raise ValueError("url does not have an authkey parameter")
        authkey = unquote(match.group(1))
    else:
        authkey = get_authkey(logfile)
    session.params['authkey'] = authkey

def fetch_gacha_endpoint(endpoint: str, **kwargs) -> dict:
    """Fetch an enpoint from mihoyo's gacha info.
    
    Takes in an endpoint url which is joined with the base url.
    A request is then sent and returns a parsed response.
    Includes error handling and getting the authkey.
    """
    session.params['authkey'] = session.params['authkey'] or get_authkey() # update authkey
    method = kwargs.pop('method','get')
    url = urljoin(GACHA_LOG_URL, endpoint)
    
    r = session.request(method,url,**kwargs)
    r.raise_for_status()
    
    data = r.json()
    if data['data'] is not None: # success
        return data['data']
    
    if   data['retcode'] == -100 and data['message'] == "authkey error":
        raise AuthKeyError('Authkey is not valid.')
    elif data['retcode'] == -101 and data['message'] == "authkey timeout":
        raise AuthKeyTimeout('Authkey has timed-out. Update it by opening the history page in Genshin.')
    else:
        raise GachaLogException(f"{data['retcode']} error: {data['message']}")

@lru_cache()
def get_gacha_types(lang: str='en') -> list:
    """Gets possible gacha types.
    
    Returns a list of dicts.
    """
    return fetch_gacha_endpoint(
        "getConfigList",
        params=dict(lang=lang)
    )['gacha_type_list']

def get_gacha_log(gacha_type: int, page: int=1, size: int=20, lang: str='en', raw: bool=False) -> list:
    """Gets the gacha pull history log.
    
    Needs a gacha type, this must be the key (for example 301).
    Possible gacha types can be found in the return of get_gacha_types().
    
    Returns a list of dicts. 
    """
    data = fetch_gacha_endpoint(
        "getGachaLog",
        params=dict(gacha_type=gacha_type,page=page,size=size,lang=lang)
    )['list']
    return data if raw else prettify_gacha_log(data)

def get_gacha_items(lang: str='en-us', raw: bool=False) -> dict:
    """Gets the list of items that can be gotten from the gacha.
    
    Returns two a dict with two lists, characters and weapons.
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
    example standard wish: a37a19624270b092e7250edfabce541a3435c2
    
    Change the language of the output with lang, 
    possible langs can be found with get_langs() under the value field.
    
    The newbie gacha has no json resource tied to it, so you can't get info about it.
    """
    r = gacha_session.get(
        f"https://webstatic-sea.mihoyo.com/hk4e/gacha_info/os_asia/{gacha_id}/{lang}.json"
    )
    r.raise_for_status()
    return r.json() if raw else prettify_gacha_details(r.json())
    