def parse_match(match_json, puuid):
    """
    Parse match data for a specific player (by PUUID)
    Returns detailed information about the match including units, traits, augments, and stats
    """
    for participant in match_json.get('info', {}).get('participants', []):
        if participant.get('puuid') == puuid:
            # Parse units with detailed information
            units_data = []
            for unit in participant.get("units", []):
                units_data.append({
                    "character_id": unit.get("character_id"),
                    "tier": unit.get("tier"),  # Stars (1, 2, 3)
                    "items": unit.get("itemNames", []),
                    "rarity": unit.get("rarity", unit.get("cost", 0)),
                })
            
            # Parse traits with activation info
            traits_data = []
            for trait in participant.get("traits", []):
                if trait.get("num_units", 0) > 0:  # Solo traits activos
                    traits_data.append({
                        "name": trait.get("name"),
                        "num_units": trait.get("num_units"),
                        "tier_current": trait.get("tier_current"),
                        "tier_total": trait.get("tier_total"),
                        "style": trait.get("style", 0)  # 0=no active, 1=bronze, 2=silver, 3=gold, 4=chromatic
                    })
            
            # Parse augments (solo los nombres)
            augments_list = participant.get("augments", [])
            
            return {
                "match_id": match_json.get('metadata', {}).get('match_id'),
                "game_datetime": match_json.get('info', {}).get('game_datetime'),
                "game_length": match_json.get('info', {}).get('game_length'),
                "tft_set_number": match_json.get('info', {}).get('tft_set_number'),
                "placement": participant.get("placement"),
                "level": participant.get("level"),
                "gold_left": participant.get("gold_left"),
                "players_eliminated": participant.get("players_eliminated", 0),
                "total_damage_to_players": participant.get("total_damage_to_players", 0),
                "time_eliminated": participant.get("time_eliminated", 0.0),
                "units": units_data,
                "traits": traits_data,
                "augments": augments_list,
                "companion": participant.get("companion", {})
            }
    return {}


def parse_all_participants(match_json):
    """
    Parse all participants in a match for leaderboard view
    """
    participants = []
    for p in match_json.get('info', {}).get('participants', []):
        participants.append({
            "puuid": p.get("puuid"),
            "placement": p.get("placement"),
            "level": p.get("level"),
            "last_round": p.get("last_round"),
        })
    return sorted(participants, key=lambda x: x['placement'])
