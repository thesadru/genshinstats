"""Genshinstats errors."""
class GenshinStatsException(Exception):
    """Base error for all Genshin Stats Errors."""

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

class InvalidCode(GenshinStatsException):
    """Invalid redemption code."""
class CodeAlreadyUsed(GenshinStatsException):
    """Redemption Code is already in use"""
class TooLowAdventureRank(GenshinStatsException):
    """Does not meet adventure rank requirements."""

class SignInException(GenshinStatsException):
    """Base SignIn Exception."""
class AlreadySignedIn(SignInException):
    """Already signed in dailies"""
class FirstSignIn(SignInException):
    """First sign in must be done manually."""
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
    """No gacha authkey was provided."""
