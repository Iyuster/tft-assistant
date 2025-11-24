"""
Formatters para mostrar datos de TFT de forma estetica en la UI
"""
import re
from typing import Dict, List


def format_ability_description(ability_data: Dict) -> str:
    """
    Formatea la descripción de una habilidad con sus stats
    """
    if not ability_data:
        return "No ability data available"
    
    name = ability_data.get('name', 'Unknown Ability')
    desc = ability_data.get('desc', ability_data.get('description', ''))
    
    # Limpiar HTML tags básicos si existen
    desc = re.sub(r'<[^>]+>', '', desc)
    
    # Variables de la habilidad
    variables = ability_data.get('variables', [])
    
    result = f"**{name}**\n\n{desc}"
    
    if variables:
        result += "\n\n**Scaling:**"
        for var in variables:
            var_name = var.get('name', '')
            values = var.get('value', [])
            if values:
                result += f"\n- {var_name}: {' / '.join(map(str, values))}"
    
    return result


def format_trait_description(trait_data: Dict) -> str:
    """
    Formatea la descripción de un trait con sus breakpoints
    """
    if not trait_data:
        return "No trait data available"
    
    name = trait_data.get('name', 'Unknown Trait')
    desc = trait_data.get('description', '')
    
    # Limpiar HTML
    desc = re.sub(r'<[^>]+>', '', desc)
    
    result = f"**{name}**\n\n{desc}"
    
    # Añadir breakpoints si existen
    effects = trait_data.get('effects', [])
    if effects:
        result += "\n\n**Breakpoints:**"
        for effect in effects:
            min_units = effect.get('minUnits', 0)
            max_units = effect.get('maxUnits', 0)
            style = effect.get('style', 0)
            
            # Determinar el estilo (bronze, silver, gold, chromatic)
            style_names = ['Inactive', 'Bronze', 'Silver', 'Gold', 'Chromatic']
            style_name = style_names[min(style, 4)]
            
            if max_units > min_units:
                result += f"\n- **{min_units}**: {style_name}"
            else:
                result += f"\n- **{min_units}**: {style_name}"
    
    return result


def format_champion_stats(champion_data: Dict, star_level: int = 1) -> str:
    """
    Formatea las stats de un campeón según su nivel de estrellas
    """
    if not champion_data:
        return "No champion data available"
    
    name = champion_data.get('name', 'Unknown Champion')
    cost = champion_data.get('cost', 0)
    
    stats = champion_data.get('stats', {})
    
    # Stats base
    hp = stats.get('hp', 0)
    armor = stats.get('armor', 0)
    mr = stats.get('magicResist', 0)
    ad = stats.get('damage', 0)
    attack_speed = stats.get('attackSpeed', 1.0)
    crit_chance = stats.get('critChance', 0)
    crit_multiplier = stats.get('critMultiplier', 1.5)
    range_val = stats.get('range', 1)
    mana_start = stats.get('initialMana', 0)
    mana_max = stats.get('mana', 100)
    
    result = f"**{name}** ({'💰' * cost})\n\n"
    
    # Multiplicador por estrellas (aproximado)
    star_multiplier = 1.0 + (star_level - 1) * 0.8
    
    result += f"**Stats ({'⭐' * star_level}):**\n"
    result += f"- ❤️ HP: {int(hp * star_multiplier)}\n"
    result += f"- 🛡️ Armor: {armor}\n"
    result += f"- 🔮 MR: {mr}\n"
    result += f"- ⚔️ AD: {int(ad * star_multiplier)}\n"
    result += f"- ⚡ Attack Speed: {attack_speed:.2f}\n"
    result += f"- 🎯 Range: {range_val}\n"
    result += f"- 💙 Mana: {mana_start}/{mana_max}\n"
    
    if crit_chance > 0:
        result += f"- 💥 Crit: {crit_chance}% ({crit_multiplier}x)\n"
    
    return result


def format_item_description(item_data: Dict) -> str:
    """
    Formatea la descripción de un item
    """
    if not item_data:
        return "Unknown Item"
    
    name = item_data.get('name', 'Unknown Item')
    desc = item_data.get('description', '')
    
    # Limpiar HTML
    desc = re.sub(r'<[^>]+>', '', desc)
    
    result = f"**{name}**\n\n{desc}"
    
    return result


def format_placement(placement: int) -> str:
    """
    Formatea el placement con emoji/color
    """
    if placement == 1:
        return "🥇 1st"
    elif placement == 2:
        return "🥈 2nd"
    elif placement == 3:
        return "🥉 3rd"
    elif placement == 4:
        return "✅ 4th"
    elif placement <= 6:
        return f"⚠️ {placement}th"
    else:
        return f"❌ {placement}th"


def format_tier_name(tier: int) -> str:
    """
    Convierte tier number (1-4) a nombre y color
    """
    tier_map = {
        0: ("Not Active", "⚪"),
        1: ("Bronze", "🟤"),
        2: ("Silver", "⚪"),
        3: ("Gold", "🟡"),
        4: ("Chromatic", "🌈")
    }
    return tier_map.get(tier, ("Unknown", "❓"))


def format_match_summary(match_data: Dict) -> str:
    """
    Crea un resumen de una partida para mostrar en la lista
    """
    if not match_data:
        return "No match data"
    
    placement = match_data.get('placement', '?')
    level = match_data.get('level', '?')
    
    # Top traits
    traits = match_data.get('traits', [])
    active_traits = [t['name'] for t in sorted(traits, key=lambda x: x.get('style', 0), reverse=True)[:3]]
    traits_str = " + ".join(active_traits) if active_traits else "No traits"
    
    # Units count
    units_count = len(match_data.get('units', []))
    
    result = f"{format_placement(placement)} | Lvl {level} | {units_count} units | {traits_str}"
    
    return result


def get_trait_style_emoji(trait: Dict) -> str:
    """
    Obtiene un emoji basado en el estilo/tier del trait
    """
    emoji_map = {
        0: "⚪",  # None
        1: "🟤",  # Bronze
        2: "⚫",  # Silver
        3: "🟡",  # Gold
        4: "💎",  # Chromatic/Prismatic
    }
    
    # Handle both old and new API formats
    style = trait.get('style', 0)
    
    # If style is a dict (new format), extract tier_current
    if isinstance(style, dict):
        style = style.get('tier_current', 0)
    
    return emoji_map.get(style, "❓")
