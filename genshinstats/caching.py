"""Install a cache into genshinstats"""
import inspect
import os
import sys
from functools import update_wrapper
from itertools import islice
from typing import Any, Callable, Dict, List, MutableMapping, Tuple, TypeVar

import genshinstats as gs

__all__ = ["permanent_cache", "install_cache", "uninstall_cache"]

C = TypeVar("C", bound=Callable[..., Any])


def permanent_cache(*params: str) -> Callable[[C], C]:
    """Like lru_cache except permanent and only caches based on some parameters"""
    cache: Dict[Any, Any] = {}

    def wrapper(func):
        sig = inspect.signature(func)

        def inner(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            # since the amount of arguments is constant we can just save the values
            key = tuple(v for k, v in bound.arguments.items() if k in params)

            if key in cache:
                return cache[key]
            r = func(*args, **kwargs)
            if r is not None:
                cache[key] = r
            return r

        inner.cache = cache
        return update_wrapper(inner, func)

    return wrapper  # type: ignore


def cache_func(func: C, cache: MutableMapping[Tuple[Any, ...], Any]) -> C:
    """Caches a normal function"""
    # prevent possible repeated cachings
    if hasattr(func, "__cache__"):
        return func

    sig = inspect.signature(func)

    def wrapper(*args, **kwargs):
        # create key (func name, *arguments)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        key = tuple(v for k, v in bound.arguments.items() if k != "cookie")
        key = (func.__name__,) + key

        if key in cache:
            return cache[key]

        r = func(*args, **kwargs)
        if r is not None:
            cache[key] = r
        return r

    setattr(wrapper, "__cache__", cache)
    setattr(wrapper, "__original__", func)
    return update_wrapper(wrapper, func)  # type: ignore


def cache_paginator(func: C, cache: MutableMapping[Tuple[Any, ...], Any], strict: bool = False) -> C:
    """Caches an id generator such as wish history

    Respects size and authkey.
    If strict mode is on then the first item of the paginator will no longer be requested every time.
    """
    if hasattr(func, "__cache__"):
        return func

    sig = inspect.signature(func)

    def wrapper(*args, **kwargs):
        # create key (func name, end id, *arguments)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        arguments = bound.arguments

        # remove arguments that might cause problems
        size, authkey, end_id = [arguments.pop(k) for k in ("size", "authkey", "end_id")]
        partial_key = tuple(arguments.values())

        # special recursive case must be ignored
        # otherwise an infinite recursion due to end_id resets will occur
        if "banner_type" in arguments and arguments["banner_type"] is None:
            return func(*args, **kwargs)

        def make_key(end_id: int) -> Tuple[Any, ...]:
            return (func.__name__,end_id,) + partial_key

        def helper(end_id: int):
            while True:
                # yield new items from the cache
                key = make_key(end_id)
                while key in cache:
                    yield cache[key]
                    end_id = cache[key]["id"]
                    key = make_key(end_id)

                # look ahead and add new items to the cache
                # since the size limit is always 20 we use that to make only a single request
                new = list(func(size=20, authkey=authkey, end_id=end_id, **arguments))
                if not new:
                    break
                # the head may not want to be cached so it must be handled separately
                if end_id != 0 or strict:
                    cache[make_key(end_id)] = new[0]
                if end_id == 0:
                    yield new[0]
                    end_id = new[0]["id"]

                for p, n in zip(new, new[1:]):
                    cache[make_key(p["id"])] = n

        return islice(helper(end_id), size)

    setattr(wrapper, "__cache__", cache)
    setattr(wrapper, "__original__", func)
    return update_wrapper(wrapper, func)  # type: ignore


def install_cache(cache: MutableMapping[Tuple[Any, ...], Any], strict: bool = False) -> None:
    """Installs a cache into every cacheable function in genshinstats

    If strict mode is on then the first item of the paginator will no longer be requested every time.
    That can however cause a variety of problems and it's therefore recommend to use it only with TTL caches.

    Please do note that hundreds of accesses may be made per call so your cache shouldn't be doing heavy computations during accesses.
    """
    functions: List[Callable] = [
        # genshinstats
        gs.get_user_stats,
        gs.get_characters,
        gs.get_spiral_abyss,
        # wishes
        gs.get_banner_details,
        gs.get_gacha_items,
        # hoyolab
        gs.search,
        gs.get_record_card,
        gs.get_recommended_users,
    ]
    paginators: List[Callable] = [
        # wishes
        gs.get_wish_history,
        # transactions
        gs.get_artifact_log,
        gs.get_crystal_log,
        gs.get_primogem_log,
        gs.get_resin_log,
        gs.get_weapon_log,
    ]
    invalid: List[Callable] = [
        # normal generator
        gs.get_claimed_rewards,
        # cookie dependent
        gs.get_daily_reward_info,
        gs.get_game_accounts,
    ]

    wrapped = []
    for func in functions:
        wrapped.append(cache_func(func, cache))
    for func in paginators:
        wrapped.append(cache_paginator(func, cache, strict=strict))

    for func in wrapped:
        # ensure we only replace actual functions from the genshinstats directory
        for module in sys.modules.values():
            if not hasattr(module, func.__name__):
                continue
            orig_func = getattr(module, func.__name__)
            if (
                os.path.split(orig_func.__globals__["__file__"])[0]
                != os.path.split(func.__globals__["__file__"])[0]  # type: ignore
            ):
                continue

            setattr(module, func.__name__, func)


def uninstall_cache() -> None:
    """Uninstalls the cache from all functions"""
    modules = sys.modules.copy()
    for module in modules.values():
        try:
            members = inspect.getmembers(module)
        except ModuleNotFoundError:
            continue

        for name, func in members:
            if hasattr(func, "__cache__"):
                setattr(module, name, getattr(func, "__original__", func))
