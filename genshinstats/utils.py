"""Various utility functions for genshinstats."""
import os.path
import re
import inspect
from typing import Callable, Optional, TypeVar, Union

from .errors import AccountNotFound

__all__ = [
    'USER_AGENT', 'recognize_server', 'is_game_uid', 'is_chinese', 'get_output_log', 'permanent_cache'
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

def recognize_server(uid: int) -> str:
    """Recognizes which server a UID is from."""
    server = {
        1:'cn_gf01',
        5:'cn_qd01',
        6:'os_usa',
        7:'os_euro',
        8:'os_asia',
        9:'os_cht',
    }.get(int(str(uid)[0])) # first digit
    if server:
        return server
    else:
        raise AccountNotFound(f"UID {uid} isn't associated with any server")

def is_game_uid(uid: int) -> bool:
    """Recognizes whether the uid is a game uid."""
    return bool(re.fullmatch(r'[6789]\d{8}',str(uid)))

def is_chinese(x: Union[int, str]) -> bool:
    """Recognizes whether the server/uid is chinese."""
    return str(x).startswith(('cn','1','5'))

def get_output_log() -> Optional[str]:
    """Find and return the Genshin Impact output log. None if not found."""
    mihoyo_dir = os.path.expanduser('~/AppData/LocalLow/miHoYo/')
    for name in ["Genshin Impact","原神","YuanShen"]:
        output_log = os.path.join(mihoyo_dir,name,'output_log.txt')
        if os.path.isfile(output_log):
            return output_log
    return None # no genshin installation

T = TypeVar('T', bound=Callable)
def permanent_cache(*params: str) -> Callable[[T], T]:
    """Like lru_cache except permanent and only caches based on some parameters"""
    cache = {}
    
    def wrapper(func):
        sig = inspect.signature(func)
        
        def inner(*args, **kwargs):
            bound = tuple(v for k,v in sig.bind(*args, **kwargs).arguments.items() if k in params)
            if bound in cache:
                return cache[bound]
            r =  func(*args, **kwargs)
            cache[bound] = r
            return r
        
        inner.cache = cache
        return inner
    return wrapper # type: ignore
