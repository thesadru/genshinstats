"""Various utility functions for genshinstats."""
import inspect
import os.path
import re
import warnings
from functools import wraps
from typing import Callable, Iterable, Optional, Type, TypeVar, Union

from .errors import AccountNotFound

__all__ = [
    "USER_AGENT",
    "recognize_server",
    "recognize_id",
    "is_game_uid",
    "is_chinese",
    "get_logfile",
]

T = TypeVar("T")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

def recognize_server(uid: int) -> str:
    """Recognizes which server a UID is from."""
    server = {
        '1':'cn_gf01',
        '5':'cn_qd01',
        '6':'os_usa',
        '7':'os_euro',
        '8':'os_asia',
        '9':'os_cht',
    }.get(str(uid)[0])
    if server:
        return server
    else:
        raise AccountNotFound(f"UID {uid} isn't associated with any server")

def recognize_id(id: int) -> Optional[str]:
    """Attempts to recognize what item type an id is"""
    if 10000000 < id < 20000000:
        return "character"
    elif 1000000 < id < 10000000:
        return "artifact_set"
    elif 100000 < id < 1000000:
        return "outfit"
    elif 50000 < id < 100000:
        return "artifact"
    elif 10000 < id < 50000:
        return "weapon"
    elif 100 < id < 1000:
        return "constellation"
    elif 10 ** 17 < id < 10 ** 19:
        return "transaction"
    # not sure about these ones:
    elif 1 <= id <= 4:
        return "exploration" 
    else:
        return None

def is_game_uid(uid: int) -> bool:
    """Recognizes whether the uid is a game uid."""
    return bool(re.fullmatch(r"[6789]\d{8}", str(uid)))

def is_chinese(x: Union[int, str]) -> bool:
    """Recognizes whether the server/uid is chinese."""
    return str(x).startswith(("cn", "1", "5"))

def get_logfile() -> Optional[str]:
    """Find and return the Genshin Impact logfile. None if not found."""
    mihoyo_dir = os.path.expanduser("~/AppData/LocalLow/miHoYo/")
    for name in ["Genshin Impact", "原神", "YuanShen"]:
        output_log = os.path.join(mihoyo_dir, name, "output_log.txt")
        if os.path.isfile(output_log):
            return output_log
    return None # no genshin installation

def retry(tries: int = 3, exceptions: Union[Type[BaseException], Iterable[Type[BaseException]]] = Exception) -> Callable[[T], T]:
    """A classic retry() decorator"""
    def wrapper(func):
        
        @wraps(func)
        def inner(*args, **kwargs):
            for _ in range(tries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    exc = e
            else:
                raise Exception(f"Maximum tries ({tries}) exceeded: {exc}") from exc # type: ignore
        
        return inner
    
    return wrapper # type: ignore

def deprecated(message: str = "{} is deprecated and will be removed in future versions") -> Callable[[T], T]:
    """Shows a warning when a function is attempted to be used"""
    def wrapper(func):
        
        @wraps(func)
        def inner(*args, **kwargs):
            warnings.warn(message.format(func.__name__), PendingDeprecationWarning)
            return func(*args, **kwargs)

        return inner
    return wrapper # type: ignore
