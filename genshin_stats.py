"""wrapper for the hoyolab.com gameRecord api

Majority of the endpoints require a cookie and a ds token, look at README.md for more info.

The wrapper is fairly simple, just save the headers in a session and then request an endpoint.
All functions are decorated with an `endpoint` wrapper. This wrapper simply formats a given url.
This is to avoid having to type something multiple times while still keeping docstrings and annotations.
"""
import os
import sys
from configparser import ConfigParser
from inspect import getcallargs
from typing import Callable, TypeVar

from requests import Session
from selenium.webdriver import FirefoxOptions
from seleniumwire import webdriver


class GenshinStatsException(Exception):
    """Base error for all Genshin Stats Errors."""
class InvalidDS(GenshinStatsException):
    """Invalid DS token, should be renewed."""
class MissingCookies(GenshinStatsException):
    """Cookies have not been provided."""
class InvalidScheduleType(GenshinStatsException):
    """Invalid Spiral Abyss schedule"""

config = ConfigParser()
config.file = sys.argv[1] if len(sys.argv)>1 else 'config.ini'
config.read(config.file)
config.save = lambda: config.write(open(config.file,'w'),False)
autorenew_ds = config['options'].getboolean('autorenew_ds')

session = Session()
session.headers = {k:v.strip('"') for k,v in config.items('headers')}

browser_url = 'https://www.hoyolab.com/genshin/accountCenter/gameRecord?id={}'
important_ajax = "https://bbs-api-os.hoyolab.com/game_record/card/wapi/getGameRecordCard"
def fetch_ds(raw_cookie: str) -> str:
    """Fetches a new ds token.
    
    Uses a webscraping approach by opening the site with seleniumwire.
    """
    cookie = dict(c.split('=') for c in raw_cookie.split('; '))
    
    opts = FirefoxOptions()
    opts.headless = True
    driver = webdriver.Firefox(options=opts, service_log_path=os.path.devnull)
    
    driver.get(browser_url.format(cookie['account_id']))
    for name,value in cookie.items():
        driver.add_cookie({'name':name,'value':value,'domain':'.hoyolab.com'})

    driver.wait_for_request(important_ajax) # wait for the response

    for request in reversed(driver.requests):
        if request.response and request.url.startswith(important_ajax):
            return request.headers['ds']
    
    raise GenshinStatsException("DS token could not be fetched.")


C = TypeVar('C',bound=Callable)
def endpoint(url: str=''):
    """Basic wrapper for genshin_stats api functions
    
    Includes error handling and ds token renewal.
    """
    def wrapper(func: C) -> C:
        """internal wrapper"""
        def inside(*args, renew_ds=True, **kwargs):
            kwargs = getcallargs(func,*args,**kwargs)
            
            r = session.get(url.format(**kwargs))
            r.raise_for_status()
            
            data = r.json()
            if data['data'] is not None: # success
                data = data['data']
                if 'list' in data and len(data)==1:
                    return data['list']
                else:
                    return data
            
            retcode = abs(data['retcode'])
            if retcode == 401: # old ds token
                if autorenew_ds and renew_ds:
                    config['headers']['ds'] = fetch_ds(config['headers']['cookie'])
                    config.save()
                    session.headers['ds'] = config['headers']['ds']
                    inside(**kwargs,renew_ds=False)
                else:
                    raise InvalidDS('Invalid DS token, please renew it.')
            elif retcode == 10001:
                raise MissingCookies('Cookies have not been provided, please add them to the header.')
            elif retcode == 1 and data['message']=='Invalid schedule type':
                raise InvalidScheduleType('Invalid Spiral Abyss schedule type, can only be 1 or 2.')
            else:
                raise GenshinStatsException(f"{retcode} Error ({data['message']}) for url: \"{r.url}\"")
        
        return inside
    return wrapper
        
@endpoint("https://bbs-api-os.hoyolab.com/community/apihub/wapi/search?keyword={keyword}&size={size}&gids=2")
def search(keyword: str, size: int=20) -> dict:
    """Searches posts, topics and users.
    
    Takes in a keyword, replaces spaces with + and quotes other characters.
    Can return up to 20 results, based on size.
    """

@endpoint("https://bbs-api-os.hoyolab.com/community/user/wapi/getUserFullInfo?uid={uid}")
def get_community_user_info(uid: int) -> dict:
    """Gets community info of a user based on their uid.
    
    Community info contains general data regarding the uid, nickname, introduction gender and so.
    It also contains stats for general community actions.
    
    Uid in this case is the community id. You can get it with `search`.
    """

@endpoint("https://bbs-api-os.hoyolab.com/game_record/card/wapi/getGameRecordCard?uid={uid}&gids=2")
def get_game_record_card(uid: int) -> list:
    """Gets a game record card of a user based on their uid.
    
    A game record contains data regarding the stats of a user for every server.
    Their UID for a given server is also included.
    In case the user has set their profile to be private, the returned list will be empty.
    
    Uid in this case is the community id. You can get it with `search`.
    """

@endpoint("https://bbs-api-os.hoyolab.com/game_record/genshin/api/index?server={server}&role_id={uid}")
def get_user_info(uid: int, server: str) -> dict:
    """Gets game user info of a user based on their uid and server.
    
    Game user info contain the main nformation regarding a user.
    Contains owned characters, stats, city and world explorations and role.
    """

@endpoint("https://bbs-api-os.hoyolab.com/game_record/genshin/api/spiralAbyss?server={server}&role_id={uid}&schedule_type={schedule_type}")
def get_spiral_abyss(uid: int, server: str, schedule_type: int=1) -> dict:
    """Gets how far the user has gotten in spiral abyss and their season progress.
    
    Spiral abyss info contains their porgress, stats and individual completes.
    
    Every season these stats refresh and you can get older stats by changing the schedule_type.
    1=current, 2=previous
    """
