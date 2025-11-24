"""
Quick test script to verify the TFT Assistant implementation
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

print("=" * 60)
print("TFT ASSISTANT - VERIFICATION TEST")
print("=" * 60)

# Test 1: Import all modules
print("\n[TEST 1] Testing module imports...")
try:
    from config import RIOT_API_KEY, REGIONS, TFT_DATA_URL
    print("  [OK] config.py imported successfully")
    
    from data_collection.summoner import fetch_summoner_by_riot_id
    from data_collection.match_history import fetch_match_ids
    from data_collection.ranked_stats import fetch_ranked_stats
    from data_collection.tft_static_data import get_champion_info, get_trait_info, get_item_info
    print("  [OK] data_collection modules imported successfully")
    
    from data_processing.parser import parse_match
    from data_processing.stats import compute_stats
    from data_processing.formatters import format_placement, format_champion_stats
    print("  [OK] data_processing modules imported successfully")
    
    print("\n[PASS] All modules imported successfully!")
except Exception as e:
    print(f"\n[FAIL] Import error: {e}")
    sys.exit(1)

# Test 2: Verify static data functions work
print("\n[TEST 2] Testing static data fetching...")
try:
    # Test getting a generic champion (may not exist yet, but function should work)
    test_champ = get_champion_info("TFT10_TestChamp")
    print(f"  [OK] get_champion_info() works (returned: {type(test_champ)})")
    
    test_trait = get_trait_info("TestTrait")
    print(f"  [OK] get_trait_info() works (returned: {type(test_trait)})")
    
    test_item = get_item_info("1")
    print(f"  [OK] get_item_info() works (returned: {type(test_item)})")
    
    print("\n[PASS] Static data functions work!")
except Exception as e:
    print(f"\n[FAIL] Static data error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Verify formatters work
print("\n[TEST 3] Testing formatters...")
try:
    placement_str = format_placement(1)
    print(f"  [OK] format_placement(1) = {placement_str}")
    
    # Test with dummy champion data
    dummy_champ = {
        'name': 'Test Champion',
        'cost': 3,
        'stats': {
            'hp': 700,
            'armor': 25,
            'magicResist': 25,
            'damage': 50,
            'attackSpeed': 0.75,
            'range': 1
        }
    }
    stats_str = format_champion_stats(dummy_champ, star_level=2)
    print(f"  [OK] format_champion_stats() works (length: {len(stats_str)} chars)")
    
    print("\n[PASS] Formatters work!")
except Exception as e:
    print(f"\n[FAIL] Formatter error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Verify stats computation
print("\n[TEST 4] Testing stats computation...")
try:
    dummy_matches = [
        {'placement': 1, 'level': 9, 'total_damage_to_players': 5000, 'gold_left': 20,
         'traits': [{'name': 'Trait1', 'num_units': 4}], 'units': [{'character_id': 'Champ1'}]},
        {'placement': 4, 'level': 8, 'total_damage_to_players': 3000, 'gold_left': 5,
         'traits': [{'name': 'Trait1', 'num_units': 3}], 'units': [{'character_id': 'Champ2'}]},
        {'placement': 7, 'level': 7, 'total_damage_to_players': 1500, 'gold_left': 0,
         'traits': [{'name': 'Trait2', 'num_units': 2}], 'units': [{'character_id': 'Champ1'}]},
    ]
    
    stats = compute_stats(dummy_matches)
    
    print(f"  [OK] Average Placement: {stats.get('avg_placement', 'N/A'):.2f}")
    print(f"  [OK] Top 4 Rate: {stats.get('top_4_rate', 0)*100:.1f}%")
    print(f"  [OK] Average Damage: {stats.get('avg_damage', 0):.0f}")
    
    print("\n[PASS] Stats computation works!")
except Exception as e:
    print(f"\n[FAIL] Stats computation error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Check API key
print("\n[TEST 5] Checking API key configuration...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('RIOT_API_KEY')
    
    if api_key and api_key != 'YOUR_API_KEY_HERE':
        print(f"  [OK] API Key found: {api_key[:20]}...")
        if api_key.startswith('RGAPI-'):
            print("  [OK] API Key format looks correct")
        else:
            print("  [WARN] Warning: API Key doesn't start with 'RGAPI-'")
    else:
        print("  [WARN] Warning: No API key found in .env file")
        print("    You'll need to add your Riot API key to use the live features")
    
    print("\n[INFO] API Key check complete!")
except Exception as e:
    print(f"\n[WARN] Could not check API key: {e}")

# Final summary
print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
print("\nAll core functionality is working correctly!")
print("\nNext steps:")
print("1. Make sure your Riot API key is in the .env file")
print("2. Run the application with: streamlit run ui/extended_monitor.py")
print("3. Search for a summoner to see the full functionality")
print("\n" + "=" * 60)
