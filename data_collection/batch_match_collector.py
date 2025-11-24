"""
Batch Match Collector - Collects matches from multiple players and saves to database
"""
import os
import sys
import time
from typing import List, Optional
from tqdm import tqdm

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import RIOT_API_KEY, RATE_LIMIT_DELAY, MATCHES_PER_PLAYER
from data_collection.match_history import fetch_match_ids, fetch_match_details
from data_processing.parser import parse_match, parse_all_participants
from database.db_manager import db_manager


def get_routing_for_region(region: str) -> str:
    """Get routing value for a region"""
    routing_map = {
        'euw1': 'europe', 'eune1': 'europe', 'tr1': 'europe', 'ru': 'europe',
        'na1': 'americas', 'br1': 'americas', 'la1': 'americas', 'la2': 'americas',
        'kr': 'asia', 'jp1': 'asia',
        'oc1': 'sea'
    }
    return routing_map.get(region.lower(), 'europe')


def collect_matches_for_player(api_key: str, puuid: str, region: str, 
                               matches_per_player: int = 20) -> int:
    """
    Collect matches for a single player and save to database
    
    Args:
        api_key: Riot API Key
        puuid: Player PUUID
        region: Region
        matches_per_player: Number of matches to collect
    
    Returns:
        Number of new matches saved
    """
    routing = get_routing_for_region(region)
    new_matches = 0
    
    # Get match IDs
    match_ids = fetch_match_ids(api_key, routing, puuid, count=matches_per_player)
    
    if not match_ids:
        return 0
    
    for match_id in match_ids:
        # Check if match already exists
        if db_manager.match_exists(match_id):
            continue  # Skip already collected matches
        
        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)
        
        # Fetch match details
        match_detail = fetch_match_details(api_key, routing, match_id)
        
        if not match_detail:
            continue
        
        # Parse match info
        match_info = match_detail.get('info', {})
        metadata = match_detail.get('metadata', {})
        
        # Extract all participants
        all_participants = []
        for participant_data in match_info.get('participants', []):
            participant_puuid = participant_data.get('puuid')
            
            # Parse participant data
            parsed = parse_match(match_detail, participant_puuid)
            if parsed:
                all_participants.append({
                    'puuid': participant_puuid,
                    'placement': parsed.get('placement'),
                    'level': parsed.get('level'),
                    'gold_left': parsed.get('gold_left'),
                    'total_damage_to_players': parsed.get('total_damage_to_players', 0),
                    'players_eliminated': parsed.get('players_eliminated', 0),
                    'time_eliminated': parsed.get('time_eliminated', 0.0),
                    'traits': parsed.get('traits', []),
                    'units': parsed.get('units', []),
                    'augments': parsed.get('augments', [])
                })
        
        # Prepare match data for database
        match_data = {
            'match_id': metadata.get('match_id'),
            'game_datetime': match_info.get('game_datetime'),
            'game_length': match_info.get('game_length', 0),
            'tft_set_number': match_info.get('tft_set_number', 0),
            'patch': _extract_patch(match_info.get('game_version', '')),
            'region': region,
            'participants': all_participants
        }
        
        # Save to database
        if db_manager.add_match(match_data):
            new_matches += 1
    
    return new_matches


def _extract_patch(game_version: str) -> str:
    """
    Extract patch number from game version string
    Example: "Version 13.24.520.9150 (Dec 06 2023/13:57:32) [PUBLIC]" -> "13.24"
    """
    if not game_version:
        return "unknown"
    
    try:
        # Extract the version number
        parts = game_version.split('.')
        if len(parts) >= 2:
            return f"{parts[0].split()[-1]}.{parts[1]}"
    except:
        pass
    
    return "unknown"


def collect_matches_batch(api_key: str, region: str, max_players: Optional[int] = None,
                         matches_per_player: int = MATCHES_PER_PLAYER):
    """
    Collect matches for all players in database from a specific region
    
    Args:
        api_key: Riot API Key
        region: Region to collect from
        max_players: Maximum number of players to process (None = all)
        matches_per_player: Number of matches per player
    """
    print(f"\n{'='*60}")
    print(f"BATCH MATCH COLLECTION - {region.upper()}")
    print(f"{'='*60}\n")
    
    # Get all players from this region
    players = db_manager.get_all_players(region=region)
    
    if not players:
        print(f"✗ No players found in database for region {region}")
        print("  Run gm_collector.py first to add players")
        return
    
    if max_players:
        players = players[:max_players]
    
    print(f"Found {len(players)} players in database")
    print(f"Collecting {matches_per_player} matches per player...\n")
    
    total_new_matches = 0
    total_skipped = 0
    
    # Process each player with progress bar
    with tqdm(total=len(players), desc="Processing players") as pbar:
        for player in players:
            pbar.set_description(f"Player: {player.game_name[:15]}")
            
            try:
                new_matches = collect_matches_for_player(
                    api_key=api_key,
                    puuid=player.puuid,
                    region=region,
                    matches_per_player=matches_per_player
                )
                
                total_new_matches += new_matches
                total_skipped += (matches_per_player - new_matches)
                
                pbar.set_postfix({
                    'new': total_new_matches,
                    'skipped': total_skipped
                })
            except Exception as e:
                pbar.write(f"✗ Error processing {player.game_name}: {e}")
            
            pbar.update(1)
    
    print(f"\n{'='*60}")
    print(f"✓ COLLECTION COMPLETE")
    print(f"  New matches: {total_new_matches}")
    print(f"  Skipped (already in DB): {total_skipped}")
    print(f"  Total matches in DB: {db_manager.get_match_count()}")
    print(f"{'='*60}\n")
    
    return total_new_matches


if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv
    
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='Collect matches for TFT Meta Tracker')
    parser.add_argument('--region', type=str, default='euw1',
                       help='Region to collect from (euw1, na1, kr, etc.)')
    parser.add_argument('--max-players', type=int, default=None,
                       help='Maximum number of players to process')
    parser.add_argument('--matches-per-player', type=int, default=MATCHES_PER_PLAYER,
                       help='Number of matches per player')
    
    args = parser.parse_args()
    
    # Get API key
    api_key = os.getenv('RIOT_API_KEY')
    if not api_key:
        print("✗ Error: RIOT_API_KEY not found in environment variables")
        sys.exit(1)
    
    # Initialize database
    db_manager.init_db()
    
    # Collect matches
    collect_matches_batch(
        api_key=api_key,
        region=args.region,
        max_players=args.max_players,
        matches_per_player=args.matches_per_player
    )
