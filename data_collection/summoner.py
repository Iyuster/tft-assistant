import requests
import os

def fetch_summoner_by_riot_id(api_key, region, routing, game_name, tag_line):
    url = f"https://{routing}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers, timeout=10)
    if response.ok:
        return response.json()
    return None

def fetch_summoner_details_by_puuid(api_key, region, puuid):
    # Try TFT endpoint first
    url_tft = f"https://{region}.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/{puuid}"
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url_tft, headers=headers, timeout=10)
    if response.ok:
        data = response.json()
        if data.get('id'):
            return data
            
    # Fallback to LoL endpoint
    url_lol = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    response = requests.get(url_lol, headers=headers, timeout=10)
    if response.ok:
        return response.json()
    return None
