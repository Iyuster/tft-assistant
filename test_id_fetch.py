import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.getenv('RIOT_API_KEY')
region = 'euw1'
routing = 'europe'
game_name = 'Iyuster'
tag_line = 'TETON'

headers = {"X-Riot-Token": api_key}

def print_json(label, data):
    print(f"\n=== {label} ===")
    print(json.dumps(data, indent=2))

# 1. Skip Account V1 (it was failing with 404, maybe encoding), use known PUUID from logs
puuid = "qVDwywLW-Gv5l_4vx-ccMIF3OqxBKmZpGdTIyIwEfuQgDHEkLzjaMGXkiyWvD_KpX6TudLhn6CTbuw"
print(f"Using PUUID: {puuid}")

# 2. Try Summoner V4 (LoL)
url_sum_lol = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
r_sum_lol = requests.get(url_sum_lol, headers=headers)
if r_sum_lol.ok:
    print_json("Summoner V4 (LoL)", r_sum_lol.json())
else:
    print(f"Error Summoner V4: {r_sum_lol.status_code}")

# 3. Try TFT Summoner V1
url_sum_tft = f"https://{region}.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/{puuid}"
r_sum_tft = requests.get(url_sum_tft, headers=headers)
if r_sum_tft.ok:
    print_json("TFT Summoner V1", r_sum_tft.json())
else:
    print(f"Error TFT Summoner V1: {r_sum_tft.status_code}")

# 4. Try Match History to find ID
url_matches = f"https://{routing}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count=1"
r_matches = requests.get(url_matches, headers=headers)
if r_matches.ok:
    match_ids = r_matches.json()
    print(f"\nMatch IDs: {match_ids}")
    
    if match_ids:
        url_match_detail = f"https://{routing}.api.riotgames.com/tft/match/v1/matches/{match_ids[0]}"
        r_detail = requests.get(url_match_detail, headers=headers)
        if r_detail.ok:
            match_data = r_detail.json()
            # Find our participant
            for p in match_data['info']['participants']:
                if p['puuid'] == puuid:
                    print_json("Participant Data in Match", p)
                    print(f"\n>>> FOUND SUMMONER ID: {p.get('summonerId')}")
                    
                    if p.get('summonerId'):
                        sid = p.get('summonerId')
                        url_ranked = f"https://{region}.api.riotgames.com/tft/league/v1/entries/by-summoner/{sid}"
                        r_ranked = requests.get(url_ranked, headers=headers)
                        if r_ranked.ok:
                            print_json("Ranked Stats (Success!)", r_ranked.json())
                        else:
                            print(f"Error Ranked Stats: {r_ranked.status_code} - {r_ranked.text}")
                    else:
                        print("Summoner ID is None in match history.")
                    break

# 5. Try Undocumented Endpoint: by-puuid
print("\n=== Testing Undocumented Endpoint: by-puuid ===")
url_undoc = f"https://{region}.api.riotgames.com/tft/league/v1/entries/by-puuid/{puuid}"
r_undoc = requests.get(url_undoc, headers=headers)
if r_undoc.ok:
    print_json("Undocumented Endpoint Success!", r_undoc.json())
else:
    print(f"Undocumented Endpoint Failed: {r_undoc.status_code} - {r_undoc.text}")

# 6. Try LoL League Endpoint (by-puuid) to extract Summoner ID
print("\n=== Testing LoL League Endpoint: by-puuid ===")
url_lol_league = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"
r_lol = requests.get(url_lol_league, headers=headers)
if r_lol.ok:
    lol_data = r_lol.json()
    print_json("LoL League Data", lol_data)
    if lol_data and len(lol_data) > 0:
        extracted_id = lol_data[0].get('summonerId')
        print(f"\n>>> FOUND SUMMONER ID FROM LOL: {extracted_id}")
        
        # Try TFT stats with this ID
        if extracted_id:
            url_ranked = f"https://{region}.api.riotgames.com/tft/league/v1/entries/by-summoner/{extracted_id}"
            r_ranked = requests.get(url_ranked, headers=headers)
            if r_ranked.ok:
                print_json("Ranked Stats (Success via LoL ID!)", r_ranked.json())
