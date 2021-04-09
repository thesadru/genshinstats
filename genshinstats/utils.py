"""Various utility functions for genshinstats."""
import os.path
import re
from typing import NoReturn, Optional

from .errors import *

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

def raise_for_error(response: dict) -> NoReturn:
    """Raises a custom genshinstats error from a response."""
    error = {
        # authorization
        -401:  InvalidDS('Invalid DS token, might be expired.'),
        -100:  NotLoggedIn('Login cookies have not been provided or are incorrect.'),
        # UID
        1009:  InvalidUID('UID could not be found.'),
        10102: DataNotPublic('User has set their data to be private. If this is your account look at the README.md to see how to make it public.'),
        # general errors
        1:     InvalidScheduleType('Invalid Spiral Abyss schedule type, can only be 1 or 2.'),
        -10002:NoGameAccount('Cannot get rewards info. Account has no game account binded to it.'),
        -1:    InvalidUID('UID is not valid.') if response['message']=='Invalid uid' else InvalidItemID('{} "{}" does not exist.'),
        # code redemption
        -2003: InvalidCode('Invalid redemption code'),
        -2017: CodeAlreadyUsed('Redemption code has been claimed already.'),
        -2021: TooLowAdventureRank('Cannot claim codes for account with adventure rank lower than 10.'),
        -1073: NoGameAccount('Cannot claim code. Account has no game account binded to it.'),
        -2016: RedeemCooldown('Redemption in cooldown. Please try again in {} second(s).'),
        # sign in
        -5003: AlreadySignedIn('Already claimed daily reward, try again tommorow.'),
        2001:  CannotCheckIn('Check-in is currently timed out, wait at least a day before checking-in again.'),
        # gacha log
        -100:  AuthKeyError('Authkey is not valid.'),
        -101:  AuthKeyTimeout('Authkey has timed-out. Update it by opening the history page in Genshin.')
    }.get(response['retcode'], GenshinStatsException("{} Error ({})"))
    error.set_response(response)
    raise error

def recognize_server(uid: int) -> str:
    """Recognizes which server a UID is from."""
    x = int(str(uid)[0])
    server = {
        1:'cn_gf01',
        5:'cn_qd01',
        6:'os_usa',
        7:'os_euro',
        8:'os_asia',
        9:'os_cht',
    }.get(x)
    if server:
        return server
    else:
        raise InvalidUID("UID isn't associated with any server")

def is_game_uid(uid: int) -> bool:
    """Recognizes whether the uid is a game uid.
    
    Return True if it's a game uid, False if it's a community uid
    """
    return bool(re.fullmatch(r'[6789]\d{8}',str(uid)))

def is_chinese(x) -> bool:
    """Recognizes whether the server/uid is chinese."""
    return str(x).startswith(('cn','1','5'))

def get_genshin_dir() -> Optional[str]:
    """Find and return the Genshin Impact directory. None if not found."""
    mihoyo_dir = os.path.expanduser('~/AppData/LocalLow/miHoYo/')
    for name in ["Genshin Impact","原神","YuanShen"]:
        directory = os.path.join(mihoyo_dir,name)
        if os.path.exists(directory):
            return directory
    return None # no genshin installation
