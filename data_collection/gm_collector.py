"""
GM Player Collector - Fetches Grandmaster and Challenger players from Riot API
"""
import os
import sys
import requests
import time
from typing import List, Dict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import RIOT_API_KEY, RATE_LIMIT_DELAY
from database.db_manager import db_manager


def fetch_challenger_players(api_key: str, region: str) -> List[Dict]:
    """
    Fetch Challenger league players for TFT
    
    Args:
        api_key: Riot API key
        region: Region (euw1, na1, etc.)
    
    Returns:
        List of player dictionaries
    """
    url = f"https://{region}.api.riotgames.com/tft/league/v1/challenger"
    headers = {"X-Riot-Token": api_key}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            entries = data.get('entries', [])
            print(f"✓ Found {len(entries)} Challenger players in {region.upper()}")
            return entries
        else:
            print(f"✗ Error fetching Challenger players: {response.status_code}")
            return []
    except Exception as e:
        print(f"✗ Exception: {e}")
        return []


def fetch_grandmaster_players(api_key: str, region: str) -> List[Dict]:
    """
    Fetch Grandmaster league players for TFT
    
    Args:
        api_key: Riot API key
        region: Region (euw1, na1, etc.)
    
    Returns:
        List of player dictionaries
    """
    url = f"https://{region}.api.riotgames.com/tft/league/v1/grandmaster"
    headers = {"X-Riot-Token": api_key}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            entries = data.get('entries', [])
            print(f"✓ Found {len(entries)} Grandmaster players in {region.upper()}")
            return entries
        else:
            print(f"✗ Error fetching Grandmaster players: {response.status_code}")
            return []
    except Exception as e:
        print(f"✗ Exception: {e}")
        return []


def fetch_summoner_by_id(api_key: str, region: str, summoner_id: str) -> Dict:
    """
    Fetch summoner details to get PUUID
    
    Args:
        api_key: Riot API Key
        region: Region
        summoner_id: Summoner ID from league entries
    
    Returns:
        Summoner data including PUUID
    """
    if not summoner_id:
        return {}
    
    url = f"https://{region}.api.riotgames.com/tft/summoner/v1/summoners/{summoner_id}"
    headers = {"X-Riot-Token": api_key}
    
    try:
        time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            # DEBUG: Print first error we encounter
            if not hasattr(fetch_summoner_by_id, '_logged_error'):
                print(f"  [DEBUG] Summoner endpoint returned {response.status_code} for ID: {summoner_id[:20]}")
                print(f"  [DEBUG] URL: {url}")
                print(f"  [DEBUG] Response: {response.text[:200]}")
                fetch_summoner_by_id._logged_error = True
            return {}
    except Exception as e:
        if not hasattr(fetch_summoner_by_id, '_logged_exception'):
            print(f"  [DEBUG] Exception on summoner endpoint: {e}")
            fetch_summoner_by_id._logged_exception = True
        return {}


def save_players_to_db(api_key: str, region: str, league_entries: List[Dict], 
                       tier: str, max_players: int = 100):
    """
    Save players to database
    
    Args:
        api_key: Riot API Key (not actually needed anymore!)
        region: Region
        league_entries: List of league entries from Riot API
        tier: CHALLENGER or GRANDMASTER
        max_players: Maximum number of players to save
    """
    print(f"\nSaving {tier} players to database...")
    saved_count = 0
    error_count = 0
    
    # Sort by LP descending to get the best players
    sorted_entries = sorted(league_entries, key=lambda x: x.get('leaguePoints', 0), reverse=True)
    
    for idx, entry in enumerate(sorted_entries[:max_players]):
        # TFT League API now includes PUUID directly in entries!
        puuid = entry.get('puuid')
        
        if not puuid:
            error_count += 1
            if error_count <= 3:
                print(f"  ✗ Entry #{idx} has no PUUID")
            continue
        
        lp = entry.get('leaguePoints', 0)
        rank = entry.get('rank', 'I')
        wins = entry.get('wins', 0)
        losses = entry.get('losses', 0)
        
        # We don't have game name from league endpoint, use a placeholder
        # This will be populated when we fetch match history
        game_name = f"{tier[:4]}_{idx}"
        tag_line = region.upper()
        
        # Save to database
        try:
            db_manager.add_player(
                puuid=puuid,
                game_name=game_name,
                tag_line=tag_line,
                tier=tier,
                rank=rank,
                lp=lp,
                region=region
            )
            saved_count += 1
            
            if (saved_count) % 10 == 0:
                print(f"  Saved {saved_count}/{max_players} players...")
        except Exception as e:
            print(f"  ✗ Error saving player: {e}")
            error_count += 1
    
    if error_count > 0 and error_count <= 3:
        print(f"  ⚠ {error_count} entries had no PUUID")
    elif error_count > 3:
        print(f"  ⚠ {error_count} entries had no PUUID")
    
    print(f"✓ Saved {saved_count}/{max_players} {tier} players from {region.upper()}")
    
    return saved_count


def collect_gm_players(api_key: str, region: str, include_challenger: bool = True,
                      include_grandmaster: bool = True, max_per_tier: int = 50):
    """
    Main function to collect GM+ players from a region
    
    Args:
        api_key: Riot API Key
        region: Region to collect from
        include_challenger: Whether to include Challenger players
        include_grandmaster: Whether to include Grandmaster players
        max_per_tier: Max players per tier to collect
    """
    print(f"\n{'='*60}")
    print(f"COLLECTING GM+ PLAYERS FROM {region.upper()}")
    print(f"{'='*60}\n")
    
    total_saved = 0
    
    if include_challenger:
        print("[1/2] Fetching Challenger players...")
        challenger_entries = fetch_challenger_players(api_key, region)
        if challenger_entries:
            saved = save_players_to_db(api_key, region, challenger_entries, 
                                      'CHALLENGER', max_per_tier)
            total_saved += saved
        time.sleep(2)  # Extra delay between tiers
    
    if include_grandmaster:
        print("\n[2/2] Fetching Grandmaster players...")
        gm_entries = fetch_grandmaster_players(api_key, region)
        if gm_entries:
            saved = save_players_to_db(api_key, region, gm_entries, 
                                      'GRANDMASTER', max_per_tier)
            total_saved += saved
    
    print(f"\n{'='*60}")
    print(f"✓ COLLECTION COMPLETE: {total_saved} players saved")
    print(f"{'='*60}\n")
    
    return total_saved


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Collect GM+ players for TFT Meta Tracker')
    parser.add_argument('--region', type=str, default='euw1', 
                       help='Region to collect from (euw1, na1, kr, etc.)')
    parser.add_argument('--max-per-tier', type=int, default=50,
                       help='Maximum players per tier to collect')
    parser.add_argument('--challenger-only', action='store_true',
                       help='Only collect Challenger players')
    parser.add_argument('--gm-only', action='store_true',
                       help='Only collect Grandmaster players')
    
    args = parser.parse_args()
    
    # Get API key from environment
    api_key = os.getenv('RIOT_API_KEY')
    if not api_key:
        print("✗ Error: RIOT_API_KEY not found in environment variables")
        print("  Please set it in your .env file")
        sys.exit(1)
    
    # Initialize database
    db_manager.init_db()
    
    # Collect players
    collect_gm_players(
        api_key=api_key,
        region=args.region,
        include_challenger=not args.gm_only,
        include_grandmaster=not args.challenger_only,
        max_per_tier=args.max_per_tier
    )
