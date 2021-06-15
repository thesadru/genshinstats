"""Genshin Impact wish history.

Gets wish history from the current banners in a clean api.
Requires an authkey that is fetched automatically from a logfile.
"""
import heapq
import os
import re
from functools import lru_cache
from itertools import chain, islice
from tempfile import gettempdir
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import unquote, urljoin

from requests import Session

from .errors import MissingAuthKey, raise_for_error
from .pretty import *
from .utils import USER_AGENT, get_output_log

__all__ = [
    'extract_authkey', 'get_authkey', 'set_authkey', 'get_banner_ids',
    'fetch_gacha_endpoint', 'get_banner_types', 'get_wish_history',
    'get_gacha_items', 'get_banner_details', 'get_uid_from_authkey'
]

GENSHIN_LOG = get_output_log()
GACHA_INFO_URL = "https://hk4e-api.mihoyo.com/event/gacha_info/api/"
AUTHKEY_FILE = os.path.join(gettempdir(), 'genshinstats_authkey.txt')

session = Session()
session.headers.update({
    # recommended header
    "user-agent": USER_AGENT
})
session.params = {
    # required params
    "authkey_ver": "1",
    "lang": "en",
    # authentications params
    "authkey": "",
}
static_session = Session()  # extra session for static resources

def _get_short_lang_code(lang: str) -> str:
    """Returns an alternative short lang code"""
    return lang if 'zh' in lang else lang.split('-')[0]

def _read_logfile(logfile: str = None) -> str:
    """Returns the contents of a logfile"""
    if GENSHIN_LOG is None:
        raise FileNotFoundError('No Genshin Installation was found, could not get gacha data.')
    with open(logfile or GENSHIN_LOG) as file:
        return file.read()

def extract_authkey(string: str) -> Optional[str]:
    """Extracts an authkey from the provided string. Returns None if not found."""
    match = re.search(r'https://.+?authkey=([^&]+)', string, re.MULTILINE)
    if match is not None:
        return unquote(match.group(1))
    return None

def get_authkey(logfile: str = None) -> str:
    """Gets the query for log requests.

    This will either be done from the logs or from a tempfile.
    """
    # first try the log
    authkey = extract_authkey(_read_logfile(logfile))
    if authkey is not None:
        with open(AUTHKEY_FILE, 'w') as file:
            file.write(authkey)
        return authkey
    # otherwise try the tempfile (may be expired!)
    if os.path.isfile(AUTHKEY_FILE):
        with open(AUTHKEY_FILE) as file:
            return file.read()

    raise MissingAuthKey('No authkey could be found in the logs or in a tempfile. '
                         'Open the history in-game first before attempting to request it.')

def set_authkey(authkey: str = None, url: str = None, logfile: str = None) -> None:
    """Sets an authkey for log requests.

    passing in authkey will simply save it, 
    passing in a url will take the authkey out of it,
    passing in a logfile will search it,
    otherwise searches the logs and a tempfile.
    """
    if authkey is not None:
        pass
    elif url is not None:
        authkey = extract_authkey(url) # type: ignore
        if authkey is None:
            raise ValueError("url does not have an authkey parameter")
    else:
        authkey = get_authkey(logfile)
    session.params['authkey'] = authkey

def get_banner_ids(logfile: str = None) -> List[str]:
    """Gets all banner ids from a log file.

    You need to open the details of all banners for this to work.
    """
    log = _read_logfile(logfile)
    ids = re.findall(r'OnGetWebViewPageFinish:https://.+?gacha_id=([^&]+)', log)
    return list(set(ids))

