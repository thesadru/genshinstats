"""Genshinstats errors.

These take in only a single argument: msg.
It's possible to add retcodes and the original api response message with `.set_reponse()`.
"""
from typing import NoReturn

class GenshinStatsException(Exception):
    """Base Exception for all genshinstats errors."""
    retcode: int = 0
    orig_msg: str = ''
    def __init__(self, msg: str):
        self.msg = msg
    
    def set_response(self, response: dict):
        """Adds an optional response object to the error."""
        self.retcode = response['retcode']
        self.orig_msg = response['message']
        if type(self) == GenshinStatsException: # for exceptions without a type
            self.msg = self.msg.format(self.retcode,self.orig_msg)

    @property
    def msg(self):
        return self.args[0]
    @msg.setter
    def msg(self, msg):
        self.args = (msg,)

class NotLoggedIn(GenshinStatsException):
    """Cookies have not been provided."""
class AccountNotFound(GenshinStatsException):
    """Tried to get data with an invalid uid."""
class DataNotPublic(GenshinStatsException):
    """User hasn't set their data to public."""

class CodeRedeemException(GenshinStatsException):
    """Code redemption failed."""

class SignInException(GenshinStatsException):
    """Sign-in failed"""

class GachaLogException(GenshinStatsException):
    """Base GachaLog Exception."""
class InvalidAuthkey(GachaLogException):
    """An authkey is invalid."""
class AuthKeyTimeout(GachaLogException):
    """An authkey has timed out."""
class MissingAuthKey(GachaLogException):
    """No gacha authkey was found."""

def raise_for_error(response: dict) -> NoReturn:
    """Raises a custom genshinstats error from a response."""
    # every error uses a different response code and message, 
    # but the codes are not unique so we must check the message at some points too.
    error = {
        # general
        -100:  NotLoggedIn('Login cookies have not been provided or are incorrect.'),
        10001: NotLoggedIn('Login cookies have not been provided or are incorrect.'),
        10102: DataNotPublic('User\'s data is not public'),
        1009:  AccountNotFound('Could not find user; uid may not be valid.'),
        -1:    AccountNotFound('Could not find user; uid may not be valid.'),
        -10002:AccountNotFound('Cannot get rewards info. Account has no game account binded to it.'),
        -108:  GenshinStatsException('Language is not valid.'),
        # code redemption
        -2003: CodeRedeemException('Invalid redemption code'),
        -2017: CodeRedeemException('Redemption code has been claimed already.'),
        -2001: CodeRedeemException('Redemption code has expired.'),
        -2021: CodeRedeemException('Cannot claim codes for account with adventure rank lower than 10.'),
        -1073: CodeRedeemException('Cannot claim code. Account has no game account bound to it.'),
        # sign in
        -5003: SignInException('Already claimed daily reward, try again tomorrow.'),
        2001:  SignInException('Already checked in today, wait at least a day before checking-in again.'),
        # gacha log
        -100:  InvalidAuthkey('Authkey is not valid.') if response['message']=='authkey error' else 
                NotLoggedIn('Login cookies have not been provided or are incorrect.'),
        -101:  AuthKeyTimeout('Authkey has timed-out. Update it by opening the history page in Genshin.')
    }.get(response['retcode'], GenshinStatsException("{} Error ({})"))
    error.set_response(response)
    raise error

del NoReturn # so we don't have to bother with __all__
