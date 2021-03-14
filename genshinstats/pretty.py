"""Prettifiers for genshinstats api returns.

Fixes the huge problem of outdated field names in the api,
that were leftover from during development
"""
import re
from math import ceil


def _recognize_character_icon(url: str):
    """Recognizes a character's icon url and returns its name."""
    exp = r'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_(?:.*)_(\w+)(?:@2x|@3x)?.png'
    match = re.fullmatch(exp,url)
    if match is None:
        return None
    character = match.group(1)
    if character.startswith("Player"):
        return "Traveler"
    elif character.startswith("Qin"):
        return "Jean"
    
    return character


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
        "name":_recognize_character_icon(a["avatar_icon"]),
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
        "character_ranks": {
            "most_chambers_won": fchars(data["reveal_rank"]),
            "most_chambers_lost": fchars(data["defeat_rank"]),
            "strongest_hit": fchars(data["damage_rank"]),
            "most_damage_taken": fchars(data["take_damage_rank"]),
            "most_bursts_used": fchars(data["normal_skill_rank"]),
            "most_skills_used": fchars(data["energy_skill_rank"]),
        },
        "floors": [{
            "floor": f["index"],
            "stars": f["star"],
            "max_stars": f["max_star"],
            "start": int(f["levels"][0]["battles"][0]["timestamp"]),
            "icon": f["icon"],
            "chambers":[{
                "chamber": l["index"],
                "stars": l["star"],
                "max_stars": l["max_star"],
                "has_halves":len(l["battles"]) == 2,
                "battles":[{
                    "half": b["index"],
                    "timestamp": int(b["timestamp"]),
                    "characters":[{
                        "name": _recognize_character_icon(c["icon"]),
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
        "alt_name":{
            "Traveler":"Aether" if "Boy" in data["icon"] else "Lumine",
            "Venti":"Barbatos",
            "Zhongli":"Morax",
            "Fischl":"Amy",
            "Albedo":"Kreideprinz",
            "Tartaglia":"Childe",
        }.get(data["name"],None),
        "rarity": data["rarity"],
        "element": data["element"] if data["name"]!="Traveler" else {
            71:"Anemo",
            91:"Geo"
        }[data["constellations"][0]["id"]], # traveler elements
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
            "refinement": weapon["affix_level"],
            "description": weapon["desc"],
            "icon": weapon["icon"],
            "id": weapon["id"],
        },
        "artifacts": [{
            "name": a["name"],
            "pos_name": {
                1:"flower",
                2:"feather",
                3:"hourglass",
                4:"goblet",
                5:"crown",
            }[a["pos"]],
            "full_pos_name": a["pos_name"],
            "pos": a["pos"],
            "rarity": a["rarity"],
            "level": a["level"],
            "set": {
                "name": a["set"]["name"],
                "effect_type": ['none','single','classic'][len(a["set"]["affixes"])],
                "effects": [{
                    "pieces":e["activation_number"],
                    "effect":e["effect"],
                } for e in a["set"]["affixes"]],
                "set_id": int(re.search(r'UI_RelicIcon_(\d+)_\d',a["icon"]).group(1)),
                "id": a["set"]["id"]
            },
            "icon": a["icon"],
            "id": a["id"],
        } for a in data["reliquaries"]],
        "constellations": [{
            "name": c["name"],
            "effect": c["effect"].replace('\\n','\n'),
            "is_activated": c["is_actived"],
            "index": c["pos"],
            "icon": c["icon"],
            "id": c["id"],
        } for c in data["constellations"]]
    }

def prettify_characters(data: list):
    """Returns a prettified version of get_characters."""
    return [prettify_character(i) for i in data]

def prettify_gacha_log(data: list):
    return [{
        "type": i["item_type"],
        "name": i["name"],
        "rarity": int(i["rank_type"]),
        "time": i["time"],
    } for i in data]

def prettify_gacha_items(data: list):
    return {
        "characters": [{
            "name": i["name"],
            "rarity": int(i["rank_type"]),
            "id": 10000000+int(i["item_id"])-1000,
        } for i in data if i["item_type"]=="Character"],
        "weapons": [{
            "name": i["name"],
            "rarity": int(i["rank_type"]),
            "id": int(i["item_id"]),
        } for i in data if i["item_type"]=="Weapon"],
    }

def prettify_gacha_details(data: dict):
    fprobs = lambda l: [{
        "type": i["item_type"],
        "name": i["item_name"],
        "rarity": int(i["rank"]),
        "is_up": i["is_up"],
        "order_index": i["order_value"],
    } for i in l]
    fitems = lambda l: [{
        "type": i["item_type"],
        "name": i["item_name"],
        "element": {
            "風":"Anemo",
            "火":"Pyro",
            "水":"Hydro",
            "雷":"Electro",
            "冰":"Cryo",
            "山":"Geo",
            "？":"Dendro",
            "":""
        }[i["item_attr"]],
        "icon": i["item_img"],
    } for i in l]
    return {
        "gacha_type": {
            "100":"Novice Wishes",
            "200":"Permanent Wish",
            "301":"Character Event Wish",
            "302":"Weapon Event Wish"
        }[data["gacha_type"]],
        "banner": re.split(r'["«»]',re.sub(r'<.*?>','',data["title"]))[1].strip(),
        "title": data["title"],
        "content": data["content"],
        "permanent": data["date_range"]=="Permanent",
        "r5_up_prob": data["r5_up_prob"],
        "r4_up_prob": data["r4_up_prob"],
        "r5_prob": data["r5_prob"],
        "r4_prob": data["r4_prob"],
        "r3_prob": data["r3_prob"],
        "r5_pity_prob": data["r5_baodi_prob"],
        "r4_pity_prob": data["r4_baodi_prob"],
        "r3_pity_prob": data["r3_baodi_prob"],
        "r5_up_items": fitems(data["r5_up_items"]),
        "r4_up_items": fitems(data["r4_up_items"]),
        "r5_prob_list": fprobs(data["r5_prob_list"]),
        "r4_prob_list": fprobs(data["r4_prob_list"]),
        "r3_prob_list": fprobs(data["r3_prob_list"]),
    }
