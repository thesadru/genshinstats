"""Genshinstats errors.

These take in only a single argument: msg.
It's possible to add retcodes and the original api response message with `.set_reponse()`.
"""
import re

class GenshinStatsException(Exception):
    """Base error for all Genshin Stats Errors."""
    retcode: int = 0
    orig_msg: str = ''
    def __init__(self, msg: str, response: dict=None):
        self.msg = msg
        if response:
            self.set_response(response)
    def set_response(self, response: dict):
        """Adds an optional response object to the error."""
        self.retcode = response['retcode']
        self.orig_msg = response['message']
        if type(self) == GenshinStatsException: # for exceptions without a type
            self.msg = self.msg.format(self.retcode,self.orig_msg)
    @property
    def msg(self): return self.args[0]
    @msg.setter
    def msg(self, msg): self.args = (msg,)

class InvalidDS(GenshinStatsException):
    """Invalid DS token, should be renewed."""
class NotLoggedIn(GenshinStatsException):
    """Cookies have not been provided."""

class InvalidUID(GenshinStatsException):
    """UID is not valid."""
class DataNotPublic(GenshinStatsException):
    """User has not allowed their data to be seen."""

class InvalidScheduleType(GenshinStatsException):
    """Invalid Spiral Abyss schedule"""
class NoGameAccount(GenshinStatsException):
    """Tried to get info without an account"""
class InvalidItemID(GenshinStatsException):
    """Item does not exist."""
    def set_response(self, response: dict):
        super().set_response(response)
        self.type,self.item = re.match(r'(.+?):(\w+)',self.orig_msg).groups()
        self.msg = self.msg.format(self.type,self.item)

class CodeRedeemException(GenshinStatsException):
    """Base CodeRedeem Exception."""
class InvalidCode(CodeRedeemException):
    """Invalid redemption code."""
class CodeAlreadyUsed(CodeRedeemException):
    """Redemption Code is already in use"""
class TooLowAdventureRank(CodeRedeemException):
    """Does not meet adventure rank requirements."""
class RedeemCooldown(CodeRedeemException):
    """Can only claim every 5 seconds."""
    cooldown: int = 5
    def set_response(self, response: dict):
        super().set_response(response)
        self.cooldown = int(re.search(r'\d+',self.orig_msg).group())
        self.msg = self.msg.format(self.cooldown)

class SignInException(GenshinStatsException):
    """Base SignIn Exception."""
class AlreadySignedIn(SignInException):
    """Already signed in dailies"""
class FirstSignIn(SignInException):
    """First sign in must be done manually. Not an API error!"""
class CannotCheckIn(GenshinStatsException):
    """Could not check in."""

class GachaLogException(GenshinStatsException):
    """Base GachaLog Exception."""
class AuthKeyError(GachaLogException):
    """Authkey error."""
class AuthKeyTimeout(GachaLogException):
    """Authkey timeout."""
class BadGachaType(GachaLogException):
    """Base GenshinGachaLog Exception."""
class MissingAuthKey(GachaLogException):
    """No gacha authkey was provided. Not an API error!"""
