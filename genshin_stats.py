"""wrapper for the [https://www.hoyolab.com/genshin/](hoyolab.com) gameRecord api

Majority of the endpoints require a cookie and a ds token, look at README.md for more info.

The wrapper is fairly simple, just save the headers in a session and then request an endpoint.
"""
import os
import sys
from configparser import ConfigParser
from typing import TypeVar

from requests import Session
from seleniumwire import webdriver
from selenium.webdriver import FirefoxOptions

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
    
    raise Exception("DS token could not be fetched.")


T = TypeVar('T')
def api_getter(func: T) -> T:
    """Basic wrapper for genshin_stats api functions
    
    Includes error handling and ds token renewal.
    """
    def inside(*args, renew_ds=True, **kwargs):
        url = func(*args,**kwargs)
        
        r = session.get(url)
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
            if config['options'].getboolean('autorenew_ds') and renew_ds:
                config['headers']['ds'] = fetch_ds(config['headers']['cookie'])
                config.save()
                session.headers['ds'] = config['headers']['ds']
                inside(*args,**kwargs,renew_ds=False)
            else:
                raise InvalidDS('Invalid DS token, please renew it.')
        elif retcode == 10001:
            raise MissingCookies('Cookies have not been provided, please add them to the header.')
        elif retcode == 1 and data['message']=='Invalid schedule type':
            raise InvalidScheduleType('Invalid Spiral Abyss schedule type, can only be 1 or 2.')
        else:
            raise GenshinStatsException(f"{retcode} Error ({data['message']}) for url: \"{r.url}\"")
    
    return inside
                
        
@api_getter
def search(keyword: str, size: int=20) -> dict:
    """Searches posts, topics and users.
    
    Takes in a keyword, replaces spaces with + and quotes other characters.
    Can return up to 20 results, based on size.
    """
    url = "https://bbs-api-os.hoyolab.com/community/apihub/wapi/search"
    return url+f'?keyword={keyword}&size={size}&gids=2'

@api_getter
def get_community_user_info(uid: int) -> dict:
    """Gets community info of a user based on their uid.
    
    Community info contains general data regarding the uid, nickname, introduction gender and so.
    It also contains stats for general community actions.
    
    Uid in this case is the community id. You can get it with `search`.
    """
    url = "https://bbs-api-os.hoyolab.com/community/user/wapi/getUserFullInfo"
    return url+f'?uid={uid}'

@api_getter
def get_game_record_card(uid: int) -> list:
    """Gets a game record card of a user based on their uid.
    
    A game record contains data regarding the stats of a user for every server.
    Their UID for a given server is also included.
    In case the user has set their profile to be private, the returned list will be empty.
    
    Uid in this case is the community id. You can get it with `search`.
    """
    url = "https://bbs-api-os.hoyolab.com/game_record/card/wapi/getGameRecordCard"
    return url+f'?uid={uid}&gids=2'

@api_getter
def get_user_info(uid: int, server: str) -> dict:
    """Gets game user info of a user based on their uid and server.
    
    Game user info contain the main nformation regarding a user.
    Contains owned characters, stats, city and world explorations and role.
    """
    url = "https://bbs-api-os.hoyolab.com/game_record/genshin/api/index"
    return url+f'?server={server}&role_id={uid}'

@api_getter
def get_spiral_abyss(uid: int, server: str, schedule_type: int=1) -> dict:
    """Gets how far the user has gotten in spiral abyss and their season progress.
    
    Spiral abyss info contains their porgress, stats and individual completes.
    
    Every season these stats refresh and you can get older stats by changing the schedule_type.
    1=current, 2=previous
    """
    url = "https://bbs-api-os.hoyolab.com/game_record/genshin/api/spiralAbyss"
    return url+f'?server={server}&role_id={uid}&schedule_type={schedule_type}'