def fetch_gacha_endpoint(endpoint: str, authkey: str = None, **kwargs) -> Dict[str, Any]:
    """Fetch an enpoint from mihoyo's gacha info.

    Takes in an endpoint url which is joined with the base url.
    If an authkey is provided, it uses that authkey specifically.
    A request is then sent and returns a parsed response.
    Includes error handling and getting the authkey.
    """
    if authkey is None:
        session.params['authkey'] = session.params['authkey'] or get_authkey()
    else:
        kwargs['params']['authkey'] = authkey
    method = kwargs.pop('method', 'get')
    url = urljoin(GACHA_INFO_URL, endpoint)

    r = session.request(method, url, **kwargs)
    r.raise_for_status()

    data = r.json()
    if data['retcode'] == 0:
        return data['data']

    raise_for_error(data)

@lru_cache()
def get_banner_types(authkey: str = None, lang: str = 'en') -> Dict[int, str]:
    """Gets ids for all banners and their names"""
    banners = fetch_gacha_endpoint(
        "getConfigList",
        authkey=authkey,
        params=dict(lang=_get_short_lang_code(lang))
    )['gacha_type_list']
    return {int(i['key']): i['name'] for i in banners}

def get_wish_history(
    banner_type: int = None, size: int = None, 
    authkey: str = None, end_id: int = 0, lang: str = 'en'
) -> Iterator[dict]:
    """Gets wish history.
    
    Note that pulls are yielded and not returned to account for pagination.
    
    When a banner_type is set, only data from that banner type is retuned.
    You can get banner types and their names from get_banner_types.
    
    If a size is set the total returned amount of pulls will be equal to or lower than the size.

    To be able to get history starting from somewhere other than the last pull
    you may pass in the id of the pull right chronologically after the one you want to start from as end_id.
    """
    if size is not None and size <= 0:
        return
    
    if banner_type is None:
        # we get data from all banners by getting data from every individual banner
        # and then sorting it by pull date with heapq.merge
        gens = [get_wish_history(banner_type, None, authkey, end_id)
                for banner_type in get_banner_types(authkey)]
        yield from islice(heapq.merge(*gens, key=lambda x: x['time'], reverse=True), size)
        return

    # we create banner_name outside prettify so we don't make extra requests
    banner_name = get_banner_types(authkey, lang)[banner_type]
    lang = _get_short_lang_code(lang)
    page_size = 20  # max size per page is 20
    
    while True:
        data = fetch_gacha_endpoint(
            "getGachaLog",
            authkey=authkey,
            params=dict(gacha_type=banner_type, size=page_size, end_id=end_id, lang=lang)
        )['list']
        data = prettify_wish_history(data, banner_name)
        yield from data

        if len(data) < page_size:
            return  # return if reached the end
        if size is not None:
            size -= page_size
            page_size = min(size, 20)
            if size <= 0:
                return

        end_id = data[-1]['id']


def get_gacha_items(lang: str = 'en-us') -> list:
    """Gets the list of characters and weapons that can be gotten from the gacha."""
    r = static_session.get(
        f"https://webstatic-sea.mihoyo.com/hk4e/gacha_info/os_asia/items/{lang}.json"
    )
    r.raise_for_status()
    return prettify_gacha_items(r.json())

def get_banner_details(banner_id: str, lang: str = 'en-us') -> dict:
    """Gets details of a specific banner.

    This requires the banner's id.
    These keep rotating so you need to get them with get_banner_ids().
    example standard wish: "a37a19624270b092e7250edfabce541a3435c2"
    
    The newbie gacha has no json resource tied to it so you can't get info about it.
    """
    r = static_session.get(
        f"https://webstatic-sea.mihoyo.com/hk4e/gacha_info/os_asia/{banner_id}/{lang}.json"
    )
    r.raise_for_status()
    return prettify_banner_details(r.json())

def get_uid_from_authkey(authkey: str = None) -> int:
    """Gets a uid from an authkey. 

    If an authkey is not passed in the function uses the currently set authkey.
    """
    # for safety we use all banners, probably overkill
    histories = [get_wish_history(i, 1, authkey) for i in get_banner_types(authkey)]
    pull = next(chain(*histories), None)
    if pull is None: # very rare but possible
        raise Exception('User has never made a wish')
    return pull['uid']
