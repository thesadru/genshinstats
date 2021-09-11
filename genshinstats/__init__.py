"""Wrapper for the Genshin Impact's api.

This is an unofficial wrapper for the Genshin Impact gameRecord and wish history api. 
Majority of the endpoints are implemented, documented and typehinted.

All endpoints require to be logged in with either a cookie or an authkey, read the README.md for more info.

https://github.com/thesadru/genshinstats
"""
from .caching import *
from .daily import *
from .errors import *
from .genshinstats import *
from .hoyolab import *
from .map import *
from .transactions import *
from .utils import *
from .wishes import *
