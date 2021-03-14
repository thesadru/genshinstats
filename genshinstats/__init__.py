"""Wrapper for the Genshin Impact's api.

This is an unofficial wrapper for the Genshin Impact's api. 
Majority of the endpoints are implemented, documented and typehinted.

Majority of the endpoints require a cookie and a ds token, look at README.md for more info.
(Some functions may have a raw parameter, this prettifies the output to a readable version.)

https://github.com/thesadru/genshinstats
"""
from .errors import *
from .gachalog import *
from .genshinstats import *
from .hoyolab import *
from .signin import *