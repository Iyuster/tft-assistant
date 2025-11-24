"""
Meta Report Generator - Get top compositions and meta statistics
"""
import os
import sys
from typing import List, Optional, Dict
from collections import Counter

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.db_manager import db_manager
from database.models import MetaStat, Composition
from config import MIN_GAMES_FOR_META


def update_meta_stats(min_games: int = MIN_GAMES_FOR_META, 
                     patch: Optional[str] = None,
                     region: Optional[str] = None):
    """
    Recalculate all meta statistics
    
    Args:
        min_games: Minimum games for a comp to be included
        patch: Filter by patch (None = all patches)
        region: Filter by region (None = all regions)
    """
    print(f"\nRecalculating meta statistics...")
    print(f"  Min games: {min_games}")
    print(f"  Patch: {patch or 'all'}")
    print(f"  Region: {region or 'ALL'}\n")
    
    meta_stats = db_manager.calculate_meta_stats(
        min_games=min_games,
        patch=patch,
        region=region
    )
    
    print(f"✓ Calculated stats for {len(meta_stats)} compositions")
    return meta_stats


def get_top_comps(limit: int = 20, min_games: int = MIN_GAMES_FOR_META,
                 patch: Optional[str] = None, region: Optional[str] = None,
                 order_by: str = 'top4_rate') -> List[MetaStat]:
    """
    Get top compositions
    
    Args:
        limit: Number of comps to return
        min_games: Minimum games played
        patch: Filter by patch
        region: Filter by region
        order_by: Metric to order by (top4_rate, top1_rate, play_count, avg_placement)
    
    Returns:
        List of MetaStat objects
    """
    return db_manager.get_top_comps(
        limit=limit,
        min_games=min_games,
        patch=patch,
        region=region,
        order_by=order_by
    )


def get_comp_details(comp_signature: str) -> Dict:
    """
    Get detailed information about a composition
    
    Args:
        comp_signature: Composition signature
    
    Returns:
        Dictionary with detailed comp info
    """
    compositions = db_manager.get_compositions_by_signature(comp_signature)
    
    if not compositions:
        return {}
    
    # Aggregate data from all instances of this comp
    all_units = []
    all_augments = []
    placements = []
    
    for comp in compositions:
        # Extract units
        for unit in comp.units or []:
            if isinstance(unit, dict):
                all_units.append(unit.get('character_id', 'Unknown'))
        
        # Extract augments
        for aug in comp.augments or []:
            all_augments.append(aug)
        
        # Get placement from participant
        if comp.participant:
            placements.append(comp.participant.placement)
    
    # Find most common units and augments
    unit_counter = Counter(all_units)
    augment_counter = Counter(all_augments)
    
    # Get primary traits from signature
    traits = comp_signature.split('+')
    
    return {
        'comp_signature': comp_signature,
        'primary_traits': traits,
        'core_units': unit_counter.most_common(8),  # Top 8 most used units
        'popular_augments': augment_counter.most_common(6),  # Top 6 augments
        'sample_count': len(compositions),
        'avg_placement': sum(placements) / len(placements) if placements else 0,
    }


def format_comp_for_display(meta_stat: MetaStat) -> Dict:
    """
    Format a MetaStat for display in UI
    
    Args:
        meta_stat: MetaStat object
    
    Returns:
        Formatted dictionary
    """
    return {
        'comp_name': meta_stat.comp_signature,
        'play_rate': f"{(meta_stat.play_count / get_total_games() * 100):.1f}%",
        'games': meta_stat.play_count,
        'top4_rate': f"{meta_stat.top4_rate * 100:.1f}%",
        'top1_rate': f"{meta_stat.top1_rate * 100:.1f}%",
        'avg_placement': f"{meta_stat.avg_placement:.2f}",
        'patch': meta_stat.patch,
        'region': meta_stat.region
    }


def get_total_games() -> int:
    """Get total number of games in database"""
    return db_manager.get_match_count()


def get_meta_summary() -> Dict:
    """Get summary of meta diversity and stats"""
    db_stats = db_manager.get_database_stats()
    
    # Get number of viable comps (50+ games)
    viable_comps = db_manager.get_top_comps(limit=1000, min_games=MIN_GAMES_FOR_META)
    
    return {
        'total_matches': db_stats['total_matches'],
        'total_players': db_stats['total_players'],
        'total_compositions': db_stats['total_compositions'],
        'viable_comps': len(viable_comps),
        'oldest_match': db_stats['oldest_match'],
        'newest_match': db_stats['newest_match']
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate TFT Meta Report')
    parser.add_argument('--update', action='store_true',
                       help='Recalculate meta statistics')
    parser.add_argument('--top', type=int, default=20,
                       help='Number of top comps to show')
    parser.add_argument('--min-games', type=int, default=MIN_GAMES_FOR_META,
                       help='Minimum games for a comp')
    parser.add_argument('--patch', type=str, default=None,
                       help='Filter by patch')
    parser.add_argument('--region', type=str, default=None,
                       help='Filter by region')
    parser.add_argument('--order-by', type=str, default='top4_rate',
                       choices=['top4_rate', 'top1_rate', 'play_count', 'avg_placement'],
                       help='Metric to order by')
    
    args = parser.parse_args()
    
    # Initialize database
    db_manager.init_db()
    
    # Update stats if requested
    if args.update:
        update_meta_stats(
            min_games=args.min_games,
            patch=args.patch,
            region=args.region
        )
    
    # Get and display top comps
    print(f"\n{'='*80}")
    print(f"TOP {args.top} COMPOSITIONS (ordered by {args.order_by})")
    print(f"{'='*80}\n")
    
    top_comps = get_top_comps(
        limit=args.top,
        min_games=args.min_games,
        patch=args.patch,
        region=args.region,
        order_by=args.order_by
    )
    
    if not top_comps:
        print("No compositions found with the specified criteria")
        print("Try running data collection first or lowering min_games")
    else:
        print(f"{'#':<4} {'Composition':<50} {'Games':<8} {'Top4%':<8} {'Top1%':<8} {'AvgPlace':<10}")
        print("-" * 80)
        
        for idx, comp in enumerate(top_comps, 1):
            formatted = format_comp_for_display(comp)
            print(f"{idx:<4} {formatted['comp_name']:<50} {formatted['games']:<8} "
                  f"{formatted['top4_rate']:<8} {formatted['top1_rate']:<8} {formatted['avg_placement']:<10}")
    
    # Show summary
    summary = get_meta_summary()
    print(f"\n{'='*80}")
    print("META SUMMARY")
    print(f"{'='*80}")
    print(f"Total Matches: {summary['total_matches']}")
    print(f"Total Players Tracked: {summary['total_players']}")
    print(f"Viable Compositions: {summary['viable_comps']}")
    print(f"{'='*80}\n")
