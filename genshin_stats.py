"""wrapper for the [https://www.hoyolab.com/genshin/](hoyolab.com) gameRecord api

Majority of the endpoints require a cookie and a ds token, look at README.md for more info.

The wrapper is fairly simple, just save the headers in a session and then request an endpoint.
"""
import sys
from configparser import ConfigParser
from urllib import parse

from requests import HTTPError, Session

config = ConfigParser()
config.read(sys.argv[1] if len(sys.argv)>1 else 'config.ini')

session = Session()
session.headers = {k:v.strip('"') for k,v in config.items('headers')}

def _parse_response(r) -> dict:
    """Parse API response and returns json or raises for error.
    
    Since errors in mohoyo's server are defined by "data":null, they're be detected here.
    """
    r.raise_for_status()
    data = r.json()
    if data['data'] is not None:
        return data['data'] # success
    
    retcode = abs(data['retcode'])
    if retcode   == 401:   tip = "ds key might be old, please renew it, also check if x-rpc headers are present"
    elif retcode == 10001: tip = "missing cookies"
    else: tip = ""
    
    raise HTTPError(f"{retcode} Error ({data['message']}{' | '+tip if tip else ''}) for url: \"{r.url}\"")


def search(keyword: str, size: int=20) -> dict:
    """Searches posts, topics and users.
    
    Takes in a keyword, replaces spaces with + and quotes other characters.
    Can return up to 20 results, based on size.
    """
    url = "https://bbs-api-os.hoyolab.com/community/apihub/wapi/search"
    keyword = parse.quote_plus(keyword)
    r = session.get(url+f'?keyword={keyword}&size={size}&gids=2')
    return _parse_response(r)

def get_community_user_info(uid: int) -> dict:
    """Gets community info of a user based on their uid.
    
    Community info contains general data regarding the uid, nickname, introduction gender and so.
    It also contains stats for general community actions.
    
    Uid in this case is the community id. You can get it with `search`.
    """
    url = "https://bbs-api-os.hoyolab.com/community/user/wapi/getUserFullInfo"
    r = session.get(url+f'?uid={uid}')
    return _parse_response(r)

def get_game_record_card(uid: int) -> list:
    """Gets a game record card of a user based on their uid.
    
    A game record contains data regarding the stats of a user for every server.
    Their UID for a given server is also included.
    In case the user has set their profile to be private, the returned list will be empty.
    
    Uid in this case is the community id. You can get it with `search`.
    """
    url = "https://bbs-api-os.hoyolab.com/game_record/card/wapi/getGameRecordCard"
    r = session.get(url+f'?uid={uid}&gids=2')
    return _parse_response(r)['list']

def get_user_info(uid: int, server: str) -> dict:
    """Gets game user info of a user based on their uid and server.
    
    Game user info contain the main nformation regarding a user.
    Contains owned characters, stats, city and world explorations and role.
    """
    url = "https://bbs-api-os.hoyolab.com/game_record/genshin/api/index"
    r = session.get(url+f'?server={server}&role_id={uid}')
    return _parse_response(r)

def get_spiral_abyss(uid: int, server: str, schedule_type: int=1) -> dict:
    """Gets how far the user has gotten in spiral abyss and their season progress.
    
    Spiral abyss info contains their porgress, stats and individual completes.
    
    Every season these stats refresh and you can get older stats by changing the schedule_type.
    1=current, 2=previous
    """
    url = "https://bbs-api-os.hoyolab.com/game_record/genshin/api/spiralAbyss"
    r = session.get(url+f'?server={server}&role_id={uid}&schedule_type={schedule_type}')
    return _parse_response(r)
