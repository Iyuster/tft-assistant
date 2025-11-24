import requests

def fetch_match_ids(api_key, routing, puuid, count=20):
    url = f"https://{routing}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count={count}"
    headers = {"X-Riot-Token": api_key}
    r = requests.get(url, headers=headers, timeout=10)
    if r.ok:
        return r.json()
    return []

def fetch_match_details(api_key, routing, match_id):
    url = f"https://{routing}.api.riotgames.com/tft/match/v1/matches/{match_id}"
    headers = {"X-Riot-Token": api_key}
    r = requests.get(url, headers=headers, timeout=10)
    if r.ok:
        return r.json()
    return None
