"""Prettifiers for genshinstats api returns.

Fixes the huge problem of outdated field names in the api,
that were leftover from during development
"""
import re
from datetime import datetime

character_icons = {
    "PlayerGirl": "Traveler",
    "PlayerBoy": "Traveler",
    "Ambor": "Amber",
    "Qin": "Jean",
    "Hutao": "Hu Tao",
    "Feiyan": "Yanfei",
    "Kazuha": "Kadehara Kazuha",
    "Sara": "Kujou Sara",
    "Shougun": "Raiden Shogun",
}

def _recognize_character_icon(url: str) -> str: 
    """Recognizes a character's icon url and returns its name."""
    exp = r'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_.*_(\w+)(?:@\dx)?.png'
    match = re.fullmatch(exp,url)
    if match is None: 
        raise ValueError(f"{url!r} is not a character icon or image url")
    character = match.group(1)
    return character_icons.get(character) or character


def prettify_stats(data):
    s = data["stats"]
    h = data["homes"][0] if data["homes"] else None
    return {
        "stats": {
            "achievements": s["achievement_number"],
            "active_days": s["active_day_number"],
            "characters": s["avatar_number"],
            "spiral_abyss": s["spiral_abyss"],
            "anemoculi": s["anemoculus_number"],
            "geoculi": s["geoculus_number"],
            "electroculi": s["electroculus_number"],
            "common_chests": s["common_chest_number"],
            "exquisite_chests": s["exquisite_chest_number"],
            "precious_chests": s["precious_chest_number"],
            "luxurious_chests": s["luxurious_chest_number"],
            "unlocked_waypoints": s["way_point_number"],
            "unlocked_domains": s["domain_number"]
        },
        "characters": [{
            "name": i["name"],
            "rarity": i["rarity"] if i["rarity"] < 100 else i["rarity"] - 100, # aloy has 105 stars
            "element": i["element"],
            "level": i["level"],
            "friendship": i["fetter"],
            "icon": i["image"],
            "id": i["id"],
        } for i in data["avatars"]],
        "teapot": {
            # only unique data between realms are names and icons
            "realms": [{
                "name": s["name"],
                "icon": s["icon"]
            } for s in data["homes"]],
            "level": h["level"],
            "comfort": h["comfort_num"],
            "comfort_name": h["comfort_level_name"],
            "comfort_icon": h["comfort_level_icon"],
            "items": h["item_num"],
            "visitors": h["visit_num"] # currently not in use
        } if h else None,
        "explorations": [{
            "name": i["name"],
            "explored": round(i["exploration_percentage"]/10, 1),
            "type": i["type"],
            "level": i["level"],
            "icon": i["icon"],
            "offerings": i["offerings"],
        } for i in data["world_explorations"]]
    }

def prettify_characters(data):
    return [{
        "name": i["name"],
        "rarity": i["rarity"] if i["rarity"] < 100 else i["rarity"] - 100, # aloy has 105 stars
        "element": i["element"],
        "level": i["level"],
        "friendship": i["fetter"],
        "constellation": sum(c["is_actived"] for c in i["constellations"]),
        "icon": i["icon"],
        "image": i["image"],
        "id": i["id"],
        "collab": i["rarity"] >= 100,
        **({"traveler_name": "Aether" if "Boy" in i["icon"] else "Lumine"} if "Player" in i["icon"] else {}),
        "weapon": {
            "name": i["weapon"]["name"],
            "rarity": i["weapon"]["rarity"],
            "type": i["weapon"]["type_name"],
            "level": i["weapon"]["level"],
            "ascension": i["weapon"]["promote_level"],
            "refinement": i["weapon"]["affix_level"],
            "description": i["weapon"]["desc"],
            "icon": i["weapon"]["icon"],
            "id": i["weapon"]["id"],
        },
        "artifacts": [{
            "name": a["name"],
            "pos_name": {
                1: "flower",
                2: "feather",
                3: "hourglass",
                4: "goblet",
                5: "crown",
            }[a["pos"]],
            "full_pos_name": a["pos_name"],
            "pos": a["pos"],
            "rarity": a["rarity"],
            "level": a["level"],
            "set": {
                "name": a["set"]["name"],
                "effect_type": ['none','single','classic'][len(a["set"]["affixes"])],
                "effects": [{
                    "pieces": e["activation_number"],
                    "effect": e["effect"],
                } for e in a["set"]["affixes"]],
                "set_id": int(re.search(r'UI_RelicIcon_(\d+)_\d+',a["icon"]).group(1)), # type: ignore
                "id": a["set"]["id"]
            },
            "icon": a["icon"],
            "id": a["id"],
        } for a in i["reliquaries"]],
        "constellations": [{
            "name": c["name"],
            "effect": c["effect"],
            "is_activated": c["is_actived"],
            "index": c["pos"],
            "icon": c["icon"],
            "id": c["id"],
        } for c in i["constellations"]],
        "outfits": [{
            "name": c["name"],
            "icon": c["icon"],
            "id": c["id"]
        } for c in i["costumes"]],
    } for i in data]

