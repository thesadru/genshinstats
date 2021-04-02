"""Various utility functions for genshinstats."""
import os.path
import re
from typing import NoReturn

from .errors import *

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

def raise_for_error(response: dict) -> NoReturn:
    """Raises a custom genshinstats error from a response."""
    retcode,msg = response['retcode'],response['message']
    # authorization
    if retcode == -401  and msg == '请求异常':
        raise InvalidDS('Invalid DS token, might be expired.')
    elif retcode == -100 or retcode == 10001 and msg == 'Please login':
        raise NotLoggedIn('Login cookies have not been provided or are incorrect.')
    # UID
    elif   retcode == 1009  and msg == "角色信息错误":
        raise InvalidUID('UID could not be found.')
    elif retcode == 10102 and msg == 'Data is not public for the user':
        raise DataNotPublic('User has set their data to be private. To enable go to https://www.hoyolab.com/genshin/accountCenter/gameRecord')
    # general errors
    elif retcode == 1     and msg == 'Invalid schedule type':
        raise InvalidScheduleType('Invalid Spiral Abyss schedule type, can only be 1 or 2.')
    elif retcode ==-10002 and msg == 'No character created yet':
        raise NoGameAccount('Cannot get rewards info. Account has no game account binded to it.')
    elif retcode == -1    and msg.endswith(' is not exists'):
        t,n = re.match(r'(.+?):(\d+)',msg).groups()
        raise InvalidItemID(f'{t} "{n}" does not exist.')
    # code redemption
    elif retcode == -2003 and msg == 'Invalid redemption code':
        raise InvalidCode('Invalid redemption code')
    elif retcode == -2017 and msg == 'This Redemption Code is already in use':
        raise CodeAlreadyUsed('Redemption code has been claimed already.')
    elif retcode == -2021 and msg == 'You do not meet the Adventure Rank requirements. This redemption code is only valid if your Adventure Rank is equal to or above 10':
        raise TooLowAdventureRank('Cannot claim codes for account with adventure rank lower than 10.')
    elif retcode == -1073 and msg == "You haven't created a character on this server. Create a character first and then try redeeming the code.":
        raise NoGameAccount('Cannot claim code. Account has no game account binded to it.')
    # sign in
    elif retcode == -5003 and msg == "Traveler, you've already checked in today~":
        raise AlreadySignedIn('Already claimed daily reward, try again tommorow.')
    elif retcode == 2001  and msg == 'Duplicate operation or update failed':
        raise CannotCheckIn('Check-in is currently timed out, wait at least a day before checking-in again.')
    elif retcode == -2016 and msg.startswith('Redemption in cooldown.'):
        t = re.search(r'\d+',msg)
        raise RedeemCooldown(f'Redemption in cooldown. Please try again in {t} second(s).')
    # gacha log
    elif retcode == -100  and msg == "authkey error":
        raise AuthKeyError('Authkey is not valid.')
    elif retcode == -101 and msg == "authkey timeout":
        raise AuthKeyTimeout('Authkey has timed-out. Update it by opening the history page in Genshin.')
    # other
    else:
        raise GenshinStatsException(f"{retcode} Error ({msg})")

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

def is_chinese(x: str) -> bool:
    """Recognizes whether the server/uid is chinese."""
    return str(x).startswith(('cn','1','5'))

def get_genshin_dir() -> str:
    """Find and return the Genshin Impact directory. None if not found."""
    mihoyo_dir = os.path.expanduser('~/AppData/LocalLow/miHoYo/')
    for name in ["Genshin Impact","原神","YuanShen"]:
        directory = os.path.join(mihoyo_dir,name)
        if os.path.exists(directory):
            return directory
    return None # no genshin installation
