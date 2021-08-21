"""Logs for currency "transactions".

Logs for artifact, weapon, resin, genesis crystol and primogem "transactions".
You may view a history of everything you have gained in the last 3 months.
"""
import math
import sys
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import urljoin

from .caching import permanent_cache
from .pretty import prettify_trans
from .wishes import fetch_gacha_endpoint, static_session

__all__ = [
    "fetch_transaction_endpoint",
    "get_primogem_log",
    "get_resin_log",
    "get_crystal_log",
    "get_artifact_log",
    "get_weapon_log",
    "current_resin",
    "approximate_current_resin",
]

YSULOG_URL = "https://hk4e-api-os.mihoyo.com/ysulog/api/"


def fetch_transaction_endpoint(endpoint: str, authkey: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Fetch an enpoint from mihoyo's transaction logs api.

    Takes in an endpoint url which is joined with the base url.
    If an authkey is provided, it uses that authkey specifically.
    A request is then sent and returns a parsed response.
    """
    url = urljoin(YSULOG_URL, endpoint)
    return fetch_gacha_endpoint(url, authkey, **kwargs)


@permanent_cache('lang')
def _get_reasons(lang: str = 'en-us') -> Dict[int, str]:
    r = static_session.get(
        f"https://mi18n-os.mihoyo.com/webstatic/admin/mi18n/hk4e_global/m02251421001311/m02251421001311-{lang}.json"
    )
    r.raise_for_status()
    data = r.json()

    return {int(k.split("_")[-1]): v for k, v in data.items() if k.startswith("selfinquiry_general_reason_")}


def _get_transactions(
    endpoint: str, size: int = None, authkey: str = None, lang: str = 'en-us', end_id: int = 0
) -> Iterator[Dict[str, Any]]:
    """A paginator that uses mihoyo's id paginator algorithm to yield pages"""
    if size is not None and size <= 0:
        return

    page_size = 20
    size = size or sys.maxsize

    while True:
        data = fetch_transaction_endpoint(
            endpoint, 
            authkey=authkey, 
            params=dict(size=min(page_size, size), end_id=end_id)
        )["list"]
        data = prettify_trans(data, _get_reasons(lang))
        yield from data

        size -= page_size
        if len(data) < page_size or size <= 0:
            break

        end_id = data[-1]["id"]


def get_primogem_log(size: int = None, authkey: str = None, lang: str = 'en-us', end_id: int = 0) -> Iterator[Dict[str, Any]]:
    """Gets all transactions of primogems

    This means stuff like getting primogems from rewards and explorations or making wishes.
    Records go only 3 months back.
    """
    return _get_transactions("getPrimogemLog", size, authkey, lang, end_id)

def get_crystal_log(size: int = None, authkey: str = None, lang: str = 'en-us', end_id: int = 0) -> Iterator[Dict[str, Any]]:
    """Get all transactions of genesis crystals

    Records go only 3 months back.
    """
    return _get_transactions("getCrystalLog", size, authkey, lang, end_id)

def get_resin_log(size: int = None, authkey: str = None, lang: str = 'en-us', end_id: int = 0) -> Iterator[Dict[str, Any]]:
    """Gets all usage of resin

    This means using them in ley lines, domains, crafting and weekly bosses.
    Records go only 3 months back.
    """
    return _get_transactions("getResinLog", size, authkey, lang, end_id)

def get_artifact_log(size: int = None, authkey: str = None, lang: str = 'en-us', end_id: int = 0) -> Iterator[Dict[str, Any]]:
    """Get the log of all artifacts gotten or destroyed in the last 3 months"""
    return _get_transactions("getArtifactLog", size, authkey, lang, end_id)


def get_weapon_log(size: int = None, authkey: str = None, lang: str = 'en-us', end_id: int = 0) -> Iterator[Dict[str, Any]]:
    """Get the log of all weapons gotten or destroyed in the last 3 months"""
    return _get_transactions("getWeaponLog", size, authkey, lang, end_id)


def current_resin(last_resin_time: datetime, last_resin_amount: float, current_time: datetime = None, authkey: str = None):
    """Gets the current resin based off an amount of resin you've had at any time before
    
    Works by getting all usages after the last resin time and emulating how the resin would be generated.
    Keep in mind that this approach works only if the user hasn't played in the last hour.
    """
    current_time = current_time or datetime.utcnow()
    
    resin_usage: List[Dict[str, Any]] = [{"time": str(current_time), "amount": 0}]
    for usage in get_resin_log(authkey=authkey):
        if datetime.fromisoformat(usage['time']) < last_resin_time:
            break
        resin_usage.append(usage)
    resin_usage.reverse()
    
    resin = last_resin_amount
    
    for usage in resin_usage:
        usage_time = datetime.fromisoformat(usage['time'])
        recovered_resin = (usage_time - last_resin_time).total_seconds() / (8 * 60)
        
        resin = min(resin + recovered_resin, 160) + usage['amount']
        
        last_resin_time = usage_time
        # better raise an error than to leave users confused
        if resin < 0:
            raise ValueError("Last resin time is wrong or amount is too low")
    
    return resin

def approximate_current_resin(time: datetime = None, authkey: str = None):
    """Roughly approximates how much resin using a minmax calculation
    
    The result can have an offset of around 5 resin in some cases.
    """
    # if any algorithm peeps can help with this one I'd appreciate it
    recovery_rate = 8 * 60
    
    current_max = shadow_max = 160.0
    current_min = shadow_min = 0.0
    time = time or datetime.utcnow()
    last_amount = 0

    for usage in get_resin_log(authkey=authkey):
        usage_time = datetime.fromisoformat(usage["time"])
        if time < usage_time:
            continue
        amount_recovered = (time - usage_time).total_seconds() / recovery_rate
        cur_amount: int = usage["amount"]
        shadow_max += cur_amount + amount_recovered
        shadow_min += last_amount + amount_recovered
        current_max = max(current_min, min(current_max, shadow_max))
        current_min = max(current_min, min(current_max, shadow_min))
        time = usage_time
        last_amount = usage["amount"]
        if math.isclose(current_max, current_min):
            break
    
    resin = (current_max + current_min) / 2
    
    return resin