def prettify_abyss(data):
    fchars = lambda d: [{
        "value": a["value"],
        "name": _recognize_character_icon(a["avatar_icon"]),
        "rarity": a["rarity"] if a["rarity"] < 100 else a["rarity"] - 100, # aloy has 105 stars
        "icon": a["avatar_icon"],
        "id": a["avatar_id"],
    } for a in d]
    todate = lambda x: datetime.fromtimestamp(int(x)).strftime("%Y-%m-%d")
    totime = lambda x: datetime.fromtimestamp(int(x)).isoformat(' ')
    return {
        "season": data["schedule_id"],
        "season_start_time": todate(data["start_time"]),
        "season_end_time": todate(data["end_time"]),
        "stats": {
            "total_battles": data["total_battle_times"],
            "total_wins": data["total_win_times"],
            "max_floor": data["max_floor"],
            "total_stars": data["total_star"],
        },
        "character_ranks": {
            "most_played": fchars(data["reveal_rank"]),
            "most_kills": fchars(data["defeat_rank"]),
            "strongest_strike": fchars(data["damage_rank"]),
            "most_damage_taken": fchars(data["take_damage_rank"]),
            "most_bursts_used": fchars(data["normal_skill_rank"]),
            "most_skills_used": fchars(data["energy_skill_rank"]),
        },
        "floors": [{
            "floor": f["index"],
            "stars": f["star"],
            "max_stars": f["max_star"],
            "start": totime(f["levels"][0]["battles"][0]["timestamp"]),
            "icon": f["icon"],
            "chambers": [{
                "chamber": l["index"],
                "stars": l["star"],
                "max_stars": l["max_star"],
                "has_halves": len(l["battles"]) == 2,
                "battles": [{
                    "half": b["index"],
                    "timestamp": totime(b["timestamp"]),
                    "characters": [{
                        "name": _recognize_character_icon(c["icon"]),
                        "rarity": c["rarity"] if c["rarity"] < 100 else c["rarity"] - 100, # aloy has 105 stars
                        "level": c["level"],
                        "icon": c["icon"],
                        "id": c["id"],

                    } for c in b["avatars"]]
                } for b in l["battles"]]
            } for l in f["levels"]]
        } for f in data["floors"]]
    }

def prettify_activities(data):
    activities = data['activities'][0]
    return {
        'hyakunin': [{
            "id": r['challenge_id'],
            "name": r['challenge_name'],
            "difficulty": r["difficulty"],
            "medal_icon": r["heraldry_icon"],
            "score": r["max_score"],
            "multiplier": r["score_multiple"],
            "lineups": [{
                "characters": [{
                    "name": _recognize_character_icon(c["icon"]),
                    "rarity": c["rarity"] if c["rarity"] < 100 else c["rarity"] - 100, # aloy has 105 stars
                    "level": c["level"],
                    "icon": c["icon"],
                    "id": c["id"],
                    "trial": c["is_trail_avatar"],
                } for c in l["avatars"]],
                "skills": [{
                    "name": s["name"],
                    "desc": s["desc"],
                    "icon": s["icon"],
                    "id": s["id"]
                } for s in l["skills"]]
            } for l in r["lineups"]]
        } for r in activities['sumo']['records']]
    }

