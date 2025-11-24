import pandas as pd

def compute_stats(match_records):
    """
    Compute aggregated statistics from match records
    """
    df = pd.DataFrame(match_records)
    if df.empty:
        return {}
    
    stats = {}
    
    # Placement stats
    if "placement" in df.columns:
        stats["avg_placement"] = df["placement"].mean()
        stats["top_4_rate"] = (df["placement"] <= 4).mean()
        stats["top_1_rate"] = (df["placement"] == 1).mean()
        stats["bot_4_rate"] = (df["placement"] >= 5).mean()
    
    # Level stats
    if "level" in df.columns:
        stats["avg_level"] = df["level"].mean()
    
    # Damage stats
    if "total_damage_to_players" in df.columns:
        stats["avg_damage"] = df["total_damage_to_players"].mean()
        stats["total_damage"] = df["total_damage_to_players"].sum()
    
    # Gold stats
    if "gold_left" in df.columns:
        stats["avg_gold_left"] = df["gold_left"].mean()
    
    # Most used traits
    if "traits" in df.columns:
        all_traits = []
        for traits_list in df["traits"]:
            if isinstance(traits_list, list):
                for trait in traits_list:
                    if isinstance(trait, dict):
                        all_traits.append(trait.get("name", "Unknown"))
        
        if all_traits:
            trait_counts = pd.Series(all_traits).value_counts()
            stats["most_used_traits"] = trait_counts.head(5).to_dict()
    
    # Most used champions
    if "units" in df.columns:
        all_champions = []
        for units_list in df["units"]:
            if isinstance(units_list, list):
                for unit in units_list:
                    if isinstance(unit, dict):
                        all_champions.append(unit.get("character_id", "Unknown"))
        
        if all_champions:
            champ_counts = pd.Series(all_champions).value_counts()
            stats["most_used_champions"] = champ_counts.head(5).to_dict()
    
    return stats
