"""Prettifiers for genshinstats api returns.

Fixes the huge problem of outdated field names in the api,
that were leftover from during development
"""
from . import genshinstats as gs
from math import ceil

def prettify_user_info(data: dict):
    """Returns a prettified version of get_user_info."""
    stats = data["stats"]
    return {
        "stats": {
            "achievements": stats["achievement_number"],
            "active_days": stats["active_day_number"],
            "characters": stats["avatar_number"],
            "spiral_abyss": stats["spiral_abyss"],
            "anemoculi": stats["anemoculus_number"],
            "geoculi": stats["geoculus_number"],
            "common_chests": stats["common_chest_number"],
            "exquisite_chests": stats["exquisite_chest_number"],
            "precious_chests": stats["precious_chest_number"],
            "luxurious_chests": stats["luxurious_chest_number"],
            "unlocked_teleports": stats["way_point_number"],
            "unlocked_domains": stats["domain_number"]
        },
        "characters": [{
            "name": i["name"],
            "rarity": i["rarity"],
            "element": i["element"],
            "level": i["level"],
            "friendship": i["fetter"],
            "icon": i["image"],
            "id": i["id"],
        } for i in data["avatars"]],
        "explorations": [{
            "name": i["name"],
            "percentage": round(i["exploration_percentage"]/10, 1),
            "type":i["type"],
            "level":i["level"],
            "icon": i["icon"],
        } for i in data["world_explorations"]]
    }


def prettify_spiral_abyss(data: dict):
    """Returns a prettified version of get_spiral_abyss."""
    fchars = lambda d: [{
        "value": a["value"],
        "name":gs.recognize_character_icon(a["avatar_icon"]),
        "rarity":a["rarity"],
        "icon":a["avatar_icon"],
        "id":a["avatar_id"],
    } for a in d]
    return {
        "season": data["schedule_id"],
        "season_start_time": int(data["start_time"]),
        "season_end_time": int(data["end_time"]),
        "stats": {
            "total_battles": data["total_battle_times"],
            "total_wins": data["total_win_times"],
            "max_floor": data["max_floor"],
            "total_stars": data["total_star"],
        },
        "ranks": {
            "played": fchars(data["reveal_rank"]),
            "defats": fchars(data["defeat_rank"]),
            "damage": fchars(data["damage_rank"]),
            "taken_damage": fchars(data["take_damage_rank"]),
            "bursts": fchars(data["normal_skill_rank"]),
            "skills": fchars(data["energy_skill_rank"]),
        },
        "floors": [{
            "floor": f["index"],
            "stars": f["star"],
            "max_stars": f["max_star"],
            "start": int(f["levels"][0]["battles"][0]["timestamp"]),
            "end": int(f["levels"][-1]["battles"][-1]["timestamp"]),
            "icon": f["icon"],
            "levels":[{
                "chamber": l["index"],
                "stars": l["star"],
                "max_stars": l["max_star"],
                "has_halves":len(l["battles"]) == 2,
                "battles":[{
                    "half": b["index"],
                    "start": int(b["timestamp"]),
                    "characters":[{
                        "name": gs.recognize_character_icon(c["icon"]),
                        "rarity": c["rarity"],
                        "level": c["level"],
                        "icon": c["icon"],
                        "id": c["id"],

                    } for c in b["avatars"]]
                } for b in l["battles"]]
            } for l in f["levels"]]
        } for f in data["floors"]]
    }


def prettify_character(data: dict):
    """Returns a prettified version of a single item from get_characters."""
    weapon = data["weapon"]
    return {
        "name": data["name"],
        "rarity": data["rarity"],
        "element": data["element"],
        "level": data["level"],
        "ascension": ceil(data["level"]//10)-1,
        "friendship": data["fetter"],
        "constellation": sum(c["is_actived"] for c in data["constellations"]),
        "icon": data["image"],
        "id": data["id"],
        "weapon": {
            "name": weapon["name"],
            "rarity": weapon["rarity"],
            "type": weapon["type_name"],
            "level": weapon["level"],
            "ascension": weapon["promote_level"],
            "description": weapon["desc"],
            "refinement": weapon["affix_level"],
            "icon": weapon["icon"],
            "id": weapon["id"],
        },
        "artifacts": [{
            "name": a["name"],
            "position": a["pos_name"],
            "position_index": a["pos"],
            "rarity": a["rarity"],
            "level": a["level"],
            "set": {
                "name": a["set"]["name"],
                "effects": a["set"]["affixes"],
                "id": a["set"]["id"],
            },
            "icon": a["icon"],
            "id": a["id"],
        } for a in data["reliquaries"]],
        "constellations": [{
            "name":c["name"],
            "effect":c["effect"],
            "is_activated":c["is_actived"],
            "index":c["pos"],
            "icon":c["icon"],
            "id":c["id"],
        } for c in data["constellations"]]
    }


def prettify_characters(data: list):
    """Returns a prettified version of get_characters."""
    return [prettify_character(i) for i in data]
