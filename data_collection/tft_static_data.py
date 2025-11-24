"""
Módulo para obtener datos estáticos de TFT desde Community Dragon API
"""
import requests
import json
import os
from typing import Dict, List, Optional

# Usar el cache del config
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import CACHE_DIR, TFT_DATA_URL

# URLs de Community Dragon (tienen datos más completos de TFT)
CDRAGON_TFT_BASE = "https://raw.communitydragon.org/latest/cdragon/tft/en_us"

class TFTStaticData:
    """Clase para manejar datos estáticos de TFT con caché"""
    
    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = cache_dir
        self.champions_cache = None
        self.traits_cache = None
        self.items_cache = None
        
    def _get_cached_or_fetch(self, cache_file: str, url: str) -> Optional[Dict]:
        """Obtiene datos del caché o los descarga si no existen"""
        cache_path = os.path.join(self.cache_dir, cache_file)
        
        # Intentar cargar desde caché
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache {cache_file}: {e}")
        
        # Si no existe en caché, descargar
        try:
            response = requests.get(url, timeout=30)
            if response.ok:
                data = response.json()
                # Guardar en caché
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return data
        except Exception as e:
            print(f"Error fetching data from {url}: {e}")
        
        return None
    
    def get_champions(self) -> Dict:
        """Obtiene información de todos los campeones de TFT"""
        if self.champions_cache is None:
            url = f"{CDRAGON_TFT_BASE}.json"
            data = self._get_cached_or_fetch('tft_champions.json', url)
            
            if data and 'setData' in data:
                # Procesar los datos para extraer campeones
                champions = {}
                for set_data in data.get('setData', []):
                    for champion in set_data.get('champions', []):
                        char_id = champion.get('character_id', champion.get('apiName', ''))
                        champions[char_id] = {
                            'name': champion.get('name', ''),
                            'cost': champion.get('cost', 0),
                            'traits': champion.get('traits', []),
                            'stats': champion.get('stats', {}),
                            'ability': champion.get('ability', {}),
                            'icon': champion.get('icon', '')
                        }
                self.champions_cache = champions
            else:
                self.champions_cache = {}
        
        return self.champions_cache
    
    def get_traits(self) -> Dict:
        """Obtiene información de todos los traits de TFT"""
        if self.traits_cache is None:
            url = f"{CDRAGON_TFT_BASE}.json"
            data = self._get_cached_or_fetch('tft_traits.json', url)
            
            if data and 'setData' in data:
                traits = {}
                for set_data in data.get('setData', []):
                    for trait in set_data.get('traits', []):
                        trait_id = trait.get('apiName', trait.get('name', ''))
                        traits[trait_id] = {
                            'name': trait.get('name', ''),
                            'description': trait.get('desc', ''),
                            'effects': trait.get('effects', []),
                            'icon': trait.get('icon', '')
                        }
                self.traits_cache = traits
            else:
                self.traits_cache = {}
        
        return self.traits_cache
    
    def get_items(self) -> Dict:
        """Obtiene información de todos los items de TFT"""
        if self.items_cache is None:
            url = f"{CDRAGON_TFT_BASE}.json"
            data = self._get_cached_or_fetch('tft_items.json', url)
            
            if data and 'items' in data:
                items = {}
                for item in data.get('items', []):
                    item_id = item.get('id', item.get('apiName', ''))
                    items[item_id] = {
                        'name': item.get('name', ''),
                        'description': item.get('desc', ''),
                        'icon': item.get('icon', ''),
                        'from': item.get('from', None)
                    }
                self.items_cache = items
            else:
                self.items_cache = {}
        
        return self.items_cache
    
    def get_champion_by_id(self, champion_id: str) -> Optional[Dict]:
        """Obtiene información de un campeón específico"""
        champions = self.get_champions()
        # Buscar con ID exacto o parcial (sin el prefijo TFT#_)
        for key, value in champions.items():
            if champion_id in key or key in champion_id:
                return value
        return None
    
    def get_trait_by_id(self, trait_id: str) -> Optional[Dict]:
        """Obtiene información de un trait específico"""
        traits = self.get_traits()
        for key, value in traits.items():
            if trait_id in key or key in trait_id:
                return value
        return None
    
    def get_item_by_id(self, item_id: str) -> Optional[Dict]:
        """Obtiene información de un item específico"""
        items = self.get_items()
        # Los items pueden venir como números o strings
        item_str = str(item_id)
        for key, value in items.items():
            if item_str in str(key) or str(key) in item_str:
                return value
        return None


# Instancia global para usar en toda la aplicación
tft_data = TFTStaticData()


def get_champion_info(champion_id: str) -> Dict:
    """Función helper para obtener info de campeón"""
    info = tft_data.get_champion_by_id(champion_id)
    return info if info else {
        'name': champion_id,
        'cost': 0,
        'traits': [],
        'stats': {},
        'ability': {}
    }


def get_trait_info(trait_id: str) -> Dict:
    """Función helper para obtener info de trait"""
    info = tft_data.get_trait_by_id(trait_id)
    return info if info else {
        'name': trait_id,
        'description': '',
        'effects': []
    }


def get_item_info(item_id: str) -> Dict:
    """Función helper para obtener info de item"""
    info = tft_data.get_item_by_id(item_id)
    return info if info else {
        'name': item_id,
        'description': '',
        'icon': ''
    }
