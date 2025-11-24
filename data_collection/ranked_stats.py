import requests

def fetch_ranked_stats(api_key, region, summoner_id):
    """
    Fetch ranked stats for a summoner by ID (Summoner ID or PUUID)
    """
    url = f"https://{region}.api.riotgames.com/tft/league/v1/entries/by-summoner/{summoner_id}"
    headers = {"X-Riot-Token": api_key}
    r = requests.get(url, headers=headers, timeout=10)
    if r.ok:
        return r.json()
    return []
