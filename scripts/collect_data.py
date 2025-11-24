"""
Main script to collect data for Meta Tracker
Orchestrates the entire data collection pipeline
"""
import os
import sys
import argparse
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data_collection.gm_collector import collect_gm_players
from data_collection.batch_match_collector import collect_matches_batch
from meta_analysis.meta_report import update_meta_stats
from database.db_manager import db_manager
from config import GM_PLAYERS_PER_REGION, MATCHES_PER_PLAYER, MIN_GAMES_FOR_META


def main():
    parser = argparse.ArgumentParser(
        description='TFT Meta Tracker - Data Collection Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect data from EUW (50 players, 20 matches each)
  python collect_data.py --region euw1 --players 50 --matches 20
  
  # Collect from multiple regions
  python collect_data.py --region euw1 na1 kr --players 30
  
  # Full pipeline: collect players, matches, and update meta
  python collect_data.py --region euw1 --full-pipeline
        """
    )
    
    parser.add_argument('--region', type=str, nargs='+', default=['euw1'],
                       help='Region(s) to collect from (can specify multiple)')
    parser.add_argument('--players', type=int, default=50,
                       help=f'Players per tier to collect (default: 50, max recommended: {GM_PLAYERS_PER_REGION})')
    parser.add_argument('--matches', type=int, default=MATCHES_PER_PLAYER,
                       help=f'Matches per player to collect (default: {MATCHES_PER_PLAYER})')
    parser.add_argument('--skip-players', action='store_true',
                       help='Skip player collection (use existing players in DB)')
    parser.add_argument('--skip-matches', action='store_true',
                       help='Skip match collection')
    parser.add_argument('--skip-meta-update', action='store_true',
                       help='Skip meta statistics update')
    parser.add_argument('--full-pipeline', action='store_true',
                       help='Run full pipeline: collect players, matches, and update meta')
    parser.add_argument('--challenger-only', action='store_true',
                       help='Only collect Challenger players')
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('RIOT_API_KEY')
    
    if not api_key:
        print("✗ Error: RIOT_API_KEY not found in environment variables")
        print("  Please set it in your .env file")
        return 1
    
    # Initialize database
    print("\nInitializing database...")
    db_manager.init_db()
    
    regions = args.region if isinstance(args.region, list) else [args.region]
    
    print(f"\n{'='*70}")
    print(f"TFT META TRACKER - DATA COLLECTION")
    print(f"{'='*70}")
    print(f"Regions: {', '.join(r.upper() for r in regions)}")
    print(f"Players per tier: {args.players}")
    print(f"Matches per player: {args.matches}")
    print(f"{'='*70}\n")
    
    # Step 1: Collect Players
    if not args.skip_players:
        for region in regions:
            print(f"\n[STEP 1/{len(regions)}] Collecting GM+ players from {region.upper()}...")
            collect_gm_players(
                api_key=api_key,
                region=region,
                include_challenger=True,
                include_grandmaster=not args.challenger_only,
                max_per_tier=args.players
            )
    else:
        print("\n[STEP 1] Skipping player collection\n")
    
    # Step 2: Collect Matches
    if not args.skip_matches:
        for region in regions:
            print(f"\n[STEP 2/{len(regions)}] Collecting matches from {region.upper()}...")
            collect_matches_batch(
                api_key=api_key,
                region=region,
                max_players=None,  # Process all players in DB
                matches_per_player=args.matches
            )
    else:
        print("\n[STEP 2] Skipping match collection\n")
    
    # Step 3: Update Meta Statistics
    if not args.skip_meta_update or args.full_pipeline:
        print("\n[STEP 3] Updating meta statistics...")
        update_meta_stats(min_games=MIN_GAMES_FOR_META)
    else:
        print("\n[STEP 3] Skipping meta update\n")
    
    # Final summary
    db_stats = db_manager.get_database_stats()
    
    print(f"\n{'='*70}")
    print(f"COLLECTION COMPLETE - DATABASE SUMMARY")
    print(f"{'='*70}")
    print(f"Total Players: {db_stats['total_players']}")
    print(f"Total Matches: {db_stats['total_matches']}")
    print(f"Total Compositions: {db_stats['total_compositions']}")
    print(f"Meta Stats Entries: {db_stats['total_meta_stats']}")
    print(f"{'='*70}\n")
    
    print("✓ Data collection pipeline complete!")
    print(f"✓ Run the Streamlit app to view meta report: streamlit run ui/extended_monitor.py")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n✗ Collection interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
