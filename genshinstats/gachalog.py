"""Genshin Impact gacha pulls log.

Gets pull data from the current banners in basic json.
Requires an auth key that can be gotten from an output_log.txt file.
"""
import os.path
import re
from tempfile import gettempdir
from urllib.parse import unquote, urljoin

import requests

from .errors import BadGachaType, GenshinGachaLogException, MissingAuthKey
from .pretty import prettify_gacha_log

GENSHIN_DIR = os.path.join(os.environ['HOME'],'AppData/LocalLow/miHoYo/Genshin Impact')
GENSHIN_LOG = os.path.join(GENSHIN_DIR,'output_log.txt')
GACHA_LOG_URL = "https://hk4e-api.mihoyo.com/event/gacha_info/api/"
AUTHKEY_FILE = os.path.join(gettempdir(),'genshinstats_authkey.txt')
_gacha_types = None

session = requests.Session()
session.params = {
    'authkey_ver':1,
    'lang':'en'
}

def get_authkey(logfile: str=None) -> str:
    """Gets the query for history requests.
    
    This will either be done from the logs or from a tempfile.
    """
    # first try the log
    log = open(logfile or GENSHIN_LOG).read()
    match = re.search(r'^OnGetWebViewPageFinish:https://.+authkey=([^&]+).+#/log$',log,re.MULTILINE)
    if match is not None:
        authkey = unquote(match.group(1))
        open(AUTHKEY_FILE,'w').write(authkey)
        return authkey
    
    # otherwise try the tempfile
    if os.path.isfile(AUTHKEY_FILE):
        return open(AUTHKEY_FILE).read()
    
    raise MissingAuthKey('No authkey could be found in the params, logs or in a tempfile.'
                         'Open the history in-game first before attempting to request it.')

def fetch_gacha_endpoint(endpoint: str, **kwargs) -> dict:
    """Fetch an enpoint from mihoyo's gacha info.
    
    Takes in an endpoint or a url and kwargs that are later formatted to a query.
    A request is then sent and returns a parsed response.
    """
    kwargs['authkey'] = kwargs.get('authkey') or get_authkey() # update authkey
    url = urljoin(GACHA_LOG_URL,endpoint)
    r = session.get(url,params=kwargs)
    r.raise_for_status()
    
    data = r.json()
    if data['data'] is not None:
        return data['data']
    
    raise GenshinGachaLogException(f"{data['retcode']} error: {data['message']}")

def get_gacha_types() -> list:
    """Gets possible gacha types.
    
    Returns a list of dicts.
    """
    global _gacha_types
    if _gacha_types is not None:
        return _gacha_types
    _gacha_types = fetch_gacha_endpoint("getConfigList")['gacha_type_list']
    return _gacha_types

def recognize_gacha_type(gacha_type) -> str:
    """Recognizes the gacha type. Case Sensitive."""
    gacha_type = str(gacha_type)
    gacha_types = get_gacha_types()
    for i in gacha_types:
        if gacha_type in i.values():
            return i['key']
    
    raise BadGachaType(f'Gacha type "{gacha_type}" is not valid, must be one of {sum((list(i.values()) for i in gacha_types),[])}')

def get_gacha_log(gacha_type: str, page: int=1, size: int=20, raw: bool=False) -> list:
    """Gets the gacha pull history log.
    
    Needs a gacha type, this can either be its name, key or id.
    Possible gacha types can be found in the return of get_gacha_types().
    Returns a list of dicts. 
    """
    gacha_type = recognize_gacha_type(gacha_type)
    data = fetch_gacha_endpoint("getGachaLog",gacha_type=gacha_type,page=page,size=size)['list']
    return data if raw else prettify_gacha_log(data)
