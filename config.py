"""
Configuración centralizada para TFT Assistant
"""
import os

# Riot API Configuration
RIOT_API_KEY = os.getenv('RIOT_API_KEY')

# Regiones disponibles
REGIONS = {
    'euw1': 'Europe West',
    'na1': 'North America',
    'kr': 'Korea',
    'eune1': 'Europe Nordic & East',
    'br1': 'Brazil',
    'la1': 'Latin America North',
    'la2': 'Latin America South',
    'oc1': 'Oceania',
    'tr1': 'Turkey',
    'ru': 'Russia',
    'jp1': 'Japan'
}

# Routings para diferentes endpoints
ROUTINGS = {
    'europe': ['euw1', 'eune1', 'tr1', 'ru'],
    'americas': ['na1', 'br1', 'la1', 'la2'],
    'asia': ['kr', 'jp1'],
    'sea': ['oc1']
}

# Data Dragon URLs
DATA_DRAGON_BASE_URL = "https://ddragon.leagueoflegends.com"
DATA_DRAGON_CDN = f"{DATA_DRAGON_BASE_URL}/cdn"
CDRAGON_BASE_URL = "https://raw.communitydragon.org"

# TFT específico - Community Dragon tiene mejores datos de TFT
TFT_DATA_URL = "https://raw.communitydragon.org/latest/cdragon/tft"

# Caché local
CACHE_DIR = os.path.join(os.path.dirname(__file__), '.cache')
os.makedirs(CACHE_DIR, exist_ok=True)

# Configuración de la aplicación
APP_TITLE = "TFT Assistant - Summoner Dashboard"
MAX_MATCHES = 20
DEFAULT_REGION = "euw1"
DEFAULT_ROUTING = "europe"

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(os.path.dirname(__file__), "tft_meta.db")}')
DATABASE_DIR = os.path.join(os.path.dirname(__file__), 'database')

# Meta Tracker Settings
MIN_GAMES_FOR_META = 50  # Mínimo de partidas para considerar una comp en el meta
GM_PLAYERS_PER_REGION = 100  # Jugadores GM+ a trackear por región
MATCHES_PER_PLAYER = 20  # Partidas a recopilar por jugador
DATA_RETENTION_DAYS = 30  # Días de datos históricos a mantener
RATE_LIMIT_DELAY = 1.2  # Segundos entre requests para respetar rate limits