def prettify_game_accounts(data):
    return [{
        "uid": int(a["game_uid"]),
        "server": a["region_name"],
        "level": a["level"],
        "nickname": a["nickname"],
        # idk what these are for:
        "biz": a["game_biz"],
        "is_chosen": a["is_chosen"], 
        "is_official": a["is_official"],
    } for a in data]

def prettify_wish_history(data, banner_name = None):
    return [{
        "type": i["item_type"],
        "name": i["name"],
        "rarity": int(i["rank_type"]),
        "time": i["time"],
        "id": int(i["id"]),
        "banner": banner_name,
        "banner_type": int(i["gacha_type"]),
        "uid": int(i["uid"]),
    } for i in data]

def prettify_gacha_items(data):
    return [{
        "name": i["name"],
        "type": i["item_type"],
        "rarity": int(i["rank_type"]),
        "id": 10000000+int(i["item_id"])-1000 if len(i["item_id"])==4 else int(i["item_id"]),
    } for i in data]

def prettify_banner_details(data):
    per = lambda p: None if p=='0%' else float(p[: -1].replace(',','.'))
    fprobs = lambda l: [{
        "type": i["item_type"],
        "name": i["item_name"],
        "rarity": int(i["rank"]),
        "is_up": bool(i["is_up"]),
        "order_value": i["order_value"],
    } for i in l] if l else []
    fitems = lambda l: [{
        "type": i["item_type"],
        "name": i["item_name"],
        "element": {
            "风": "Anemo",
            "火": "Pyro",
            "水": "Hydro",
            "雷": "Electro",
            "冰": "Cryo",
            "岩": "Geo",
            "？": "Dendro",
            "": None
        }[i["item_attr"]],
        "icon": i["item_img"],
    } for i in l] if l else []
    return {
        "banner_type_name": {
            100: "Novice Wishes",
            200: "Permanent Wish",
            301: "Character Event Wish",
            302: "Weapon Event Wish"
        }[int(data["gacha_type"])],
        "banner_type": int(data["gacha_type"]),
        "banner": re.sub(r'<.*?>','',data["title"]).strip(),
        "title": data["title"],
        "content": data["content"],
        "date_range": data["date_range"],
        "r5_up_prob": per(data["r5_up_prob"]), # probability for rate-up 5*
        "r4_up_prob": per(data["r4_up_prob"]), # probability for rate-up 4*
        "r5_prob": per(data["r5_prob"]), # probability for 5*
        "r4_prob": per(data["r4_prob"]), # probability for 4*
        "r3_prob": per(data["r3_prob"]), # probability for 3*
        "r5_guarantee_prob": per(data["r5_baodi_prob"]), # probability for 5* incl. guarantee
        "r4_guarantee_prob": per(data["r4_baodi_prob"]), # probability for 4* incl. guarantee
        "r3_guarantee_prob": per(data["r3_baodi_prob"]), # probability for 3* incl. guarantee
        "r5_up_items": fitems(data["r5_up_items"]), # list of 5* rate-up items that you can get from banner
        "r4_up_items": fitems(data["r4_up_items"]), # list of 4* rate-up items that you can get from banner
        "r5_items": fprobs(data["r5_prob_list"]), # list 5* of items that you can get from banner
        "r4_items": fprobs(data["r4_prob_list"]), # list 4* of items that you can get from banner
        "r3_items": fprobs(data["r3_prob_list"]), # list 3* of items that you can get from banner
        "items": fprobs(sorted(
            data["r5_prob_list"]+data["r4_prob_list"]+data["r3_prob_list"],
            key=lambda x: x["order_value"]))
    }

def prettify_trans(data, reasons={}):
    if data and "name" in data[0]:
        # transaction item
        return [{
            "time": i["time"],
            "name": i["name"],
            "rarity": int(i["rank"]),
            "amount": int(i["add_num"]),
            "reason": reasons.get(int(i["reason"]), ""),
            "reason_id": int(i["reason"]),
            "uid": int(i["uid"]),
            "id": int(i["id"]),
        } for i in data]
    else:
        # transaction
        return [{
            "time": i["time"],
            "amount": int(i["add_num"]),
            "reason": reasons.get(int(i["reason"]), ""),
            "reason_id": int(i["reason"]),
            "uid": int(i["uid"]),
            "id": int(i["id"]),
        } for i in data]
