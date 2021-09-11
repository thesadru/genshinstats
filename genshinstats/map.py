"""The official genshin map

Gets data from the official genshin map such as categories, points and similar.
"""
import json
from typing import Any, Dict, List
from urllib.parse import urljoin

from .caching import permanent_cache
from .genshinstats import fetch_endpoint

OS_MAP_URL = "https://api-os-takumi-static.mihoyo.com/common/map_user/ys_obc/v1/map/"

__all__ = [
    "fetch_map_endpoint",
    "get_map_image",
    "get_map_icons",
    "get_map_labels",
    "get_map_locations",
    "get_map_points",
    "get_map_tile",
]


def fetch_map_endpoint(endpoint: str, **kwargs) -> Dict[str, Any]:
    """Fetch an enpoint from mihoyo's webstatic map api.

    Only currently liyue is supported.

    Takes in an endpoint url which is joined with the base url.
    A request is then sent and returns a parsed response.
    """
    kwargs.setdefault("params", {}).update({"map_id": 2, "app_sn": "ys_obc", "lang": "en-us"})
    url = urljoin(OS_MAP_URL, endpoint)
    return fetch_endpoint(url, cookie={}, **kwargs)


@permanent_cache()
def get_map_image() -> str:
    """Get the url to the entire map image"""
    data = fetch_map_endpoint("info")["info"]["detail"]
    return json.loads(data)["slices"][0][0]["url"]

@permanent_cache()
def get_map_icons() -> Dict[int, str]:
    """Get all icons for the map"""
    data = fetch_map_endpoint("spot_kind/get_icon_list")["icons"]
    return {i["id"]: i["url"] for i in data}

@permanent_cache()
def get_map_labels() -> List[Dict[str, Any]]:
    """Get labels and label categories"""
    return fetch_map_endpoint("label/tree")["tree"]

def get_map_locations() -> List[Dict[str, Any]]:
    """Get all locations on the map"""
    return fetch_map_endpoint("map_anchor/list")["list"]

def get_map_points() -> List[Dict[str, Any]]:
    """Get points on the map"""
    return fetch_map_endpoint("point/list")["point_list"]

def get_map_tile(x: int, y: int, width: int, height: int, resolution: int = 1, image: str = None) -> str:
    """Gets a map tile at a position

    You may set an x, y, width and height of the resulting image
    however you shoudl prefer to use multiples of 256 because they are cached
    on the mihoyo servers.

    Resolution dictates the resolution of the image as a percentage. 100 is highest and 0 is lowest.
    You should pick values from 100, 50, 25 and 12.5
    """
    image = image or get_map_image()
    return image + f"?x-oss-process=image/resize,p_{round(resolution)}/crop,x_{x},y_{y},w_{width},h_{height}"