else:
    print(f"LoL League Endpoint Failed: {r_lol.status_code} - {r_lol.text}")

# 7. Try High Elo Leagues (Challenger/GM/Master) - Last Resort
print("\n=== Testing High Elo Leagues Search ===")
tiers = ['challenger', 'grandmaster', 'master']
found_in_high_elo = False

for tier in tiers:
    print(f"Checking {tier}...")
    url_league = f"https://{region}.api.riotgames.com/tft/league/v1/{tier}"
    r_league = requests.get(url_league, headers=headers)
    if r_league.ok:
        data = r_league.json()
        for entry in data.get('entries', []):
            if entry.get('summonerName', '').lower() == 'iyuster':
                 print_json(f"Found in {tier}!", entry)
                 found_in_high_elo = True
                 sid = entry.get('summonerId')
                 print(f">>> FOUND SUMMONER ID IN HIGH ELO: {sid}")
                 break
    if found_in_high_elo:
        break

if not found_in_high_elo:
    print("Not found in High Elo leagues.")

# 8. Try Old Matches (Archeology Strategy)
# Maybe older matches still have the summonerId?
print("\n=== Testing Archeology Strategy (Old Matches) ===")
import time
six_months_ago = int(time.time()) - (180 * 24 * 60 * 60)
url_old_matches = f"https://{routing}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count=1&startTime={six_months_ago}&endTime={int(time.time()) - (60*24*60*60)}" # Matches between 6 months and 2 months ago
r_old = requests.get(url_old_matches, headers=headers)

if r_old.ok:
    old_ids = r_old.json()
    print(f"Old Match IDs found: {old_ids}")
    if old_ids:
        url_detail = f"https://{routing}.api.riotgames.com/tft/match/v1/matches/{old_ids[0]}"
        r_detail = requests.get(url_detail, headers=headers)
        if r_detail.ok:
             match_data = r_detail.json()
             for p in match_data['info']['participants']:
                if p['puuid'] == puuid:
                    sid = p.get('summonerId')
                    print(f">>> FOUND SUMMONER ID IN OLD MATCH: {sid}")
                    if sid:
                        # Verify it works
                        url_ranked = f"https://{region}.api.riotgames.com/tft/league/v1/entries/by-summoner/{sid}"
                        r_ranked = requests.get(url_ranked, headers=headers)
                        if r_ranked.ok:
                            print_json("Ranked Stats (Success via Archeology!)", r_ranked.json())
                    break
else:
    print(f"Old Matches Search Failed: {r_old.status_code}")

# 9. Try Indirect Route: PUUID -> AccountID -> SummonerID
print("\n=== Testing Indirect Route (PUUID -> AccountID -> SummonerID) ===")
# First, get accountId from the response we already got (or get it again)
url_sum_lol = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
r_sum = requests.get(url_sum_lol, headers=headers)
if r_sum.ok:
    data = r_sum.json()
    acc_id = data.get('accountId')
    print(f"Account ID found: {acc_id}")
    
    if acc_id:
        # Now try by-account endpoint
        url_by_acc = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-account/{acc_id}"
        r_acc_id = requests.get(url_by_acc, headers=headers)
        if r_acc_id.ok:
            acc_data = r_acc_id.json()
            print_json("By-Account Response", acc_data)
            sid = acc_data.get('id')
            print(f">>> FOUND SUMMONER ID VIA ACCOUNT-ID: {sid}")
            
            if sid:
                 # Verify it works
                url_ranked = f"https://{region}.api.riotgames.com/tft/league/v1/entries/by-summoner/{sid}"
                r_ranked = requests.get(url_ranked, headers=headers)
                if r_ranked.ok:
                    print_json("Ranked Stats (Success via AccountID!)", r_ranked.json())
        else:
            print(f"By-Account Endpoint Failed: {r_acc_id.status_code}")
    else:
        print("No Account ID in summoner response.")
else:
    print(f"Initial Summoner Fetch Failed: {r_sum.status_code}")
